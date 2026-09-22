"""Load the fixed base questionnaire from Excel (or CSV).

Expected sheet layout — one row per answer option (long format). Free-text questions have one row with an
empty `option_text`.

| product_line | product            | question_key | role | order | question_text                         | option_text        |
|--------------|--------------------|--------------|------|-------|---------------------------------------|--------------------|
| Non-Life     | Cancer             | reason_why   | core | 1     | เหตุผลที่คุณต้องการซื้อประกันโรคมะเร็ง | มีคนใกล้ตัวเป็นมะเร็ง … |
| Non-Life     | Cancer             | budget       | core | 2     | คุณมีงบประมาณ…                        | <10,000            |

Optional sheet `products` with columns `product`, `description`, `min_age`, `max_age` adds a one-line product
description and the insured entry-age window used to prune impossible age brackets.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from deep_question.schema import BaseQuestion, ProductQuestionnaire

REQUIRED_COLUMNS = ["product_line", "product", "question_key", "role", "order", "question_text", "option_text"]


def _read(path: Path, sheet: str | int | None) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, dtype=str).fillna("")
    return pd.read_excel(path, sheet_name=sheet if sheet is not None else 0, dtype=str).fillna("")


def _read_products_sheet(path: Path) -> dict[str, dict]:
    """Optional `products` sheet: product, description, min_age, max_age."""
    if path.suffix.lower() == ".csv":
        return {}
    try:
        df = pd.read_excel(path, sheet_name="products", dtype=str).fillna("")
    except ValueError:  # sheet not present
        return {}

    def _int(v: str) -> int | None:
        v = str(v).strip()
        return int(float(v)) if v else None

    return {
        str(r["product"]).strip(): {
            "description": str(r.get("description", "")).strip(),
            "entry_age_min": _int(r.get("min_age", "")),
            "entry_age_max": _int(r.get("max_age", "")),
        }
        for _, r in df.iterrows()
    }


def load_all(path: str | Path, sheet: str | int | None = None) -> dict[str, ProductQuestionnaire]:
    """Return {product_name: ProductQuestionnaire} for every product in the file."""
    path = Path(path)
    df = _read(path, sheet)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name} is missing columns: {missing}. Expected {REQUIRED_COLUMNS}")

    for col in REQUIRED_COLUMNS:
        df[col] = df[col].astype(str).str.strip()
    meta = _read_products_sheet(path)

    result: dict[str, ProductQuestionnaire] = {}
    for (line, product), pdf in df.groupby(["product_line", "product"], sort=False):
        questions: list[BaseQuestion] = []
        for key, qdf in pdf.groupby("question_key", sort=False):
            first = qdf.iloc[0]
            options = [o for o in qdf["option_text"].tolist() if o]
            questions.append(
                BaseQuestion(
                    key=key,
                    role=first["role"],  # type: ignore[arg-type]
                    order=int(first["order"] or 0),
                    text=first["question_text"],
                    options=options,
                )
            )
        questions.sort(key=lambda q: (q.role != "default", q.order))
        result[product] = ProductQuestionnaire(
            product=product,
            product_line=line,  # type: ignore[arg-type]
            questions=questions,
            **meta.get(product, {}),
        )
    return result


def load_product(path: str | Path, product: str, sheet: str | int | None = None) -> ProductQuestionnaire:
    catalogs = load_all(path, sheet)
    if product not in catalogs:
        raise KeyError(f"Product '{product}' not found. Available: {sorted(catalogs)}")
    return catalogs[product]
