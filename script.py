import functools
import unidecode
import os

from yahoo_fin import stock_info as si
from datetime import datetime, timedelta
from fbchat import Client
from fbchat.models import Message

from tabulate import tabulate
from PIL import Image, ImageDraw

from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter

import psycopg2


def get_connection():
    return psycopg2.connect(
        dbname='d9tl95lq12ovod',
        user='nugopuasheavnw',
        password='17899264589c19c0d3cdcd69bc948aee1a1ccba9beb703f8cee842deb54c2434',
        host='ec2-99-80-200-225.eu-west-1.compute.amazonaws.com')


class MessageBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        if (int(author_id) == 100002404483520 or int(author_id) == 100000656116842) and isinstance(message_object.text,
                                                                                     str):
            msg = str(message_object.text).lower()
            user_name = unidecode.unidecode(self.fetchUserInfo(thread_id)[str(thread_id)].first_name)
            sender = functools.partial(message_sender, self, thread_id)

            if msg == 'hi':
                sender(f'Hey, {user_name}')
            elif msg == 'usd' or msg == 'eur':
                sender(round(CurrencyRates().get_rate(msg.upper(), 'HUF'), 2))
            elif msg == 'btc':
                sender(round(BtcConverter().get_latest_price('USD'), 2))
            elif msg == '?' or msg == '?p':
                sender(get_buyable_stocks(get_watchlist(user_name)), message_object.text == '?')
            elif msg[:4] == 'all?':
                result = []
                for row in get_watchlist(user_name):
                    result.append([row[1].upper(), round(float(si.get_live_price(row[1])), 2), row[2]])

                if msg[-1:] == 'p':
                    sender(tabulate(result, headers=['Ticker', 'CPrice', 'TPrice'], tablefmt='presto'), is_text=False)
                else:
                    sender(tabulate(result, headers=['Ticker', 'CPrice', 'TPrice'], tablefmt='presto'))
            elif msg[-1] == '?' and len(msg.split()) == 1:
                try:
                    sender(round(si.get_live_price(msg), 2))
                except Exception:
                    sender('Ticker not found')
            elif msg == '--help':
                sender(
                    "Commands:\n \u2022 hi\n \u2022 ?\n \u2022 ?p\n \u2022 all?\n \u2022 all?p\n \u2022 usd\n \u2022 "
                    "eur\n \u2022 btc\n \u2022 [ticker]?\n \u2022 add [ticker] [price]\n \u2022 update [ticker] ["
                    "price]\n \u2022 delete [ticker]\n \u2022 --all\n \u2022 --allp\n \u2022 --help\n\n(not "
                    "case\nsensitive words)")
            elif msg[:5] == '--all':
                result = []
                for row in get_watchlist(user_name):
                    result.append([row[1].upper(), row[2]])

                if msg[-1:] == 'p':
                    sender(tabulate(result, headers=['Ticker', 'TPrice'], tablefmt='presto'), is_text=False,
                           is_all=True)
                else:
                    sender(tabulate(result, headers=['Ticker', 'TPrice'], tablefmt='presto'))
            elif msg[:3] == 'add':
                try:
                    (symbol, price) = msg[4:].split()
                    float(price)
                except ValueError:
                    sender('Check the format')
                    return

                try:
                    si.get_live_price(symbol)
                except AssertionError:
                    sender('Ticker not found')
                    return

                conn = get_connection()
                cur = conn.cursor()

                cur.execute(f'SELECT * FROM watchlist_{user_name} WHERE ticker = %(tik)s', {"tik": f"{symbol}"})
                result = cur.fetchall()

                if len(result) != 0:
                    sender(f'Ticker already exists with {result[0][2]}$ price')
                    cur.close()
                    conn.close()
                    return

                cur.execute(f'INSERT INTO watchlist_{user_name} (ticker, targetPrice) VALUES (%s, %s)',
                            (symbol, price))

                cur.close()
                conn.commit()
                conn.close()
                sender('Add successfully')

            elif msg[:6] == 'update':
                try:
                    (symbol, price) = msg[7:].split()
                    float(price)
                except ValueError:
                    sender('Check the format')
                    return

                conn = get_connection()
                cur = conn.cursor()

                cur.execute(f'SELECT * FROM watchlist_{user_name} WHERE ticker = %(tik)s', {"tik": f"{symbol}"})

                if len(cur.fetchall()) != 1:
                    sender('Ticker not found')
                    cur.close()
                    conn.close()
                    return

                cur.execute(f'UPDATE watchlist_{user_name} SET targetPrice = %(pr)s WHERE ticker = %(tik)s',
                            {"pr": f"{price}", "tik": f"{symbol}"})

                cur.close()
                conn.commit()
                conn.close()
                sender('Update successfully')

            elif msg[:6] == 'delete':
                conn = get_connection()
                cur = conn.cursor()

                cur.execute(f'SELECT * FROM watchlist_{user_name} WHERE ticker = %(tik)s',
                            {"tik": f"{msg[7:]}"})

                if len(cur.fetchall()) != 1:
                    sender('Ticker not found')
                    cur.close()
                    conn.close()
                    return

                cur.execute(f'DELETE FROM watchlist_{user_name} WHERE ticker = %(tik)s', {"tik": f"{msg[7:]}"})

                cur.close()
                conn.commit()
                conn.close()
                sender('Delete successfully')


def get_watchlist(user_name: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM watchlist_{user_name} ORDER BY id')
    result = cur.fetchall()
    cur.close()
    conn.close()

    return result


def get_buyable_stocks(watchlist: list):
    closest_stock = ("", 99999, 0, 0)

    stock_details = []

    for row in watchlist:
        diff = float(si.get_live_price(row[1])) - float(row[2])
        if closest_stock[1] > diff > 0:
            closest_stock = (row[1].upper(), diff, round(float(si.get_live_price(row[1])), 2), float(row[2]))

        if float(si.get_live_price(row[1])) < float(row[2]):
            stock_details.append([row[1].upper(), round(float(si.get_live_price(row[1])), 2), float(row[2])])

    if len(closest_stock[0]) > 0:
        stock_details.append([f"({closest_stock[0]})", closest_stock[2], closest_stock[3]])

    return f"{tabulate(stock_details, headers=['Ticker', 'CPrice', 'TPrice'], tablefmt='presto')}"


def message_sender(client: Client, thread_id: int, message: str, is_text: bool = True, is_all: bool = False):
    print(f'Request from {client.fetchUserInfo(thread_id)[str(thread_id)].name}')
    client.send(Message(text=message), thread_id=thread_id) if is_text else client.sendLocalImage(
        get_image(message, is_all),
        thread_id=thread_id)


def get_image(message: str, is_all: bool):
    length = len(message.split('\n'))
    img = Image.new('RGB', (
    (150 if is_all else 215), 70 + (length - 3) * 14 + (6 if length < 7 else (9 if length < 15 else 13))),
                    color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10, 10),
           f"{' ' if is_all else '       '}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{message}",
           fill=(255, 255, 0))
    path = f"/app/{'all' if is_all else 'buyable'}_stocks.png"
    img.save(path)

    return path


if __name__ == '__main__':
    os.system('tzutil /s "Central Europe Standard Time"')

    MessageBot("stockswatcher21@gmail.com", "stockSender21", max_tries=1,
               user_agent='[FB_IAB/MESSENGER;FBAV/310.0.0.0.83;]').listen()
