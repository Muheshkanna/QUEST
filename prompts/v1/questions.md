# Question Generation Prompt

You are an expert curriculum designer and math quest puzzle master for 5th and 6th graders.
Generate a high-quality math multiple choice question that can be deterministically verified.

## Curriculum Grounding
- **Topic ID**: {topic_id}
- **Topic Title**: {topic_title}
- **Standard Code**: {standard}
- **Standard Description**: {standard_text}
- **Target Difficulty**: {difficulty}
- **Verifier Type**: {verifier_type}

## Allowed Misconception IDs for Wrong Options
{misconceptions_text}

## Rules
1. Mathematical precision: The `expression` MUST evaluate to the correct answer using python AST evaluator (e.g. "3/4 + 1/2", "37 * 42", "divmod_rem(818, 94)", "25 * 0.40").
2. Exactly 4 options: A, B, C, D. One option has the correct answer (`misconception_id`: null).
3. Every wrong option MUST be mapped to a genuine misconception ID from the list above. Never use random filler numbers or duplicate options.
4. Stem parameters: Any numbers in the math expression must appear naturally in the story problem stem.
5. Tone: Kid-friendly, engaging fantasy quest or relatable real-world setting.
6. Explanation: Step-by-step walkthrough of how to solve the problem correctly with zero unnecessary jargon.

## Output Format
Return ONLY a valid JSON object matching the schema below. No markdown fences, no explanatory text outside the JSON.

```json
{{
  "id": "q-generated-1",
  "topic_id": "{topic_id}",
  "standard": "{standard}",
  "difficulty": "{difficulty}",
  "verifier_type": "{verifier_type}",
  "stem": "The narrative math problem presenting the scenario clearly.",
  "expression": "3/4 + 1/2",
  "options": [
    {{
      "id": "A",
      "text": "5/4",
      "misconception_id": null
    }},
    {{
      "id": "B",
      "text": "4/6",
      "misconception_id": "added_tops_and_bottoms"
    }},
    {{
      "id": "C",
      "text": "3/8",
      "misconception_id": "multiplied_instead_of_adding"
    }},
    {{
      "id": "D",
      "text": "1/4",
      "misconception_id": "subtracted_instead_of_adding"
    }}
  ],
  "correct_index": 0,
  "explanation": "To add fractions with unlike denominators, find a common denominator first...",
  "hint": "What is the common denominator between the two fractions?",
  "model": "gemini-1.5-flash",
  "prompt_version": "v1",
  "provenance": "verified"
}}
```
