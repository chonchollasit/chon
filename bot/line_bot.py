import os
import threading
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient, Configuration, MessagingApi,
    ReplyMessageRequest, PushMessageRequest, TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from routines import RemyRoutine, AdamsRoutine, JKRoutine
from bot.session import sessions, Session
from bot.reviser import revise_content

app = Flask(__name__)

handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
_line_config = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

ROUTINE_MAP = {
    "remy": RemyRoutine,
    "adams": AdamsRoutine,
    "jk": JKRoutine,
}

HELP_TEXT = (
    "สวัสดี! พิมพ์คำสั่งได้เลย:\n\n"
    "• run — รันทุก routine พร้อมกัน\n"
    "• remy / adams / jk — รัน routine เดียว\n\n"
    "หลังได้เอกสารแล้ว:\n"
    "• revise <คอมเมนต์> — แก้ไขเอกสารตามที่บอก\n"
    "• thank — จบงาน เอกสารพร้อมส่งแล้ว"
)


def _push(user_id: str, text: str):
    with ApiClient(_line_config) as api_client:
        MessagingApi(api_client).push_message(
            PushMessageRequest(to=user_id, messages=[TextMessage(text=text)])
        )


def _run_and_push(user_id: str, routine_cls):
    try:
        routine = routine_cls()
        results, file_id, link, filename = routine.run_and_return_link()
        sessions[user_id] = Session(
            routine_name=routine.name,
            routine_title=routine.title,
            routine_cls=routine_cls,
            content=results,
            file_id=file_id,
            doc_link=link,
            original_filename=filename,
        )
        _push(user_id, (
            f"✅ {routine.name} ({routine.title}) เสร็จแล้ว!\n\n"
            f"📄 {link}\n\n"
            f"พิมพ์ 'revise <คอมเมนต์>' ถ้าอยากแก้ไข\n"
            f"หรือพิมพ์ 'thank' ถ้าโอเคแล้ว 😊"
        ))
    except Exception as e:
        _push(user_id, f"❌ เกิดข้อผิดพลาดตอนรัน: {e}")


def _revise_and_push(user_id: str, feedback: str):
    session = sessions[user_id]
    try:
        revised = revise_content(session.content, feedback)
        routine = session.routine_cls()
        doc_path = routine._create_document(revised, filename=session.original_filename)

        from drive.uploader import update_file_in_drive
        link = update_file_in_drive(session.file_id, doc_path)

        os.remove(doc_path)

        sessions[user_id].content = revised
        sessions[user_id].doc_link = link

        _push(user_id, (
            f"✏️ แก้ไขเสร็จแล้ว! อัปเดตในไฟล์เดิมเลยนะ\n\n"
            f"📄 {link}\n\n"
            f"พิมพ์ 'revise <คอมเมนต์>' ถ้าอยากแก้เพิ่ม\n"
            f"หรือพิมพ์ 'thank' ถ้าโอเคแล้ว 😊"
        ))
    except Exception as e:
        _push(user_id, f"❌ แก้ไขไม่ได้: {e}")


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()
    text_lower = text.lower()

    with ApiClient(_line_config) as api_client:
        line_api = MessagingApi(api_client)

        def reply(msg: str):
            line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=msg)],
                )
            )

        if user_id in sessions:
            if text_lower == "thank":
                del sessions[user_id]
                reply("Thank you! เอกสารพร้อมส่งแล้ว 🚀🎉")
            elif text_lower.startswith("revise "):
                feedback = text[7:].strip()
                reply("กำลังแก้ไขให้นะ รอแป๊บนึง... ✍️")
                threading.Thread(target=_revise_and_push, args=(user_id, feedback)).start()
            elif text_lower == "revise":
                reply("บอกด้วยนะว่าอยากแก้อะไร เช่น: revise ทำให้กระชับขึ้น")
            else:
                reply("พิมพ์ 'revise <คอมเมนต์>' เพื่อแก้ไข หรือ 'thank' เมื่อเสร็จแล้ว")
            return

        if text_lower == "run":
            reply("กำลังรันทุก routine อยู่นะ รอแป๊บ... 🔄")
            for routine_cls in ROUTINE_MAP.values():
                threading.Thread(target=_run_and_push, args=(user_id, routine_cls)).start()

        elif text_lower in ROUTINE_MAP:
            routine_cls = ROUTINE_MAP[text_lower]
            reply(f"กำลังรัน {routine_cls.name} อยู่นะ รอแป๊บ... 🔄")
            threading.Thread(target=_run_and_push, args=(user_id, routine_cls)).start()

        else:
            reply(HELP_TEXT)
