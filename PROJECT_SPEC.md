# PROJECT_SPEC.md — Math Quest Architecture & Execution Specification

## 1. Pitch
A Nuxt 3 dark-fantasy educational math adventure where every question is AI-generated but strictly verified by deterministic code, every wrong answer is automatically diagnosed as a specific conceptual misconception, and a built-in evaluation dashboard proves AI accuracy with empirical benchmark data.

---

## 2. Tech Stack

### Frontend
- **Framework**: Nuxt 3 (Vue 3) + TypeScript.
- **Rendering**: Static Single Page Application (`ssr: false`, built with `npx nuxt generate` into `.output/public`).
- **State Management**: Pinia (stores/game.ts) for reactive gameplay, adaptive progression, and student inventory.
- **Styling**: Scoped Vanilla CSS & Design Tokens in `app/assets/css/main.css` adhering to `DESIGN.md`. Tailwind CSS configured only as a utility layer without clashing with existing tokens.
- **Animation & Celebration**: GSAP for boss animations and card state transitions, `canvas-confetti` for victory moments.
- **Audio & Accessibility**: Web Speech API (`window.speechSynthesis`) for interactive read-aloud narration.

### Backend & AI
- **Runtime**: Python 3.11, FastAPI, Pydantic v2, `httpx`, `python-dotenv`.
- **Deployment**: Vercel Serverless Python function located at `api/index.py` (`includeFiles: "data/**"`).
- **Mathematical Verifier**: Python standard library `fractions.Fraction` and a safe AST-based arithmetic expression evaluator (`ast.parse`). No unsafe `eval()`, no heavy `sympy`.
- **AI Models**:
  - Primary Generator: Google Gemini API (`gemini-1.5-flash` or current free tier).
  - Benchmark Comparative Model: Groq (`llama-3.1-70b-versatile` / `llama3-8b-8192`) used for offline evaluation.
  - Image Generator: Pollinations.ai (free REST endpoint, no API key needed).
  - Prompt Engineering: Versioned system prompts in `prompts/v1/` and `prompts/v2/`.
- **Data & Evaluation**:
  - Offline evaluation and statistical analysis using `pandas` in `scripts/run_eval.py` (Pandas is strictly omitted from runtime dependencies).
  - Bayesian Knowledge Tracing (BKT) in `api/_lib/bkt.py` to calculate probability of topic mastery $P(L_t)$.
- **Storage**: Zero external databases, zero user logins. Local JSON datasets in `data/` combined with browser `localStorage` for progress persistence.
- **Testing**: `pytest` for Python API verification and BKT logic; `vitest` for frontend composables.
- **Deployment**: Vercel monorepo configuration (`vercel.json`), single origin URL, zero CORS overhead.

### Technical Tradeoffs (Why Certain Technologies are NOT Used)
- **No Supabase / PostgreSQL**: Unnecessary architectural complexity, network latency, and operational cost for an assessment without multi-user accounts.
- **No TensorFlow / PyTorch**: Deep neural models require massive labeled datasets and slow down serverless execution; Bayesian Knowledge Tracing (BKT) is closed-form, deterministic, interpretable, and instantaneous.
- **No AWS Lambda / S3**: Multi-cloud deployment introduces operational failure modes and credential friction for this assessment; generated Pollinations images can be cached in the browser or committed to Git.
- **No MySQL or Flask**: Redundant with FastAPI and static JSON storage.

---

## 3. Repository Architecture

```text
math-quest/
├── app/                              # Nuxt 3 Client Application (Existing QUEST Shell)
│   ├── assets/css/main.css           # Canonical design tokens & typography
│   ├── components/                   # Reusable UI components
│   │   ├── CharacterCodex.vue        # Existing profile & achievement trophies
│   │   ├── DailyTrialCard.vue        # Existing daily crucible widget
│   │   ├── HeroBanner.vue            # Existing continue adventure banner
│   │   ├── QuestHeader.vue           # Existing top navigation HUD
│   │   ├── RealmCards.vue            # Existing 3 realm portals
│   │   ├── TopicMasteryCard.vue      # Existing mastery overview
│   │   ├── WorldMap.vue              # Planned: Interactive realm map & island nodes
│   │   ├── BossQuestion.vue          # Planned: Milestone boss encounter with HP bar
│   │   ├── MisconceptionCard.vue     # Planned: Diagnostic feedback component
│   │   ├── DifficultyLadder.vue      # Planned: Easy/Medium/Hard progression ladder
│   │   ├── Infographic.vue           # Planned: Pollinations + Animated SVG key steps
│   │   ├── Explainer.vue             # Planned: Video-style slide player with Web Speech TTS
│   │   ├── MasteryMeter.vue          # Planned: Radial SVG BKT mastery indicator
│   │   ├── Companion.vue             # Planned: Reactive dragon/familiar companion
│   │   ├── XPBar.vue                 # Planned: Precision gamified XP track
│   │   ├── FractionBar.vue           # Planned: Manipulative for g5-fractions-add
│   │   ├── RatioTable.vue            # Planned: Manipulative for g6-ratios
│   │   └── VolumeBuilder.vue         # Planned: Manipulative for g5-volume
│   ├── composables/                  # State & API hooks
│   │   ├── useQuestData.ts           # Client-side fallbacks & seed structures
│   │   ├── useQuestState.ts          # Core gameplay progression & localStorage state
│   │   ├── useAdaptive.ts            # Planned: 2-up 1-down difficulty manager
│   │   ├── useNarration.ts           # Planned: Web Speech API synthesizer
│   │   └── useApi.ts                 # Planned: Client fetch wrapper for /api/*
│   ├── pages/                        # Nuxt File-Based Routes
│   │   ├── index.vue                 # Command Center dashboard
│   │   ├── map.vue                   # World map with 20 islands
│   │   ├── lesson/[id].vue           # AI Lesson + Infographic + Narrated Explainer
│   │   ├── quiz/[id].vue             # Adaptive Quiz Crucible with Manipulatives
│   │   ├── results.vue               # Performance breakdown & diagnostic review
│   │   ├── codex.vue                 # Mastery Matrix & Axiom records
│   │   ├── vault.vue                 # Hall of Trophies
│   │   └── eval.vue                  # /eval AI accuracy benchmark dashboard
│   ├── public/fallback/              # Committed offline fallback questions & assets
│   ├── stores/game.ts                # Pinia global game state
│   └── types/quest.ts                # TypeScript interfaces
├── api/                              # Python 3.11 FastAPI Serverless Backend
│   ├── index.py                      # FastAPI entrypoint (/api/health, /api/question, /api/answer, /api/eval)
│   └── _lib/
│       ├── schemas.py                # Pydantic v2 data models
│       ├── verifier.py               # AST arithmetic evaluator & fraction comparator
│       ├── adaptive.py               # 2-up 1-down difficulty engine
│       ├── llm.py                    # Gemini & Groq client integrations
│       ├── grounding.py              # Prompt context builder
│       └── bkt.py                    # Bayesian Knowledge Tracing update formulas
├── data/                             # Static JSON Repositories
│   ├── topics.json                   # Canonical 20-topic curriculum registry
│   ├── bank/                         # Pre-generated and verified question banks
│   ├── lessons/                      # Verified lesson content & infographics
│   └── eval_results.json             # Benchmark evaluation metrics (Gemini vs Groq, v1 vs v2)
├── prompts/                          # Versioned Prompt Engineering
│   ├── v1/                           # Baseline generation prompts
│   └── v2/                           # Few-shot grounded prompts with strict JSON schema
├── scripts/                          # Offline Maintenance & Evaluation Tools
│   ├── generate_bank.py              # Offline question bank batch generator
│   ├── seed_bank.py                  # Bank validation & caching script
│   ├── run_eval.py                   # Model benchmark scoring script (Pandas-powered)
│   └── requirements-dev.txt          # Development dependencies (pandas, pytest, uvicorn)
├── tests/                            # Test Suites
│   ├── test_verifier.py              # Unit tests for AST evaluator & fractions
│   ├── test_bkt.py                   # Unit tests for Bayesian Knowledge Tracing
│   └── test_schemas.py               # Pydantic schema validation tests
├── vercel.json                       # Vercel deployment & routing config
├── requirements.txt                  # Production serverless dependencies (FastAPI, Pydantic, httpx)
├── package.json                      # Frontend dependencies & scripts
├── nuxt.config.ts                    # Nuxt 3 SPA configuration
├── README.md                         # Project documentation, deploy guide, verification logs
├── TECHNICAL_NOTES.md                # Architecture decisions & trade-off rationale
├── DESIGN.md                         # Visual source of truth & CSS design tokens
└── PROJECT_SPEC.md                   # This document
```

---

## 4. Topics Registry (20 Total Topics)

All curriculum nodes are driven entirely by `data/topics.json`. The user interface contains zero hardcoded topic logic.

### Grade 5 Topics (10)
1. `g5-place-value`: Place Value & Powers of 10 (`5.NR.1`) — Realm: Enchanted Forest
2. `g5-multiply`: Multi-Digit Multiplication (`5.NR.2`) — Realm: Celestial Frontier
3. `g5-divide`: Multi-Digit Division with Remainders (`5.NR.2`) — Realm: Celestial Frontier
4. `g5-decimal-ops`: Decimal Addition and Subtraction (`5.NR.4`) — Realm: Enchanted Forest
5. `g5-fractions-add`: Adding & Subtracting Fractions with Unlike Denominators (**FLAGSHIP**, `5.NR.3.3`) — Realm: Temple of Wisdom
6. `g5-fractions-multiply`: Multiplying Fractions and Whole Numbers (`5.NR.3.4`) — Realm: Temple of Wisdom
7. `g5-fractions-divide-unit`: Division of Unit Fractions and Whole Numbers (`5.NR.3.6`) — Realm: Temple of Wisdom
8. `g5-volume`: Volume of Rectangular Prisms (**FLAGSHIP-LITE**, `5.GSR.8.3`) — Realm: Temple of Wisdom
9. `g5-order-ops`: Order of Operations & Numerical Expressions (`5.NR.5`) — Realm: Celestial Frontier
10. `g5-decimal-compare-round`: Reading, Comparing & Rounding Decimals (`5.NR.4`) — Realm: Enchanted Forest

### Grade 6 Topics (10)
11. `g6-ratios`: Ratios and Equivalent Ratios (**FLAGSHIP**, `6.NR.4.1`) — Realm: Enchanted Forest
12. `g6-unit-rates`: Unit Rates and Unit Pricing (`6.NR.4.4`) — Realm: Enchanted Forest
13. `g6-percents`: Percent as a Rate per 100 (`6.NR.4.6`) — Realm: Enchanted Forest
14. `g6-fraction-division`: Dividing Fractions by Fractions (`6.NR.1.2`) — Realm: Temple of Wisdom
15. `g6-decimals`: Multi-Digit Decimal Operations (`6.NR.1.3`) — Realm: Temple of Wisdom
16. `g6-integers`: Integers, Opposites & Absolute Value (`6.NR.3.1`) — Realm: Temple of Wisdom
17. `g6-equiv-expressions`: Generating Equivalent Expressions & Distributive Law (`6.PAR.6.5`) — Realm: Celestial Frontier
18. `g6-equations`: Solving One-Step Linear Equations (`6.PAR.7.1`) — Realm: Celestial Frontier
19. `g6-mean-median`: Measures of Center (Mean as Equal Share & Median) (`6.NR.2.1`) — Realm: Celestial Frontier
20. `g6-exponents`: Numerical Expressions with Whole-Number Exponents (`6.PAR.6.1`) — Realm: Celestial Frontier

*(Note: There are zero geometry and zero coordinate-plane topics outside the Grade 5 volume standard).*

---

## 5. Realms & World Taxonomy

The three established QUEST realms map to the following mathematical domains:
- **The Enchanted Forest** (Emerald `#28745B`): Numbers, Place Value, Decimals, Ratios, and Rates.
- **The Temple of Wisdom** (Antique Gold `#D9B66F`): Fractions, Parts of Wholes, Division, and Volume.
- **The Celestial Frontier** (Mystic Violet `#9C8AD6`): Advanced Operations, Expressions, Equations, Exponents, and Statistics.

### Alignment Fix from Early Design Mockups
The initial version of `DESIGN.md` described the realms using high-concept themes (e.g. biology, astrophysics, and computer science). In this educational product, the realms represent pure mathematical disciplines (Forest = Numbers & Ratios, Temple = Fractions & Measurement, Celestial = Patterns & Algebra). Fantasy flavor is preserved in evocative titles, while subtitles always provide clear, plain-language mathematical descriptions.

---

## 6. Question Schema & Verifier Rules

### Question Data Model & UI Contract
```json
{
  "id": "g5-fractions-add-medium-1",
  "topic_id": "g5-fractions-add",
  "standard": "5.NR.3.3",
  "difficulty": "medium",
  "verifier_type": "fraction_arithmetic",
  "template_id": "g5-fractions-add-medium-nature",
  "params": { "a": 2, "b": 3, "c": 1, "d": 6 },
  "stem": "A plant grew 2/3 metre in spring and 1/6 metre in summer. How much did it grow altogether?",
  "expression": "2/3 + 1/6",
  "options": [
    { "id": "A", "text": "1/3", "misconception_id": "added_tops_and_bottoms" },
    { "id": "B", "text": "1/2", "misconception_id": "renamed_bottom_kept_tops" },
    { "id": "C", "text": "1/9", "misconception_id": "multiplied_instead_of_adding" },
    { "id": "D", "text": "5/6", "misconception_id": null }
  ],
  "correct_index": 3,
  "answer": "5/6",
  "hint": "The bottoms are different. Find a number that both 3 and 6 go into evenly before adding.",
  "explanation": "Find the smallest number both 3 and 6 go into: 6. Rename 2/3 as 4/6. Now add: 4/6 + 1/6 = 5/6.",
  "provenance": "verified",
  "model": "template-seed",
  "prompt_version": "seed-v2"
}
```

*UI Contract Note (Option & MisconceptionCard)*:
- The legacy duplicate option property `misconception` is superseded by `misconception_id` (null for correct answer, string rule ID for wrong options).
- When a student selects a wrong option, the client `MisconceptionCard` renders diagnostic feedback looked up from the registry by `misconception_id`, displaying `kid_label`, `diagnosis`, `why_it_fails`, and `mini_example`.

### Deterministic Verifier Protocol
1. **Schema Integrity**: Validated against Pydantic model (`schemas.QuestionModel`). Exactly 4 options, valid difficulty string, matching standard code.
2. **AST Evaluation**: The `expression` string is parsed via Python's `ast` module (supporting only binary operators `+`, `-`, `*`, `/`). Operands are evaluated into exact `fractions.Fraction` objects. No floating-point rounding errors.
3. **Canonical Agreement**: Exactly one option must mathematically equate to the AST result. `correct_index` must agree with that option.
4. **Distractor Sanitization**: All 4 options must be distinct after fraction normalization (e.g. `2/4` and `1/2` cannot coexist).
5. **Misconception Tagging**: Every incorrect distractor must carry a non-null, identifiable misconception string explaining the student's mistake.
6. **Rejection & Safety Valve**: If verification fails, the server retries generation once. If it fails a second time, the server returns a pre-verified question from the static bank in `data/bank/<topic_id>.json`.

---

## 7. Core Feature Requirements

1. **Onboarding**: Simple nickname & grade picker (Grade 5 or Grade 6). Zero PII or external login required.
2. **Interactive World Map**: Visual constellation of 10 island nodes per grade, grouped by realm with lock/unlock states and mastery rings.
3. **AI-Generated Lessons**: Kid-friendly conceptual explanations with step-by-step worked solutions, tagged "AI-generated" or "Offline content".
4. **AI Infographics**: Pollinations fantasy illustration paired with a deterministic animated SVG breakdown.
5. **Narrated Explainer**: Multi-slide presentation with browser Web Speech synthesis, synchronized text highlights, play/pause, and playback speed controls.
6. **Adaptive Crucible**: Dynamic 2-up 1-down difficulty ladder (2 correct = level up, 1 wrong = level down; wrong on hard gives a hint and retry for partial XP).
7. **Misconception Feedback**: Specific feedback targeting the student's conceptual error rather than generic "try again" prompts.
8. **Gamified Economics**: XP weighted by difficulty (Easy: 10, Medium: 20, Hard: 35), combo multiplier capped at 2x, boss battle HP bar, 8+ badges, evolving companion, and victory confetti. XP is only awarded for verified correct answers.
9. **Bayesian Knowledge Tracing (BKT)**: Calculates mastery probability $P(L)$ using prior, slip, guess, and transition parameters ($P(L_0)=0.2$, $P(T)=0.15$, $P(S)=0.1$, $P(G)=0.25$).
10. **Interactive Manipulatives**:
    - `FractionBar`: Segmented visual fraction addition & equivalence ruler.
    - `RatioTable`: Proportional reasoning table calculator.
    - `VolumeBuilder`: 3D isometric/block cube stacking sandbox.
11. **Evaluation Dashboard (`/eval`)**: Interactive charts comparing model accuracy, latency, distractor quality, and listing sample rejected questions.
12. **Content Safety Valve**: An island is only unlocked if its verified question bank contains at least 9 verified questions (3 per difficulty level).
13. **Resilience & Offline Bundling**: Graceful handling of network timeouts, 429 rate limits, and bundled static fallbacks to guarantee zero dead screens.
14. **Accessibility**: 360px mobile-first responsiveness, 44px touch targets, visible focus states, ARIA roles, and `prefers-reduced-motion` compliance.

---

## 8. Known Problems in the Existing Shell (To Be Resolved in Later Steps)

1. **Fake Seed Data**: Hardcoded student profile ("Kaelen Vance", Level 7, 18,920 XP, 14-day streak, pre-filled achievements). New users must start fresh at Level 1, 0 XP, 0 streak.
2. **Unearned Click-XP**: "Continue Adventure" awards +120 XP unconditionally on click without answering any question. XP must be earned exclusively through verified correct answers.
3. **Hardcoded Daily Trial**: Client-side trial with fantasy jargon ("harmonious prime-adjacent value") and a misleading pattern explanation. Must be backed by `/api/question` and validated via `/api/answer`.
4. **Off-Scope Lore Topics**: Existing mock topic lists feature topics not in the Georgia Grade 5/6 standards (e.g. *Orbital Kinematics*, *Spectral Polynomials*, *Fibonacci Spire Puzzles*). These must be replaced with the 20 official Georgia standards topics.
5. **UI & Routing Limitations**:
   - Navigation tabs jump via internal element IDs rather than real Nuxt routes (`/map`, `/lesson/[id]`, `/quiz/[id]`, `/eval`).
   - Minor typography contrast issues on tertiary metadata labels.
   - Runaway fantasy jargon confusing for 5th graders (preserve fantasy names in titles, but pair with plain-language mathematical subtitles).
