from yahoo_fin import stock_info as si

from fbchat import Client
from fbchat.models import Message, ThreadType

from tabulate import tabulate

from PIL import Image, ImageDraw

from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter


class MessageBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        if int(thread_id) == 100002404483520 or int(thread_id) == 100000656116842 and isinstance(message_object.text, str):
            if message_object.text.lower() == 'usd':
                sender(self, thread_id, CurrencyRates().get_rate('USD', 'HUF'))
            elif message_object.text.lower() == 'eur':
                sender(self, thread_id, CurrencyRates().get_rate('EUR', 'HUF'))
            elif message_object.text.lower() == 'btc':
                sender(self, thread_id, BtcConverter().get_latest_price('USD'))
            elif message_object.text == '?' or message_object.text == '?p':
                msg_id = self.send(Message(text="Processing..."), thread_id=thread_id, thread_type=ThreadType.USER)
                sender(self, thread_id, get_buyable_stocks(), message_object.text == '?')
                self.deleteMessages(msg_id)


def get_buyable_stocks():
    closest_stock = ("", 99999, 0, 0)

    with open("/app/stock_price_target.csv", "r") as file:
        next(file)
        line = file.readline().split(";")

        stock_details = []

        while line[0] != '':
            diff = float(si.get_live_price(line[0])) - float(line[1])
            if closest_stock[1] > diff > 0:
                closest_stock = (line[0].upper(), diff, round(float(si.get_live_price(line[0])), 2), float(line[1]))

            if float(si.get_live_price(line[0])) < float(line[1]):
                stock_details.append([line[0].upper(), round(float(si.get_live_price(line[0])), 2), float(line[1])])

            line = file.readline().split(";")

    stock_details.append([f"({closest_stock[0]})", closest_stock[2], closest_stock[3]])

    return f"{tabulate(stock_details, headers=['Ticker', 'CPrice', 'TPrice'], tablefmt='presto')}"


def sender(client: Client, thread_id: int, message: str, is_text: bool = True):
    print(f'Request from {client.fetchUserInfo(thread_id)[str(thread_id)].name}')
    client.send(Message(text=message), thread_id=thread_id) if is_text else client.sendLocalImage(get_image(message), thread_id=thread_id)


def get_image(message: str):
    img = Image.new('RGB', (215, 58 + (len(message.split('\n')) - 3) * 14 + 5), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10, 10), message, fill=(255, 255, 0))
    path = '/app/image.png'
    img.save(path)

    return path


my_client = MessageBot("stockswatcher21@gmail.com", "stockSender21", max_tries=1, user_agent='[FB_IAB/MESSENGER;FBAV/310.0.0.0.83;]')
my_client.listen()

