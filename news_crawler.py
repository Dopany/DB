import requests
from bs4 import BeautifulSoup
import csv, re, datetime

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

            # Default time value
            time = None

            # Check if time_element contains time information
            if time_element:
                time_text = time_element.get_text(strip=True)
                # Check if time_text contains specific text indicating time
                if '시간 전' in time_text:
                    match = re.search(r'(\d+)시간 전', time_text)
                    hours_ago = int(match.group(1))
                    current_time = datetime.datetime.now()
                    time = current_time - datetime.timedelta(hours=hours_ago)
                    time = time.strftime('%Y-%m-%d %H:%M')

            articles.append({'Title': title, 'Preview': preview, 'URL': link, 'Time': time})

    return articles



def save_to_csv(data, filename):
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        fieldnames = ['Title', 'Preview', 'URL', 'Time']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for article in data:
            writer.writerow(article)

if __name__ == "__main__":
    search = input("네이버 뉴스에서 검색할 키워드를 입력하세요: ")
    start_page = 1
    end_page = 2
    articles = crawl_naver_news(search, start_page, end_page)
    save_to_csv(articles, f"{search}_news.csv")
    print(f"뉴스 정보를 {search}_news.csv 파일에 성공적으로 저장했습니다.")
