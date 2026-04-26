import os
from abc import ABC, abstractmethod
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from drive.uploader import upload_to_researcher_folder, upload_to_folder

_THAI_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
    "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม",
    "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
]


def _thai_date(dt: datetime) -> str:
    return f"{dt.day} {_THAI_MONTHS[dt.month - 1]} {dt.year + 543}"


def _thai_datetime(dt: datetime) -> str:
    return f"{_thai_date(dt)} เวลา {dt.strftime('%H:%M')} น."


class BaseRoutine(ABC):
    name: str = "BaseRoutine"
    title: str = ""
    folder_id: str = None  # if set, upload to this Drive folder instead of Researcher

    def run(self):
        print(f"[{self.name}] Starting routine...")
        _, _file_id, link, _filename = self.run_and_return_link()
        print(f"[{self.name}] Document uploaded to Researcher folder in Google Drive: {link}")

    def run_and_return_link(self) -> tuple:
        results = self.execute()
        doc_path = self._create_document(results)
        filename = os.path.basename(doc_path)
        if self.folder_id:
            file_id, link = upload_to_folder(doc_path, self.folder_id)
        else:
            file_id, link = upload_to_researcher_folder(doc_path)
        os.remove(doc_path)
        return results, file_id, link, filename

    @abstractmethod
    def execute(self) -> dict:
        """Run routine logic and return a dict of result data."""

    def _create_document(self, results: dict, filename: str = None) -> str:
        now = datetime.now()
        if filename is None:
            friendly_date = now.strftime("%B %d %Y").replace(" 0", " ")
            filename = f"{self.name} - อัปเดตงาน, {friendly_date}.docx"
        path = os.path.join("/tmp", filename)

        doc = Document()

        title = doc.add_heading(f"อัปเดตงานของ {self.name} 🗂️", level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        subtitle = doc.add_paragraph()
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        byline = f"เขียนโดย {self.name}"
        if self.title:
            byline += f" ({self.title})"
        byline += f"  ·  {_thai_date(now)}"
        run = subtitle.add_run(byline)
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

        doc.add_paragraph()

        for section_title, content in results.items():
            doc.add_heading(section_title, level=2)
            body = doc.add_paragraph(str(content))
            body.style.font.size = Pt(11)

        doc.save(path)
        print(f"[{self.name}] Document saved to {path}")
        return path
