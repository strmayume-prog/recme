# main.py
import os, stripe, datetime, json
from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse

app = FastAPI()
stripe.api_key = os.environ["STRIPE_API_KEY"]
WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]

DB_FILE = "db.json"

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(d):
    with open(DB_FILE, "w") as f:
        json.dump(d, f, indent=2)

def grant_access(telegram_id):
    # TODO: implementar com python-telegram-bot:
    # bot.add_chat_member(GROUP_ID, telegram_id) ou bot.invite_link
    # e salvar expiry no DB
    data = load_db()
    expiry = (datetime.datetime.utcnow() + datetime.timedelta(days=30)).isoformat()
    data[str(telegram_id)] = expiry
    save_db(data)

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature: {e}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        telegram_id = session.get("metadata", {}).get("telegram_id")
        if telegram_id:
            grant_access(telegram_id)
    return JSONResponse({"status":"ok"})
