# KNOWLEDGE · SEGMENTS

How the four factors change the person in front of you. Combine them; they interact.

## Factor 1 · Channel (Prospect character)

| Channel | Mental state at click | Copy register | Default archetype | Typical primary bias | What kills the page |
|---|---|---|---|---|---|
| **tiktok** | Scrolling fast, emotionally primed by a short video, impulsive, low patience | Very short lines, numbers first, visceral verbs, casual particles ("เลย", "นะ") | Instant gratification | Hyperbolic discounting, framing | Long sentences, formal tone, anything that reads like a form |
| **facebook** | Browsing family/friend updates, often saw an illness or hospital post, duty-minded | Polite, consultative, caring vocabulary ("คนที่บ้าน", "คนในครอบครัว", "คนที่คุณห่วงใย"), medium sentences | Fear-driven → Risk-averse | Loss aversion, availability | Hype, slang, pressure |
| **instagram** | Lifestyle browsing, aspirational, self-care, aesthetic sensitivity, social comparison | Warm, aspirational, "people like you", clean short lines, lifestyle nouns | Social-driven | Social proof, endowment | Fear imagery, clinical jargon |
| **google** | Searched a specific term; already has intent; comparing; wants clarity and control | Clear, structured, comparative, respects intelligence, explains the mechanism | Smart decision maker | Anchoring, framing | Emotional manipulation, vagueness, hidden numbers |

Channel notes from the business: Facebook skews 35–55 and family-oriented (the upper half of 23–45 and most of 46–60); TikTok 18–35 and emotion-led (the top of 0–22 under `me`, and the younger half of 23–45); Instagram 25–40 and lifestyle (mostly 23–45); Google is intent-led across all brackets. Use the channel as one of the signals that places the person inside a wide bracket (see Factor 4).

## Factor 2 · Product (what the person is actually buying)

### Non-Life (health & protection)

| Product | What it is | Core anxiety | Best Maslow frame | Underwriting sensitivities |
|---|---|---|---|---|
| **Health Lumpsum Plus** | Comprehensive IPD medical with a lump-sum annual limit | Private-hospital cost, room rates, company welfare gaps | Safety | Health condition, occupation |
| **Health D-Koom (Deductible)** | Medical plan with a deductible, lower premium | Paying twice for cover they already have; wants efficiency | Esteem (smart) + Safety | Works best for people with existing group cover |
| **Senior Extra 7** | Health plan for seniors | Senior hospital bills, protecting family savings and dignity | Love & Belonging | Age caps, health condition |
| **Cancer** | Lump-sum payout on diagnosis | Treatment cost of targeted therapy; proximity (someone they know) | Safety, framed as freedom of choice | Waiting period, no health question in the base set |
| **Critical Illness** | Lump-sum on diagnosis of listed serious diseases | Income loss, long recovery, family finances | Safety + Love | Disease list, waiting period |

### Life

| Product | What it is | Core anxiety | Best Maslow frame | Notes |
|---|---|---|---|---|
| **Senior55** | Whole-life for seniors, typically guaranteed issue | Funeral cost, leaving something, peace of mind for loved ones | Love & Belonging (legacy) | No health questions; often bought for senior family members |
| **Senior So Good** | Senior life with a savings flavour | Same as above plus "getting something back" | Love + Esteem | Same |
| **Gen Life Plus 10** | Endowment / savings life with cash-back | Saving discipline, children's future, tax | Esteem (smart saver) + Love | Health condition and occupation asked |
| **PA Pay Money** | Personal accident with cash benefits | Accidents from active lifestyle, commuting, risky job | Safety, framed as freedom to keep living actively | Occupation matters |

The product is also a strong clue to **where in the bracket** the insured sits: a senior product in 46–60 means the upper end (entry age 55+); a health product with an upper cap of 65 or 70 in 60+ means the lower end; PA or a savings-life plan under `me` in 23–45 leans young; Cancer or Critical Illness for oneself in 23–45 leans toward the late 30s and 40s.

## Factor 3 · Applicant (who the visitor is buying for)

The landing page asks this first, so you always know it.

| Applicant | Who you are talking to | What changes |
|---|---|---|
| **me** | The visitor is the insured. Age and gender describe them. | Second person throughout ("คุณ"). Health-condition and occupation questions are about themselves; keep them non-judgemental. `buy_for_who` is redundant: defer as `dropped`. Under `me`, a 0–22 insured can only be a 20–22-year-old; a 60+ insured is most likely 60–65, still independent and comfortable online. |
| **other** | The visitor is a **buyer** (caregiver, family member, financial protector); the insured is someone else. Age and gender describe the insured. | Write to the buyer using warm, empathetic, and respectful caring language. The landing page already captured who they are buying for upfront, so **`buy_for_who` is NOT asked (defer as `dropped`)**. Never assume or declare a specific relationship (we do not know buyer age or role). The 5 steps follow the standard SPIN arc from the buyer's caring perspective: questions address their goals and observations for the insured, options reflect their protective inner voice ("อยากให้เขา...", "อยากให้ท่าน..."), and health questions are gentle and observational. The TSR will speak to the buyer; describe their caregiving driver in `tsr_brief_notes`. |

## Factor 4 · Insured age bracket

Four brackets. Each one is wide and holds more than one life stage, so the bracket alone does not tell you who the insured is. Read it together with applicant, product and channel to **place the person inside the bracket**, name that placement in `persona_read`, and write for that point. Do not write copy that tries to speak to a newborn and a 22-year-old at the same time; pick the most likely life stage for the insured and write for it. For 0–22 when `applicant = other`, the buyer is caring for a dependent (do not assume exact relationship or buyer age). For `60+`, eligibility is the first worry, not the last.

| Bracket | Who the insured is (life stages inside the bracket) | Who the buyer usually is | How to place the person inside the bracket | Tone toward the buyer | What the buyer fears | What convinces |
|---|---|---|---|---|---|---|
| **0–22 · Child to young adult** | **Infant / toddler (0–5):** frequent minor illness, RSV, dengue, hand-foot-mouth, hospital stays. **School-age (6–17):** sports, commuting, dengue, accidents. **University / first job (18–22):** motorbike commuting, part-time work, transitioning off existing family cover. | When `other`, someone caring for a young dependent (do not assume exact relationship or buyer age). Under `me`, a 20–22 young adult applying for themselves. | `me` → 20–22 young adult, casual and short. `other` + Health Lumpsum Plus → lean early childhood/dependent illness risks. `other` + Gen Life Plus 10 → school-age, savings planning. `other` + PA → active or school/commute age. Product `entry_age` min rules out infants if above 0. | Warm, reassuring, practical; clear and concise. Casual and very short if `me`. | The dependent in hospital; private-room and paediatric costs; unexpected bills; accidents; disruptions to plans. | Peace of mind, private hospital access and IPD cover, starting early for lower premiums, savings with cash-back, accident coverage. |
| **23–45 · Building to peak responsibility** | **Building (23–32):** first salary, career start, marriage, early independence. **Peak responsibility (33–45):** mortgage, growing responsibilities, career pressure, family care; time-poor; health starting to matter. | Themselves most of the time. When `other`, someone caring for an adult in this bracket (partner, sibling, family member — do not assume which). | tiktok / instagram → lean younger half. facebook → lean older half. google → intent-driven; let the product decide. PA or Gen Life Plus 10 under `me` → younger, smart-saver. Cancer, Critical Illness or Health Lumpsum Plus under `me` → lean late 30s to 40s. | Younger reading: casual-polite, direct, efficient; "คุณ"; plain numbers. Older reading: polite, consultative, caring vocabulary ("คนที่บ้าน", "คนในครอบครัว", "คนที่คุณห่วงใย"); respect competence. | Paying for something unused; missing a smarter option; health signals appearing; unexpected hospital bills affecting savings. | Monthly pricing, smart-saver and tax framing, locking in coverage early, GAP analysis with concrete scenarios, protecting family savings. |
| **46–60 · Sandwich generation to retirement** | **Sandwich (46–55):** peak career, pre-retirement planning, emerging health checkup signals. **Transition (56–60):** retiring soon; company welfare ending; fixed income begins; senior products now open (entry age 55). | Themselves most of the time. When `other`, someone caring for a loved one in this transition stage. | google + Critical Illness or Cancer → checkup-result reader, lower half. facebook + Health Lumpsum Plus → welfare ending, upper half. Senior products → upper half by definition (55+); confirm exact age. | Polite, grounded, thoughtful; numbers welcome without rushing. Upper reading: warmer, unhurried, clear explanations. | Becoming uninsurable; savings eroded by illness; losing employer coverage; rising premiums. | Protecting retirement savings, qualifying while healthy as a factual window, coverage continuity after employment, dignity and independence. |
| **60+ · Retirement to advanced age** | **Just retired (60–65):** active, often eligible for health products at the edge of their window, comfortable online. **Early senior (66–70):** health is a daily topic; some health products cap out, senior products still accept. **Senior (70+):** eligibility is the primary concern; fit is senior life or senior health with explicit age caps. | When `other`, someone caring for an older loved one (do NOT assume relationship or buyer age). Under `me`, the insured is most likely 60–65 and independent. | `me` → lean 60–65; address as a capable adult. `other` → respect that the insured is an older loved one; check product `entry_age` max to confirm whether the product window caps at 65, 70, or higher. Senior life with guaranteed issue → lead with eligibility relief. | Warm, unhurried, respectful of the buyer's care for an older loved one; short clear sentences; never rush; no jokes about age; respectful pronoun "ท่าน". | Rejection or complex underwriting; hidden conditions; heavy medical bills falling on the family; loss of dignity. | Immediate eligibility clarity, guaranteed issue where true, continuity of cover, dignity and peace of mind, protecting family financial stability. |

**Eligibility care at the edges.** Because the brackets are wide, many of them straddle a product's entry-age window. Compare the bracket with `product.entry_age` every time. Typical cases: 0–22 under `me` against a product that starts at 20; 46–60 against a senior product that starts at 55; 60+ against a health product that stops at 65 or 70. Where the bracket only partly overlaps the window, the profile step must confirm the insured's exact age and the copy must not imply acceptance. For 60+ and for all senior products, eligibility is the visitor's first worry: answer it early and honestly rather than at the end.

## Factor 5 · Insured gender

Use as a modifier, never as a stereotype the visitor can feel. When `applicant = other`, this describes the insured, not the buyer; use it strictly for relevant health and medical context. **Never assume relationship (no "แม่", "พ่อ", "ลูก").** Always use neutral caring terms ("คนที่คุณห่วงใย", "คนสำคัญของคุณ", "คนที่คุณต้องการดูแล", "คนในครอบครัว") with pronoun "เขา" or respectful "ท่าน" (for 60+).

| Gender | Tendencies that are safe to lean on | Avoid |
|---|---|---|
| **Female** | Often the household health decision-maker; responds to care-for-others framing and to being taken seriously on finances; specific illness relevance (breast, cervical, ovarian cancers) may be mentioned factually | Assuming she buys only for others; softening numbers as if she will not understand them |
| **Male** | Often responds to provider/duty framing, to efficiency and to numbers; specific illness relevance (prostate, liver, heart) may be mentioned factually | Assuming indifference to emotion; macho pressure tactics |

## Combining the factors (worked hints)

- **tiktok × me × 23–45 × PA**: Instant gratification. Channel and product both point to the younger half. Hook on lifestyle ("ออกกำลังกาย ขี่มอไซค์ เดินทางบ่อย?"). Per-day framing. Two-line micro-reflections.
- **facebook × other × 0–22 × Health Lumpsum Plus**: Buyer is caring for a young dependent. Do NOT assume relationship. Protective and reassuring tone. Hook on protecting someone they care about from private hospital and IPD costs; GAP on sudden treatment expenses; emotion step on peace of mind knowing they are covered. Gentle observational health questions.
- **facebook × other × 0–22 × Gen Life Plus 10**: Buyer is planning financial security/savings for a young dependent. Smart decision maker with Love & Belonging. Anchor on future readiness, cash-back timing, and long-term security.
- **tiktok × me × 0–22 × PA**: The only `me` reading in this bracket: a 20–22-year-old on a motorbike, first job or final year. Very short, casual, numbers first; "cover yourself now that you are leaving your parents' plan".
- **facebook × me × 23–45 × female × Cancer**: Read her as the older half: someone who likely saw a diagnosis nearby. Fear-driven softened to protective. Hook with proximity, gap with treatment-cost anchor, emotion step on "choose treatment freely".
- **google × me × 23–45 × male × Health D-Koom**: Smart decision maker; the deductible product itself implies existing group cover, so an employed man in his 30s. Lead with the mechanism (deductible sits on top of group cover). Anchor premium difference. Respect comparison intent; the brand-comparison spare question may be worth using.
- **instagram × me × 23–45 × female × Gen Life Plus 10**: Social-driven, aspirational, younger half. "People like you are already saving this way." Endowment framed as a lifestyle habit, not a sacrifice; tax as the smart bonus.
- **google × me × 46–60 × Critical Illness**: Smart decision maker with a loss-aversion undertone; read the lower half (checkup result in hand). Anchor on retirement savings versus one long illness; "still qualify while healthy" as a factual window, never a threat.
- **facebook × me × 46–60 × Health Lumpsum Plus**: Read the upper half: group cover is ending or has ended. If the product's window stops at or near 60, confirm exact age in the profile step. GAP step on continuity of cover; family as gentle motivation.
- **facebook × me × 46–60 × Senior55 / Senior So Good**: Senior product for themselves means 55+ by definition. Frame as planning ahead and leaving something behind on their own terms, not as "you are old now". Confirm exact age early; the lower half of the bracket is not eligible.
- **facebook × other × 60+ × Senior Extra 7 / Senior55**: Buyer is caring for an older loved one (60+). Do NOT assume relationship or buyer age. Love & Belonging / family protection. Hook on wanting the best hospital care for someone they care about without medical debt falling on the family. Reflect on care, comfort, and dignity. Emotion step on receiving quality care without financial worry. Options in caregiver's voice using respectful neutral pronoun ("ท่าน").
- **facebook × me × 60+ × Health Lumpsum Plus**: The `me` reading is the recently retired 60–65 person, still independent. The bracket runs past the product's cap, so eligibility and exact age come first, framed as relief ("ยังสมัครได้") only once confirmed. Continuity of cover after employment is the GAP.
- **any × other × 60+ × Senior life**: Buyer is caring for an older loved one (60+). Do NOT assume relationship or buyer age. Risk-averse. Slow down. Eligibility and guaranteed issue as relief, first. Legacy, comfort, and dignity.
