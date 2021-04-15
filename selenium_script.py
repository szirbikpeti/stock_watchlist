
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
driver.get('https://www.androidapksbox.com/facebook/')

table = driver.find_element_by_xpath(
    '/html/body/div[1]/div[2]/div/article/div[1]/p[2]')

version = [row[9:].split(" (")[0] for row in table.text.split("\n") if str(row).startswith("Version")][0]

print(version)


