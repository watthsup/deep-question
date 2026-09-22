# KNOWLEDGE · SEGMENTS

How the four factors change the person in front of you. Combine them; they interact.

## Factor 1 · Channel (Prospect character)

| Channel | Mental state at click | Copy register | Default archetype | Typical primary bias | What kills the page |
|---|---|---|---|---|---|
| **tiktok** | Scrolling fast, emotionally primed by a short video, impulsive, low patience | Very short lines, numbers first, visceral verbs, casual particles ("เลย", "นะ") | Instant gratification | Hyperbolic discounting, framing | Long sentences, formal tone, anything that reads like a form |
| **facebook** | Browsing family/friend updates, often saw an illness or hospital post, duty-minded | Polite, consultative, family vocabulary ("คนที่บ้าน", "ลูก", "พ่อแม่"), medium sentences | Fear-driven → Risk-averse | Loss aversion, availability | Hype, slang, pressure |
| **instagram** | Lifestyle browsing, aspirational, self-care, aesthetic sensitivity, social comparison | Warm, aspirational, "people like you", clean short lines, lifestyle nouns | Social-driven | Social proof, endowment | Fear imagery, clinical jargon |
| **google** | Searched a specific term; already has intent; comparing; wants clarity and control | Clear, structured, comparative, respects intelligence, explains the mechanism | Smart decision maker | Anchoring, framing | Emotional manipulation, vagueness, hidden numbers |

Channel notes from the business: Facebook skews 35–55 and family-oriented; TikTok 18–35 and emotion-led; Instagram 25–40 and lifestyle; Google is intent-led across ages.

## Factor 2 · Product (what the person is actually buying)

### Non-Life (health & protection)

| Product | What it is | Core anxiety | Best Maslow frame | Underwriting sensitivities |
|---|---|---|---|---|
| **Health Lumpsum Plus** | Comprehensive IPD medical with a lump-sum annual limit | Private-hospital cost, room rates, company welfare gaps | Safety | Health condition, occupation |
| **Health D-Koom (Deductible)** | Medical plan with a deductible, lower premium | Paying twice for cover they already have; wants efficiency | Esteem (smart) + Safety | Works best for people with existing group cover |
| **Senior Extra 7** | Health plan for seniors, often bought by adult children | Parents' hospital bills, not wanting to be a burden / not wanting parents to be | Love & Belonging | Age caps, health condition |
| **Cancer** | Lump-sum payout on diagnosis | Treatment cost of targeted therapy; proximity (someone they know) | Safety, framed as freedom of choice | Waiting period, no health question in the base set |
| **Critical Illness** | Lump-sum on diagnosis of listed serious diseases | Income loss, long recovery, family finances | Safety + Love | Disease list, waiting period |

### Life

| Product | What it is | Core anxiety | Best Maslow frame | Notes |
|---|---|---|---|---|
| **Senior55** | Whole-life for seniors, typically guaranteed issue | Funeral cost, leaving something, not burdening children | Love & Belonging (legacy) | No health questions; often bought as a gift to parents |
| **Senior So Good** | Senior life with a savings flavour | Same as above plus "getting something back" | Love + Esteem | Same |
| **Gen Life Plus 10** | Endowment / savings life with cash-back | Saving discipline, children's future, tax | Esteem (smart saver) + Love | Health condition and occupation asked |
| **PA Pay Money** | Personal accident with cash benefits | Accidents from active lifestyle, commuting, risky job | Safety, framed as freedom to keep living actively | Occupation matters |

## Factor 3 · Applicant (who the visitor is buying for)

The landing page asks this first, so you always know it.

| Applicant | Who you are talking to | What changes |
|---|---|---|
| **me** | The visitor is the insured. Age and gender describe them. | Second person throughout ("คุณ"). Health-condition and occupation questions are about themselves; keep them non-judgemental. `buy_for_who` is redundant: defer as `dropped`. |
| **other** | The visitor is a **buyer**; the insured is someone else. Age and gender describe the insured. Infer the buyer from the relationship: an insured aged 0–5 or 6–22 means the buyer is almost always a parent (typically 23–45); an insured aged 56+ usually means an adult child (36–55) or a spouse of similar age. | Write to the buyer about the insured ("คุณแม่", "ลูกของคุณ", "คนที่คุณดูแล"). Maslow level shifts toward Love & Belonging even for health products. The `buy_for_who` base question is now high-value (often the hook: it tells the TSR the relationship). Health and occupation questions are about the insured; the buyer may not know the answers precisely, so offer an honest "ไม่แน่ใจ" path only if the base options allow it, otherwise phrase gently. The TSR will speak to the buyer; say so in `tsr_brief_notes`. |

## Factor 4 · Insured age bracket

Eight brackets. Adjacent brackets are different people; do not write the same copy for 23–35 and 36–45. For 0–5 and 6–22 the applicant is effectively always `other` (a parent). For `me`, a 6–22 insured means a 20–22-year-old applying for themselves.

| Bracket | Who the insured is | Who the buyer usually is | Tone toward the buyer | What the buyer fears | What convinces |
|---|---|---|---|---|---|
| **0–5 · Infant / toddler** | Baby or small child; frequent minor illness, RSV, dengue, hand-foot-mouth, hospital stays that need a parent off work | Parent, 23–45, often the mother | Warm, reassuring, practical; a parent under sleep debt; short sentences | Their child in a hospital bed; private-room and paediatric costs; missing work; "did I prepare enough" | Peace of mind framing, private-hospital paediatric access, IPD room cover, savings-life for education (Gen Life), "start early while premiums are lowest" |
| **6–22 · Child / student** | School or university; sports, commuting, dengue, accidents; parents pay | Parent, 36–55 (or a 20–22-year-old themselves under `me`) | Polite-practical for parents; casual and short if `me` | Accidents at school or on a motorbike; education plans derailed by illness; a child leaving group cover at 20–22 | PA and health for accidents, education-linked savings, tax framing for parents, "cover the gap when they leave your company plan" |
| **23–35 · Building** | First real salary, first credit card, moving out, marriage, first child; optimistic, still healthy | Themselves; occasionally a spouse or parent | Casual-polite, direct, efficient; "คุณ"; plain numbers | Paying for something they will not use; missing a smarter option; parents' health starting to show | Smart-saver and tax framing, per-month numbers, "start before premiums climb", first-time-buyer normalising, savings-life and PA fit naturally |
| **36–45 · Peak responsibility** | Mortgage, young children, career pressure, parents in their 60s–70s; time-poor | Themselves; also the main **buyer** for parents' and children's plans | Polite but efficient; family vocabulary ("คนที่บ้าน", "ลูก", "พ่อแม่"); respect competence, do not lecture | Being a burden or leaving a gap for the children; a parent's hospital bill; a gap in company welfare they did not see | GAP analysis with concrete scenarios, protecting savings and family income, buying for parents as an act of care |
| **46–55 · Sandwich generation** | Children in university, parents very old, own health signals appearing (checkup results), pre-retirement planning; peak income | Themselves; sometimes a spouse | Polite, grounded, a little slower; acknowledge experience; numbers welcome but not rushed | Becoming uninsurable; a condition appearing; retirement savings eroded by one illness | Loss aversion on retirement savings, "still healthy enough to qualify" as a factual window, critical illness, senior products may now be for themselves (entry age 55) |
| **56–65 · Transition to retirement** | Retiring or just retired; company welfare ending; fixed income begins; grandchildren | Themselves, or an adult child (36–55) buying for them | Warm, unhurried, respectful; shorter sentences but more of them; explain terms | Losing group cover; being rejected for health; rising premiums; being a burden on children | Guaranteed-issue facts, continuity of cover after employment, dignity and independence, legacy; involve the children softly |
| **66–70 · Early senior** | Retired; health is a daily topic; many health products stop accepting new insureds in this range, senior products still do | Usually an adult child (36–55); sometimes themselves | Warm, slow, respectful; short clear sentences; never rush | Rejection, complexity, hidden conditions, being a burden | Simplicity, guaranteed-issue facts, "no health questions" where true, legacy and peace of mind; permission-based copy ("ไม่ต้องรีบ ค่อยๆ ดูได้") |
| **70+ · Senior** | Advanced age; eligibility is the first question, not the last; the buyer is nearly always the adult child and the fit is senior life or senior health with explicit age caps | Adult child (40–60) | Warm, plain, respectful of both buyer and parent; larger type on the front-end; no jokes about age | Being told "no"; funeral cost and debt falling on children; a parent feeling like a burden | Eligibility clarity up front, guaranteed issue where true, funeral and legacy planning as an act of love, "you are doing the responsible thing" for the buyer |

**Eligibility care at the edges.** Compare the bracket with `product.entry_age`. Where the bracket only partly overlaps the window, the profile step must confirm the insured's exact age and the copy must not imply acceptance. For 70+ and for senior products, eligibility is the visitor's first worry: answer it early and honestly rather than at the end.

## Factor 5 · Insured gender

Use as a modifier, never as a stereotype the visitor can feel. When `applicant = other`, this is the insured's gender, not the buyer's; use it for illness relevance and for how to refer to the insured (คุณแม่ / คุณพ่อ, ลูกสาว / ลูกชาย), not for the buyer's tone.

| Gender | Tendencies that are safe to lean on | Avoid |
|---|---|---|
| **Female** | Often the household health decision-maker; responds to care-for-others framing and to being taken seriously on finances; specific illness relevance (breast, cervical, ovarian cancers) may be mentioned factually | Assuming she buys only for others; softening numbers as if she will not understand them |
| **Male** | Often responds to provider/duty framing, to efficiency and to numbers; specific illness relevance (prostate, liver, heart) may be mentioned factually | Assuming indifference to emotion; macho pressure tactics |

## Combining the factors (worked hints)

- **tiktok × me × 23–35 × PA**: Instant gratification. Hook on lifestyle ("ออกกำลังกาย ขี่มอไซค์ เดินทางบ่อย?"). Per-day framing. Two-line micro-reflections.
- **facebook × other × 0–5 × Health Lumpsum Plus**: Buyer is a young parent. Fear-driven softened to protective. Hook on the last time the child was sick; GAP on paediatric IPD costs and lost workdays; emotion step on "sleep at night". Health-condition question is about the child: gentle, factual.
- **facebook × other × 6–22 × Gen Life Plus 10**: Buyer is a parent planning education. Smart decision maker with Love & Belonging. Anchor on tuition, cash-back timing aligned with school years, tax benefit.
- **facebook × me × 36–45 × female × Cancer**: Fear-driven softened to protective. She likely saw a diagnosis nearby. Hook with proximity, gap with treatment cost anchor, emotion step on "choose treatment freely".
- **google × me × 36–45 × male × Health D-Koom**: Smart decision maker. Lead with the mechanism (deductible sits on top of group cover). Anchor premium difference. Respect comparison intent; the brand-comparison spare question may be worth using.
- **facebook × other × 56–65 / 66–70 × Senior Extra 7 / Senior55**: Buyer is the adult child (36–55). Love & Belonging. Hook with the `buy_for_who` relationship, reflect on gratitude, emotion step on "พ่อแม่ได้รักษาแบบไม่ต้องคิดเรื่องเงิน". Eligibility answered early.
- **google × me × 46–55 × Critical Illness**: Smart decision maker with a loss-aversion undertone. Anchor on retirement savings versus one long illness; "still qualify while healthy" as a factual window, never a threat.
- **facebook × me × 56–65 × Health Lumpsum Plus**: Group cover is ending or has ended; bracket sits at the product's upper edge, so confirm exact age in the profile step. GAP step on continuity of cover; children as gentle motivation, not guilt.
- **any × other × 70+ × Senior life**: Buyer is the adult child, possibly reading with the parent. Risk-averse. Slow down. Eligibility and guaranteed issue as relief, first. Legacy and dignity. No implication question that sounds like mortality pressure.
