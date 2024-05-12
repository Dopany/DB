import requests
import csv
import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains 


login_info = {
    'id': 'joongh0113@gmail.com',
    'password': 'Wndgus2023!',
}

# csv 파일 세팅
data_folder = '../companies_info/'
folder_list = os.listdir(data_folder)
folder_list.remove('.DS_Store')
file_path_list = []
for i in folder_list:
    for j in os.listdir(data_folder + i):
            file_path_list.append(data_folder + i + '/' + j)


def DataSet(file_path):
    f = open(file_path, 'r')
    reader = csv.reader(f)
    company_name_list = set()
    for line in reader:
        company_name = line[2]
        company_name_list.add(company_name)
    company_name_list.remove('company_name')
    return company_name_list

def URLCrawler(file_path):
    review_url = []
    is_company_name_list = []
    url = 'https://www.jobplanet.co.kr/users/sign_in?_nav=gb'
    
    # selenium 시작
    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
        driver.get(url)
        # 로그인
        driver.implicitly_wait(10)
        login_id = login_info['id']
        id_input = driver.find_element(By.XPATH, "//*[@id='user_email']")
        login_password = login_info['password']
        password_input = driver.find_element(By.XPATH, "//*[@id='user_password']")
        login_button = driver.find_element(By.XPATH, "//*[@id='signInSignInCon']/div[2]/div/section[3]/fieldset/button")
        
        ActionChains(driver)\
            .send_keys_to_element(id_input, login_id)\
            .send_keys_to_element(password_input, login_password)\
            .click(login_button)\
            .perform()
        time.sleep(3)
        
        # '이미 로그인 되어있는 계정이 있습니다.' 창이 뜰 때 처리
        login_check = True
        try:
            already_login_element = driver.find_element(By.XPATH, "//*[@id='duplicate_login_msg']/div/div/div[2]/a")
            ActionChains(driver)\
                .click(already_login_element)\
                .perform()
        except NoSuchElementException:
            login_check = False
            
        # url 수집 시작
        company_name_list = DataSet(file_path)
        for company_name in company_name_list:
            removed_name = company_name.replace('(주)', '').replace('(주 )', '').replace('( 주)', '').replace('㈜', '').replace('( 유)', '').replace('(유 )', '').replace('(유)', '')
            modified_name = company_name.replace('(주 )', '(주)').replace('( 주)', '(주)').replace('㈜', '(주)').replace('( 유)', '(유)').replace('(유 )', '(유)')
            
            text_input = driver.find_element(By.XPATH, "//*[@id='search_bar_search_query']")
            text_input.clear()
            ActionChains(driver)\
                .send_keys_to_element(text_input, removed_name)\
                .perform()
            driver.implicitly_wait(2)
            try:
                search_item = driver.find_element(By.XPATH, "//*[@id='search_form']/div/div").find_elements(By.CLASS_NAME, "company")
                for i in search_item:
                    compare_name = i.get_attribute("data-term")
                    corp_name = compare_name.replace('(주)', '').replace('(주 )', '').replace('( 주)', '').replace('㈜', '').replace('(유)', '').replace('(유 )', '').replace('( 유)', '')
                    if modified_name == compare_name\
                    or modified_name == corp_name\
                    or modified_name == corp_name + '(주)'\
                    or modified_name == '(주)' + corp_name\
                    or modified_name == '(유)' + corp_name\
                    or modified_name == corp_name + '(유)':
                        company_id = i.get_attribute("data-id")
                        review_url.append('https://www.jobplanet.co.kr/companies/{0}/reviews/{1}'.format(company_id, corp_name.replace(' ', '-')))
                        is_company_name_list.append(company_name)
                        break
            except NoSuchElementException:
                continue
    
            # url_df = pd.DataFrame(review_url, columns=['url'])
            # url_df['company_name'] = is_company_name_list
            # url_df.to_csv(file_path[18:] + "URL.csv", index = False)
        data = {
            'URL': review_url,
            'company_name': is_company_name_list,
        }
        url_df = pd.DataFrame(data)
        file_path = file_path.replace('.csv', '_')
        url_df.to_csv("./review_url/" + file_path[18:] + "URL.csv", index = False)
    
if __name__=='__main__':
    for i in range(8, len(file_path_list)):
        company_url_list = URLCrawler(file_path_list[i])
    # 9 아직 안함
    