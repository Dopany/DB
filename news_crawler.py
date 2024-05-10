import requests
from bs4 import BeautifulSoup
import csv, re, datetime
import psycopg2

def read_db_credentials(file_path):
    credentials = {}
    with open(file_path, mode='r') as file:
        for line in file:
            key, value = line.strip().split('=')
            credentials[key] = value
    return credentials

def fetch_company_data_from_db(credentials):
    try:
        conn = psycopg2.connect(
            dbname=credentials['DB_NAME'],
            user=credentials['DB_USER'],
            password=credentials['DB_PASSWORD'],
            host=credentials['DB_HOST'],
            port=credentials['DB_PORT']
        )
        cur = conn.cursor()
        cur.execute("SELECT company_id, company_name FROM ETF_company")
        companies = cur.fetchall()
        cur.close()
        conn.close()
        return companies
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL database:", e)

def get_table_names(dbname, user, password, host, port):
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    table_names = [row[0] for row in cur.fetchall()]
    conn.close()
    return table_names

# 연결 정보
dbname = "postgres"
user = "kimseunghyun"
password = ""
host = "localhost"
port = "5432"

# 테이블 이름 가져오기
table_names = get_table_names(dbname, user, password, host, port)
print("테이블 이름:")
for name in table_names:
    print(name)
    
    
def crawl_and_save_news_for_companies(companies, start_page, end_page):
    for company in companies:
        company_id = company[0]  
        company_name = company[1]  
        search = company_name  
        articles = crawl_naver_news(search, start_page, end_page)  
        # 크롤링 결과를 CSV 파일에 저장
        save_to_csv(articles, f"{company_name}_news.csv", company_id, company_name)

def crawl_naver_news(search, start_page, end_page):
    articles = []

    for page in range(start_page, end_page + 1):
        start = (page - 1) * 10 + 1
        url = f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query={search}&start={start}"

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        news_items = soup.find_all('div', class_='news_wrap')

        for item in news_items:
            title = item.find('a', class_='news_tit').get_text(strip=True)
            preview = item.find('div', class_='news_dsc').get_text(strip=True)
            link = item.find('a', class_='news_tit')['href']
            time_element = item.find('span', class_='info')

            time = None

            if time_element:
                time_text = time_element.get_text(strip=True)
                if '시간 전' in time_text:
                    match = re.search(r'(\d+)시간 전', time_text)
                    hours_ago = int(match.group(1))
                    current_time = datetime.datetime.now()
                    time = current_time - datetime.timedelta(hours=hours_ago)
                    time = time.strftime('%Y-%m-%d %H:%M')

            articles.append({'Title': title, 'Preview': preview, 'URL': link, 'Time': time})

    return articles

def save_to_csv(data, filename, company_id, company_name):
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        fieldnames = ['company_id', 'company_name', 'news_title', 'news_text', 'news_url', 'posted_at']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for idx, article in enumerate(data, start=1):
            article['company_name'] = company_name
            article['company_id'] = company_id
            writer.writerow(article)

if __name__ == "__main__":
    db_credentials_file = '/Users/kimseunghyun/TrendyDE/DEproject/DB/db_credentials.txt'
    db_credentials = read_db_credentials(db_credentials_file)

    companies = fetch_company_data_from_db(db_credentials)

    start_page = 1
    end_page = 2
    crawl_and_save_news_for_companies(companies, start_page, end_page)
