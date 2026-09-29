"""Build a single static, offline HTML preview site from generated catalogs in output/*.json.

    python scripts/build_site.py                    # reads output/, writes site/index.html
    python scripts/build_site.py --catalogs output --out site/index.html
    open site/index.html                             # just double-click it, no server needed

Generali Executive Presentation Edition (Luminous Premium Aesthetics):
* Modern, warm, luminous ambient canvas (mesh gradient with soft rose & warm gold lighting).
* Studio-grade typography: 'Plus Jakarta Sans' (for titles, stats, numbers) + 'IBM Plex Sans Thai' (for legible, elegant Thai copy).
* No psychological prefixes exposed to the customer: cognitive bias cards show pure natural priming text to customers; technical bias names appear ONLY in Reviewer View.
* Typeform-caliber interactive option cards with A/B/C/D letter pills, hover lift, and silky-smooth selection states.
* 100% Responsive full-screen design that breathes on desktop, laptop, tablet, and mobile.
* Interactive Journey:
    1. Screen 1: Diagnostic Hook (Dynamic Headline, Luxury Anchor Card, Promise, CTA)
    2. Interactive 5 Questions (Instant advisor micro-reflections & smooth selection animations)
    3. Screen 2: Pre-Submit Landing (Social Proof, Personalized AI Insight, High-Converting CTA)
    4. Screen 3: Evaluated Results (Animated SVG Risk Gauge, Live Policy Tier Card, Gap Diagnosis, Lead Form with 1-click Demo Fill)
* Executive Presenter Stepper: Instant jump between Hook -> Quiz -> Pre-Submit -> Results.
* Live Interactive Budget Recalculator on Result Screen for live client presentation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_CATALOGS_DIR = Path("output")
DEFAULT_OUT = Path("site/index.html")
SCORING_ENGINE_PATH = Path("site/scoring-engine.js")


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
    """JSON-encode for safe embedding inside a <script> tag."""
    blob = json.dumps(value, ensure_ascii=False)
    return blob.replace("</script", "<\\/script").replace("<!--", "<\\!--")


# ---------------------------------------------------------------------------------------------- CSS

CSS = """
:root {
  --gen-red: #c8102e;          /* Generali Primary Red */
  --gen-red-dark: #980b22;
  --gen-red-soft: #fdf2f4;
  --gen-red-soft-border: #fad2d8;
  
  --gen-gold: #b38a3e;         /* Generali Warm Gold */
  --gen-gold-soft: #fcf9f2;
  --gen-gold-border: #ebd9b8;
  
  --bg-canvas: #faf9f7;
  --card-bg: rgba(255, 255, 255, 0.96);
  --card-border: rgba(230, 227, 222, 0.85);
  --card-inner: #f8f7f5;
  
  --text-main: #181b20;        /* Deep, sharp, comfortable charcoal */
  --text-secondary: #525a66;   /* Balanced, readable slate */
  --text-muted: #828a96;       /* Subtle caption */
  --line-divider: #edebe7;
  
  --font-display: 'Plus Jakarta Sans', 'Prompt', sans-serif;
  --font-body: 'IBM Plex Sans Thai', 'Inter', -apple-system, sans-serif;
  
  --radius-card: 26px;
  --radius-inner: 18px;
  --radius-pill: 999px;
  
  --shadow-luminous: 0 20px 50px -12px rgba(28, 25, 23, 0.08), 0 30px 80px -20px rgba(200, 16, 46, 0.06);
  --shadow-btn: 0 8px 24px rgba(200, 16, 46, 0.35);
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: 
    radial-gradient(ellipse 90% 50% at 50% -15%, rgba(254, 226, 226, 0.5) 0%, transparent 70%),
    radial-gradient(ellipse 60% 40% at 100% 40%, rgba(254, 243, 199, 0.35) 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 0% 70%, rgba(241, 245, 249, 0.7) 0%, transparent 60%),
    var(--bg-canvas);
  color: var(--text-main);
  font-family: var(--font-body);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px 70px;
  -webkit-font-smoothing: antialiased;
}

/* ==========================================================================
   EXECUTIVE PRESENTATION HEADER & CONTROLS
   ========================================================================== */
.presentation-bar {
  width: 100%;
  max-width: 820px;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid var(--card-border);
  border-radius: 18px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  backdrop-filter: blur(16px);
  margin-bottom: 26px;
}
.brand-group {
  display: flex;
  align-items: center;
  gap: 12px;
}
.gen-lion-badge {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--gen-red), var(--gen-red-dark));
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-weight: 900;
  color: #fff;
  font-size: 17px;
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.28);
}
.brand-text {
  display: flex;
  flex-direction: column;
}
.brand-title {
  font-family: var(--font-display);
  font-size: 13.5px;
  font-weight: 800;
  letter-spacing: .08em;
  color: var(--text-main);
  text-transform: uppercase;
}
.brand-subtitle {
  font-size: 11px;
  color: var(--gen-gold);
  font-weight: 600;
}

/* Presenter Stepper Jump */
.presenter-nav {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #f1f0ec;
  padding: 4px;
  border-radius: 12px;
}
.p-step-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  padding: 7px 14px;
  border-radius: 9px;
  cursor: pointer;
  transition: all .15s ease;
  font-family: var(--font-display);
}
.p-step-btn:hover {
  color: var(--text-main);
  background: #e6e4de;
}
.p-step-btn.active {
  background: var(--gen-red);
  color: #fff;
  box-shadow: 0 2px 8px rgba(200, 16, 46, 0.28);
}

.controls-right {
  display: flex;
  align-items: center;
  gap: 14px;
}
.toggle-reviewer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  color: var(--text-secondary);
  cursor: pointer;
  user-select: none;
}
.switch {
  width: 36px; height: 18px; border-radius: 999px; background: #d0cdd4; position: relative;
  transition: background .2s;
}
.switch::after {
  content: ""; position: absolute; top: 2px; left: 2px; width: 14px; height: 14px; border-radius: 50%;
  background: white; box-shadow: 0 1px 2px rgba(0,0,0,.25); transition: left .2s;
}
.switch.on { background: var(--gen-red); }
.switch.on::after { left: 20px; }

/* ==========================================================================
   RESPONSIVE APP CONTAINER
   ========================================================================== */
.responsive-app-card {
  width: 100%;
  max-width: 760px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-luminous);
  backdrop-filter: blur(20px);
  padding: 42px 48px;
  position: relative;
  margin: 0 auto;
  color: var(--text-main);
  transition: all .2s ease;
}

@media (max-width: 768px) {
  .responsive-app-card {
    padding: 28px 20px 36px;
    border-radius: 20px;
  }
}

/* Generali In-App Brand Header */
.app-header-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--line-divider);
  margin-bottom: 26px;
}
.app-logo {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 900;
  letter-spacing: .12em;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 6px;
}
.app-logo span { color: var(--gen-red); }
.app-badge-meta {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 700;
  color: var(--gen-gold);
  background: var(--gen-gold-soft);
  border: 1px solid var(--gen-gold-border);
  padding: 4px 11px;
  border-radius: 8px;
  text-transform: uppercase;
  letter-spacing: .04em;
}

/* ==========================================================================
   SEGMENT SELECTOR (START SCREEN)
   ========================================================================== */
.selector-card {
  width: 100%;
  max-width: 720px;
  background: var(--card-bg);
  color: var(--text-main);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-luminous);
  padding: 40px 44px;
  position: relative;
  margin: 0 auto;
}
.eyebrow {
  font-family: var(--font-display);
  font-size: 12px;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--gen-red);
  font-weight: 800;
  margin: 0 0 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}
h1.title {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 800;
  margin: 0 0 8px;
  color: var(--text-main);
  line-height: 1.3;
}
.subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0 0 26px;
  line-height: 1.55;
}
.dim-block { margin-bottom: 20px; }
.dim-label {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 700;
  color: #2b303a;
  margin-bottom: 9px;
  display: block;
}
.pills { display: flex; flex-wrap: wrap; gap: 8px; }
.pill {
  border: 1.5px solid #dedcd7;
  background: #ffffff;
  border-radius: 999px;
  padding: 8px 18px;
  font-size: 13px;
  cursor: pointer;
  transition: all .15s;
  color: #374151;
  font-family: inherit;
}
.pill:hover:not(.disabled) {
  border-color: var(--gen-red);
  color: var(--gen-red);
  background: #fff;
  transform: translateY(-1px);
}
.pill.active {
  background: var(--gen-red);
  border-color: var(--gen-red);
  color: #fff;
  font-weight: 700;
  box-shadow: 0 3px 10px rgba(200, 16, 46, 0.25);
}
.pill.disabled {
  color: #b0aba2;
  border-color: #edebe6;
  background: #fbfaf8;
  cursor: not-allowed;
}

.match-banner {
  margin-top: 24px;
  padding: 16px 20px;
  border-radius: 16px;
  background: var(--gen-red-soft);
  border: 1px solid var(--gen-red-soft-border);
  display: none;
  align-items: flex-start;
  gap: 12px;
  font-size: 14px;
  line-height: 1.55;
  color: #920b20;
}
.match-banner.show { display: flex; }
.cta-launch {
  margin-top: 26px;
  width: 100%;
  padding: 17px 28px;
  border: none;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--gen-red), var(--gen-red-dark));
  color: #fff;
  font-family: var(--font-display);
  font-size: 16.5px;
  font-weight: 800;
  cursor: pointer;
  box-shadow: var(--shadow-btn);
  transition: transform .12s, box-shadow .15s, opacity .15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.cta-launch:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(200, 16, 46, 0.5);
}
.cta-launch:disabled { opacity: .4; cursor: not-allowed; transform: none; }

/* ==========================================================================
   SCREEN 1: LANDING HOOK
   ========================================================================== */
.hook-badge-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--gen-red-soft);
  border: 1px solid var(--gen-red-soft-border);
  color: var(--gen-red);
  font-family: var(--font-display);
  font-size: 12.5px;
  font-weight: 700;
  padding: 6px 16px;
  border-radius: 999px;
  margin-bottom: 20px;
}
.hook-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1.35;
  margin: 0 0 24px;
}
@media (min-width: 640px) {
  .hook-title { font-size: 32px; }
}
.anchor-card-luxury {
  background: linear-gradient(180deg, #ffffff 0%, #fff8f8 100%);
  border: 1.5px solid var(--gen-red-soft-border);
  border-radius: var(--radius-inner);
  padding: 30px 24px;
  text-align: center;
  margin-bottom: 24px;
  box-shadow: 0 12px 32px rgba(200, 16, 46, 0.07);
  position: relative;
}
.anchor-label-text {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
}
.anchor-stat-highlight {
  font-family: var(--font-display);
  font-size: 46px;
  font-weight: 900;
  color: var(--gen-red);
  letter-spacing: .01em;
  line-height: 1.1;
  margin-bottom: 10px;
}
@media (min-width: 640px) {
  .anchor-stat-highlight { font-size: 54px; }
}
.anchor-sub-text {
  font-size: 12.5px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.hook-promise-box {
  background: #f8f9fb;
  border: 1px solid #e7eaee;
  border-radius: var(--radius-inner);
  padding: 18px 22px;
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
  margin-bottom: 26px;
}

.btn-generali-cta {
  width: 100%;
  background: linear-gradient(135deg, #d31231 0%, #a00c24 100%);
  color: #fff;
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 800;
  border: none;
  border-radius: 999px;
  padding: 17px 30px;
  cursor: pointer;
  box-shadow: var(--shadow-btn);
  transition: transform .12s, box-shadow .15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-generali-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(200, 16, 46, 0.5);
}
.btn-generali-cta:active { transform: translateY(1px); }

.trust-strip {
  margin-top: 24px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  font-size: 12.5px;
  color: var(--text-muted);
}

/* ==========================================================================
   COURSIV-STYLE INTERACTIVE QUIZ & INTERSTITIAL QUOTE SCREENS
   ========================================================================== */
.coursiv-nav-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0 16px;
  position: relative;
}
.coursiv-back-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 1.5px solid #e5e7eb;
  background: #ffffff;
  color: var(--text-secondary);
  font-size: 17px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all .15s ease;
}
.coursiv-back-btn:hover {
  background: #f3f4f6;
  color: var(--text-main);
  border-color: #d1d5db;
  transform: translateX(-2px);
}
.coursiv-logo {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 900;
  letter-spacing: .08em;
  color: var(--text-main);
}
.coursiv-logo span {
  color: var(--gen-red);
}
.coursiv-step-badge {
  font-family: var(--font-display);
  font-size: 13.5px;
  font-weight: 800;
  color: #6b7280;
  background: #f3f4f6;
  padding: 5px 12px;
  border-radius: 999px;
}
.coursiv-progress-line {
  width: 100%;
  height: 5px;
  background: #f1f2f4;
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 30px;
}
.coursiv-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #c8102e 0%, #ff6b7e 100%);
  border-radius: 999px;
  transition: width .35s cubic-bezier(0.4, 0, 0.2, 1);
}

.quiz-content-body {
  max-width: 640px;
  margin: 0 auto;
  text-align: center;
}
.quiz-headline {
  font-family: var(--font-display);
  font-size: 25px;
  font-weight: 800;
  color: var(--text-main);
  margin: 0 0 10px;
  line-height: 1.35;
  text-align: center;
}
@media (min-width: 640px) {
  .quiz-headline { font-size: 28px; }
}
.quiz-subheadline {
  font-size: 14.5px;
  color: var(--text-secondary);
  margin: 0 0 28px;
  line-height: 1.55;
  text-align: center;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 13px;
  margin-bottom: 24px;
}
.option-item-wrap {
  display: flex;
  flex-direction: column;
  width: 100%;
}
.option-card-interactive {
  background: #f4f5f7;
  border: 2px solid transparent;
  border-radius: 18px;
  padding: 17px 22px;
  cursor: pointer;
  transition: all .16s ease;
  display: flex;
  align-items: center;
  gap: 16px;
  text-align: left;
  font-family: inherit;
  width: 100%;
}
.option-card-interactive:hover {
  background: #ebedf2;
  transform: translateY(-2px);
  box-shadow: 0 8px 22px rgba(0,0,0,0.05);
}
.option-card-interactive.selected {
  background: #ffffff;
  border-color: var(--gen-red);
  box-shadow: 0 10px 28px rgba(200, 16, 46, 0.15);
}

.opt-emoji {
  font-size: 25px;
  line-height: 1;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.opt-label {
  flex: 1;
  font-size: 15.5px;
  font-weight: 600;
  color: var(--text-main);
  line-height: 1.45;
}
.option-card-interactive.selected .opt-label {
  color: var(--gen-red-dark);
}
.opt-check-circle {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid #cbd2dc;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all .15s ease;
  background: #ffffff;
}
.option-card-interactive.selected .opt-check-circle {
  border-color: var(--gen-red);
  background: var(--gen-red);
}
.opt-check-circle::after {
  content: "✓";
  font-size: 12px;
  font-weight: 900;
  color: #fff;
  opacity: 0;
  transition: opacity .15s;
}
.option-card-interactive.selected .opt-check-circle::after {
  opacity: 1;
}

/* Coursiv-Caliber Reflection Bubble */
.coursiv-reflection-bubble {
  background: linear-gradient(135deg, #fffcf9 0%, #fff7f7 100%);
  border: 1.5px solid #ebd9b8;
  border-radius: 18px;
  padding: 16px 20px;
  margin-top: 10px;
  margin-bottom: 4px;
  display: flex;
  gap: 14px;
  align-items: flex-start;
  text-align: left;
  animation: fadeInDown .2s ease;
  box-shadow: 0 4px 18px rgba(179, 138, 62, 0.08);
}
.advisor-avatar-circle {
  width: 40px;
  height: 40px;
  background: #fdf3e2;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 21px;
  flex-shrink: 0;
  border: 1.5px solid var(--gen-gold);
}
.reflection-text-col { flex: 1; }
.reflection-advisor-label {
  font-family: var(--font-display);
  font-size: 12.5px;
  font-weight: 800;
  color: #8c6820;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.reflection-quote-content {
  font-size: 14.5px;
  color: #3b352b;
  line-height: 1.6;
}

/* Big Coursiv-Style Continue Button */
.btn-coursiv-continue {
  width: 100%;
  background: linear-gradient(135deg, #d31231 0%, #980b22 100%);
  color: #ffffff;
  font-family: var(--font-display);
  font-size: 16.5px;
  font-weight: 800;
  border: none;
  border-radius: 14px;
  padding: 17px 32px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(200, 16, 46, 0.35);
  transition: all .16s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-coursiv-continue:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(200, 16, 46, 0.48);
}
.btn-coursiv-continue:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

/* ==========================================================================
   COURSIV-STYLE INTERSTITIAL QUOTE / BRIDGE SCREEN (CLEAN & CENTERED)
   ========================================================================== */
.interstitial-container {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
  padding: 10px 0 16px;
}
.interstitial-badge-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--gen-gold-soft);
  border: 1px solid var(--gen-gold-border);
  color: #8c6820;
  font-size: 12.5px;
  font-weight: 700;
  padding: 6px 14px;
  border-radius: 999px;
  margin-bottom: 20px;
}
.interstitial-headline {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1.35;
  margin: 0 0 22px;
  text-align: center;
}
@media (min-width: 640px) {
  .interstitial-headline { font-size: 29px; }
}
.interstitial-quote-lead {
  font-size: 18px;
  font-weight: 600;
  color: var(--gen-red-dark);
  line-height: 1.7;
  margin: 0 0 32px;
  background: linear-gradient(135deg, rgba(200, 16, 46, 0.04) 0%, rgba(200, 16, 46, 0.08) 100%);
  padding: 24px 28px;
  border-radius: 20px;
  border: 1.5px solid var(--gen-red-soft-border);
  box-shadow: 0 8px 24px rgba(200, 16, 46, 0.05);
  text-align: center;
}

/* ==========================================================================
   SCREEN 2: PRE-SUBMIT LANDING (BRIDGE)
   ========================================================================== */
.social-proof-card {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: var(--radius-inner);
  padding: 18px 22px;
  font-size: 14px;
  color: #166534;
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 22px;
  line-height: 1.5;
}
.live-dot {
  width: 9px;
  height: 9px;
  background: #10ac84;
  border-radius: 50%;
  box-shadow: 0 0 8px #10ac84;
  animation: pulse 1.8s infinite;
}
.insight-card-luxury {
  background: linear-gradient(180deg, #ffffff 0%, #fffbfc 100%);
  border: 1.5px solid var(--gen-red-soft-border);
  border-radius: var(--radius-inner);
  padding: 26px;
  margin-bottom: 28px;
  box-shadow: 0 10px 28px rgba(200, 16, 46, 0.05);
}
.insight-header {
  font-family: var(--font-display);
  font-size: 13px;
  color: var(--gen-red);
  font-weight: 800;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.insight-message {
  font-size: 14.5px;
  color: #374151;
  line-height: 1.65;
}
.cta-subcopy {
  text-align: center;
  font-size: 12.5px;
  color: var(--text-muted);
  margin-top: 12px;
}

/* ==========================================================================
   SCREEN 3: RESULT EVALUATION SCREEN
   ========================================================================== */
.result-canvas {
  display: flex;
  flex-direction: column;
}
.result-badge {
  align-self: center;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #047857;
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 800;
  padding: 6px 16px;
  border-radius: 999px;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: .04em;
}
.result-main-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 800;
  color: var(--text-main);
  text-align: center;
  line-height: 1.35;
  margin: 0 0 6px;
}
@media (min-width: 640px) {
  .result-main-title { font-size: 28px; }
}
.result-basis-text {
  font-size: 13.5px;
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: 24px;
}

/* Animated SVG Gauge */
.gauge-meter-wrapper {
  background: #fbfbf9;
  border: 1px solid var(--card-border);
  border-radius: var(--radius-inner);
  padding: 24px 18px 26px;
  text-align: center;
  margin-bottom: 22px;
  position: relative;
}
.gauge-svg {
  margin: 0 auto;
  display: block;
}
.gauge-center-val {
  font-family: var(--font-display);
  font-size: 44px;
  font-weight: 900;
  color: var(--text-main);
  margin-top: -38px;
  line-height: 1;
}
.gauge-center-sub {
  font-size: 12.5px;
  color: var(--text-muted);
  margin-bottom: 12px;
}
.gauge-pill-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 800;
  padding: 6px 16px;
  border-radius: 999px;
  text-transform: uppercase;
}
.gauge-pill-tag.high { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
.gauge-pill-tag.medium { background: #fef3c7; color: #b45309; border: 1px solid #fcd34d; }
.gauge-pill-tag.low { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }

/* Generali Policy Card (Box 6) */
.generali-policy-card {
  background: linear-gradient(135deg, #ffffff 0%, #fff7f8 100%);
  border: 1.5px solid var(--gen-red-soft-border);
  border-radius: var(--radius-inner);
  padding: 26px 28px;
  margin-bottom: 22px;
  box-shadow: 0 12px 32px rgba(200, 16, 46, 0.08);
  position: relative;
  overflow: hidden;
}
.policy-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
}
.policy-label {
  font-family: var(--font-display);
  font-size: 12px;
  text-transform: uppercase;
  color: var(--gen-red);
  font-weight: 800;
  letter-spacing: .04em;
}
.sum-insured-num {
  font-family: var(--font-display);
  font-size: 34px;
  font-weight: 900;
  color: var(--gen-red-dark);
  line-height: 1.1;
  margin: 4px 0;
}
.sum-insured-range {
  font-size: 13.5px;
  color: var(--text-secondary);
}
.premium-divider {
  border-top: 1px solid var(--line-divider);
  margin: 16px 0 14px;
}
.premium-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.premium-monthly {
  font-family: var(--font-display);
  font-size: 23px;
  font-weight: 800;
  color: var(--text-main);
}
.premium-disclaimer {
  font-size: 12px;
  color: var(--text-muted);
}

/* Live Budget Adjuster Pill Row */
.live-budget-selector {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px dashed #fad2d8;
}
.live-budget-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
}
.budget-live-pills {
  display: flex;
  gap: 8px;
}
.b-live-pill {
  flex: 1;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  color: #4b5563;
  font-family: var(--font-display);
  font-size: 11.5px;
  font-weight: 600;
  padding: 8px 4px;
  border-radius: 10px;
  cursor: pointer;
  text-align: center;
  transition: all .15s;
}
.b-live-pill:hover {
  background: #e5e7eb;
  color: var(--text-main);
}
.b-live-pill.active {
  background: var(--gen-red);
  color: #fff;
  border-color: var(--gen-red);
  font-weight: 700;
  box-shadow: 0 2px 10px rgba(200, 16, 46, 0.25);
}

/* Vulnerability Gap Box (Box 7) */
.gap-alert-card {
  background: #fffbeb;
  border: 1.5px solid #fde68a;
  border-radius: var(--radius-inner);
  padding: 18px 22px;
  margin-bottom: 24px;
}
.gap-alert-header {
  font-family: var(--font-display);
  font-size: 13.5px;
  font-weight: 800;
  color: #b45309;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.gap-alert-body {
  font-size: 14px;
  color: #78350f;
  line-height: 1.55;
}

/* Lead Capture Form */
.lead-box-luxury {
  background: #f9fafb;
  border: 1.5px solid #e5e7eb;
  border-radius: var(--radius-inner);
  padding: 26px 28px;
  margin-top: 10px;
}
.lead-box-title {
  margin: 0 0 16px;
  font-family: var(--font-display);
  font-size: 15.5px;
  font-weight: 800;
  color: var(--text-main);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.demo-fill-link {
  font-size: 12.5px;
  color: var(--gen-red);
  cursor: pointer;
  text-decoration: underline;
  font-weight: 700;
}
.lead-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 16px;
}
@media (max-width: 600px) {
  .lead-grid { grid-template-columns: 1fr; gap: 10px; }
}
.field-group { margin-bottom: 0; }
.field-group label {
  font-size: 12.5px;
  color: var(--text-secondary);
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
}
.field-group input {
  width: 100%;
  background: #ffffff;
  border: 1.5px solid #d1d5db;
  border-radius: 12px;
  padding: 13px 16px;
  font-size: 14.5px;
  color: var(--text-main);
  outline: none;
  font-family: inherit;
  transition: border-color .15s, box-shadow .15s;
}
.field-group input:focus {
  border-color: var(--gen-red);
  box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.12);
}

.lead-success-card {
  background: #ecfdf5;
  border: 1.5px solid #a7f3d0;
  border-radius: var(--radius-inner);
  padding: 28px 22px;
  text-align: center;
  color: #065f46;
  animation: fadeInDown .25s ease;
}
.success-check-circle {
  width: 50px;
  height: 50px;
  background: #10ac84;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  font-size: 24px;
  box-shadow: 0 4px 16px rgba(16, 172, 132, 0.3);
}

/* ==========================================================================
   REVIEWER / DESIGNER INTEL DRAWER
   ========================================================================== */
.reviewer-intel-card {
  margin-top: 26px;
  background: #f8f9fa;
  border: 1px solid #e2e4e8;
  border-radius: 16px;
  padding: 18px 22px;
  font-size: 13px;
  color: #4b5563;
  line-height: 1.6;
  border-left: 4px solid var(--gen-red);
}
.reviewer-intel-card b { color: var(--text-main); font-family: var(--font-display); }
.intel-tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 8px 0;
}
.intel-tag {
  font-size: 11.5px;
  background: #e9ecef;
  color: #495057;
  padding: 3px 9px;
  border-radius: 6px;
  font-family: var(--font-display);
}
.intel-tag.red { background: var(--gen-red-soft); color: var(--gen-red); border: 1px solid var(--gen-red-soft-border); }
.intel-tag.gold { background: var(--gen-gold-soft); color: #8c6820; border: 1px solid var(--gen-gold-border); }

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.6; }
  100% { transform: scale(1); opacity: 1; }
}
"""

# ---------------------------------------------------------------------------------------------- JS

JS = """
const CATALOGS = JSON.parse(document.getElementById('catalog-data').textContent);

const DIMS = ['product', 'channel', 'applicant', 'age_bracket', 'gender'];
const AGE_ORDER = ['0-5','6-22','23-35','36-45','46-55','56-65','66-70','70+'];
const AGE_MAP = {
  '0-5': '0-22', '6-22': '0-22', '23-35': '23-45', '36-45': '23-45',
  '46-55': '46-60', '56-65': '46-60', '66-70': '60+', '70+': '60+',
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

const state = {
  sel: {},
  catalog: null,
  view: 'selector', // selector | hook | question | presubmit | result
  qIndex: 0,
  answers: [],
  selectedOptionId: null,
  evalResult: null,
  designer: false,
};

function dimValues(dim) {
  if (dim === 'age_bracket') {
    const presentTargets = new Set(CATALOGS.map(c => c.metadata.age_bracket));
    return FIXED_ORDER.age_bracket.filter(v => presentTargets.has(AGE_MAP[v] || v));
  }
  const present = new Set(CATALOGS.map(c => c.metadata[dim]));
  const order = FIXED_ORDER[dim];
  if (order) return order.filter(v => present.has(v));
  return [...present];
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
  if (matches(trial).length === 0) return;
  state.sel = trial;
  for (const d of DIMS) {
    if (d !== dim && state.sel[d] && matches(state.sel).length === 0) delete state.sel[d];
  }
  renderSelector();
}

function updatePresenterNav() {
  const bar = document.getElementById('presenter-stepper');
  if (!bar) return;
  if (!state.catalog || state.view === 'selector') {
    bar.style.display = 'none';
    return;
  }
  bar.style.display = 'flex';
  const steps = [
    { id: 'hook', label: '1. Hook' },
    { id: 'q0', label: 'ข้อ 1' },
    { id: 'quote0', label: '💡 Quote 1' },
    { id: 'q1', label: 'ข้อ 2' },
    { id: 'q2', label: 'ข้อ 3' },
    { id: 'quote2', label: '💡 Quote 3' },
    { id: 'q3', label: 'ข้อ 4' },
    { id: 'q4', label: 'ข้อ 5' },
    { id: 'presubmit', label: '2. Pre-Submit' },
    { id: 'result', label: '3. สรุปผล' },
  ];

  let currentKey = state.view;
  if (state.view === 'question') currentKey = 'q' + state.qIndex;
  if (state.view === 'quote') currentKey = 'quote' + state.quoteIndex;

  bar.innerHTML = steps.map(s => {
    const active = currentKey === s.id ? 'active' : '';
    return `<button class="p-step-btn ${active}" onclick="jumpToPresenterStep('${s.id}')">${s.label}</button>`;
  }).join('') + `<button class="p-step-btn" onclick="renderSelector()">⚙️ Segment</button>`;
}

function jumpToPresenterStep(stepId) {
  if (!state.catalog) return;
  if (stepId === 'hook') {
    renderLandingHook();
  } else if (stepId.startsWith('q')) {
    state.qIndex = parseInt(stepId.replace('q', ''), 10);
    state.selectedOptionId = state.answers[state.qIndex] || null;
    renderQuestion();
  } else if (stepId.startsWith('quote')) {
    const qIdx = parseInt(stepId.replace('quote', ''), 10);
    renderInterstitialQuote(qIdx);
  } else if (stepId === 'presubmit') {
    renderPreSubmit();
  } else if (stepId === 'result') {
    if (state.answers.length === 0 && state.catalog.questions.length > 0) {
      // Provide standard answers for instant result demo
      state.answers = state.catalog.questions.map(q => q.options[0].option_id);
    }
    executeScoringAndShowResult();
  }
}

/* ==========================================================================
   RENDER: SELECTOR SCREEN
   ========================================================================== */
function renderSelector() {
  state.view = 'selector';
  updatePresenterNav();
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
        <span class="icon">🦁</span>
        <div><b>ชุดคำถามพร้อมนำเสนอ:</b> ${found[0].metadata.product}
        (${pillLabel('channel', found[0].metadata.channel)} ·
        ${pillLabel('applicant', found[0].metadata.applicant)} ·
        ${pillLabel('age_bracket', state.sel.age_bracket)} ·
        ${pillLabel('gender', found[0].metadata.gender)})</div></div>`;
  } else if (allPicked && found.length === 0) {
    banner = `<div class="match-banner show"><span class="icon">🚧</span>
        <div>ยังไม่มีชุดคำถามสำหรับ Segment นี้ในโฟลเดอร์ output/</div></div>`;
  }

  root.innerHTML = `
    <div class="selector-card">
      <p class="eyebrow"><span>🦁</span> Generali Thailand · Deep Question Engine</p>
      <h1 class="title">เลือก Segment เพื่อเปิดการสาธิต</h1>
      <p class="subtitle">ระบบดึงข้อมูล ${CATALOGS.length} ชุดคำถามจากแค็ตตาล็อก — เลือกตัวเลือกด้านล่างเพื่อเริ่มสัมผัส Interactive Journey แบบเต็มจอ Responsive</p>
      ${blocks}
      ${banner}
      <button class="cta-launch" ${ctaDisabled} onclick="startJourney()">
        <span>เริ่มสัมผัส Interactive Journey</span> <span>➔</span>
      </button>
      ${state.sel && Object.keys(state.sel).length ? '<button class="p-step-btn" style="margin-top:14px;width:100%;color:#495057;background:#f3f4f6;" onclick="resetSelector()">เริ่มเลือกใหม่</button>' : ''}
    </div>
  `;
}

function resetSelector() { state.sel = {}; renderSelector(); }

function startJourney() {
  const found = matches(state.sel);
  if (found.length !== 1) return;
  state.catalog = found[0];
  state.qIndex = 0;
  state.answers = [];
  state.selectedOptionId = null;
  state.evalResult = null;

  renderLandingHook();
}

function wrapWithAppFrame(contentHtml, showOuterHeader = true) {
  const meta = state.catalog ? state.catalog.metadata : null;
  const metaBadge = meta ? `${meta.product} · ${meta.channel} · ${meta.age_bracket}` : 'GENERALI';
  const headerHtml = showOuterHeader ? `
    <div class="app-header-strip">
      <div class="app-logo"><span>GENERALI</span> THAILAND</div>
      <div class="app-badge-meta">${metaBadge}</div>
    </div>` : '';
  return `
    <div class="responsive-app-card">
      ${headerHtml}
      ${contentHtml}
    </div>
  `;
}

/* ==========================================================================
   SCREEN 1: LANDING HOOK (IMAGE 1)
   ========================================================================== */
function renderLandingHook() {
  state.view = 'hook';
  updatePresenterNav();
  const c = state.catalog;
  const hook = c.landing_hook;
  const root = document.getElementById('app');

  const designerBox = state.designer && hook.hook_rationale ? `
    <div class="reviewer-intel-card">
      <b>TSR / Copywriter Intel:</b><br>
      • Hook Lever: ${hook.hook_rationale}<br>
      • Target Segment: ${c.metadata.age_bracket} (${c.metadata.gender}) · ${c.metadata.tone}
    </div>` : '';

  const innerHtml = `
    <div style="text-align:center;">
      <div class="hook-badge-pill">
        <span>🛡️</span> <span>วิเคราะห์ความเสี่ยงเฉพาะบุคคล · ประมาณ 2 นาที</span>
      </div>
    </div>

    <h2 class="hook-title">${hook.headline}</h2>
    
    <div class="anchor-card-luxury">
      <div class="anchor-label-text">${hook.anchor_card.label}</div>
      <div class="anchor-stat-highlight">${hook.anchor_card.highlight_number}</div>
      <div class="anchor-sub-text">
        <span>⚠️</span> <span>${hook.anchor_card.sub_caption}</span>
      </div>
    </div>

    <div class="hook-promise-box">
      ${hook.diagnostic_promise}
    </div>

    <button class="btn-generali-cta" onclick="startQuestions()">
      <span>${hook.cta_text}</span> <span>➔</span>
    </button>

    <div class="trust-strip">
      <span>🔒 ปลอดภัยตาม PDPA</span>
      <span>⚡ ทราบผลทันที</span>
      <span>🎯 ไม่มีข้อผูกมัด</span>
    </div>

    ${designerBox}
  `;

  root.innerHTML = wrapWithAppFrame(innerHtml);
}

function startQuestions() {
  state.qIndex = 0;
  renderQuestion();
}

/* ==========================================================================
   QUIZ QUESTIONS (COURSIV-STYLE INTERACTIVE OPTIONS + INTERSTITIAL QUOTES)
   ========================================================================== */
function getOptionEmoji(label, idx) {
  const text = label || '';
  if (/คนใกล้ตัว|ครอบครัว|คนที่บ้าน|คนรัก/i.test(text)) return '👨‍👩‍👧‍👦';
  if (/วางแผน|งบ|ประหยัด|การเงิน/i.test(text)) return '📊';
  if (/เอกชน|โรงพยาบาล/i.test(text)) return '🏥';
  if (/ไม่แข็งแรง|ร่างกาย|เหนื่อย|สัญญาณ/i.test(text)) return '⏳';
  if (/ข่าว|เห็นข่าว/i.test(text)) return '📰';
  if (/ภาษี|ลดหย่อน/i.test(text)) return '💰';
  if (/ทางเลือก|มากกว่า/i.test(text)) return '✨';
  if (/วงเงิน|ความคุ้มครอง/i.test(text)) return '🛡️';
  if (/ค่าห้อง|เตียง/i.test(text)) return '🛏️';
  if (/เบี้ย|ราคา/i.test(text)) return '💵';
  if (/เครือข่าย|ครอบคลุม/i.test(text)) return '🌐';
  if (/ชื่อเสียง|ความมั่นคง/i.test(text)) return '🏛️';
  if (/เคลม|รวดเร็ว/i.test(text)) return '⚡';
  if (/แข็งแรงดี|ไม่มีโรค/i.test(text)) return '💪';
  if (/โรคประจำตัว|ทานยา/i.test(text)) return '💊';
  if (/หายป่วย/i.test(text)) return '🌱';
  if (/รักษาอยู่/i.test(text)) return '🩺';
  if (/บัตรเครดิต/i.test(text)) return '💳';
  if (/Mobile Banking|โอน/i.test(text)) return '📱';
  if (/บัตรเดบิต/i.test(text)) return '🏦';
  if (/อื่นๆ|ระบุ/i.test(text)) return '✍️';
  if (/ต่ำกว่า|<10/i.test(text)) return '🥉';
  if (/10,000-20,000/i.test(text)) return '🥈';
  if (/20,000-30,000/i.test(text)) return '🥇';
  if (/มากกว่า|>30/i.test(text)) return '💎';

  const FALLBACK_EMOJIS = ['💡', '🎯', '✨', '⚡', '🔹', '🌟'];
  return FALLBACK_EMOJIS[idx % FALLBACK_EMOJIS.length];
}

const INTERSTITIAL_QUOTES = {
  0: {
    title: 'เพราะเรื่องใกล้ตัว... สะกิดให้เราเริ่มวางแผน',
    badge: 'ข้อคิดชวนคิด',
    nextLabel: 'ไปต่อที่คำถามที่ 2 ➔',
  },
  2: {
    title: 'ค่าห้องและวงเงิน... คือตัวชี้วัดความอุ่นใจที่แท้จริง',
    badge: 'ข้อคิดชวนคิด',
    nextLabel: 'ไปต่อที่คำถามที่ 4 ➔',
  }
};

function getQuoteData(qIndex, q) {
  if (INTERSTITIAL_QUOTES[qIndex]) return INTERSTITIAL_QUOTES[qIndex];
  return {
    title: 'ข้อคิดสำคัญเพื่อความมั่นใจของคุณ',
    badge: 'ข้อคิดชวนคิด',
    nextLabel: `ไปต่อที่คำถามที่ ${qIndex + 2} ➔`,
  };
}

function renderQuestion() {
  state.view = 'question';
  updatePresenterNav();
  const c = state.catalog;
  const q = c.questions[state.qIndex];
  const total = c.questions.length;
  const root = document.getElementById('app');

  const progressPercent = Math.round(((state.qIndex + 1) / total) * 100);

  const chosen = q.options.find(o => o.option_id === state.selectedOptionId);

  const optionsHtml = q.options.map((o, idx) => {
    const isSelected = state.selectedOptionId === o.option_id;
    const selectedClass = isSelected ? 'selected' : '';
    const emoji = getOptionEmoji(o.label, idx);
    const weightBadge = state.designer && typeof o.risk_weight === 'number'
      ? `<span class="intel-tag red" style="margin-left:auto;">+${o.risk_weight}</span>` : '';

    let inlineReflectionHtml = '';
    if (isSelected && o.micro_reflection) {
      inlineReflectionHtml = `
        <div class="coursiv-reflection-bubble">
          <div class="advisor-avatar-circle">🧑‍💼</div>
          <div class="reflection-text-col">
            <div class="reflection-advisor-label"><span>💡</span> คำแนะนำจากที่ปรึกษา Generali</div>
            <div class="reflection-quote-content">“${o.micro_reflection}”</div>
            ${state.designer ? `
              <div class="intel-tag-row" style="margin-top:8px;">
                <span class="intel-tag gold">${o.reflection_technique}</span>
                <span class="intel-tag">${o.underlying_intent}</span>
                ${o.gap_statement ? `<span class="intel-tag red">Gap: ${o.gap_statement}</span>` : ''}
              </div>` : ''}
          </div>
        </div>
      `;
    }

    return `
      <div class="option-item-wrap">
        <button class="option-card-interactive ${selectedClass}" onclick="chooseOption('${q.question_id}','${o.option_id}')">
          <span class="opt-emoji">${emoji}</span>
          <span class="opt-label">${o.label}</span>
          <span class="opt-check-circle"></span>
          ${weightBadge}
        </button>
        ${inlineReflectionHtml}
      </div>
    `;
  }).join('');

  const designerBox = state.designer ? `
    <div class="reviewer-intel-card" style="margin-top:24px;">
      <b>Question Strategy:</b> ${q.step_phase} · ${q.spin_stage}<br>
      • Rationale: ${q.design_rationale}
    </div>` : '';

  const innerHtml = `
    <!-- Top Nav Strip (Single Clean Header) -->
    <div class="coursiv-nav-strip">
      <button class="coursiv-back-btn" onclick="${state.qIndex === 0 ? 'renderLandingHook()' : 'prevQuestion()'}" title="ย้อนกลับ">←</button>
      <div class="coursiv-logo"><span>GENERALI</span> THAILAND</div>
      <div class="coursiv-step-badge">${state.qIndex + 1} / ${total}</div>
    </div>
    <div class="coursiv-progress-line">
      <div class="coursiv-progress-fill" style="width: ${progressPercent}%;"></div>
    </div>

    <!-- Question Content Body -->
    <div class="quiz-content-body">
      <h2 class="quiz-headline">${q.headline}</h2>
      <p class="quiz-subheadline">${q.sub_headline}</p>

      <div class="options-list">${optionsHtml}</div>

      <button class="btn-coursiv-continue" ${chosen ? '' : 'disabled'} onclick="nextQuestion()">
        <span>${state.qIndex === total - 1 ? 'ดูผลการประเมินของคุณ ➔' : 'ไปต่อ ➔'}</span>
      </button>

      ${designerBox}
    </div>
  `;

  root.innerHTML = wrapWithAppFrame(innerHtml, false);
}

function chooseOption(questionId, optionId) {
  state.selectedOptionId = optionId;
  renderQuestion();
}

function prevQuestion() {
  if (state.qIndex > 0) {
    state.qIndex -= 1;
    state.answers.pop();
    state.selectedOptionId = state.answers[state.qIndex] || null;
    renderQuestion();
  }
}

function nextQuestion() {
  const q = state.catalog.questions[state.qIndex];
  const chosen = q.options.find(o => o.option_id === state.selectedOptionId);
  if (!chosen) return;
  state.answers.push(chosen.option_id);
  state.selectedOptionId = null;

  // Interstitial Quote Bridge check (Coursiv style: interleave quotes at strategic milestones)
  if (state.qIndex === 0) {
    renderInterstitialQuote(0);
    return;
  }
  if (state.qIndex === 2) {
    renderInterstitialQuote(2);
    return;
  }

  if (state.qIndex < state.catalog.questions.length - 1) {
    state.qIndex += 1;
    renderQuestion();
  } else {
    // Finished all 5 questions -> go to Screen 2 (Pre-Submit Landing)
    if (state.catalog.pre_submit_landing) {
      renderPreSubmit();
    } else {
      executeScoringAndShowResult();
    }
  }
}

/* ==========================================================================
   COURSIV-STYLE INTERSTITIAL QUOTE / BRIDGE SCREEN (CLEAN & CENTERED)
   ========================================================================== */
function renderInterstitialQuote(afterQIndex) {
  state.view = 'quote';
  state.quoteIndex = afterQIndex;
  updatePresenterNav();

  const q = state.catalog.questions[afterQIndex];
  const quoteMeta = getQuoteData(afterQIndex, q);
  const root = document.getElementById('app');

  const designerBox = state.designer && q.bias_card ? `
    <div class="reviewer-intel-card" style="margin-top:24px;text-align:left;">
      <b>Reviewer Intel · Cognitive Bias Strategy:</b><br>
      • Principle: <span class="intel-tag gold">${q.bias_card.bias}</span><br>
      • Why this bias fits: ${q.bias_card.why_this_bias}<br>
      ${q.bias_card.needs_fact_check ? '• <span class="intel-tag red">⚠️ Needs Fact Check</span><br>' : ''}
      • Question Phase: ${q.step_phase} (${q.spin_stage})
    </div>` : '';

  const innerHtml = `
    <!-- Top Nav Strip (Single Clean Header) -->
    <div class="coursiv-nav-strip">
      <button class="coursiv-back-btn" onclick="backToQuestion(${afterQIndex})" title="ย้อนกลับ">←</button>
      <div class="coursiv-logo"><span>GENERALI</span> THAILAND</div>
      <div class="coursiv-step-badge">${afterQIndex + 1} / ${state.catalog.questions.length}</div>
    </div>
    <div class="coursiv-progress-line">
      <div class="coursiv-progress-fill" style="width: ${Math.round(((afterQIndex + 1) / state.catalog.questions.length) * 100)}%;"></div>
    </div>

    <!-- Main Interstitial Quote (Clean & Centered) -->
    <div class="interstitial-container">
      <div class="interstitial-badge-pill">
        <span>💡</span> <span>${quoteMeta.badge}</span>
      </div>

      <h2 class="interstitial-headline">${quoteMeta.title}</h2>

      <div class="interstitial-quote-lead">
        “${q.bias_card.text}”
      </div>

      <!-- Action Button -->
      <button class="btn-coursiv-continue" onclick="continueFromQuote(${afterQIndex})">
        <span>${quoteMeta.nextLabel}</span>
      </button>

      ${designerBox}
    </div>
  `;

  root.innerHTML = wrapWithAppFrame(innerHtml, false);
}

function continueFromQuote(afterQIndex) {
  state.qIndex = afterQIndex + 1;
  state.selectedOptionId = null;
  renderQuestion();
}

function backToQuestion(afterQIndex) {
  state.qIndex = afterQIndex;
  const prevAnswer = state.answers.pop();
  state.selectedOptionId = prevAnswer || null;
  renderQuestion();
}

/* ==========================================================================
   SCREEN 2: PRE-SUBMIT LANDING (IMAGE 2)
   ========================================================================== */
function renderPreSubmit() {
  state.view = 'presubmit';
  updatePresenterNav();
  const c = state.catalog;
  const pre = c.pre_submit_landing;
  const root = document.getElementById('app');

  const designerBox = state.designer && pre.closing_rationale ? `
    <div class="reviewer-intel-card">
      <b>Pre-submit Conversion Psychology:</b> ${pre.closing_rationale}
    </div>` : '';

  const innerHtml = `
    <!-- Frame 3: Social Proof Banner -->
    <div class="social-proof-card">
      <div class="live-dot"></div>
      <div style="font-size:18px;">👥</div>
      <div>${pre.social_proof}</div>
    </div>

    <!-- Frame 4: Personalized Insight Card -->
    <div class="insight-card-luxury">
      <div class="insight-header">
        <span>✨</span> <span>${pre.insight_card.title}</span>
      </div>
      <div class="insight-message">
        "${pre.insight_card.message}"
      </div>
    </div>

    <!-- Frame 5: High-Converting CTA -->
    <button class="btn-generali-cta" onclick="executeScoringAndShowResult()">
      <span>${pre.cta_label}</span> <span>➔</span>
    </button>
    <div class="cta-subcopy">${pre.cta_subtext}</div>

    <div class="trust-strip" style="margin-top:28px;">
      <span>🔒 เข้ารหัส 256-bit</span>
      <span>⚡ วิเคราะห์ผลแบบเรียลไทม์</span>
      <span>🎯 ไม่มีค่าใช้จ่าย</span>
    </div>

    ${designerBox}
  `;

  root.innerHTML = wrapWithAppFrame(innerHtml);
}

/* ==========================================================================
   SCREEN 3: RESULT EVALUATION SCREEN (IMAGE 3)
   ========================================================================== */
function executeScoringAndShowResult() {
  if (typeof DeepQuestionScoringEngine === 'undefined') {
    alert('Scoring engine library not found!');
    return;
  }
  state.evalResult = DeepQuestionScoringEngine.evaluate(state.catalog, state.answers);
  renderResultScreen();
}

function renderResultScreen() {
  state.view = 'result';
  updatePresenterNav();
  const c = state.catalog;
  const res = state.evalResult;
  const root = document.getElementById('app');

  const designerPanel = state.designer ? `
    <div class="reviewer-intel-card">
      <b>Scoring & TSR Brief Breakdown:</b><br>
      • Base Risk: ${c.result_matrix ? c.result_matrix.base_risk_score : 20}<br>
      • Options Picked: ${res.applied_options.map(o => `${o.option_id} (+${o.risk_weight})`).join(', ')}<br>
      • Budget Tier Mapped: ${res.applied_budget_option || 'None (Default)'}<br>
      • Final Score: ${res.score} / ${res.max_score} (${res.level_name})<br>
      • TSR Brief Notes: ${c.tsr_brief_notes}
    </div>` : '';

  // Gauge Meter SVG arc
  const score = res.score;
  const radius = 60;
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  const color = res.risk_tier === 'low' ? '#10ac84' : (res.risk_tier === 'high' ? '#c8102e' : '#f39c12');

  const budgetTiers = ['<10,000', '10,000-20,000', '20,000-30,000', '>30,000'];
  const liveBudgetPills = budgetTiers.map(t => {
    const isAct = res.coverage.budget_tier === t || (res.applied_budget_option && res.applied_budget_option.includes(t));
    return `<button class="b-live-pill ${isAct ? 'active' : ''}" onclick="recalculateBudgetLive('${t}')">${t}</button>`;
  }).join('');

  const innerHtml = `
    <div class="result-canvas">
      <!-- Frame 1: Badge -->
      <div style="text-align:center;">
        <div class="result-badge">📊 ผลประเมินความคุ้มครองเฉพาะบุคคล</div>
      </div>

      <!-- Frame 2: Headline -->
      <h2 class="result-main-title">${res.headline}</h2>

      <!-- Frame 3: Basis -->
      <div class="result-basis-text">${res.evaluation_basis}</div>

      <!-- Frame 4: Risk Score Gauge -->
      <div class="gauge-meter-wrapper">
        <svg class="gauge-svg" width="180" height="100" viewBox="0 0 160 90">
          <path d="M 20 80 A 60 60 0 0 1 140 80" fill="none" stroke="#e9ecef" stroke-width="12" stroke-linecap="round"/>
          <path d="M 20 80 A 60 60 0 0 1 140 80" fill="none" stroke="${color}" stroke-width="12" stroke-linecap="round"
                stroke-dasharray="${circumference}" stroke-dashoffset="${strokeDashoffset}"
                style="transition: stroke-dashoffset 1s ease-out;"/>
        </svg>
        <div class="gauge-center-val" id="score-counter">${res.score}</div>
        <div class="gauge-center-sub">/ ${res.max_score} คะแนนความเสี่ยง</div>
        <div class="gauge-pill-tag ${res.risk_tier}">
          <span>●</span> <span>${res.level_name}</span>
        </div>
      </div>

      <!-- Frame 6: Generali Policy Card (Coverage & Estimated Premium) -->
      <div class="generali-policy-card">
        <div class="policy-card-top">
          <div>
            <div class="policy-label">ทุนประกันที่แนะนำสำหรับคุณ</div>
            <div class="sum-insured-num">${res.coverage.recommended_sum_insured}</div>
            <div class="sum-insured-range">${res.coverage.sum_insured_range}</div>
          </div>
          <div style="font-size:28px;">🛡️</div>
        </div>

        <div class="premium-divider"></div>

        <div class="premium-row">
          <div>
            <div class="policy-label">เบี้ยโดยประมาณ</div>
            <div class="premium-monthly">${res.coverage.estimated_monthly_premium}</div>
          </div>
          <div class="premium-disclaimer">${res.coverage.premium_disclaimer}</div>
        </div>

        <!-- Live Presenter Budget Switcher -->
        <div class="live-budget-selector">
          <div class="live-budget-label">
            <span>คำนวณตามงบประมาณที่คุณระบุ (ลองปรับสดได้):</span>
            <span style="color:var(--gen-red);font-weight:700;">${res.coverage.budget_tier}</span>
          </div>
          <div class="budget-live-pills">${liveBudgetPills}</div>
        </div>
      </div>

      <!-- Frame 7: Vulnerability Gap Box -->
      <div class="gap-alert-card">
        <div class="gap-alert-header">
          <span>⚠️</span> <span>ช่องโหว่ที่พบในสถานการณ์ของคุณ</span>
        </div>
        <div class="gap-alert-body">${res.vulnerability_gap}</div>
      </div>

      <!-- Lead Capture Form Mockup -->
      <div id="lead-form-box" class="lead-box-luxury">
        <div class="lead-box-title">
          <span>รับข้อเสนอและให้ผู้เชี่ยวชาญ Generali ติดต่อกลับ</span>
          <span class="demo-fill-link" onclick="demoFillLead()">✨ กรอกตัวอย่าง (Demo)</span>
        </div>
        <div class="lead-grid">
          <div class="field-group">
            <label>ชื่อ-นามสกุล</label>
            <input type="text" id="lead-name" placeholder="เช่น คุณวิภาวี สดใส">
          </div>
          <div class="field-group">
            <label>เบอร์โทรศัพท์</label>
            <input type="tel" id="lead-phone" placeholder="08x-xxx-xxxx">
          </div>
        </div>
        <button class="btn-generali-cta" onclick="submitLeadResult()">
          <span>ยืนยันรับแผนความคุ้มครองนี้</span> <span>➔</span>
        </button>
      </div>

      <div id="lead-success-box" class="lead-success-card" style="display:none;">
        <div class="success-check-circle">✓</div>
        <h4 style="margin:0 0 8px;font-size:17px;color:#065f46;">ส่งข้อมูลเรียบร้อยแล้ว</h4>
        <div style="font-size:13px;color:#047857;line-height:1.55;">
          ที่ปรึกษาผู้เชี่ยวชาญ Generali จะติดต่อกลับเพื่ออธิบายสิทธิประโยชน์โดยละเอียดตามช่วงเวลาที่คุณสะดวก
        </div>
      </div>

      ${designerPanel}
    </div>
  `;

  root.innerHTML = wrapWithAppFrame(innerHtml);
}

function recalculateBudgetLive(tier) {
  if (!DeepQuestionScoringEngine || !DeepQuestionScoringEngine.DEFAULT_BUDGET_TIERS) return;
  const newCoverage = DeepQuestionScoringEngine.DEFAULT_BUDGET_TIERS[tier];
  if (newCoverage && state.evalResult) {
    state.evalResult.coverage = { ...newCoverage };
    state.evalResult.applied_budget_option = tier;
    renderResultScreen();
  }
}

function demoFillLead() {
  const nameEl = document.getElementById('lead-name');
  const phoneEl = document.getElementById('lead-phone');
  if (nameEl && phoneEl) {
    nameEl.value = 'คุณสมใจ มั่นคงดี';
    phoneEl.value = '089-555-1234';
  }
}

function submitLeadResult() {
  const formBox = document.getElementById('lead-form-box');
  const successBox = document.getElementById('lead-success-box');
  if (formBox && successBox) {
    formBox.style.display = 'none';
    successBox.style.display = 'block';
  }
}

function toggleDesigner() {
  state.designer = !state.designer;
  document.getElementById('designer-switch').classList.toggle('on', state.designer);
  if (state.view === 'selector') renderSelector();
  else if (state.view === 'hook') renderLandingHook();
  else if (state.view === 'question') renderQuestion();
  else if (state.view === 'presubmit') renderPreSubmit();
  else if (state.view === 'result') renderResultScreen();
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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@300;400;500;600;700&family=Inter:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@500;600;700;800;900&display=swap" rel="stylesheet">
<style>__CSS__</style>
</head>
<body>
  <!-- Executive Presentation Control Bar -->
  <header class="presentation-bar">
    <div class="brand-group">
      <div class="gen-lion-badge">G</div>
      <div class="brand-text">
        <span class="brand-title">Generali Thailand</span>
        <span class="brand-subtitle">Deep Question · Interactive Presentation</span>
      </div>
    </div>

    <div class="controls-right">
      <button class="p-step-btn" style="background:#f1f0eb;color:var(--text-secondary);font-size:12.5px;padding:6px 14px;border-radius:10px;" onclick="renderSelector()">⚙️ เปลี่ยน Segment</button>
      <div class="toggle-reviewer" onclick="toggleDesigner()">
        <span>Reviewer View</span>
        <span class="switch" id="designer-switch"></span>
      </div>
    </div>
  </header>

  <!-- Interactive Application Viewport -->
  <main id="app" style="width:100%;display:flex;justify-content:center;"></main>

  <script id="catalog-data" type="application/json">__CATALOG_DATA__</script>
  <!-- Standalone Scoring Engine Module -->
  <script>__SCORING_ENGINE_JS__</script>
  <!-- UI Controller -->
  <script>__JS__</script>
</body>
</html>
"""


def build(catalogs_dir: Path, out_path: Path, title: str) -> int:
    catalogs = load_catalogs(catalogs_dir)
    if not catalogs:
        raise SystemExit(f"no valid catalogs found in {catalogs_dir}/ — generate some with `python -m deep_question` first")

    # Read standalone scoring engine JS
    scoring_engine_code = ""
    if SCORING_ENGINE_PATH.exists():
        scoring_engine_code = SCORING_ENGINE_PATH.read_text(encoding="utf-8")
    else:
        alt_path = Path(__file__).resolve().parent.parent / "site" / "scoring-engine.js"
        if alt_path.exists():
            scoring_engine_code = alt_path.read_text(encoding="utf-8")

    html = (
        HTML_TEMPLATE
        .replace("__TITLE__", title)
        .replace("__CSS__", CSS)
        .replace("__SCORING_ENGINE_JS__", scoring_engine_code)
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
    p.add_argument("--title", default="Deep Question — Generali Diagnostic Journey Previewer")
    args = p.parse_args()

    n = build(args.catalogs, args.out, args.title)
    size_kb = args.out.stat().st_size / 1024
    print(f"embedded {n} catalog(s) from {args.catalogs}/ -> {args.out}  ({size_kb:.0f} KB)")
    print(f"open with:  open {args.out}" if size_kb else "")


if __name__ == "__main__":
    main()
