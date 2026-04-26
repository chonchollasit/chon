import json
from datetime import datetime
import anthropic
from .base import BaseRoutine, _thai_datetime

_client = anthropic.Anthropic()

_SYSTEM_PROMPT = """You are Remy, a viral food content researcher for a Thai social media agency.

Your job each run: surface 3 high-potential recipe concepts for TikTok / Reels / YouTube Shorts targeting Thai audiences.

Rules:
- High-protein (30g+), low-calorie (under 400 kcal)
- Visually stunning — cheese pull, ASMR crunch, shocking volume-to-calorie ratio
- Ingredients must be available in Thai supermarkets (or easily swappable)
- Must have a strong hook. No hook = skip it
- Skip: boring plain chicken/salads, calorie-dense "healthy" food, 15+ step recipes, ugly food

Return a JSON array of exactly 3 findings. Each finding has these keys:
- concept: 1 sentence (e.g. "300-Calorie Cheesy Pad Kra Pao with 40g Protein")
- hook: 1 punchy Thai scroll-stopping opening line
- macros: string with kcal / protein / carbs / fats (e.g. "380 kcal | P: 42g | C: 28g | F: 8g")
- secret_hack: what makes this recipe special
- thai_adaptation: how to swap hard-to-find ingredients with local Thai ones
- content_angle: visual format suggestion (ASMR, fast-cut, minimalist, etc.)
- source: describe where this trend is from (platform + niche)
- score: integer 1-5 viral potential

Return only the JSON array, no other text."""


def _parse_findings(raw: str) -> list[dict]:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


class RemyRoutine(BaseRoutine):
    name = "Remy"
    title = "Researcher"
    folder_id = "1qPhgMizbhJ6e_g0dQi4pL4C4rTcKYwuo"

    def execute(self) -> dict:
        print(f"[{self.name}] Researching viral recipes...")

        response = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2500,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": "Research and deliver today's 3 best viral high-protein low-calorie recipe findings."}],
        )

        findings = _parse_findings(response.content[0].text)

        result = {}
        for i, f in enumerate(findings, 1):
            score_stars = "⭐" * f.get("score", 0)
            result[f"🥗 Finding #{i} — {f['concept']}"] = (
                f"Hook: {f['hook']}\n\n"
                f"Macros: {f['macros']}\n\n"
                f"Secret Hack: {f['secret_hack']}\n\n"
                f"Thai Adaptation: {f['thai_adaptation']}\n\n"
                f"Content Angle: {f['content_angle']}\n\n"
                f"Source: {f['source']}\n\n"
                f"Viral Potential: {score_stars} ({f.get('score')}/5)"
            )

        result["เสร็จตอน"] = _thai_datetime(datetime.now())
        return result
