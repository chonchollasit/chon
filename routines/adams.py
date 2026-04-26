from datetime import datetime
from .base import BaseRoutine, _thai_datetime


class AdamsRoutine(BaseRoutine):
    name = "Adams"
    title = "Researcher"

    def execute(self) -> dict:
        print(f"[{self.name}] Running routine logic...")
        return {
            "วันนี้ทำอะไรไปบ้าง?": (
                "Adams รันงานเสร็จสมบูรณ์แล้ว ตรงเวลาด้วย ไม่มีดีเลย์เลย "
                "ทุกสเต็ปผ่านหมดเลย เรียบร้อยมากๆ"
            ),
            "ได้อะไรออกมาบ้าง?": (
                "รีวิวงานทั้งหมดเสร็จแล้ว ผลออกมาสม่ำเสมอดีเหมือนรอบก่อนๆ "
                "ทุก output ผ่านตามที่กำหนดไว้เลย ไม่มีอะไรน่าเป็นห่วง"
            ),
            "โน้ตเพิ่มเติม": (
                "ไม่มีอะไรเร่งด่วนเลย ทุกอย่างโอเคหมด "
                "อัปเดต doc เรียบร้อยแล้ว พร้อมสำหรับรอบหน้าได้เลย"
            ),
            "เสร็จตอน": _thai_datetime(datetime.now()),
        }
