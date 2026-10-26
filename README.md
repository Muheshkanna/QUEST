# Math Quest (QUEST)

A gamified math practice app for **Grade 5 and Grade 6** students, aligned to the Georgia Mathematics Standards. This is my submission for **Task 1: Gamified Math Learning Platform**.

- **Live demo:** https://potterhead-math-quest.vercel.app/
- **GitHub:** https://github.com/Muheshkanna/QUEST
- **Author:** MUHESH KANNA M

> **Core idea:** every practice question is checked by code, and every wrong answer is diagnosed as a specific misconception. The app recomputes each answer on the server, so a wrong question cannot reach a student.

---

## What the app does

- **Onboarding without accounts.** The student picks Grade 5 or 6 and a nickname. There is no password, no sign-in and no personal data. Progress is saved in the browser (`localStorage`).
- **World map.** Three themed realms (Enchanted Forest, Temple of Wisdom, Celestial Frontier) group the topics for each grade. 20 topics are registered, and **12 are playable** (see the table below). The rest show "Coming soon".
- **Lessons.** A plain-language explanation, a step-by-step worked example, vocabulary and common mistakes. A badge shows whether the content is **AI-generated** or **Offline content**.
- **"Refresh with AI".** Calls Gemini through the backend for a fresh lesson. The result is validated, and the app falls back to the stored lesson on any failure.
- **Infographic.** An AI-generated illustration (Pollinations.ai) next to an animated SVG step diagram. The math text is drawn by code, so it is always correct.
- **Narrated explainer.** A slide walkthrough narrated with the browser's Web Speech API, with play/pause, speed control and a transcript.
- **Adaptive boss quiz.** 10 questions across easy, medium and hard.
- **Misconception cards.** A wrong answer explains the specific mistake that led to it, then gives a hint and the correct answer with an explanation.
- **Gamification.** Difficulty-weighted XP, combo multiplier, boss HP bar, levels, badges, a results screen (score, accuracy by difficulty, mastery, top misconception to fix) and confetti.
- **Mastery tracking.** Bayesian Knowledge Tracing estimates mastery per topic (Novice, Learning, Proficient, Mastered).
- **Resilience.** If the API is down, the app uses bundled fallback content and shows an "offline content" notice.

### Playable topics (12)

| Grade 5 | Grade 6 |
|---|---|
| Adding and Subtracting Fractions (flagship) | Ratios (flagship) |
| Volume of Rectangular Prisms (flagship) | Unit Rates |
| Multiplying Fractions | Percents |
| Decimal Addition and Subtraction | Dividing Fractions by Fractions |
| Multi-Digit Multiplication | One-Variable Equations |
| Multi-Digit Division with Remainders | Mean and Median |

**Registered but "Coming soon" (8):** Place Value, Comparing and Rounding Decimals, Dividing Unit Fractions, Order of Operations (Grade 5); Multi-Digit Decimals, Integers, Equivalent Expressions, Exponents (Grade 6). I chose to ship fewer topics that are fully verified rather than more topics with weak content. A topic is only playable if its bank has enough verified questions (at least 3 per level).

**Infographic and narrated explainer available for:** [LIST THE TOPICS THAT HAVE BOTH, e.g. Adding and Subtracting Fractions, Ratios, Volume, ...]

---

## How AI is used

| Where | What it does |
|---|---|
| **Gemini API** (`GEMINI_MODEL`) | Generates a fresh lesson on request (`POST /api/lesson/{id}/refresh`). The output is validated with Pydantic and a math check, and the stored lesson is returned on timeout, bad JSON or wrong math. |
| **Pollinations.ai** | Generates the illustration for the infographic. A local fallback is shown if the image fails to load. |
| **Web Speech API** (browser) | Reads the explainer narration aloud. |
| **Versioned prompts** (`prompts/v1/`) | Prompt templates with the standard text and misconception registry injected. |

**Honest note on question generation:** the shipped question bank is **not produced by an LLM at runtime**. It comes from deterministic templates, so every distractor is computed from a known student error and every answer is checked by code. The LLM client (`api/_lib/llm.py`) and the question prompt (`prompts/v1/questions.md`) exist, but bulk LLM question generation was not completed in the time available. Any LLM-written question would have to pass the same verifier before it could be shown.

---

## Correctness: how questions are verified

1. **Safe evaluator.** Every question stores a machine-checkable `expression`, evaluated with Python `fractions.Fraction` through an AST whitelist. There is no `eval()`, and guards limit length, exponent size and node count.
2. **Server-side recomputation.** `POST /api/answer` recomputes the correct answer from the expression instead of trusting the stored `correct_index`. A test corrupts the stored index and checks the server overrides it.
3. **Structural checks.** Exactly 4 options, exactly one equals the computed answer, options are distinct after normalization (for example `1/2` and `0.5`), and `correct_index` agrees.
4. **Distractor provenance.** Every wrong option stores a `misconception_id`. The verifier re-runs that misconception's rule on the question's saved numbers (`params`) and requires the result to equal the option text. A mislabeled or filler distractor fails verification.
5. **Misconception registry** (`data/misconceptions.json`, rules in `api/_lib/misconceptions.py`). Each entry has a kid-friendly label, a diagnosis, why the mistake fails, and a mini example. Rules describe exactly what the student did, for example `added_tops_and_bottoms`: 1/4 + 1/8 becomes 2/12.
6. **Audit script.** `python scripts/audit_bank.py` re-verifies every bank and checks answer-position balance (no position above 35%), per-level counts and use of each misconception rule.

**Limit:** the verifier proves the options match the expression. It cannot prove the story in the stem matches the expression, so stems were reviewed by hand (`data/template_review.md`).

## Adaptive logic and scoring

- Start at medium. **2 correct in a row moves up a level. 1 wrong moves down a level.** A wrong answer on hard shows a hint and allows one retry for 50% XP. Levels are clamped at easy and hard.
- **XP:** easy 10, medium 20, hard 35, multiplied by a combo multiplier capped at 2.0x. XP is awarded only for correct answers.
- **Mastery:** Bayesian Knowledge Tracing with different guess/slip values per difficulty (`api/_lib/bkt.py`).
- The ladder, XP and BKT logic exist in both Python and TypeScript so the quiz works offline, and tests check that both give the same results on shared fixtures.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Nuxt 3 (Vue 3), TypeScript, Pinia, GSAP, canvas-confetti (static/SPA build) |
| Backend | Python, FastAPI, Pydantic v2, httpx |
| Math checking | `fractions.Fraction` plus an AST-based safe evaluator |
| AI | Google Gemini API, Pollinations.ai, browser Web Speech API |
| Data | Static JSON in `data/` and browser `localStorage` (no database) |
| Tests | pytest, Vitest |
| Hosting | Vercel (static frontend and Python serverless function, one URL) |

## Repository structure

```
app/                  Nuxt frontend (pages, components, stores, composables, public/fallback)
api/index.py          FastAPI app (Vercel function entry)
api/_lib/             verifier, misconceptions, adaptive, bkt, llm, grounding, schemas
data/                 topics.json, misconceptions.json, bank/, lessons/, infographics/, explainers/
prompts/v1/           prompt templates
scripts/              seedgen/ (template generators), audit_bank.py, build_fallback.py
tests/                pytest suites
vercel.json           routing and build settings
```

## Running locally

Requirements: Node 18+ and Python 3.11+.

```bash
# 1. Frontend
npm install
npm run dev                      # http://localhost:3000

# 2. Backend (second terminal)
pip install -r requirements.txt
uvicorn api.index:app --reload   # http://127.0.0.1:8000  (docs at /api/docs)
```

Create a local `.env` (never commit it):

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Without a key the app still works fully. Only "Refresh with AI" falls back to the stored lesson.

### Environment variables (names only)

| Name | Purpose |
|---|---|
| `GEMINI_API_KEY` | Gemini API key. Read only by the server. |
| `GEMINI_MODEL` | Model name, for example `gemini-2.5-flash`. |
| `GEMINI_MODEL_FALLBACKS` | Optional comma-separated backup models. |

### Tests and checks

```bash
pytest -q                       # backend, verifier, rules, provenance, API
npx vitest run                  # frontend adaptive logic and parity with Python
python scripts/audit_bank.py    # re-verify every question bank
python scripts/build_fallback.py  # rebuild offline bundle in app/public/fallback
```

## Deploying to Vercel

1. Push the repo to GitHub and import it in Vercel.
2. Set **Framework Preset** to **Other**.
3. Build command `npx nuxt generate`, output directory `.output/public` (also set in `vercel.json`).
4. Add environment variables `GEMINI_API_KEY` and `GEMINI_MODEL` in Project Settings.
5. Deploy, then open `/api/health` to confirm the backend is running.

## How to test the main features

1. Open the live URL in a private window and pick a grade and nickname.
2. Open **Adding and Subtracting Fractions**. Read the lesson, and check the **Infographic** and **Explainer** tabs (press play to hear the narration).
3. Click **Refresh with AI**. The badge shows whether the lesson is AI-generated or fell back to offline content.
4. Start the boss battle. Answer some correctly and watch the difficulty ladder move up. Answer one wrong to see the misconception card.
5. Finish the 10 questions to see the results screen, XP and badges.
6. Open `/api/docs` to try the API directly.

---

## Known limitations

- **Only 12 of the 20 registered topics are playable.** The others are marked "Coming soon" rather than shipped with unverified content.
- **The shipped question bank is template-generated, not LLM-generated.** LLM generation is supported by the client and prompts but was not completed. The LLM is used for lesson refresh.
- **No LLM evaluation dashboard.** `/api/eval` returns an empty state. No model-comparison results are claimed.
- **No accounts, by design.** Progress is stored per browser. A new device or private window starts fresh. This keeps the app free of personal data for children.
- **Standards:** every topic has a `standard_verified` flag in `data/topics.json`, and the standard badge is only shown when it is true. Codes not confirmed against georgiastandards.org are marked unverified: [LIST THEM, e.g. g5-place-value, g5-decimal-ops, g5-multiply]. Please check codes against the official site.
- **Image generation depends on Pollinations.ai**, which can be slow. A local fallback image is shown when it fails.
- **Narration depends on the browser's voices.** If speech is unavailable, the explainer advances on a timer with text only.
- **Free-tier Gemini limits** apply to "Refresh with AI" and may cause fallbacks to stored lessons during heavy use.
- Stem wording was checked by hand, but a small number of awkward questions may remain.

## Privacy and safety

No personal data is collected. The nickname is stored only in the student's browser. API keys are read only on the server from environment variables and are not in the repository or the client bundle.

## AI-assistance disclosure

I used AI coding assistants during development, as the assessment allows. I reviewed and tested the code, and I can explain the verifier, the misconception rules, the adaptive logic, BKT and the deployment setup.
