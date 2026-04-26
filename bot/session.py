from dataclasses import dataclass, field


@dataclass
class Session:
    routine_name: str
    routine_title: str
    routine_cls: type
    content: dict
    file_id: str
    doc_link: str
    original_filename: str
    waiting_for_confirm: bool = False


sessions: dict[str, Session] = {}
