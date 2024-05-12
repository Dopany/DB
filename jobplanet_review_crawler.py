import csv, re, datetime, time, os, psycopg2, requests
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
# data_folder = './review_url/'
# folder_list = os.listdir(data_folder)
# folder_list.remove('.DS_Store')
# file_path_list = []
# for i in folder_list:
#     for j in os.listdir(data_folder + i):
#             file_path_list.append(data_folder + i + '/' + j)

data_folder = './review_url/it'
data = os.listdir(data_folder)
data.remove('.DS_Store')
file_list = []
for line in data:
    file_list.append(data_folder + '/' + line)

# db 연걸 정보
db_connection_path = './db_connection.txt'

def DataSet(file_path):
    f = open(file_path, 'r')
    reader = csv.reader(f)
    company_list = {
        'URL': [],
        'company_name': []
    }
    for line in reader:
        company_list['URL'].append(line[0])
        company_list['company_name'].append(line[1])
    company_list['URL'].remove('URL')
    company_list['company_name'].remove('company_name')
    return company_list

def CompanyData(db_connection_info, company_name):
    # db 연결
    connection_info = {}
    with open(db_connection_info, mode='r') as file:
        for line in file:
            key, value = line.strip().split('=')
            connection_info[key] = value
    try:
        conn = psycopg2.connect(
            dbname=connection_info['DB_NAME'],
            user=connection_info['DB_USER'],
            password=connection_info['DB_PASSWORD'],
            host=connection_info['DB_HOST'],
            port=connection_info['DB_PORT']
        )
        cur = conn.cursor()
        cur.execute('SELECT company_id, company_name FROM "Company_company" WHERE company_name = {}'.format("\'" + company_name.strip() + "\'"))
        companies = cur.fetchall()
        cur.close()
        conn.close()
        return companies
    except psycopg2.Error as e:
        print("DB Connect Error", e)
        
def ReviewCrawler(domain):
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
        time.sleep(5)
        
        # '이미 로그인 되어있는 계정이 있습니다.' 창이 뜰 때 처리
        login_check = True
        try:
            already_login_element = driver.find_element(By.XPATH, "//*[@id='duplicate_login_msg']/div/div/div[2]/a")
            ActionChains(driver)\
                .click(already_login_element)\
                .perform()
        except NoSuchElementException:
            login_check = False

        URL_LIST = domain['URL']
        COMPANY_NAME_LIST = domain['company_name']
        
        for i in range(0, len(URL_LIST)):
            time.sleep(2)
            cons_review = []
            pros_review = []
            url_count = 1
            review_count = 1
            # company_info = (company_id, company_name)
            company_info = CompanyData(db_connection_path, COMPANY_NAME_LIST[i])
            print(company_info)
            company_id = company_info[0][0]
            company_name = company_info[0][1]
            
            while review_count != 30:
                time.sleep(0.5)
                driver.get(URL_LIST[i] + "?page={0}".format(url_count))
                review_box = driver.find_elements(By.CLASS_NAME, 'content_body_ty1')
                if review_box == None or len(review_box) == 0:
                    break
                for review in review_box:
                    cons = review.find_element(By.CSS_SELECTOR, '.merit + .df1').find_element(By.TAG_NAME, 'span').text.replace('<br>', ' ').replace('\n', ' ')
                    pros = review.find_element(By.CSS_SELECTOR, '.disadvantages + .df1').find_element(By.TAG_NAME, 'span').text.replace('<br>', ' ').replace('\n', ' ')
                    print(cons, pros)
                    cons_review.append(cons)
                    pros_review.append(pros)
                    review_count += 1
                url_count += 1
            
            length = len(cons_review)
            pros_data = {
                'company_name': [company_name] * length,
                'company_id': [company_id] * length,
                'review_text': pros_review,
            }
            url_df = pd.DataFrame(pros_data)
            url_df.to_csv("./review/it/pros/" + company_name + "_pros.csv", index=True)
            
            cons_data = {
                'company_name': [company_name] * length,
                'company_id': [company_id] * length,
                'review_text': cons_review,
            }
            url_df = pd.DataFrame(cons_data)
            url_df.to_csv("./review/it/cons/" + company_name + "_cons.csv", index=True)

if __name__=='__main__':
    for file_path in file_list:
        domain = DataSet(file_path)
        ReviewCrawler(domain)
    