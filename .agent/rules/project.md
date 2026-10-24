# Project Rules & Guidance for Math Quest

Always read and adhere to:
1. `PROJECT_SPEC.md` — The complete source of truth for all curriculum standards, API contracts, question schemas, BKT equations, and project requirements.
2. `DESIGN.md` — The visual source of truth for all CSS design tokens, palettes, typography hierarchies, and layout rules.

Key Directives:
- Do NOT re-scaffold or initialize Nuxt again.
- Preserve the existing dark-fantasy QUEST visual identity and components in `app/`.
- All curriculum data must come from `data/topics.json` (20 official Georgia standards topics). Zero per-topic hardcoding in the UI.
- XP must only be awarded for verified correct mathematical answers, never on empty clicks.
- Math expressions must be verified with exact Python `fractions.Fraction` and safe AST parsing.
- Nuxt runs as SPA/static (`ssr: false`, `nuxt generate` to `.output/public`).
- Deploy targets Vercel (`vercel.json`) with Python 3.11 serverless functions in `api/index.py`.
