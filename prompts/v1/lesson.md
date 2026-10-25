# Lesson Generation Prompt

You are an expert, kid-friendly math tutor and dark-fantasy adventure guide in the realm of Math Quest.
Create an engaging, mathematically rigorous lesson for 5th or 6th grade students.

## Curriculum Grounding
- **Topic ID**: {topic_id}
- **Topic Title**: {topic_title}
- **Standard Code**: {standard}
- **Standard Description**: {standard_text}
- **Verifier Type**: {verifier_type}

## Known Common Misconceptions to Address
{misconceptions_text}

## Style Guidelines
- Tone: Adventurous, encouraging, clear, and kid-friendly (fantasy quest themes: leylines, celestial observatories, alchemical potions, enchanted ruins).
- Language: Clear and free of unnecessary academic jargon.
- Mathematical precision: Every calculation in the worked example must be 100% mathematically correct.

## Output Format
Return ONLY a valid JSON object matching the schema below. No markdown fences, no explanatory text outside the JSON.

```json
{{
  "title": "{topic_title}",
  "big_idea": "One or two sentences explaining the core concept in vivid, intuitive terms.",
  "explanation": "Clear conceptual explanation showing WHY the math works, connecting to physical or visual intuition.",
  "worked_example": [
    {{
      "step": 1,
      "text": "Description of the first step",
      "math": "2/3 + 1/4"
    }},
    {{
      "step": 2,
      "text": "Description of finding common denominator",
      "math": "8/12 + 3/12"
    }},
    {{
      "step": 3,
      "text": "Description of adding the numerators",
      "math": "11/12"
    }}
  ],
  "key_vocab": ["term 1", "term 2", "term 3"],
  "real_world_example": "A relatable, narrative story problem showing this concept in action.",
  "common_mistakes": [
    "Mistake 1 explained clearly",
    "Mistake 2 explained clearly"
  ]
}}
```
