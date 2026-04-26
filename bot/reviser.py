import json
import anthropic

_client = anthropic.Anthropic()


def revise_content(current_content: dict, feedback: str) -> dict:
    content_text = "\n".join(f"{k}: {v}" for k, v in current_content.items())

    msg = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": (
                f"นี่คือเนื้อหาในเอกสารปัจจุบัน:\n\n{content_text}\n\n"
                f"ผู้ใช้ต้องการแก้ไขว่า: {feedback}\n\n"
                "กรุณาเขียนเนื้อหาใหม่เป็นภาษาไทยแบบสบายๆ สไตล์พนักงานบริษัทโฆษณา "
                "ตอบกลับเป็น JSON โดยใช้ key เดิมทุกอัน "
                "ยกเว้น key 'เสร็จตอน' ให้คงค่าเดิมไว้เสมอ\n\n"
                "ตอบแค่ JSON เท่านั้น ไม่ต้องมีข้อความอื่น"
            ),
        }],
    )

    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)
