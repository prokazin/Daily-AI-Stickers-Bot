import os
import time
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("OPENAI_API_KEY")
TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

def get_updates(offset=None):
    url = TG_URL + "getUpdates"
    params = {"timeout": 60, "offset": offset}
    try:
        return requests.get(url, params=params).json()
    except Exception as e:
        print("Error getting updates:", e)
        return {}

def send_sticker(chat_id, image_url):
    url = TG_URL + "sendSticker"
    data = {"chat_id": chat_id, "sticker": image_url}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Error sending sticker:", e)

def send_message(chat_id, text):
    url = TG_URL + "sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": text})
    except Exception as e:
        print("Error sending message:", e)

def generate_image(prompt):
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "512x512"
    }

    try:
        r = requests.post(url, headers=headers, json=data)
        resp = r.json()
        print("OpenAI response:", resp)

        if "data" not in resp:
            return None

        return resp["data"][0]["url"]

    except Exception as e:
        print("Error generating image:", e)
        return None

def process_message(message):
    if "message" not in message:
        return
    chat_id = message["message"]["chat"]["id"]
    text = message["message"].get("text", "")

    if text.startswith("/sticker"):
        query = text.replace("/sticker", "").strip()
        if not query:
            send_message(chat_id, "Напиши так: /sticker кот космонавт")
            return

        img = generate_image(query)
        if img is None:
            send_message(chat_id, "⚠️ Ошибка генерации изображения. Попробуй другой запрос.")
            return

        send_sticker(chat_id, img)

def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for msg in updates["result"]:
                offset = msg["update_id"] + 1
                process_message(msg)
        time.sleep(1)

if __name__ == "__main__":
    main()
