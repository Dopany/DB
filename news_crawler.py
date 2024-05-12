import requests
from bs4 import BeautifulSoup
import csv, re, datetime, time, os, psycopg2

# 디비 연결 정보 불러오기 
def read_db_credentials(file_path):
    credentials = {}
    with open(file_path, mode='r') as file:
        for line in file:
            key, value = line.strip().split('=')
            credentials[key] = value
    return credentials

# 디비에서 회사 정보 가져오기
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
        cur.execute('SELECT company_id, company_name FROM "ETF_company" WHERE company_name NOT LIKE \'%(주)%\' AND company_name NOT LIKE \'%㈜%\'')
        companies = cur.fetchall()
        cur.close()
        conn.close()
        return companies
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL database:", e)

# company_name을 검색어로 하여 네이버 뉴스 크롤링 결과 csv저장
def crawl_and_save_news_for_companies(companies, start_page):
    for company in companies:
        company_id = company[0]  
        company_name = company[1]  
        search = company_name 
        
        
        articles = crawl_naver_news(search, start_page)  
        # 크롤링 결과가 있다면, CSV 파일에 저장
        if articles:
            save_to_csv(articles, f"{company_name}_news.csv", company_id, company_name)
            print(f"Crawling news for company: {company_name}, O")   # 크롤링이 성공적으로 수행됨을 표시
        else:
            print(f"Crawling news for company: {company_name}, X")  # 크롤링이 실패함을 표시
            
# 네이버 뉴스 크롤링
def crawl_naver_news(search, start_page):
    articles = []
    url = f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query={search}&start={start_page}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    news_items = soup.find_all('div', class_='news_wrap')

    for item in news_items:
        title = item.find('a', class_='news_tit').get_text(strip=True)
        preview = item.find('div', class_='news_dsc').get_text(strip=True)
        link = item.find('a', class_='news_tit')['href']
        time_element = item.find('span', class_='info')

        post_time = None
        
        # 작성 시간 yyyy-mm-dd 구조로 변경
        if time_element:
            time_text = time_element.get_text(strip=True)
            if '시간 전' in time_text:
                match = re.search(r'(\d+)시간 전', time_text)
                hours_ago = int(match.group(1))
                current_time = datetime.datetime.now()
                post_time = current_time - datetime.timedelta(hours=hours_ago)
                post_time = post_time.strftime('%Y-%m-%d %H:%M')

        articles.append({'news_title': title, 'news_text': preview, 'news_url': link, 'posted_at': post_time})
        time.sleep(1)
    return articles

# csv 저장
def save_to_csv(data, filename, company_id, company_name):
    if not os.path.exists('news_csv'):
        os.makedirs('news_csv')

    # 파일 경로를 news_csv 폴더 내의 파일로 지정
    filepath = os.path.join('news_csv', filename)
    
    with open(filepath, mode='w', encoding='utf-8', newline='') as file:
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
    crawl_and_save_news_for_companies(companies, start_page)
