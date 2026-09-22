"""Build data/base_questionnaire.xlsx from the business's fixed question sets (docs/INB-*.md).

Run once:  python scripts/build_sample_excel.py
Then edit the Excel directly when the business changes a question or option — the code never needs to change.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "base_questionnaire.xlsx"

# ---- shared option sets -----------------------------------------------------------------------
BUDGET = ["<10,000", "10,000-20,000", "20,000-30,000", ">30,000"]
PAYMENT = ["ผ่านบัตรเครดิต", "ผ่านบัตรเดบิต", "ผ่าน Mobile Banking"]
HEALTH = ["สุขภาพแข็งแรงดี ไม่มีโรคประจำตัว", "อยู่ในระหว่างการรักษา", "เพิ่งหายป่วย", "มีโรคประจำตัว ทานยาตามแพทย์สั่งเป็นประจำ"]
BUY_FOR_WHO = ["แม่", "พ่อ", "ลูก", "ภรรยา / สามี", "พี่ / น้อง", "ญาติคนอื่นๆ"]
CRITERIA_HEALTH = ["วงเงินความคุ้มครอง", "ค่าห้อง", "ราคา", "แบรนด์", "การบริการ", "อื่นๆ โปรดระบุ"]
CRITERIA_BASIC = ["วงเงินความคุ้มครอง", "ราคา", "แบรนด์", "การบริการ", "อื่นๆ โปรดระบุ"]

REASON_HEALTH = [
    "อยากรักษาที่รพ.เอกชน",
    "มีทางเลือกการรักษาที่มากขึ้น",
    "มีคนใกล้ตัวป่วย กังวลว่าจะเกิดกับตัวเอง",
    "สุขภาพไม่แข็งแรงเหมือนเมื่อก่อน",
    "เห็นข่าวเกี่ยวกับคนเป็นโรคต่างๆ มากขึ้น จนเริ่มกังวล",
    "วางแผนการเงิน เพื่อลดภาระค่าใช้จ่ายที่คาดไม่ถึง",
    "เป็นห่วง อยากดูแลคนที่รัก ให้ได้รับการรักษาที่ดีที่สุด",
    "เพื่อลดหย่อนภาษี",
    "อื่นๆ โปรดระบุ",
]
REASON_SENIOR_HEALTH = REASON_HEALTH[:6] + ["วางแผนค่าใช้จ่ายยามเจ็บป่วยให้พ่อแม่ ไม่อยากเป็นภาระลูกหลาน", "เพื่อลดหย่อนภาษี", "อื่นๆ โปรดระบุ"]
REASON_CANCER = [
    "อยากซื้อเพิ่มเติมจากประกันสุขภาพ เผื่อไว้สำหรับยามเกิดการเบิกค่ารักษาที่มากขึ้น",
    "มีคนใกล้ตัวเป็นมะเร็ง กังวลว่าจะเกิดกับตัวเอง",
    "สุขภาพไม่แข็งแรงเหมือนเมื่อก่อน",
    "เห็นข่าวเกี่ยวกับคนเป็นโรคมะเร็ง มากขึ้น จนเริ่มกังวล",
    "ค่ารักษาในกรณีที่เป็นมะเร็งจะค่อนข้างสูง กังวลเรื่องค่าใช้จ่ายและภาระทางการเงิน",
    "เป็นห่วง อยากดูแลคนที่รัก ให้ได้รับการรักษาที่ดีที่สุด",
    "เพื่อลดหย่อนภาษี",
    "อื่นๆ โปรดระบุ",
]
REASON_CI = [
    "อยากซื้อเพิ่มเติมจากประกันสุขภาพ เผื่อไว้สำหรับยามเกิดการรักษาโรคร้ายแรงที่มากขึ้น",
    "มีคนใกล้ตัวเป็นโรคร้ายแรง กังวลว่าจะเกิดกับตัวเอง",
    "สุขภาพไม่แข็งแรงเหมือนเมื่อก่อน",
    "เห็นข่าวเกี่ยวกับคนเป็นโรคร้ายแรง มากขึ้น จนเริ่มกังวล",
    "ค่ารักษาโรคกลุ่มนี้เป็นจำนวนค่อนข้างสูง กังวลเรื่องค่าใช้จ่ายและภาระทางการเงิน",
    "เป็นห่วง อยากดูแลคนที่รัก ให้ได้รับการรักษาที่ดีที่สุด",
    "เพื่อลดหย่อนภาษี",
    "อื่นๆ โปรดระบุ",
]
REASON_SENIOR_LIFE = ["เป็นมรดกให้ลูกหลาน", "ไม่อยากเป็นภาระลูกหลาน", "มีโรคประจำตัว สมัครประกันอื่นไม่ได้",
                      "วางแผนค่าใช้จ่ายงานศพ", "เป็นของขวัญให้พ่อแม่", "ลดหย่อนภาษี", "อื่นๆ โปรดระบุ"]
REASON_SAVINGS = ["เพื่อออมเงิน", "เพื่อวางแผนอนาคตให้ลูก", "ลดหย่อนภาษี", "อื่นๆ โปรดระบุ"]
REASON_PA = ["ชอบออกกำลังกาย กังวลเรื่องอุบัติเหตุ", "ต้องใช้วิถีชีวิตนอกบ้านเป็นประจำ กังวลเรื่องความปลอดภัย",
             "อาชีพมีความเสี่ยง กังวลเรื่องความปลอดภัย", "เห็นข่าวเกี่ยวกับอุบัติเหตุต่างๆ มากขึ้น จนเริ่มกังวล",
             "วางแผนการเงิน เพื่อลดภาระค่าใช้จ่ายที่คาดไม่ถึง"]


def product_rows(line: str, product: str, noun: str, reason: list[str], criteria: list[str],
                 health: list[str] | None, occupation: bool, criteria_noun: str | None = None) -> list[dict]:
    """One product's fixed questions. `noun` is the Thai product noun used inside question texts."""
    cn = criteria_noun or noun
    q: list[tuple[str, str, int, str, list[str]]] = [
        # Landing-page journey starts here: who is this for -> insured age -> insured gender. All three are factors.
        ("applicant", "default", 0, "คุณต้องการทำประกันนี้ให้ตัวเอง หรือให้คนอื่น", ["ตัวเอง", "คนอื่น"]),
        ("age", "default", 0, "อายุ ของ ผู้รับประกัน คนที่จะใช้ประกันนี้", []),
        ("gender", "default", 0, "เพศ ของ ผู้รับประกัน หรือคนที่จะใช้ประกันนี้", []),
        ("reason_why", "core", 1, f"เหตุผลที่คุณต้องการซื้อ{noun}", reason),
        ("budget", "core", 2, f"คุณมีงบประมาณสำหรับการซื้อ{noun}อยู่ที่ประมาณเท่าไหร่?", BUDGET),
        ("purchase_criteria", "core", 3, f"ปัจจัยอะไรที่มีความสำคัญต่อการเลือก{cn}ของคุณ", criteria),
    ]
    if health is not None:
        q.append(("health_condition", "core", 4, "วัดระดับความฟิตของคุณ", health))
    q.append(("payment_method", "core", 5, "ปกติคุณชำระค่าสินค้าและบริการ ด้วยวิธีไหน", PAYMENT))
    if occupation:
        q.append(("occupation", "uw", 6, "อาชีพ ของ ผู้รับประกัน หรือคนที่จะใช้ประกันนี้", []))
    q += [
        ("brand_comparison", "spare", 7, f"คุณกำลังเปรียบเทียบ{noun}ของบริษัทไหนอยู่", []),
        ("existing_policy", "spare", 8, f"ปัจจุบัน คุณมี{noun}อยู่แล้วหรือไม่", []),
        ("buy_for_who", "spare", 9, f"คุณต้องการซื้อ{noun}ให้กับใคร ?", BUY_FOR_WHO),
    ]
    rows = []
    for key, role, order, text, options in q:
        for opt in options or [""]:
            rows.append({"product_line": line, "product": product, "question_key": key, "role": role,
                         "order": order, "question_text": text, "option_text": opt})
    return rows


rows: list[dict] = []
# ---- Non-Life --------------------------------------------------------------------------------
rows += product_rows("Non-Life", "Health Lumpsum Plus", "ประกันสุขภาพ", REASON_HEALTH, CRITERIA_HEALTH, HEALTH, True)
rows += product_rows("Non-Life", "Health D-Koom", "ประกันสุขภาพ", REASON_HEALTH, CRITERIA_HEALTH, HEALTH, True)
rows += product_rows("Non-Life", "Senior Extra 7", "ประกันสุขภาพ", REASON_SENIOR_HEALTH, CRITERIA_HEALTH, HEALTH, True)
rows += product_rows("Non-Life", "Cancer", "ประกันโรคมะเร็ง", REASON_CANCER,
                     ["วงเงินความคุ้มครอง", "ระยะที่คุ้มครอง", "ราคา", "แบรนด์", "การบริการ", "อื่นๆ โปรดระบุ"], None, True)
rows += product_rows("Non-Life", "Critical Illness", "ประกันโรคร้ายแรง", REASON_CI,
                     ["วงเงินความคุ้มครอง", "โรคที่คุ้มครอง", "ราคา", "แบรนด์", "การบริการ", "อื่นๆ โปรดระบุ"], None, True)
# ---- Life ------------------------------------------------------------------------------------
rows += product_rows("Life", "Senior55", "ประกันชีวิตผู้สูงวัย", REASON_SENIOR_LIFE, CRITERIA_BASIC, None, False)
rows += product_rows("Life", "Senior So Good", "ประกันชีวิตผู้สูงวัย", REASON_SENIOR_LIFE, CRITERIA_BASIC, None, False)
rows += product_rows("Life", "Gen Life Plus 10", "ประกันชีวิตสะสมทรัพย์", REASON_SAVINGS,
                     ["วงเงินความคุ้มครอง", "เงินคืนระหว่างปี", "ผลประโยชน์หลังครบกำหนด", "ราคา", "แบรนด์", "การบริการ", "อื่นๆ โปรดระบุ"],
                     HEALTH, True)
rows += product_rows("Life", "PA Pay Money", "ประกันอุบัติเหตุ", REASON_PA, CRITERIA_BASIC, None, True)

# min_age / max_age = insured ENTRY-age window. The CLI prunes age brackets outside it and the model is told the
# window so it can write eligibility-aware copy.
# !! The numbers below are PLACEHOLDERS chosen to be plausible for Thai products of this type. The product team
# !! must confirm them in the Excel before catalogs are shipped. Only "senior products start at 55" came from the business.
descriptions = pd.DataFrame([
    {"product": "Health Lumpsum Plus", "min_age": 0,  "max_age": 65, "description": "Comprehensive IPD health plan with a lump-sum annual coverage limit; private hospital access."},
    {"product": "Health D-Koom",       "min_age": 20, "max_age": 65, "description": "Health plan with a deductible (co-pay first tranche) in exchange for a lower premium; ideal on top of group/company cover."},
    {"product": "Senior Extra 7",      "min_age": 55, "max_age": 75, "description": "Health plan for seniors; often bought by adult children for parents."},
    {"product": "Cancer",              "min_age": 1,  "max_age": 65, "description": "Lump-sum cash payout on cancer diagnosis; freedom to choose treatment and hospital."},
    {"product": "Critical Illness",    "min_age": 20, "max_age": 60, "description": "Lump-sum cash payout on diagnosis of listed critical illnesses; covers income loss and recovery."},
    {"product": "Senior55",            "min_age": 55, "max_age": 75, "description": "Whole-life plan for seniors, simplified/guaranteed issue; legacy and funeral planning."},
    {"product": "Senior So Good",      "min_age": 55, "max_age": 75, "description": "Senior life plan with savings/cash-back element."},
    {"product": "Gen Life Plus 10",    "min_age": 0,  "max_age": 65, "description": "Endowment (savings) life plan with periodic cash-back and maturity benefit; tax deductible."},
    {"product": "PA Pay Money",        "min_age": 1,  "max_age": 65, "description": "Personal accident plan paying cash benefits for accidental injury, hospitalisation and disability."},
])
descriptions["notes"] = "min_age/max_age are PLACEHOLDERS - confirm with product team"
descriptions.loc[descriptions["product"].str.startswith("Senior"), "notes"] = "min_age 55 per business rule; max_age is a PLACEHOLDER"

OUT.parent.mkdir(parents=True, exist_ok=True)
with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
    pd.DataFrame(rows).to_excel(xw, sheet_name="questions", index=False)
    descriptions.to_excel(xw, sheet_name="products", index=False)
print(f"wrote {OUT}  ({len(rows)} rows, {pd.DataFrame(rows)['product'].nunique()} products)")
