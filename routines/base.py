import os
from abc import ABC, abstractmethod
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from drive.uploader import upload_to_researcher_folder


class BaseRoutine(ABC):
    name: str = "BaseRoutine"

    def run(self):
        print(f"[{self.name}] Starting routine...")
        results = self.execute()
        doc_path = self._create_document(results)
        upload_to_researcher_folder(doc_path)
        os.remove(doc_path)
        print(f"[{self.name}] Document uploaded to Researcher folder in Google Drive.")

    @abstractmethod
    def execute(self) -> dict:
        """Run routine logic and return a dict of result data."""

    def _create_document(self, results: dict) -> str:
        now = datetime.now()
        # Human-readable filename: e.g. "Remy - Research Report, April 26 2026.docx"
        friendly_date = now.strftime("%B %d %Y").replace(" 0", " ")
        filename = f"{self.name} - Research Report, {friendly_date}.docx"
        path = os.path.join("/tmp", filename)

        doc = Document()

        # Title
        title = doc.add_heading(f"Research Report", level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Subtitle: who wrote it and when
        subtitle = doc.add_paragraph()
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = subtitle.add_run(f"Prepared by {self.name}  |  {now.strftime('%B %d, %Y')}")
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

        doc.add_paragraph()  # spacing

        # Body sections — each key becomes a natural heading + paragraph
        for section_title, content in results.items():
            doc.add_heading(section_title, level=2)
            body = doc.add_paragraph(str(content))
            body.style.font.size = Pt(11)

        doc.save(path)
        print(f"[{self.name}] Document saved to {path}")
        return path
