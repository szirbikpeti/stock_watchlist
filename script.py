from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from tabulate import tabulate
from yahoo_fin import stock_info as si
from PIL import Image, ImageDraw
import os


os.mkdir('/app/test')


GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google-chrome'
CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.binary_location = GOOGLE_CHROME_PATH

driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
driver.get('https://www.messenger.com/')


email_input = driver.find_element_by_xpath(
    '/html/body/div/div/div/div[1]/div/div/div/div[1]/div/div[3]/div/div[7]/div[1]/div/div[2]/div[1]/div/form/div/input[6]')
email_input.send_keys('stockswatcher21@gmail.com')

password_input = driver.find_element_by_xpath(
    '/html/body/div/div/div/div[1]/div/div/div/div[1]/div/div[3]/div/div[7]/div[1]/div/div[2]/div[1]/div/form/div/input[7]')
password_input.send_keys('stockSender21')
password_input.send_keys(Keys.ENTER)

driver.implicitly_wait(10)


def check_request(thread_id: int):
    driver.get(f'https://www.messenger.com/t/{thread_id}')
    messages = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div/div/div[1]/div[1]/div/div/div[3]/div')

    if messages.text[-1] == '?':
        input_field = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div/div/div[2]/div/form/div/div[3]/div[2]/div[1]/div/div/div/div/div[2]/div/div/div/div')

        get_buyable_stocks()
		
        image = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div/div/div[2]/div/form/div/div[3]/div[1]/input')
        image.send_keys('/app/buyable_stocks.png')
		
        input_field.send_keys(Keys.ENTER)


def get_buyable_stocks():
    closest_stock = ("", 99999, 0, 0)

    with open("/app/stock_price_target.csv", "r") as file:
        next(file)
        line = file.readline().split(";")

        stock_details = []

        while line[0] != '':
            print(line[0].upper(), si.get_live_price(line[0]))
            diff = float(si.get_live_price(line[0])) - float(line[1])
            if closest_stock[1] > diff > 0:
                closest_stock = (line[0].upper(), diff, round(float(si.get_live_price(line[0])), 2), float(line[1]))

            if float(si.get_live_price(line[0])) < float(line[1]):
                stock_details.append([line[0].upper(), round(float(si.get_live_price(line[0])), 2), float(line[1])])

            line = file.readline().split(";")

    stock_details.append([f"({closest_stock[0]})", closest_stock[2], closest_stock[3]])

    img = Image.new('RGB', (215, 58 + (len(stock_details) - 1) * 14 + 5), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10, 10), f"{tabulate(stock_details, headers=['Ticker', 'CPrice', 'TPrice'], tablefmt='presto')}",
           fill=(255, 255, 0))
    img.save('/app/buyable_stocks.png')


while True:
    check_request(100002404483520)
    check_request(100000656116842)


