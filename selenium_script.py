
#selenium==3.141.0
#webdriver-manager==3.3.0
#Pillow==8.1.2
#https://medium.com/@mikelcbrowne/running-chromedriver-with-python-selenium-on-heroku-acc1566d161c
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from tabulate import tabulate
from yahoo_fin import stock_info as si
from PIL import Image, ImageDraw
import os.path
from os import path


GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google-chrome'
CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.binary_location = GOOGLE_CHROME_PATH

driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
driver.get('https://www.messenger.com/')

try:
	accept_cookies_button = driver.find_element_by_xpath(
		'/html/body/div[2]/div[2]/div/div/div/div/div[3]/button[2]')
	accept_cookies_button.click()
except:
	pass

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

        input_field.send_keys("Successful!")
        input_field.send_keys(Keys.ENTER)


while True:
    check_request(100002404483520)
    check_request(100000656116842)


