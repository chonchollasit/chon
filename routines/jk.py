from datetime import datetime
from .base import BaseRoutine, _thai_datetime


class JKRoutine(BaseRoutine):
    name = "JK"
    title = "Writer"

    def execute(self) -> dict:
        print(f"[{self.name}] Running routine logic...")
        return {
            "วันนี้ทำอะไรไปบ้าง?": (
                "JK เคลียร์งานเสร็จหมดแล้วนะ ทุก task ที่รับมาทำเสร็จครบ "
                "ไม่มีตกหล่นเลยสักอัน"
            ),
            "ได้อะไรออกมาบ้าง?": (
                "ประมวลผลและเช็คข้อมูลทุกอย่างเสร็จสิ้นแล้ว "
                "ไม่เจอ error หรืออะไรที่ผิดปกติเลย ผ่านฉลุยทุกจุด"
            ),
            "โน้ตเพิ่มเติม": (
                "งานเดินตามแผนเป๊ะๆ เลย ไม่มี alert ไม่มีอะไรให้กังวล "
                "โอเคพร้อมรอบหน้าได้เลย"
            ),
            "เสร็จตอน": _thai_datetime(datetime.now()),
        }
