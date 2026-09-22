# AI1 Behavioral Questionnaire Engine: System Specification & Master Prompt Architecture

---

## 1. Consolidated Requirements & Architectural Paradigm

The objective of the **Question Generation Engine** for Project AI1 is to replace legacy, high-dropoff landing pages with a **Config-Driven Personalized Questionnaire Engine**.

┌────────────────────────────────────────────────────────────────────────┐
│                        LEGACY VS. AI1 PARADIGM                         │
├────────────────────────────────────────────────────────────────────────┤
│ Legacy Flow (High Friction, Low Value):                                │
│   Landing Page ──> Form (Name, Phone, Email, Age) + OTP ──> Raw Lead   │
│   (Result: TSR calls blind, spends 3-5 mins qualifying from scratch)   │
├────────────────────────────────────────────────────────────────────────┤
│ AI1 Target Flow (Value-First Conversation):                            │
│   Channel (UTM) ──> Hook ──> 5 Adaptive Questions ──> Risk Score       │
│                     │         (Instant Micro-Reframe) │                │
│                     └─────────────────────────────────┴──> Rich Lead   │
│   (Result: 20+ Telemetry data points + Pre-Call Brief for TSR)         │
└────────────────────────────────────────────────────────────────────────┘


* **Value-First Principle:** Invert the traditional funnel from "demanding customer trust upfront" (forcing phone numbers and OTP verifications on screen 1) to "delivering immediate diagnostic value" via an empathetic 5-question consultative dialogue with a free personal risk assessment.


* **Single-Agent Synthesis (Zero Latency Serving):** Discard nightly automated AI prompt rewriting and live-runtime LLM generation to eliminate runtime latency, infrastructure cost, and regulatory underwriting drift. A single, highly specialized **Behavioral Question Generation Agent** synthesizes static, fully compliant JSON catalogs offline for instant client-side rendering.


* **4-Factor Ingestion Matrix:** Question sets dynamically adapt across four critical dimensions:


1. Factor 1 (Channel / Prospect Character): Ingested via utm_source (`facebook`, `tiktok`, `instagram`, `google`).


2. Factor 2 (Product Type): Non-Life products (Health Lumpsum Plus, Health D-Knom, Senior Extra 7, Cancer) and Life products (Senior55, Senior So Good, Gen Life Plus 10, PA Pay Money).


3. Factor 3 (Age Bracket): Young Achievers (18–30), Established Family (31–49), and Mature/Senior (50+).


4. Factor 4 (Gender): Male, Female.




* **5-Step Psychological Progression:** Every catalog strictly executes five progressive stages: Q1 Open/Demographic Hook, Q2 Concrete Pain Point, Q3 Coverage Gap & Readiness, Q4 Underwriting/Identity Verification, and Q5 Dominant Emotional Driver.


* **Dynamic Micro-Reflection Requirement:** Each selectable option must be paired with an instant psychological reframe displayed dynamically upon user selection, validating their emotion and bridging to the next step.


* **System Demarcation:**
* **Part 1 (This Agent):** Offline Behavioral Question Generation & Micro-Reflection Synthesis.
* **Part 2 (Downstream Engine):** Submission Telemetry Processing, Lead Scoring (20+ fields), and TSR Pre-Call Brief Enrichment.





---

## 2. Input and Output Specifications

┌────────────────────────────────────────────────────────────────────────┐
│                        INPUT / OUTPUT BOUNDARIES                       │
└────────────────────────────────────────────────────────────────────────┘
  INPUTS:
  ├── [Canonical Underwriting Base] ──> Raw Product Spreadsheets (10 Products)
  ├── [Channel Behavioral Rules]    ──> UTM Dynamics (TikTok, FB, IG, Google)
  ├── [Demographic Segments]        ──> Age Brackets (18-30, 31-49, 50+) & Gender
  └── [Psychological Knowledge Base]──> 5 Archetypes, SPIN, GAP, FAB, Biases
                                        │
                                        ▼
                   [BEHAVIORAL QUESTION GENERATION AGENT]
                                        │
                                        ▼
  OUTPUTS:
  └── [Static Production JSON]      ──> Deterministic Question Catalogs
                                        ├── Personalized Headlines & Context
                                        ├── Empathetic Choices + Intent Tags
                                        ├── Instant Dynamic Micro-Reflections
                                        └── Cognitive Bias Transition Cards


### 2.1 Input Data Specification

1. **Canonical Product Rules (Excel Ground Truth):** Invariant core underwriting requirements across 10 products, including budget tiers (`<10k`, `10k-20k`, `20k-30k`, `>30k`), purchase criteria, payment modes, and pre-existing condition declarations.


2. **Channel Behavioral Archetypes:**
* `tiktok`: High-speed consumption, visceral emotion, hyper-concise text, hyperbolic discounting, numbers-first.


* `facebook`: Family-centric security, loss aversion, duty to dependents, polite and consultative tone.


* `instagram`: Lifestyle preservation, aesthetic, aspirational self-care, social proof.


* `google`: High search intent, objective clarity, smart financial decision framing.




3. **Demographic Modifiers:** Age groups and gender classifications determining vocabulary, deference levels, and relational focus.


4. **Behavioral Psychology Directives:** Dark AI Marketing archetypes, SPIN progression, GAP analysis, and cognitive bias triggers.



### 2.2 Output Data Specification

The agent outputs a schema-validated **Production JSON Catalog** structured for instant loading by client-side form engines:

* `catalog_id`: Deterministic unique identifier (e.g., `CANCER_FB_3149_F_V1`).
* `metadata`: Complete targeting classification (product, channel, age, gender, archetype, tone).
* `questions[]`: Exactly 5 sequential question objects containing:
* `question_id`: Stable identifier (e.g., `Q1`).
* `step_phase`: Mapping to the 5-step framework.


* `headline`: Audience-tailored conversational question text.


* `sub_headline`: Contextual framing or statistical primer.


* `options[]`: Array of choice objects containing `option_id`, label (internal-monologue phrasing), underlying_intent (psychological classification for sales), underwriting_value (normalized policy filter), and micro_reflection (instant dynamic feedback copy).


* `bias_card`: Cognitive bias priming text displayed at the question footer.





---

## 3. Psychological Frameworks & Behavioral choice Architecture

┌────────────────────────────────────────────────────────────────────────┐
│                   PSYCHOLOGICAL PROGRESSION MAPPING                    │
├──────────────┬───────────────────┬─────────────────────────────────────┤
│ 5-Step Phase │ Sales Methodology │ Psychological Objective             │
├──────────────┼───────────────────┼─────────────────────────────────────┤
│ Q1: Hook     │ Situation (SPIN)  │ Maslow Baseline: Security / Self    │
│ Q2: Pain     │ Problem (SPIN)    │ GAP Analysis: Assumption vs Reality │
│ Q3: Gap      │ Implication (SPIN)│ Loss Aversion / Availability Bias   │
│ Q4: Profile  │ Underwriting Fact │ Anchoring: Reframing cost per day   │
│ Q5: Emotion  │ Need-Payoff (SPIN)│ Commitment & Consistency to TSR     │
└──────────────┴───────────────────┴─────────────────────────────────────┘


### 3.1 Cognitive & Sales Methodologies

* **SPIN Selling Progression:**
* Situation (Q1): Non-invasive baseline qualification.


* Problem (Q2): Exposing implicit friction in existing medical/life coverage.


* Implication (Q3): Magnifying financial fallout if unaddressed using Availability Bias and Loss Aversion.


* Need-Payoff (Q5): Prompting the user to select the core emotional relief they seek.




* **GAP Analysis:** Juxtaposing perceived readiness against actual costs (e.g., company welfare vs. targeted therapy costs of 1.5M+ THB).


* **Maslow Hierarchy Alignment:** Aligning personal healthcare with basic Safety needs, and family/senior plans with Love, Belonging, and Generational Duty.


* **FAB (Feature-Advantage-Benefit):** Translating policy jargon into personal autonomy (e.g., translating "Deductible" into "lower annual fixed cost while keeping catastrophic protection").


* **Feel-Felt-Found:** Drafting options that validate hesitations before pivoting to empowerment.



### 3.2 Dark AI Marketing 5 Archetypes

Targeting copy is adapted across five psychological profiles:

1. **Fear-Driven:** Loss Aversion and Scarcity focus; emphasizes protecting savings from depletion.


2. **Instant Gratification:** Hyperbolic Discounting focus; short copy, instant calculation, immediate payoff.


3. **Smart Decision Maker:** Framing and Anchoring focus; presents insurance as proactive portfolio hedging.


4. **Social-Driven:** Social Proof focus; cites demographic consensus to lower decision anxiety.


5. **Risk-Averse:** Commitment & Consistency focus; gentle, respectful, reassurance-led with zero pressure.



### 3.3 Dynamic Micro-Reflection Mechanism

Beneath each option, the engine provides a micro_reflection that renders on the frontend upon selection. This acts as a conversational validation, reassuring the user before they proceed:

| User Selection Example | Psychological Intent | Dynamic Micro-Reflection Copy

 |
| --- | --- | --- |
| *"I don't want to burden my family."*<br> | Altruism / Fear of Burden

 | "Insurance is never truly bought for oneself; it is the highest form of love and independence you gift to those who walk beside you." |
| *"I already have corporate welfare."*<br> | Complacency / False Security | "Corporate plans provide a solid baseline for routine care, but dedicated top-up plans protect your personal savings from medical inflation." |
| *"Afraid of cancer therapy costs."*<br> | Loss Aversion / Catastrophic Fear

 | *"Modern targeted therapies achieve high remission rates, but average over 1.5M THB. Converting that risk