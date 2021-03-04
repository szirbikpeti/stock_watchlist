import pathlib
from time import sleep

from yahoo_fin import stock_info as si

from fbchat import Client
from fbchat.models import Message, ThreadType

from tabulate import tabulate

#base_path = "C:\\Users\\Vostro 15\\Google Drive\\Egyetem_SZTE\\5_felev\\Szkriptnyelvek\\gyakorlat\\tobbi"
my_thread_id = 100002404483520


class MessageBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        if (int(thread_id) == my_thread_id) and message_object.text == '?':
            msg_id = self.send(Message(text="Processing..."), thread_id=my_thread_id, thread_type=ThreadType.USER)
            get_buyable_stocks(my_client)
            self.deleteMessages(msg_id)


def get_buyable_stocks(client: Client = None):
    closest_stock = ("", 99999, 0, 0)

    with open(str(pathlib.Path(__file__).parent.absolute()) + "/stock_price_target.csv", "r") as file:
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

    print("Sent!") if len(stock_details) > 0 else print("Nothing to show!")

    stock_details.append([f"({closest_stock[0]})", closest_stock[2], closest_stock[3]])

    if client is not None:
        client.send(
            Message(text=f"{tabulate(stock_details, headers=['Ticker', 'CPrice', 'TPrice'], tablefmt='presto')}"),
            thread_id=my_thread_id, thread_type=ThreadType.USER)

        client.markAsUnread(my_thread_id)
    else:
        print(f"{tabulate(stock_details, headers=['Ticker', 'CPrice', 'TPrice'], tablefmt='presto')}")

    print(f"The closest: {closest_stock[0]} (diff: {closest_stock[1]})")
    sleep(10)


my_client = MessageBot("stockswatcher21@gmail.com", "stockSender21", max_tries=1)
my_client.listen()
