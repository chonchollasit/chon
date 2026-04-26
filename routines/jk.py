import io
import json
from datetime import datetime, timezone, timedelta
import anthropic
from docx import Document
from .base import BaseRoutine, _thai_datetime, _thai_date
from drive.uploader import list_files_in_folder, download_file_from_drive

_client = anthropic.Anthropic()

ADAM_FOLDER_ID = "162o6fu1-OSlEEIAzgJEdLX6YdltMjYgc"
REMY_FOLDER_ID = "1qPhgMizbhJ6e_g0dQi4pL4C4rTcKYwuo"

BANGKOK_TZ = timezone(timedelta(hours=7))

_WRITER_PROMPT = """You are JK, a creative writer for Thai TikTok content at an ad agency.

From the research below, pick 3 topics with the strongest storytelling potential and write a full TikTok script for each.

Script format for EACH of the 3 scripts:
- Topic Name
- Hook Option 1 (use one of: what-if, opposite reveal, personal relevance, or shock)
- Hook Option 2 (different hook strategy from option 1)
- Full Script (150-200 Thai words): include visual directions in [brackets], use Gen Z conversational Thai, connect to Thai culture, end with a CTA
- Takeaway (1 sentence: the core message)
- Structure used: MINI-ARC / CHARACTER FOCUS / PROCESS UNPACKING

Rules:
- 100% Thai language for all scripts
- Visual directions in [brackets] throughout
- Each script must use a different structure
- Strong hooks only — if it won't stop the scroll, rewrite it

Research:
{research}

Return a JSON array of exactly 3 script objects with keys:
topic, hook1, hook2, script, takeaway, structure

Return only the JSON array, no other text."""


def _read_docx_bytes(content: bytes) -> str:
    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _get_todays_research() -> tuple[str, str]:
    today = datetime.now(BANGKOK_TZ).date().isoformat()
    research_parts = []
    sources = []

    for folder_name, folder_id in [("Remy", REMY_FOLDER_ID), ("Adam", ADAM_FOLDER_ID)]:
        files = list_files_in_folder(folder_id, max_results=5)
        for f in files:
            created_date = f["createdTime"][:10]
            if created_date == today:
                content = download_file_from_drive(f["id"])
                text = _read_docx_bytes(content)
                research_parts.append(f"=== Research from {folder_name} ({f['name']}) ===\n{text}")
                sources.append(folder_name)
                break

    if not research_parts:
        for folder_name, folder_id in [("Remy", REMY_FOLDER_ID), ("Adam", ADAM_FOLDER_ID)]:
            files = list_files_in_folder(folder_id, max_results=1)
            if files:
                content = download_file_from_drive(files[0]["id"])
                text = _read_docx_bytes(content)
                research_parts.append(
                    f"=== Research from {folder_name} (latest available) ===\n{text}"
                )
                sources.append(folder_name)
                break

    combined = "\n\n".join(research_parts)
    source_label = " & ".join(sources) if sources else "unknown"
    return combined, source_label


def _write_scripts(research: str) -> list[dict]:
    response = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": _WRITER_PROMPT.format(research=research)}],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)


def _format_script_for_line(i: int, s: dict) -> str:
    return (
        f"🎬 Script {i}: {s['topic']}\n"
        f"({s['structure']})\n\n"
        f"Hook 1: {s['hook1']}\n"
        f"Hook 2: {s['hook2']}\n\n"
        f"{s['script']}\n\n"
        f"💡 Takeaway: {s['takeaway']}"
    )


class JKRoutine(BaseRoutine):
    name = "JK"
    title = "Writer"

    def execute(self) -> dict:
        print(f"[{self.name}] Reading research from Drive...")
        research, source_label = _get_todays_research()

        print(f"[{self.name}] Writing 3 TikTok scripts from {source_label} research...")
        self._scripts = _write_scripts(research)

        now = datetime.now(BANGKOK_TZ)
        result = {"📋 Research Source": source_label}
        for i, s in enumerate(self._scripts, 1):
            result[f"🎬 Script {i} — {s['topic']}"] = (
                f"Structure: {s['structure']}\n\n"
                f"Hook 1: {s['hook1']}\n"
                f"Hook 2: {s['hook2']}\n\n"
                f"{s['script']}\n\n"
                f"Takeaway: {s['takeaway']}"
            )
        result["เสร็จตอน"] = _thai_datetime(now.replace(tzinfo=None))
        return result

    def line_messages(self) -> list[str]:
        """Returns each script as a separate LINE message."""
        if not hasattr(self, "_scripts"):
            return []
        return [_format_script_for_line(i, s) for i, s in enumerate(self._scripts, 1)]
