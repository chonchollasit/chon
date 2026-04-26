from dataclasses import dataclass


@dataclass
class Session:
    routine_name: str
    routine_title: str
    routine_cls: type
    content: dict
    file_id: str
    doc_link: str
    original_filename: str


sessions: dict[str, Session] = {}
