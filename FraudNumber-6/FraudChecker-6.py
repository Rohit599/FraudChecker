from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
import time
import pandas as pd
from PIL import Image
import pytesseract
import os
import logging

# Initialize logging
logging.basicConfig(filename='web_scraper-6.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the WebDriver
# Specify the path to the ChromeDriver
chrome_driver_path = '/usr/lib/chromium-browser/chromedriver'  # Update the path
# Initialize the Service object
service = Service(chrome_driver_path)

# Add options to maximize the window
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# Initialize the WebDriver with the Service object and options
driver = webdriver.Chrome(service=service, options=options)

# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Update the path

# Open the website
driver.get('https://cybercrime.gov.in/Webform/suspect_search_repository.aspx')

# Path to the CSV file
csv_file_path = 'fraud_numbers-6.csv'
progress_file_path = 'progress-6.txt'

# Write headers to the CSV file if it doesn't exist
if not os.path.isfile(csv_file_path):
    with open(csv_file_path, 'w') as f:
        f.write('number,is_fraud\n')

# Read the last processed number from the progress file
if os.path.isfile(progress_file_path):
    with open(progress_file_path, 'r') as f:
        start_number = int(f.read().strip())
else:
    start_number = 7000000000

# Generator to yield numbers in the specified ranges
def number_generator(start):
    for number in range(start, 6000000000, -1):
        yield number

# Use the generator starting from the last processed number
for number in number_generator(start_number):
    while True:
        try:
            # time.sleep(2)
            number_str = str(number)

            # logging.info(f'Starting processing for number: {number_str}')

            # Find the input field and enter the number
            input_field = driver.find_element(By.ID, 'ContentPlaceHolder1_idverify')
            input_field.clear()
            input_field.send_keys(number_str)

            # time.sleep(2)

            # Capture the CAPTCHA image
            captcha_image = driver.find_element(By.ID, 'ContentPlaceHolder1_Image1')
            captcha_image.screenshot('captcha-6.png')

            # Use OCR to read the CAPTCHA
            captcha_text = pytesseract.image_to_string(Image.open('captcha-6.png')).strip()

            # Enter the CAPTCHA text into the input field
            captcha_input_field = driver.find_element(By.ID, 'ContentPlaceHolder1_txtcapcha')
            captcha_input_field.clear()
            captcha_input_field.send_keys(captcha_text)

            # time.sleep(2)

            # Submit the form
            submit_button = driver.find_element(By.ID, 'ContentPlaceHolder1_btnverify')
            submit_button.click()

            # Wait for the result to load
            time.sleep(2)  # Adjust sleep time as needed

            # Locate the div containing the result
            result_div = driver.find_element(By.CLASS_NAME, 'sweet-alert')

            # Get the h2 text inside the div
            result_text = result_div.find_element(By.TAG_NAME, 'h2').text

            # Determine if the number is fraud based on the result text
            if "Not Found" in result_text:
                is_fraud = False
            else:
                is_fraud = True
            
            # Append the result to the CSV file
            with open(csv_file_path, 'a') as f:
                f.write(f'{number_str},{is_fraud}\n')

            # Save the current progress to the file
            with open(progress_file_path, 'w') as f:
                f.write(str(number + 1))
            
            # Break out of the while loop if no exception occurred
            break
        except Exception as e:
            # logging.error(f"An error occurred with number {number_str}: {e}. Retrying...")
            continue

    # Navigate back to the search page if needed
    driver.get('https://cybercrime.gov.in/Webform/suspect_search_repository.aspx')

# Close the WebDriver
driver.quit()
