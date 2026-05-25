import imaplib
import email
import time
import os
import telegram

GMAIL_USER  = os.environ["GMAIL_USER"]
GMAIL_PASS  = os.environ["GMAIL_APP_PASS"]
TG_TOKEN    = os.environ["TG_TOKEN"]
TG_CHAT_ID  = os.environ["TG_CHAT_ID"]

bot = telegram.Bot(token=TG_TOKEN)

def send_telegram(msg):
    bot.send_message(chat_id=TG_CHAT_ID, text=msg)

def format_message(raw):
    try:
        parts    = dict(p.strip().split(": ", 1) for p in raw.split("|") if ": " in p)
        direction = raw.split("|")[0].strip()
        symbol    = raw.split("|")[1].strip()
        entry     = parts.get("Entry", "?")
        sl        = parts.get("SL", "?")
        tp        = parts.get("TP", "?")
        emoji     = "🟢" if direction == "BUY" else "🔴"
        return (
            f"{emoji} {direction} SIGNAL — {symbol}\n"
            f"━━━━━━━━━━━━━━\n"
            f"📍 Entry: {entry}\n"
            f"🛑 SL:    {sl}\n"
            f"🎯 TP:    {tp}\n"
            f"━━━━━━━━━━━━━━\n"
            f"Manage your risk. Manual execution."
        )
    except:
        return raw

def check_mail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(GMAIL_USER, GMAIL_PASS)
    mail.select("inbox")
    _, ids = mail.search(None, "UNSEEN")
    for uid in ids[0].split():
        _, data = mail.fetch(uid, "(RFC822)")
        msg  = email.message_from_bytes(data[0][1])
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()
        body = body.strip()
        if ("BUY" in body or "SELL" in body) and "Entry:" in body:
            print(f"Signal: {body}")
            send_telegram(format_message(body))
        mail.store(uid, "+FLAGS", "\\Seen")
    mail.logout()

print("Bot running...")
while True:
    try:
        check_mail()
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(15)
