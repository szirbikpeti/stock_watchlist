import functools
from datetime import datetime, timedelta

from yahoo_fin import stock_info as si

from fbchat import Client
from fbchat.models import Message

from tabulate import tabulate

from PIL import Image, ImageDraw

from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter

import git


class MessageBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        if (int(author_id) == 100002404483520 or int(author_id) == 100000656116842) and isinstance(message_object.text, str):
            msg = str(message_object.text).lower()
            sender = functools.partial(message_sender, self, thread_id)

            if msg == 'hi':
                sender(f'Hey, {self.fetchUserInfo(thread_id)[str(thread_id)].first_name}')
            elif msg == 'usd' or msg == 'eur':
                sender(round(CurrencyRates().get_rate(msg.upper(), 'HUF'), 2))
            elif msg == 'btc':
                sender(round(BtcConverter().get_latest_price('USD'), 2))
            elif msg == '?' or msg == '?p':
                sender(get_buyable_stocks(), message_object.text == '?')
            elif msg[-1] == '?' and len(msg.split()) == 1:
                try:
                    sender(round(si.get_live_price(msg), 2))
                except Exception:
                    sender('Ticker was not found')
            elif msg == '--help':
                sender("Commands:\n \u2022 hi\n \u2022 ?\n \u2022 ?p\n \u2022 usd\n \u2022 eur\n \u2022 btc\n \u2022 [ticker]?\n\n(not case\nsensitive words)")


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


def message_sender(client: Client, thread_id: int, message: str, is_text: bool = True):
    print(f'Request from {client.fetchUserInfo(thread_id)[str(thread_id)].name}')
    client.send(Message(text=message), thread_id=thread_id) if is_text else client.sendLocalImage(get_image(message), thread_id=thread_id)


def get_image(message: str):
    img = Image.new('RGB', (215, 70 + (len(message.split('\n')) - 3) * 14 + 6), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10, 10), f"       {(datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')}\n{message}", fill=(255, 255, 0))
    path = '/app/image.png'
    img.save(path)

    return path
	

try:
    repo = git.Repo.clone_from('git@github.com:szirbikpeti/stock_watchlist.git', '/app/stockWatchlist')
except git.GitCommandError:
    repo = git.Repo('/app/stockWatchlist')


with open('/app/stockWatchlist/random.txt', 'w') as file:
    file.write('Random text here!')


repo.git.add('random.txt')
repo.index.commit('Add random text file')
origin = repo.remote(name='origin')
origin.push()


MessageBot("stockswatcher21@gmail.com", "stockSender21", max_tries=1, user_agent='[FB_IAB/MESSENGER;FBAV/310.0.0.0.83;]').listen()

