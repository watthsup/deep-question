# Deep Question — Personalized Questionnaire Generation Engine (POC)

Turns the business's **fixed base questionnaire** (Excel) into a **personalized, value-first 5-question
conversation** for one audience segment (channel × product × age × gender), with every question, option,
micro-reflection and bias card **explained by the marketing / psychology principle behind it** (SPIN, GAP,
Maslow, FAB, cognitive biases).

The output is a static JSON catalog. Every generated option still maps back to a base option, so
underwriting, lead scoring and the TSR system keep working unchanged.

```
Excel (fixed Q&A)  ──►  loader  ──►  engine (prompt + one LLM call)  ──►  Catalog JSON  (+ explanations)
                                          ▲
                              prompts/system.md + frameworks.md + segments.md   ← the real product
```

## Layout

| Path | What it is |
|---|---|
| `prompts/system.md` | **The core AI instruction.** Role, data contract, how to think (Steps A–F), style rules. Edit this to change behaviour. |
| `prompts/frameworks.md` | Knowledge: SPIN, GAP, Maslow, FAB, Feel-Felt-Found, cognitive biases, 5 archetypes, micro-reflection rules. |
| `prompts/segments.md` | Knowledge: how channel / product / age / gender change the person. Add product facts here. |
| `deep_question/schema.py` | Pydantic models. Input (base questionnaire, factors) and output (`Catalog`). Field descriptions are sent to the model as the JSON schema, so they are instructions too. |
| `deep_question/loader.py` | Excel/CSV → `ProductQuestionnaire`. |
| `deep_question/llm.py` | `ChatAnthropic` factory: Bedrock (no boto3) primary, Anthropic direct fallback. |
| `deep_question/engine.py` | Assembles messages, calls the model with structured output, validates the data contract. |
| `deep_question/cli.py` | `python -m deep_question …` |
| `scripts/build_sample_excel.py` | Builds `data/base_questionnaire.xlsx` from the business question sets in `docs/`. |
| `docs/` | Project context and the raw question/answer sets. |

## Setup

```bash
conda activate deep-question
pip install -r requirements.txt
cp .env.example .env         # then fill in credentials
python scripts/build_sample_excel.py   # (already done once; re-run if you change the script)
```

### Credentials (`.env`)

* **Bedrock, no boto3** — Bedrock serves the native Anthropic Messages API at
  `https://bedrock-mantle.<region>.api.aws/anthropic` and accepts a *Bedrock API key* as a bearer token.
  Set `AWS_BEARER_TOKEN_BEDROCK` and `AWS_REGION`. Model IDs carry the `anthropic.` prefix
  (`anthropic.claude-opus-5`).
* **Anthropic direct** — set `ANTHROPIC_API_KEY`.
* `LLM_PROVIDER=auto` (default): Bedrock if its token is present, else Anthropic. If **both** are set,
  Bedrock is primary and Anthropic is an automatic fallback (LangChain `with_fallbacks`).

## Usage

```bash
# what products are in the Excel?
python -m deep_question --list-products

# see the exact prompt that will be sent (no LLM call, no credentials needed)
python -m deep_question --product Cancer --channel facebook --applicant me --age 36-45 --gender female --dry-run

# generate one catalog
python -m deep_question --product Cancer --channel facebook --applicant me --age 36-45 --gender female

# buying for someone else: age and gender describe the INSURED (here: a parent), the visitor is the buyer
python -m deep_question --product Senior55 --channel facebook --applicant other --age 66-70 --gender female

# several segments in one run (cartesian product of the comma-separated values)
python -m deep_question --product "Health D-Koom" --channel google,facebook --applicant me --age 36-45 --gender male,female

# omit a factor (or pass "all") to expand it to every value; impossible combos are pruned automatically
python -m deep_question --product Cancer                  # every eligible channel × applicant × age × gender
python -m deep_question --yes                             # every eligible combo for every product, no prompt

# see what a run WOULD generate, without any LLM call (safe even with credentials in .env)
python -m deep_question --plan-only
python -m deep_question --product Senior55 --applicant other --plan-only
```

**Factors.** The landing-page journey starts with *who is this for* (`--applicant me|other`), then the insured's
age bracket, then the insured's gender. So age and gender always describe the **insured**; with `other` the
visitor is a buyer (parent or adult child) and the copy is written to them.

| Factor | Values |
|---|---|
| `--channel` | `facebook` `tiktok` `instagram` `google` |
| `--applicant` | `me` `other` |
| `--age` (insured) | `0-5` `6-22` `23-35` `36-45` `46-55` `56-65` `66-70` `70+` |
| `--gender` (insured) | `male` `female` |

**Eligibility pruning.** Each product's `min_age` / `max_age` (sheet `products`) define the insured entry-age
window. Brackets that do not overlap it are skipped, and `me` is skipped for brackets too young to apply for
themselves (under 20). `--list-products` shows the eligible brackets per product and applicant;
`--no-eligibility-filter` disables the pruning for testing. The plan line reports how many combos were pruned.

> The `min_age` / `max_age` values in the sample Excel are **placeholders** except the business rule that senior
> products start at 55. Confirm them with the product team before shipping catalogs.

Before calling the model the CLI prints the plan (how many catalogs, one LLM call each) and asks for
confirmation when it is more than one; `--yes` / `-y` skips the question. Use `--plan-only` to inspect the plan
without generating anything. With the placeholder entry ages, the full run is 704 catalogs (1152 raw
combinations minus 448 ineligible).

Catalogs are written to `output/<product>__<channel>__<age>__<gender>.json` and a readable summary is
printed, including **contract warnings** (a core question not covered, an option that does not map to a
base option) and **claims to verify** (any number the model used that was not in the input).

## The Excel input format

Sheet `questions`, one row per answer option (long format):

| product_line | product | question_key | role | order | question_text | option_text |
|---|---|---|---|---|---|---|
| Non-Life | Cancer | reason_why | core | 1 | เหตุผลที่คุณต้องการซื้อประกันโรคมะเร็ง | มีคนใกล้ตัวเป็นมะเร็ง … |
| Non-Life | Cancer | budget | core | 2 | คุณมีงบประมาณ… | <10,000 |
| Non-Life | Cancer | occupation | uw | 6 | อาชีพ … | *(blank = free text)* |

`role` tells the model how to treat the question:

* `default` — applicant (ตัวเอง/คนอื่น), insured age, insured gender: collected first on the landing page, so they are the factors; not asked again.
* `core` — the fixed qualification questions; each must be covered exactly once across the steps.
* `uw` — underwriting facts (occupation); folded into the profile step or deferred to the TSR call.
* `spare` — optional; used only when it strengthens the conversation for that segment.

Sheet `products` (`product`, `description`, `min_age`, `max_age`) gives the model a one-line product description
and the insured entry-age window used for eligibility pruning.

## What the output contains (per catalog)

* `persona_read`, `strategy`, `metadata.primary_archetype / maslow_level / tone` — the thinking.
* `questions[]` — `step_phase` (hook → pain → gap → profile → emotion), `spin_stage`, headline,
  sub-headline, options with `source_question_key` + `source_option` (the data contract),
  `underlying_intent` (for the TSR), `micro_reflection` + `reflection_technique`, a `bias_card`, and
  `design_rationale`.
* `deferred_questions[]` — base questions not asked on the page and who handles them.
* `principles_applied[]` — each principle, where it appears, plain-English explanation.
* `tsr_brief_notes`, `claims_to_verify`.

## Previewing catalogs in a browser

```bash
python scripts/build_site.py          # reads output/*.json, writes site/index.html
open site/index.html                   # double-click it — no server, works fully offline
```

One static, dependency-free HTML file. Pick product / channel / applicant / age / gender with pill
buttons; any combination that has no generated catalog is greyed out automatically (a live filter against
whichever catalogs exist in `output/`, not a fixed list). Once a combination resolves to one catalog, click
through the 5 questions like the real flow: pick an option, see its micro-reflection, then continue. The
result ends on a mock lead-capture screen (no data is actually sent anywhere).

Toggle **Reviewer view** (top right) to reveal the reasoning behind the copy: persona, archetype, SPIN
stage, `design_rationale` per question, the bias name and rationale, and — on the final screen — the TSR
brief and the list of claims that need fact-checking. Off by default so the base view reads like the real
customer flow; on for reviewing *why* the AI wrote what it wrote.

Re-run the build script any time `output/` changes; it just re-embeds whatever catalogs are present.

## If a run fails

* **`OutputTruncated: model stopped at max_tokens`** — the catalog did not fit in `LLM_MAX_TOKENS`. Thinking
  tokens count against the same budget and Thai text is token-heavy. Raise `LLM_MAX_TOKENS` (48000 default) or
  lower `LLM_EFFORT`. Requests stream, so large values do not hit HTTP timeouts.
* **`OUTPUT_PARSING_FAILURE` with "Field required"** — same root cause on older versions; upgrade to the current
  code, which reports truncation explicitly.
* **Contract warnings** in the summary are not failures: they flag where the model bent the data contract so a
  human can fix the prompt or accept the deviation.

## Iterating on the engine

1. Change the prompt files, then `--dry-run` to read what the model will see.
2. Generate one segment, read the summary, adjust the prompt. The schema (`schema.py`) is the second lever:
   adding a field with a good description is often enough to get a new behaviour.
3. Keep `system.md` about *how to think* and put facts (products, channels, numbers you have verified) in
   `segments.md`. The model is told to flag any number it did not receive.

## Next steps (not in this POC)

* Batch-generate all combinations and diff catalogs between prompt versions.
* A small eval: a rubric-based judge scoring persona fit, contract compliance and tone per channel.
* Downstream (Part 2): lead scoring and TSR pre-call brief from submitted answers.
