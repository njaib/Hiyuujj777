import telebot
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler


# ======================
# تنظیمات
# ======================

BOT_TOKEN = "8946269599:AAFUk-sEkKl53apo-5XzXe0IKkDJQgtzyMY"

CHANNEL_ID = "@YOUR_CHANNEL"

SITE = "https://mangaup.ir/"


bot = telebot.TeleBot(BOT_TOKEN)


translator = GoogleTranslator(
    source="auto",
    target="fa"
)


sent_items = set()



# ======================
# پورت برای Render
# ======================

class Health(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)

        self.end_headers()

        self.wfile.write(
            b"Bot is running"
        )



def start_server():

    server = HTTPServer(
        ("0.0.0.0",10000),
        Health
    )

    server.serve_forever()



# ======================
# گرفتن مانگا
# ======================

def get_manga():

    print("Checking website...")


    try:

        r = requests.get(
            SITE,
            headers={
                "User-Agent":"Mozilla/5.0"
            },
            timeout=20
        )


        print(
            "Website status:",
            r.status_code
        )


        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )


        data=[]


        for img in soup.find_all("img"):


            title = (
                img.get("alt")
                or
                img.get("title")
            )


            image = (
                img.get("src")
                or
                img.get("data-src")
            )


            if title and image:


                if image.startswith("/"):

                    image = SITE + image[1:]


                data.append(
                    {
                    "title":title,
                    "image":image
                    }
                )



        print(
            "Found:",
            len(data)
        )


        return data



    except Exception as e:

        print(
            "Site Error:",
            e
        )

        return []





# ======================
# ارسال تلگرام
# ======================

def bot_worker():


    print(
        "Bot started..."
    )


    while True:


        items = get_manga()



        for item in items:


            title=item["title"]


            if title in sent_items:

                continue



            try:


                fa = translator.translate(
                    title
                )


                text=f"""

📚 {fa}


🌐 منبع:
{SITE}

"""


                bot.send_photo(

                    CHANNEL_ID,

                    item["image"],

                    caption=text

                )



                sent_items.add(title)



                print(
                    "Sent:",
                    title
                )



                time.sleep(60)



            except Exception as e:

                print(
                    "Telegram Error:",
                    e
                )



        time.sleep(30)




# ======================
# اجرا
# ======================

if __name__=="__main__":


    threading.Thread(
        target=start_server,
        daemon=True
    ).start()



    bot_worker()