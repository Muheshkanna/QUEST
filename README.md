# QUEST: Math Quest

A gamified math learning adventure for Grade 5 and Grade 6 students aligned with the official **Georgia Mathematics Standards (K-12)**. Every question is AI-generated and verified by deterministic code (`fractions.Fraction` and safe AST parsing), misconceptions are diagnosed with targeted conceptual feedback, and an empirical evaluation dashboard (`/eval`) tracks AI reliability.

---

## Architecture Overview

- **Frontend**: Nuxt 3 (Vue 3) + TypeScript, Pinia, GSAP, `canvas-confetti`, Web Speech API. Deployed as a static SPA (`ssr: false`, `nuxt generate` into `.output/public`).
- **Backend API**: Python 3.11, FastAPI, Pydantic v2, `httpx`, `python-dotenv`. Deployed as a Vercel Serverless Function (`api/index.py`).
- **Mathematical Verifier**: AST-based arithmetic evaluator and exact `fractions.Fraction` equality comparator.
- **Evaluation Benchmark**: Bayesian Knowledge Tracing (BKT) engine and offline Gemini vs. Groq benchmark scripts (`scripts/run_eval.py`).

---

## Local Development

### 1. Frontend (Nuxt 3)
```bash
npm install
npm run dev
```
Access the application at `http://localhost:3000`.

### 2. Backend (FastAPI)
Install Python dependencies and run Uvicorn:
```bash
pip install -r requirements.txt
pip install -r scripts/requirements-dev.txt
uvicorn api.index:app --reload --port 8000
```
Verify the health endpoint at:
`http://localhost:8000/api/health`

### 3. Static Generation
```bash
npm run generate
```
Builds the static application to `.output/public/` with `200.html` SPA routing.

---

## Deploy to Vercel

Follow these exact steps to deploy to Vercel:

1. **GitHub Push**:
   Ensure all local changes are committed and push to your GitHub repository:
   ```bash
   git push origin main
   ```

2. **Import into Vercel**:
   - Navigate to the [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New Project**.
   - Select your imported GitHub repository (`QUEST` or `math-quest`).
   - Keep framework preset as `Other` (or null, as configured in `vercel.json`).
   - Build Command is automatically configured as `npx nuxt generate`.
   - Output Directory is automatically set to `.output/public`.
   - Python Serverless Function is automatically configured at `api/index.py` via `vercel.json` (`includeFiles: "data/**"`).

3. **Set Environment Variables**:
   In Vercel **Project Settings > Environment Variables**, add the following required variables:
   - `GEMINI_API_KEY`: Your Google AI Studio API key (obtainable at [aistudio.google.com](https://aistudio.google.com)).
   - `GEMINI_MODEL`: The Gemini model to use for live content (e.g. `gemini-1.5-flash` or `gemini-2.0-flash`).
   - `GROQ_API_KEY`: (Optional) Groq API key if running comparative evaluation benchmarks.

4. **Verify Live Deployment**:
   - Once deployment completes, verify the health endpoint on your live URL:
     ```bash
     curl https://<your-project>.vercel.app/api/health
     ```
     Expected output:
     ```json
     {"status":"online","version":"1.0.0","time":"...","engine":"FastAPI + Python 3.11"}
     ```
   - Verify `/api/topics?grade=5` and `/api/questions/g5-fractions-add?difficulty=easy&limit=3`.
   - In the frontend application HUD, verify that the status indicator displays `API: online`.


---

## Fallback Architecture Note

> **Serverless Python Fallback Notice:**
> If Vercel encounters platform restrictions deploying Python Serverless Functions alongside Nuxt static assets, the architecture supports a direct, zero-breaking-change fallback:
> - Port `api/index.py` and `api/_lib/` into Nuxt Nitro server routes at `server/api/` using TypeScript and the `fraction.js` library.
> - Maintain the exact same endpoint routes (`/api/health`, `/api/question`, `/api/answer`, `/api/eval`) and Pydantic-equivalent Zod/TypeScript schemas.
> *Do NOT switch to this fallback unless instructed.*

---

## TODO: Georgia Mathematics Standards Verification

All 20 curriculum topics are mapped to official Georgia K-12 standards:

| Topic ID | Grade | Georgia Standard Code | Standard Title / Description | Status |
|---|---|---|---|---|
| `g5-place-value` | Grade 5 | `5.NR.1` | Place Value & Powers of 10 | Unverified (cluster code) |
| `g5-multiply` | Grade 5 | `5.NR.2` | Multi-Digit Whole Number Multiplication | Unverified (cluster code) |
| `g5-divide` | Grade 5 | `5.NR.2.2` | Multi-Digit Whole Number Division | Verified |
| `g5-decimal-ops` | Grade 5 | `5.NR.4` | Decimal Addition and Subtraction to Hundredths | Unverified (cluster code) |
| `g5-fractions-add` | Grade 5 | `5.NR.3.3` | Addition & Subtraction of Fractions with Unlike Denominators | Verified |
| `g5-fractions-multiply` | Grade 5 | `5.NR.3.4` | Multiplying Fractions and Whole Numbers | Verified |
| `g5-fractions-divide-unit`| Grade 5 | `5.NR.3.6` | Division of Unit Fractions and Whole Numbers | Verified |
| `g5-volume` | Grade 5 | `5.GSR.8.3` | Discovering Volume by Packing Right Rectangular Prisms | Verified |
| `g5-order-ops` | Grade 5 | `5.NR.5` | Order of Operations & Numerical Expressions | Unverified (cluster code) |
| `g5-decimal-compare-round`| Grade 5| `5.NR.4` | Comparing & Rounding Decimals to Thousandths | Unverified (cluster code) |
| `g6-ratios` | Grade 6 | `6.NR.4.1` | Ratios and Describing Relationships Between Quantities | Verified |
| `g6-unit-rates` | Grade 6 | `6.NR.4.4` | Rates and Unit Rates in Ratio Relationships | Verified |
| `g6-percents` | Grade 6 | `6.NR.4.6` | Calculating Percent as Rate per 100 | Verified |
| `g6-fraction-division` | Grade 6 | `6.NR.1.2` | Dividing Fractions by Fractions | Verified |
| `g6-decimals` | Grade 6 | `6.NR.1.3` | Multi-Digit Decimal Operations | Verified |
| `g6-integers` | Grade 6 | `6.NR.3.1` | Integers, Opposites, and Zero Reference Points | Verified |
| `g6-equiv-expressions` | Grade 6 | `6.PAR.6.5` | Applying Properties of Operations to Generate Equivalent Expressions | Verified |
| `g6-equations` | Grade 6 | `6.PAR.7.2` | Writing and Solving One-Step Linear Equations | Verified |
| `g6-mean-median` | Grade 6 | `6.NR.2.1` | Measures of Center: Mean as Equal Share and Median | Unverified (needs 6.DS.8.2) |
| `g6-exponents` | Grade 6 | `6.PAR.6.1` | Numerical Expressions Involving Whole-Number Exponents | Verified |

*(Standard codes confirmed against the official Georgia K-12 Mathematics Standards on `georgiastandards.org`; cluster-level codes 5.NR.1, 5.NR.2, 5.NR.4, 5.NR.5 and mismatched standard numbers are marked Unverified).*

---

## Rollout Status & Content Safety Valve

In accordance with the content safety valve policy, only curriculum topics that pass full audit verification (deterministic distractor provenance, rule diversity, position distributions <= 35%, and complete per-level counts) are shipped to the active question bank. Topics awaiting rollout have empty banks and display as **"Coming Soon"** on the world map.

| Topic ID | Status | Bank Size | Provenance |
|---|---|---|---|
| `g5-fractions-add` | Shipped (Pilot) | 18 questions | Verified (18/18) |
| `g5-volume` | Shipped (Pilot) | 18 questions | Verified (18/18) |
| `g6-percents` | Shipped (Pilot) | 18 questions | Verified (18/18) |
| `g6-equations` | Shipped (Pilot) | 18 questions | Verified (18/18) |
| `g5-divide` | Shipped (Pilot) | 18 questions | Verified (18/18) |
| `g6-ratios` | Shipped (Batch A) | 18 questions | Verified (18/18) |
| `g6-unit-rates` | Shipped (Batch A) | 18 questions | Verified (18/18) |
| `g5-fractions-multiply` | Shipped (Batch A) | 18 questions | Verified (18/18) |
| `g6-mean-median` | Shipped (Batch A) | 18 questions | Verified (18/18) |
| `g5-decimal-ops` | Shipped (Batch B) | 18 questions | Verified (18/18) |
| `g5-multiply` | Shipped (Batch B) | 18 questions | Verified (18/18) |
| `g6-fraction-division` | Shipped (Batch B) | 18 questions | Verified (18/18) |
| `g5-place-value` | Coming Soon (Incomplete) | 0 questions | Empty bank |
| `g5-decimal-compare-round`| Coming Soon (Incomplete) | 0 questions | Empty bank |
| `g5-fractions-divide-unit`| Coming Soon (Incomplete) | 0 questions | Empty bank |
| `g5-order-ops` | Coming Soon (Incomplete) | 0 questions | Empty bank |
| `g6-decimals` | Coming Soon (Incomplete) | 0 questions | Empty bank |
| `g6-integers` | Coming Soon (Incomplete) | 0 questions | Empty bank |
| `g6-equiv-expressions` | Coming Soon (Incomplete) | 0 questions | Empty bank |
| `g6-exponents` | Coming Soon (Incomplete) | 0 questions | Empty bank |

