import os
from abc import ABC, abstractmethod
from datetime import datetime
from docx import Document
from docx.shared import Pt
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
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.name}_{timestamp}.docx"
        path = os.path.join("/tmp", filename)

        doc = Document()
        doc.add_heading(f"{self.name} Routine Report", level=0)

        meta = doc.add_paragraph()
        meta.add_run("Generated: ").bold = True
        meta.add_run(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        doc.add_heading("Results", level=1)
        for key, value in results.items():
            p = doc.add_paragraph(style="List Bullet")
            run = p.add_run(f"{key}: ")
            run.bold = True
            run.font.size = Pt(11)
            p.add_run(str(value))

        doc.save(path)
        print(f"[{self.name}] Document saved to {path}")
        return path
