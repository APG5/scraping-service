# main.py
from flask import Flask, send_file
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import chromedriver_binary  # Adds chromedriver binary to path
import time, pickle, json, os, re, yagmail
from datetime import datetime
from collections import Counter

user = 'le.ngoc.apg1@gmail.com'
app_password = 'gijkkhcxbgaqoxwn' # not plain password 
to = ['baongoc159@gmail.com','anhhang.mar@gmail.com']
#to = ['baongoc159@gmail.com']
subject = '[APG] cap nhat hang moi'
#contents = ['mail body content','pytest.ini','test.png']

def check_duplicate_dates(text, date_format="%d-%m-%Y"):
    #print(text)
    dates = re.split(';| |,', text)
    unique_dates = set()

    for date in dates:
        #print(date)
        try:
            # Validate if the string is a date
            datetime.strptime(date, date_format)
            # If the date is already in the set, it's a duplicate
            if date in unique_dates:
                return True
            else:
                unique_dates.add(date)
        except ValueError:
            pass
            #print(f"'{date}' is not a valid date in the format {date_format}")
    #input()
    return False
def cellExist(cell, filename="cells.txt"):
    """
    This function checks if the first cell exists in the file.
    If it does, it returns 'Fail'. If it doesn't, it writes the first cell to the file and returns 'Success'.
    """
    # Check if the file exists and the first cell is in the file
    if os.path.exists(filename) and cell in open(filename).read():
        return True
    else:
        # Write the first cell to the file
        with open(filename, 'a') as file:
            file.write(cell + '\n')
        return False
    
# Initialize Flask
app = Flask(__name__)

# The following options are required to make headless Chrome
# work in a Docker container
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-data-dir=userdata")
chrome_options.add_argument("window-size=1024,768")
chrome_options.add_argument("--no-sandbox")

# Initialize a new browser
driver = webdriver.Chrome(chrome_options=chrome_options)
@app.route("/")
def hello_world():
    driver.get('https://erp.anphucgia.vn/pages/real-estate-for-sale')
    start_time = time.time()
    while time.time() - start_time < 10:  # 600 seconds = 10 minutes
        if 'sign-in' in driver.current_url:
            time.sleep(2)

            print("Element not found. URL has changed and it contains 'log-in'")
            email_inputs = driver.find_elements(By.CSS_SELECTOR, 'input.mat-input-element')

            if email_inputs:
                email_inputs[0].clear()
                email_inputs[0].send_keys('anhhang.mar@gmail.com')
            else:
                print("No email input field found")
            
            password_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
            if password_inputs:
                # Clear the input field
                password_inputs[0].clear()

                # Type the password into the input field
                password_inputs[0].send_keys('Gin@270521')
            else:
                print("No password input field found")
            #time.sleep(1)
            checkboxes = driver.find_elements(By.CSS_SELECTOR, ".mat-checkbox-input")
            for checkbox in checkboxes:
                driver.execute_script("arguments[0].click();", checkbox)
            time.sleep(1)
            # Find the checkbox by its CSS selector
            buttons = driver.find_elements(By.CSS_SELECTOR, ".submit-button")
            for button in buttons:
                driver.execute_script("arguments[0].click();", button)

            break
        try:
            # Try to find the element and break the loop if found
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".mat-row")))
            break
        except TimeoutException:
            # If the element is not found within 1 second, continue the loop
            pass

    # Define the URL
    print("done login")
    time.sleep(5)
    num_iterations = 3
    file_name = 'test.png'

    try:
        contentsText = ""
        for url in ['https://erp.anphucgia.vn/pages/real-estate-for-sale', 'https://erp.anphucgia.vn/pages/real-estate-for-hire']: 
            print(url)
            # if 'real-estate-for-sale' in driver.current_url and 'real-estate-for-sale' in url:
            #     pass
            # else:
            driver.get(url)
            #print("see1")
            #time.sleep(5)
            #print("see1")
            #driver.save_screenshot(file_name)
            #return send_file(file_name) 
            exit_outer_loop = False
            for i in range(num_iterations):
                if exit_outer_loop: break
                #try:
                element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".mat-row"))
                    )
                    # Continue with the rest of your code here...
                time.sleep(1)

                print("see")
                # Locate the rows
                rows = driver.find_elements(By.CSS_SELECTOR, '.mat-row')
                for row in rows:
                    # Locate the cells within the row
                    cells = row.find_elements(By.CSS_SELECTOR, '.mat-cell')

                    # Scrape the text from each cell
                    texts = [cell.text.replace('\n', ';') for cell in cells]
                    
                    # Concatenate the texts with a comma separator
                    line = ', '.join(texts)
                    #print(line)
                    if 'Đã'  in line and not 'Đang ' in line : continue
                    if check_duplicate_dates(line): 
                        if cellExist( line ):
                            exit_outer_loop = True
                            break
                        # Print the line
                        print(line)
                        contentsText = contentsText + '\n' + '\n' + line
                        #contents.append(line)
                #print("end")
                # Find the next button using its CSS class and click it
                next_button = driver.find_element(By.CSS_SELECTOR, '.mat-paginator-navigation-next')
                driver.execute_script("arguments[0].click();", next_button)
                print(f"end{i}-------------")
        #print(contents)
        #exit()

        if contentsText:
            print('Prepare to send mail')
            with yagmail.SMTP(user, app_password) as yag:
                yag.send(to, subject, contentsText)
                print('Sent email successfully')
        else:
            print('No change')        
        time.sleep(300)
        #exit()
    except Exception as e:
        print(f"An error occurred---: {e}")
        #break
    print("end all")
    return("end")

