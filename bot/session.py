from dataclasses import dataclass


@dataclass
class Session:
    routine_name: str
    routine_title: str
    routine_cls: type
    content: dict
    doc_link: str


sessions: dict[str, Session] = {}
