import os
import time
import requests
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("OPENAI_API_KEY")

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

def get_updates(offset=None):
    url = TG_URL + "getUpdates"
    params = {"timeout": 60, "offset": offset}
    return requests.get(url, params=params).json()

def send_sticker(chat_id, image_url):
    url = TG_URL + "sendSticker"
    data = {"chat_id": chat_id, "sticker": image_url}
    requests.post(url, data=data)

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

    r = requests.post(url, headers=headers, json=data)
    return r.json()["data"][0]["url"]

def process_message(message):
    chat_id = message["message"]["chat"]["id"]
    text = message["message"].get("text", "")

    if text.startswith("/sticker"):
        query = text.replace("/sticker", "").strip()
        
        if not query:
            requests.post(TG_URL + "sendMessage", data={
                "chat_id": chat_id,
                "text": "Напиши так: /sticker кот космонавт"
            })
            return

        img = generate_image(query)
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
