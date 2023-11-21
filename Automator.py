from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import csv
from tabulate import tabulate
import cv2
import easyocr
import cv2
import urllib
import numpy as np
from PIL import Image

def get_marks(uid, password):
    # create a new Firefox session
    opts = Options()
    opts.add_argument('-headless')
    driver = webdriver.Firefox(options=opts)
    driver.implicitly_wait(30)
    driver.maximize_window()

    # Navigate to the application home page
    driver.get("https://uims.cuchd.in/uims")
    print("Page Opened")

    # Click the UID Input Field, enter the UID and Submit
    driver.find_element("name","txtUserId").send_keys(uid)
    driver.find_element("name","btnNext").click()

    # Enter the Password and Submit
    driver.find_element("name","txtLoginPassword").send_keys(password)
    driver.find_element("id","imgCaptcha").screenshot('challenge.png')

    image=cv2.imread('challenge.png')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #cv2.imwrite('challenge.jpg',image)

	# Define a threshold value to identify dark shades (adjust as needed)
    threshold_value = 50

	# Apply a binary threshold to segment dark areas
    _, mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

	# Invert the mask so that dark areas are white and the rest is blac
    mask = cv2.bitwise_not(mask)

	# Create a copy of the original image
    result = image.copy()

	# Use the mask to remove the dark areas from the original image
    result[mask == 0] = [255, 255, 255]  # Set dark areas to white

	# Display the result
	# cv2.imshow('Result', result)
    cv2.imwrite('result.jpg',result)


	
    reader = easyocr.Reader(['en'])  # 'en' for English, you can specify other languages

	
    results = reader.readtext(result)

	
    for (bbox, text, prob) in results:
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)


        cv2.putText(image, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        for (bbox, text, prob) in results:
            print(f"Text: {text}, Probability: {prob}")

    driver.find_element("id","txtcaptcha").send_keys(text)
    driver.find_element("name","btnLogin").click()
    print("UID and Password Entered and Submitted")

    driver.get('https://uims.cuchd.in/uims/frmStudentMarksView.aspx')
    pageSource=driver.page_source
    soup = BeautifulSoup(pageSource, "html.parser")

    # print(pageSource)
    results = soup.find(id="accordion")
    subject=results.find_all("h3")
    table = results.find_all('table')
    l=len(subject)

    for num in range(0,l-1):
        print(subject[num].text.strip())
        data=[]

        table_body = table[num].find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])
        print(tabulate(data))

    ch = input("Would you like to Quit?")
    if ch == "yes":
        driver.quit()

print("Welcome to CUIMS CLI!")
uid = input("Please enter your UID: ")
password = input("Please enter your Password: ")


get_marks(uid, password)
