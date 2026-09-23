"""Command-line entry point.

    python -m deep_question --excel data/base_questionnaire.xlsx --product Cancer \
        --channel facebook --applicant me --age 23-45 --gender female

    python -m deep_question --list-products                  # products + entry-age window + eligible brackets
    python -m deep_question --product Cancer --channel tiktok --applicant me --age 23-45 --gender male --dry-run
    python -m deep_question --product Senior55 --applicant other --age 60+ --channel facebook --gender female
    python -m deep_question --product Cancer                 # every eligible combo for one product
    python -m deep_question --yes                            # every eligible combo for every product

Factors describe the INSURED (age, gender) plus who is applying (--applicant me|other).
Age brackets: 0-22 | 23-45 | 46-60 | 60+
Omitted factors expand to all values, then impossible combos are pruned: brackets outside the product's
entry-age window (products sheet min_age/max_age) and "me" for brackets too young to apply for themselves.
"""

from __future__ import annotations

import argparse
import itertools
import re
import sys
from pathlib import Path
from typing import get_args

from dotenv import load_dotenv

from deep_question import engine
from deep_question.loader import load_all
from deep_question.schema import AgeBracket, Applicant, Channel, Factors, Gender

DEFAULT_EXCEL = Path("data/base_questionnaire.xlsx")
DEFAULT_OUT = Path("output")


CHANNELS = list(get_args(Channel))
APPLICANTS = list(get_args(Applicant))
AGES = list(get_args(AgeBracket))
GENDERS = list(get_args(Gender))


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("+", "plus")).strip("-")


def _expand(value: str | None, universe: list[str], name: str) -> list[str]:
    """None or 'all' -> every value; otherwise a comma-separated subset, validated against `universe`."""
    if value is None or value.strip().lower() == "all":
        return list(universe)
    # lower-case and collapse spaces for factor tokens ("Me" -> "me"); products keep their exact Excel spelling
    norm = (lambda v: v.strip()) if name == "product" else (lambda v: re.sub(r"\s+", "-", v.strip().lower()))
    chosen = [norm(v) for v in value.split(",") if v.strip()]
    bad = [v for v in chosen if v not in universe]
    if bad and name != "product":  # products are validated against the Excel by the caller
        raise SystemExit(f"invalid {name} value(s) {bad}. Allowed: {universe}")
    return chosen


def _print_catalog_summary(catalog) -> None:
    m = catalog.metadata
    print(f"\n=== {catalog.catalog_id}  [{m.applicant} · {m.primary_archetype} · {m.maslow_level} · {m.tone}]")
    print(f"persona: {catalog.persona_read[:220]}{'…' if len(catalog.persona_read) > 220 else ''}")
    for q in catalog.questions:
        print(f"\n{q.question_id} [{q.step_phase}/{q.spin_stage}] <- {q.source_question_key}")
        print(f"   {q.headline}")
        print(f"   {q.sub_headline}")
        for o in q.options:
            print(f"     - {o.label}   ({o.underlying_intent})")
        if q.bias_card:
            flag = " [VERIFY]" if q.bias_card.needs_fact_check else ""
            print(f"   bias: {q.bias_card.bias}{flag} — {q.bias_card.text}")
    if catalog.deferred_questions:
        print("\ndeferred:", [(d.source_question_key, d.handled_by) for d in catalog.deferred_questions])
    if catalog.claims_to_verify:
        print("claims to verify:", catalog.claims_to_verify)
    usage = catalog.__dict__.get("usage") or {}
    if usage:
        print(f"tokens: in={usage.get('input_tokens')} out={usage.get('output_tokens')} "
              f"(cache read={usage.get('input_token_details', {}).get('cache_read')})")
    warnings = catalog.__dict__.get("contract_warnings") or []
    if warnings:
        print("\n⚠ contract warnings:")
        for w in warnings:
            print("   -", w)


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    p = argparse.ArgumentParser(description="Generate a personalized questionnaire catalog for one or more segments.")
    p.add_argument("--excel", type=Path, default=DEFAULT_EXCEL, help="Base questionnaire .xlsx/.csv")
    p.add_argument("--sheet", default=None, help="Sheet name (default: first sheet)")
    p.add_argument("--list-products", action="store_true", help="List products in the Excel and exit")
    # Each factor: omit it (or pass "all") to expand to every value. Comma-separate for a subset.
    p.add_argument("--product", default=None, help="Product name as in the Excel. Omit = all products")
    p.add_argument("--channel", default=None, help=f"{'|'.join(CHANNELS)}. Omit = all")
    p.add_argument("--applicant", default=None, help=f"{'|'.join(APPLICANTS)} (who the visitor applies for). Omit = all")
    p.add_argument("--age", default=None, help=f"Insured age bracket: {'|'.join(AGES)}. Omit = all eligible")
    p.add_argument("--gender", default=None, help=f"Insured gender: {'|'.join(GENDERS)}. Omit = all")
    p.add_argument("--no-eligibility-filter", action="store_true",
                   help="Keep age brackets outside the product's entry-age window (useful for testing)")
    p.add_argument("--steps", type=int, default=5, help="Number of questions in the catalog")
    p.add_argument("--copy-lang", default="th", help="Language for customer-facing copy")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output directory for JSON catalogs")
    p.add_argument("--dry-run", action="store_true", help="Print the assembled prompt for the first combo and exit")
    p.add_argument("--plan-only", action="store_true", help="Print the plan (combos and pruning) and exit; no LLM call")
    p.add_argument("--yes", "-y", action="store_true", help="Skip the confirmation when generating many catalogs")
    args = p.parse_args(argv)

    products = load_all(args.excel, args.sheet)
    if args.list_products:
        for name, pq in products.items():
            core = [q.key for q in pq.core_questions()]
            window = f"{pq.entry_age_min if pq.entry_age_min is not None else '?'}-{pq.entry_age_max if pq.entry_age_max is not None else '?'}"
            print(f"- {name}  [{pq.product_line}]  entry_age={window}")
            print(f"    core={core}")
            for app in APPLICANTS:
                print(f"    eligible({app:5s}) = {pq.eligible_age_brackets(app)}")
        return

    product_names = _expand(args.product, list(products), "product")
    unknown = [n for n in product_names if n not in products]
    if unknown:
        p.error(f"unknown product(s) {unknown}. Available: {sorted(products)}")
    channels = _expand(args.channel, CHANNELS, "channel")
    applicants = _expand(args.applicant, APPLICANTS, "applicant")
    ages = _expand(args.age, AGES, "age")
    genders = _expand(args.gender, GENDERS, "gender")

    raw = list(itertools.product(product_names, channels, applicants, ages, genders))
    if args.no_eligibility_filter:
        combos = raw
    else:
        combos = [c for c in raw if c[3] in products[c[0]].eligible_age_brackets(c[2])]
    pruned = len(raw) - len(combos)
    if not combos:
        p.error("no eligible combinations: the requested age bracket(s) fall outside the product's entry-age window "
                "or are too young for --applicant me. Use --list-products to see eligible brackets.")

    if args.dry_run:
        prod, channel, applicant, age, gender = combos[0]
        factors = Factors(channel=channel, applicant=applicant, age_bracket=age, gender=gender,
                          copy_language=args.copy_lang, n_steps=args.steps)
        for m in engine.build_messages(products[prod], factors):
            content = m.content if isinstance(m.content, str) else m.content[0]["text"]
            print(f"\n##### {m.type.upper()} #####\n{content}")
        return

    print(f"Plan: {len(combos)} catalog(s) from {len(product_names)} product × {len(channels)} channel "
          f"× {len(applicants)} applicant × {len(ages)} age × {len(genders)} gender = {len(raw)}, "
          f"minus {pruned} ineligible  (one LLM call each)")
    if args.plan_only:
        for prod, channel, applicant, age, gender in combos:
            print(f"  {prod} × {channel} × {applicant} × {age} × {gender}")
        return
    if len(combos) > 1 and not args.yes and sys.stdin.isatty():
        if input("Proceed? [y/N] ").strip().lower() not in ("y", "yes"):
            print("aborted")
            return

    from deep_question.llm import build_llm  # imported late so --dry-run/--list-products need no credentials

    llm, desc = build_llm()
    print(f"LLM: {desc}")
    args.out.mkdir(parents=True, exist_ok=True)

    for i, (prod, channel, applicant, age, gender) in enumerate(combos, 1):
        base = products[prod]
        factors = Factors(channel=channel, applicant=applicant, age_bracket=age, gender=gender,
                          copy_language=args.copy_lang, n_steps=args.steps)
        print(f"\n>>> [{i}/{len(combos)}] generating {base.product} × {channel} × {applicant} × {age} × {gender} …",
              flush=True)
        try:
            catalog = engine.generate(base, factors, llm)
        except Exception as e:  # noqa: BLE001 — POC: surface and continue with the next combo
            print(f"!!! failed: {type(e).__name__}: {e}", file=sys.stderr)
            continue
        path = args.out / f"{_slug(base.product)}__{channel}__{applicant}__{_slug(age)}__{gender}.json"
        path.write_text(catalog.model_dump_json(indent=2, exclude_none=False), encoding="utf-8")
        _print_catalog_summary(catalog)
        print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
