from datetime import datetime
from .base import BaseRoutine, _thai_datetime


class RemyRoutine(BaseRoutine):
    name = "Remy"
    title = "Researcher"

    def execute(self) -> dict:
        print(f"[{self.name}] Running routine logic...")
        return {
            "วันนี้ทำอะไรไปบ้าง?": (
                "รันงานของ Remy เสร็จแล้วนะ ทุกอย่างไหลลื่นดีมาก ไม่มีติดขัดเลยสักนิด "
                "งานเดินหน้าตามแผนที่วางไว้ทุกอย่างเลย"
            ),
            "ได้อะไรออกมาบ้าง?": (
                "เช็คทุกจุดครบแล้ว ตัวเลขออกมาดีตามที่คาด ไม่มีอะไรผิดปกติเลย "
                "โอเคมากๆ เลยรอบนี้"
            ),
            "โน้ตเพิ่มเติม": (
                "ตอนนี้ยังไม่มีอะไรให้ต้องตามต่อนะ ระบบจะรันรอบหน้าเองเลย "
                "ถ้ามีอะไรจะแจ้งให้รู้ทันที"
            ),
            "เสร็จตอน": _thai_datetime(datetime.now()),
        }
