from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.firefox.options import Options
import os
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import schedule
from datetime import datetime


time_param = '&time_range=%2522LAST_7D%2522'


#Данные для входа в аккаунт и работы

#text это сообщение которое будет автоматически отвечать на непрочитанные сообщения

#Что бы добавить новые данные то внутри переменной  config в новых фигурные скобках в том же формате впишите данные 
config = [{'username' :'','password': '','real_username' :'','text':''},]













def login_to_instagram(username, password):
    
    user_agent = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.196 Mobile Safari/537.36"
    # Create a new instance of the Firefox driver
    options = Options()
    options.set_preference("general.useragent.override", user_agent)
    driver = webdriver.Firefox(options=options)
    # Navigate to the Instagram login page
    driver.get("https://www.instagram.com/accounts/login/")
    global coockies
    coockies = driver.get_cookies()
    # Wait for the login form to load
    driver.implicitly_wait(5)
    # Find the username and password input fields and enter the credentials
    username_input = driver.find_element(By.NAME,"username")
    password_input = driver.find_element(By.NAME,"password")
    username_input.send_keys(username)
    password_input.send_keys(password)

    # Press Enter to submit the login form
    password_input.send_keys(Keys.ENTER)
    options.set_preference("user-data-dir=selenium",coockies)

    # Wait for the login process to complete
    driver.implicitly_wait(10)

    # Return the driver instance for further use
    return driver




def unread_messages(driver, text):
    driver.get("https://www.instagram.com/direct/inbox/")
    time.sleep(5)
    try:
        button = driver.find_element(By.CSS_SELECTOR,"[CLASS='_a9-- _a9_1']")
        button.click()
    except Exception as e:
        print(e)
    print('Начинаем проверку непрочитанных сообщений')
    
    element = driver.find_elements(By.CSS_SELECTOR,"span[data-visualcompletion='ignore']")
    print(element)
    for i in element:
        print(i)
        i.click()
        answer_row = driver.find_element(By.CSS_SELECTOR,"[aria-describedby='Message']")
        for i in text:
            answer_row.send_keys(i)
        time.sleep(5)
        answer_row.send_keys(Keys.ENTER)
        client_name = driver.find_element(By.CSS_SELECTOR,"span[CLASS='x1lliihq x193iq5w x6ikm8r x10wlt62 xlyipyv xuxw1ft']")
        inst_id = driver.find_element(By.CSS_SELECTOR,"a[CLASS='x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1q0g3np x87ps6o x1lku1pv x1a2a7pz xjp7ctv xeq5yr9']")
        client_name = inst_id.get_attribute('href').split('/')[-1]
        inst_id = 'https://www.instagram.com/'+client_name
        url = 'https://24baza.ru/crm_inst'
        last_message = driver.find_elements(By.CSS_SELECTOR,"div[CLASS='x6prxxf x1fc57z9 x1yc453h x126k92a xzsf02u']")[-1].text
        params = {'client_name':client_name,'inst_id':inst_id, 'last_message':last_message}
        print(params)
        response = requests.post(url, data=params)
        driver.get("https://www.instagram.com/direct/inbox/") 
    print('Все проверенно и отвеченно!')
            











def get_views(driver):
    print('Начинаем парсинг статистики по аккаунту')
    driver.get("https://business.facebook.com/")
    time.sleep(5)
    login = driver.find_element(By.CSS_SELECTOR,"button[type='submit']")
    login.click()
    time.sleep(5)
    url = driver.current_url
    id = url.split('=')[1]
    driver.get("https://business.facebook.com/latest/insights/results?asset_id=".format(id)+time_param)
    time.sleep(5)
    try:
        close_alert = driver.find_element(By.CSS_SELECTOR,"[role='button']")
        close_alert.click()
    except Exception as e:
        #press enter
        close_alert.send_keys(Keys.ENTER)
    handeled_accounts = driver.find_elements(By.CSS_SELECTOR,"span[CLASS='x1xqt7ti x10d9sdx x1iikomf xrohxju x1heor9g xq9mrsl x1h4wwuj xeuugli']")[0].text
    visits = driver.find_elements(By.CSS_SELECTOR,"span[CLASS='x1xqt7ti x10d9sdx x1iikomf xrohxju x1heor9g xq9mrsl x1h4wwuj xeuugli']")[1].text
    print('Охваченых аккаунтов',handeled_accounts,'посетителей',visits)
    data = [handeled_accounts,visits]
    return data



def data_base(data,username):
    #make database if not exists
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, посетителей INTEGER, охват_аккаунтов INTEGER, date TEXT, username TEXT)")
    conn.commit()
    #add data to database
    cursor.execute("INSERT INTO data (посетителей, охват_аккаунтов, date) VALUES (?,?,?,?)", (data[0], data[1],str(datetime.now()),username))
    conn.commit()




def main(username,password,real_username, text):
    driver = login_to_instagram(username, password)
    for cookie in coockies:
        driver.add_cookie(cookie)
    time.sleep(10)
    driver.get("https://www.instagram.com/{real_username}/".format(real_username=real_username))
    unread_messages(driver,text)
    time.sleep(10)
    driver.get("https://www.instagram.com/{real_username}/".format(real_username=real_username))
    new_cookies = driver.get_cookies()
    for i in new_cookies:
        driver.add_cookie(i)
    time.sleep(10)
    data = get_views(driver)
    data_base(data,username)
    driver.quit()


def main1():
    for i in range(len(config)):
        main(config[i]['username'],config[i]['password'],config[i]['real_username'],config[i]['text'])

if __name__ == "__main__":
    #Поменяйте 10 на лбьое число
    schedule.every(10).minutes.do(main1)
    while True:
        schedule.run_pending()
    
