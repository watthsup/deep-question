"""Build a single static, offline HTML preview site from generated catalogs in output/*.json.

    python scripts/build_site.py                    # reads output/, writes site/index.html
    python scripts/build_site.py --catalogs output --out site/index.html
    open site/index.html                             # just double-click it, no server needed

Design notes (read before changing the templates below):

* One self-contained HTML file. All catalogs are embedded as a JSON blob inside the page, not fetched
  from separate files. This is deliberate: opening a page via `file://` and `fetch()`-ing a sibling
  `.json` file is blocked by the browser in many setups (a `file://` CORS footgun), and this tool needs
  to be double-click-able by non-technical stakeholders with zero server. Embedding also means the file
  can be emailed or dropped in a shared drive and still work.
* "Disable options with no path" is implemented as a live faceted filter: every selector pill's enabled
  state is recomputed from the *other* current selections, against the embedded catalog list. A pill is
  disabled exactly when no embedded catalog matches the combination it would produce.
* Vanilla HTML/CSS/JS. No build step, no CDN, no framework — matches the project's "keep it minimal"
  constraint and means this script has nothing to install.
* A "Reviewer view" toggle reveals the reasoning fields (persona_read, bias names, design_rationale,
  tsr_brief_notes, claims_to_verify) for internal review; it is OFF by default so the default view reads
  like the actual customer-facing flow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_CATALOGS_DIR = Path("output")
DEFAULT_OUT = Path("site/index.html")


def load_catalogs(catalogs_dir: Path) -> list[dict]:
    catalogs = []
    for path in sorted(catalogs_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"!!! skipping {path.name}: invalid JSON ({e})")
            continue
        if not all(k in data for k in ("catalog_id", "metadata", "questions")):
            print(f"!!! skipping {path.name}: missing catalog_id/metadata/questions")
            continue
        catalogs.append(data)
    return catalogs


def embed_json(value) -> str:
    """JSON-encode for safe embedding inside a <script> tag (guards against a literal `</script`)."""
    blob = json.dumps(value, ensure_ascii=False)
    return blob.replace("</script", "<\\/script").replace("<!--", "<\\!--")


# ---------------------------------------------------------------------------------------------- CSS

CSS = """
:root {
  --accent: #a6192e;       /* placeholder brand red — swap for the real brand color */
  --accent-soft: #fbeaec;
  --accent-soft-2: #f7dde1;
  --ink: #1f2328;
  --muted: #6b7280;
  --line: #e6e3e1;
  --bg: #f4f3f1;
  --card: #ffffff;
  --radius: 18px;
  --shadow: 0 10px 30px -12px rgba(31, 35, 40, 0.18);
  font-family: -apple-system, "Segoe UI", "Noto Sans Thai", "Leelawadee UI", Tahoma, sans-serif;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 16px 80px;
}
.topbar {
  width: 100%;
  max-width: 640px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-size: 14px;
  color: var(--muted);
}
.topbar .brand { font-weight: 700; color: var(--ink); }
.toggle {
  display: flex; align-items: center; gap: 8px; cursor: pointer; user-select: none;
}
.switch {
  width: 40px; height: 22px; border-radius: 999px; background: #d8d5d1; position: relative;
  transition: background .2s;
}
.switch::after {
  content: ""; position: absolute; top: 2px; left: 2px; width: 18px; height: 18px; border-radius: 50%;
  background: white; box-shadow: 0 1px 2px rgba(0,0,0,.3); transition: left .2s;
}
.switch.on { background: var(--accent); }
.switch.on::after { left: 20px; }

.card {
  width: 100%; max-width: 640px; background: var(--card); border-radius: var(--radius);
  box-shadow: var(--shadow); padding: 36px 32px; position: relative; overflow: hidden;
}
.eyebrow { font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); font-weight: 700; margin: 0 0 6px; }
h1.title { font-size: 24px; margin: 0 0 4px; line-height: 1.35; }
.subtitle { color: var(--muted); font-size: 14.5px; margin: 0 0 24px; }

.dim-block { margin-bottom: 22px; }
.dim-label { font-size: 13px; font-weight: 700; color: var(--ink); margin-bottom: 10px; display: block; }
.pills { display: flex; flex-wrap: wrap; gap: 8px; }
.pill {
  border: 1.5px solid var(--line); background: #fff; border-radius: 999px; padding: 8px 16px;
  font-size: 14px; cursor: pointer; transition: all .15s; color: var(--ink);
}
.pill:hover:not(.disabled) { border-color: var(--accent); transform: translateY(-1px); }
.pill.active { background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600; }
.pill.disabled { color: #b9b6b2; border-color: #ece9e6; cursor: not-allowed; background: #fbfaf9; }

.match-banner {
  margin-top: 18px; padding: 16px 18px; border-radius: 14px; background: var(--accent-soft);
  display: none; align-items: flex-start; gap: 10px; font-size: 14.5px;
}
.match-banner.show { display: flex; }
.match-banner .icon { font-size: 18px; }
.cta {
  margin-top: 18px; width: 100%; padding: 14px 20px; border: none; border-radius: 12px;
  background: var(--accent); color: #fff; font-size: 16px; font-weight: 700; cursor: pointer;
  transition: transform .12s, opacity .15s;
}
.cta:hover { transform: translateY(-1px); }
.cta:disabled { opacity: .4; cursor: not-allowed; transform: none; }
.cta.ghost { background: #fff; color: var(--accent); border: 1.5px solid var(--accent); }

.empty-note { font-size: 13.5px; color: var(--muted); background: #f8f7f5; border-radius: 12px; padding: 14px 16px; }

/* --- quiz --- */
.progress-row { display: flex; gap: 6px; margin-bottom: 22px; }
.progress-seg { flex: 1; height: 5px; border-radius: 4px; background: var(--line); }
.progress-seg.done { background: var(--accent); }
.step-label { font-size: 12.5px; color: var(--muted); margin-bottom: 6px; font-weight: 600; }
.headline { font-size: 21px; font-weight: 700; margin: 0 0 8px; line-height: 1.4; }
.sub_headline { color: var(--muted); font-size: 14.5px; margin: 0 0 20px; }

.designer-chip-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
.chip {
  font-size: 11.5px; background: #eef0f2; color: #45505c; border-radius: 999px; padding: 4px 10px;
  font-weight: 600;
}
.chip.warn { background: #fdecea; color: #a12f2a; }
.rationale-box {
  font-size: 13px; color: #45505c; background: #f4f6f8; border-radius: 12px; padding: 12px 14px;
  margin-bottom: 16px; border-left: 3px solid #9aa5b1;
}

.options { display: flex; flex-direction: column; gap: 10px; margin-bottom: 6px; }
.option {
  text-align: left; border: 1.5px solid var(--line); border-radius: 14px; padding: 14px 16px;
  background: #fff; cursor: pointer; font-size: 15px; transition: all .15s; line-height: 1.5;
}
.option:hover { border-color: var(--accent); background: var(--accent-soft); }
.option.selected { border-color: var(--accent); background: var(--accent-soft-2); font-weight: 600; }

.reflection {
  max-height: 0; overflow: hidden; transition: max-height .25s ease;
}
.reflection.show { max-height: 240px; }
.reflection-inner {
  margin-top: 12px; padding: 14px 16px; border-radius: 14px; background: #fff7ec;
  border: 1px solid #f1e2c4; font-size: 14px; display: flex; gap: 10px; align-items: flex-start;
}
.reflection-inner .icon { font-size: 16px; }
.reflection-meta { margin-top: 8px; }

.bias-footer {
  margin-top: 20px; padding: 12px 14px; border-radius: 12px; background: #f6f5f3;
  font-size: 13px; color: #5b5650; display: flex; gap: 8px; align-items: flex-start;
}

.nav-row { display: flex; justify-content: flex-end; margin-top: 20px; }

/* --- final screen --- */
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 13px; color: var(--muted); margin-bottom: 6px; }
.field input {
  width: 100%; border: none; border-bottom: 1.5px solid var(--line); padding: 8px 2px; font-size: 15px;
  background: transparent; outline: none; font-family: inherit;
}
.field input:focus { border-bottom-color: var(--accent); }
.consent { font-size: 12px; color: var(--muted); margin: 18px 0; line-height: 1.6; }
.success-panel {
  display: none; text-align: center; padding: 30px 10px;
}
.success-panel.show { display: block; }
.success-panel .big { font-size: 40px; margin-bottom: 10px; }

.designer-panel { margin-top: 26px; border-top: 1px dashed var(--line); padding-top: 20px; }
.designer-panel h3 { font-size: 14px; margin: 0 0 10px; }
.designer-panel .row { font-size: 13.5px; margin-bottom: 10px; line-height: 1.6; }
.designer-panel .row b { color: var(--ink); }
.claim-list { font-size: 13px; color: #a12f2a; padding-left: 18px; margin: 6px 0; }
.persona-box {
  background: #f4f6f8; border-radius: 14px; padding: 16px 18px; font-size: 14px; line-height: 1.6;
  margin-bottom: 20px; color: #333;
}
.meta-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
"""

# ---------------------------------------------------------------------------------------------- JS

JS = """
const CATALOGS = JSON.parse(document.getElementById('catalog-data').textContent);

const DIMS = ['product', 'channel', 'applicant', 'age_bracket', 'gender'];
const AGE_ORDER = ['0-5','6-22','23-35','36-45','46-55','56-65','66-70','70+'];
// Map 8 UI button ranges to our 4 consolidated catalog groups (56-65 rounded to 46-60)
const AGE_MAP = {
  '0-5': '0-22',
  '6-22': '0-22',
  '23-35': '23-45',
  '36-45': '23-45',
  '46-55': '46-60',
  '56-65': '46-60',
  '66-70': '60+',
  '70+': '60+',
};
const FIXED_ORDER = {
  channel: ['facebook','tiktok','instagram','google'],
  applicant: ['me','other'],
  age_bracket: AGE_ORDER,
  gender: ['male','female'],
};
const LABEL = {
  channel: {facebook:'Facebook', tiktok:'TikTok', instagram:'Instagram', google:'Google'},
  applicant: {me:'ซื้อให้ตัวเอง', other:'ซื้อให้คนอื่น'},
  gender: {male:'ชาย', female:'หญิง'},
  age_bracket: {
    '0-5':'0–5 ปี','6-22':'6–22 ปี','23-35':'23–35 ปี','36-45':'36–45 ปี',
    '46-55':'46–55 ปี','56-65':'56–65 ปี','66-70':'66–70 ปี','70+':'70+ ปี',
    '0-22':'0–22 ปี','23-45':'23–45 ปี','46-60':'46–60 ปี','60+':'60+ ปี',
  },
};
const DIM_TITLE = {
  product: 'ผลิตภัณฑ์', channel: 'ช่องทาง', applicant: 'ซื้อให้ใคร',
  age_bracket: 'ช่วงอายุผู้เอาประกัน', gender: 'เพศผู้เอาประกัน',
};

const state = { sel: {}, catalog: null, qIndex: 0, answers: [], selectedOptionId: null, designer: false };

function dimValues(dim) {
  if (dim === 'age_bracket') {
    const presentTargets = new Set(CATALOGS.map(c => c.metadata.age_bracket));
    return FIXED_ORDER.age_bracket.filter(v => presentTargets.has(AGE_MAP[v] || v));
  }
  const present = new Set(CATALOGS.map(c => c.metadata[dim]));
  const order = FIXED_ORDER[dim];
  if (order) return order.filter(v => present.has(v));
  return [...present]; // product: first-seen order
}

function matches(sel) {
  return CATALOGS.filter(c => DIMS.every(d => {
    if (!sel[d]) return true;
    if (d === 'age_bracket') {
      const target = AGE_MAP[sel[d]] || sel[d];
      return c.metadata.age_bracket === target;
    }
    return c.metadata[d] === sel[d];
  }));
}

function pillLabel(dim, value) {
  return (LABEL[dim] && LABEL[dim][value]) || value;
}

function selectDim(dim, value) {
  const trial = { ...state.sel, [dim]: value };
  if (matches(trial).length === 0) return; // guard: should already be disabled
  state.sel = trial;
  // dropping any other already-picked dim that no longer has a match
  for (const d of DIMS) {
    if (d !== dim && state.sel[d] && matches(state.sel).length === 0) delete state.sel[d];
  }
  renderSelector();
}

function renderSelector() {
  const root = document.getElementById('app');
  const blocks = DIMS.map(dim => {
    const values = dimValues(dim);
    const pills = values.map(v => {
      const enabled = matches({ ...state.sel, [dim]: v }).length > 0;
      const active = state.sel[dim] === v;
      const cls = ['pill', active ? 'active' : '', enabled ? '' : 'disabled'].join(' ').trim();
      return `<button class="${cls}" ${enabled ? '' : 'disabled'}
                onclick="selectDim('${dim}','${v}')">${pillLabel(dim, v)}</button>`;
    }).join('');
    return `<div class="dim-block">
              <span class="dim-label">${DIM_TITLE[dim]}</span>
              <div class="pills">${pills}</div>
            </div>`;
  }).join('');

  const found = matches(state.sel);
  const allPicked = DIMS.every(d => state.sel[d]);
  let banner = '';
  let ctaDisabled = 'disabled';
  if (allPicked && found.length === 1) {
    ctaDisabled = '';
    banner = `<div class="match-banner show">
        <span class="icon">✅</span>
        <div>พร้อมแล้ว — ชุดคำถามสำหรับ <b>${found[0].metadata.product}</b>
        (${pillLabel('channel', found[0].metadata.channel)} ·
        ${pillLabel('applicant', found[0].metadata.applicant)} ·
        ${pillLabel('age_bracket', state.sel.age_bracket)} ·
        ${pillLabel('gender', found[0].metadata.gender)})</div></div>`;
  } else if (allPicked && found.length === 0) {
    banner = `<div class="match-banner show"><span class="icon">🚧</span>
        <div>ยังไม่มีชุดคำถามสำหรับตัวเลือกนี้ — ลองรันเอนจินสำหรับ segment นี้ก่อน</div></div>`;
  }

  root.innerHTML = `
    <p class="eyebrow">Deep Question · Catalog Previewer</p>
    <h1 class="title">เลือกชุดคำถามที่ต้องการดู</h1>
    <p class="subtitle">${CATALOGS.length} ชุดคำถามที่สร้างไว้แล้ว — ตัวเลือกที่ยังไม่มีชุดคำถามจะถูก disable ไว้อัตโนมัติ</p>
    ${blocks}
    ${banner}
    <button class="cta" ${ctaDisabled} onclick="startQuiz()">เริ่มตอบคำถาม</button>
    ${state.sel && Object.keys(state.sel).length ? '<button class="cta ghost" onclick="resetSelector()">เริ่มเลือกใหม่</button>' : ''}
  `;
}

function resetSelector() { state.sel = {}; renderSelector(); }

function startQuiz() {
  const found = matches(state.sel);
  if (found.length !== 1) return;
  state.catalog = found[0];
  state.qIndex = 0;
  state.answers = [];
  renderQuestion();
}

function designerPersonaIntro(c) {
  if (!state.designer) return '';
  const m = c.metadata;
  return `
    <div class="meta-chips">
      <span class="chip">${m.primary_archetype}${m.secondary_archetype ? ' + ' + m.secondary_archetype : ''}</span>
      <span class="chip">${m.maslow_level}</span>
      <span class="chip">${m.tone}</span>
    </div>
    <div class="persona-box"><b>Persona:</b> ${c.persona_read}</div>
  `;
}

function renderQuestion() {
  const c = state.catalog;
  const q = c.questions[state.qIndex];
  const total = c.questions.length;
  const root = document.getElementById('app');

  const segs = c.questions.map((_, i) =>
    `<div class="progress-seg ${i <= state.qIndex ? 'done' : ''}"></div>`).join('');

  const designerChips = state.designer
    ? `<div class="designer-chip-row">
         <span class="chip">${q.step_phase} · ${q.spin_stage}</span>
       </div>
       <div class="rationale-box"><b>ทำไมถึงถามแบบนี้:</b> ${q.design_rationale}</div>`
    : '';

  const optionsHtml = q.options.map(o => {
    const selected = state.selectedOptionId === o.option_id ? 'selected' : '';
    return `<button class="option ${selected}" onclick="chooseOption('${q.question_id}','${o.option_id}')">${o.label}</button>`;
  }).join('');

  const chosen = q.options.find(o => o.option_id === state.selectedOptionId);
  const reflectionHtml = chosen ? `
    <div class="reflection show">
      <div class="reflection-inner">
        <span class="icon">💭</span>
        <div>
          ${chosen.micro_reflection}
          ${state.designer ? `<div class="reflection-meta">
              <span class="chip">${chosen.reflection_technique}</span>
              <span class="chip">${chosen.underlying_intent}</span>
            </div>` : ''}
        </div>
      </div>
    </div>` : '<div class="reflection"></div>';

  const biasHtml = q.bias_card ? `
    <div class="bias-footer">
      <span class="icon">💡</span>
      <div>${q.bias_card.text}
        ${state.designer ? `<div class="reflection-meta">
            <span class="chip">${q.bias_card.bias}</span>
            ${q.bias_card.needs_fact_check ? '<span class="chip warn">ต้องตรวจสอบตัวเลข</span>' : ''}
          </div>
          <div style="margin-top:6px;color:#6b7280;font-size:12.5px;">${q.bias_card.why_this_bias}</div>` : ''}
      </div>
    </div>` : '';

  root.innerHTML = `
    <div class="progress-row">${segs}</div>
    <p class="step-label">คำถามที่ ${state.qIndex + 1} จาก ${total}</p>
    ${designerChips}
    <h2 class="headline">${q.headline}</h2>
    <p class="sub_headline">${q.sub_headline}</p>
    <div class="options">${optionsHtml}</div>
    ${reflectionHtml}
    ${biasHtml}
    <div class="nav-row">
      <button class="cta" style="width:auto;padding:12px 28px" ${chosen ? '' : 'disabled'} onclick="nextQuestion()">
        ${state.qIndex === total - 1 ? 'ดูสรุป' : 'ถัดไป'}
      </button>
    </div>
  `;
}

function chooseOption(questionId, optionId) {
  state.selectedOptionId = optionId;
  renderQuestion();
}

function nextQuestion() {
  const q = state.catalog.questions[state.qIndex];
  const chosen = q.options.find(o => o.option_id === state.selectedOptionId);
  state.answers.push({ question: q.headline, source_question_key: q.source_question_key,
                        label: chosen.label, underlying_intent: chosen.underlying_intent });
  state.selectedOptionId = null;
  if (state.qIndex < state.catalog.questions.length - 1) {
    state.qIndex += 1;
    renderQuestion();
  } else {
    renderFinal();
  }
}

function renderFinal() {
  const c = state.catalog;
  const root = document.getElementById('app');

  const designerPanel = state.designer ? `
    <div class="designer-panel">
      <h3>สรุปสำหรับทีม TSR</h3>
      <div class="row">${c.tsr_brief_notes}</div>
      <h3>คำตอบที่เลือก</h3>
      ${state.answers.map(a => `<div class="row"><b>${a.question}</b><br>${a.label}
          <span class="chip" style="margin-left:6px">${a.underlying_intent}</span></div>`).join('')}
      ${c.claims_to_verify && c.claims_to_verify.length ? `
        <h3>ตัวเลข/ข้อความที่ต้องตรวจสอบก่อนใช้จริง</h3>
        <ul class="claim-list">${c.claims_to_verify.map(x => `<li>${x}</li>`).join('')}</ul>` : ''}
    </div>` : '';

  root.innerHTML = `
    <p class="eyebrow">สนใจผลิตภัณฑ์</p>
    <h1 class="title">${c.metadata.product}</h1>
    <p class="subtitle">จากคำตอบของคุณ ทีมงานเข้าใจสิ่งที่คุณกำลังมองหาแล้ว เหลืออีกนิดเดียว</p>

    <div class="success-panel" id="success-panel">
      <div class="big">🎉</div>
      <p><b>ขอบคุณค่ะ</b><br>ทีมงานจะติดต่อกลับเร็ว ๆ นี้</p>
      <button class="cta ghost" onclick="resetAll()">ดูชุดคำถามอื่น</button>
    </div>

    <div id="lead-form">
      <div class="field"><label>ชื่อ-นามสกุล</label><input type="text" placeholder="เช่น สมชาย ใจดี"></div>
      <div class="field"><label>เบอร์โทรศัพท์</label><input type="tel" placeholder="0812345678"></div>
      <div class="field"><label>อีเมล</label><input type="email" placeholder="you@example.com"></div>
      <p class="consent">การกดส่งข้อมูล ท่านตกลงยินยอมให้ทีมงานติดต่อกลับเพื่อให้คำแนะนำผลิตภัณฑ์ที่เหมาะกับท่าน
        (หน้านี้เป็นต้นแบบสำหรับรีวิวภายในเท่านั้น ไม่มีการส่งข้อมูลจริง)</p>
      <button class="cta" onclick="submitLead()">ส่งข้อมูล</button>
    </div>

    ${designerPanel}
  `;
}

function submitLead() {
  document.getElementById('lead-form').style.display = 'none';
  document.getElementById('success-panel').classList.add('show');
}

function resetAll() {
  state.catalog = null; state.qIndex = 0; state.answers = []; state.selectedOptionId = null;
  resetSelector();
}

function toggleDesigner() {
  state.designer = !state.designer;
  document.getElementById('designer-switch').classList.toggle('on', state.designer);
  if (state.catalog) {
    if (document.getElementById('lead-form')) renderFinal(); else renderQuestion();
  } else {
    renderSelector();
  }
}

renderSelector();
"""

# ---------------------------------------------------------------------------------------------- HTML

HTML_TEMPLATE = """<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>__CSS__</style>
</head>
<body>
  <div class="topbar">
    <span class="brand">Deep Question</span>
    <div class="toggle" onclick="toggleDesigner()">
      <span>Reviewer view</span>
      <span class="switch" id="designer-switch"></span>
    </div>
  </div>
  <div class="card" id="app"></div>

  <script id="catalog-data" type="application/json">__CATALOG_DATA__</script>
  <script>__JS__</script>
</body>
</html>
"""


def build(catalogs_dir: Path, out_path: Path, title: str) -> int:
    catalogs = load_catalogs(catalogs_dir)
    if not catalogs:
        raise SystemExit(f"no valid catalogs found in {catalogs_dir}/ — generate some with `python -m deep_question` first")

    html = (
        HTML_TEMPLATE
        .replace("__TITLE__", title)
        .replace("__CSS__", CSS)
        .replace("__JS__", JS)
        .replace("__CATALOG_DATA__", embed_json(catalogs))
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return len(catalogs)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--catalogs", type=Path, default=DEFAULT_CATALOGS_DIR, help="Directory of catalog *.json files")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output HTML file")
    p.add_argument("--title", default="Deep Question — Catalog Previewer")
    args = p.parse_args()

    n = build(args.catalogs, args.out, args.title)
    size_kb = args.out.stat().st_size / 1024
    print(f"embedded {n} catalog(s) from {args.catalogs}/ -> {args.out}  ({size_kb:.0f} KB)")
    print(f"open with:  open {args.out}" if size_kb else "")


if __name__ == "__main__":
    main()
