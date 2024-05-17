import requests
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
"""
need to install "lxml"
-> "pip install lxml" 
"""

def get_soup_from_page_with(url):
    """
    :param url:
    :return soup object of web page:
    """
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    })
    return bs(response.text, 'lxml')


def get_recruitment_links(soup, urls):
    """

    :param soup: 잡코리아 검색결과 페이지의 soup 객체
    :param urls: 채용공고 url을 저장할 dataframe
    :return: 채용공고 게시글 목록을 담고있는 li 태그 요소, None이면 더 이상 수집할 채용공고가 없는 것으로 수집을 종료함
    """
    if isBlocked(soup):
        raise AttributeError
    query_list = soup.select_one("div.recruit-info")
    recruitments = query_list.select("ul.clear > li.list-post")
    for recruitment in recruitments:
        a = recruitment.find("div", "post-list-info").find("a")
        due_date = recruitment.find("span", "date").text
        urls.loc[len(urls)] = ["https://www.jobkorea.co.kr/" + a['href'], due_date]
    return recruitments

def isBlocked(soup):
    """
    서버로부터 차단됐는지 확인 후 boolean 반환
    :param 채용공고 게시글 soup:
    :return 차단 여부 boolean:
    """
    if soup.select_one("#step1_1"):
        return True
    return False

def main():
    """
    잡코리아에 직무별로 "채용" 키워드를 검색하여 나온 공고들의 url들을 모두 수집하여 csv로 저장,
    서버로부터 차단시 수집완료된 부분까지 csv로 저장,
    get_recruitment_links()의 반환 값이 없으면 더 이상 수집할 공고가 없으므로 수집 종료
    :return:
    """
    query = "채용"
    jobs = ['백엔드개발자', '프론트엔드개발자', '웹개발자', '앱개발자',
            '시스템엔지니어', '네트워크엔지니어','DBA', '데이터엔지니어', '데이터사이언티스트',
            '보안엔지니어', '소프트웨어개발자', '게임개발자', '하드웨어개발자',
            '머신러닝엔지니어', '블록체인개발자', '클라우드엔지니어', '웹퍼블리셔', 'IT컨설팅', 'QA']
    backend_job_code = 1000229

    for idx, job in enumerate(jobs):
        job_code = backend_job_code + idx
        recruitment_urls = pd.DataFrame(columns=[f'recruitment_url', 'due_date'])
        page_no = 1
        while True:
            url = f"https://www.jobkorea.co.kr/Search/?stext={query}&duty={job_code}&focusTab=&focusGno=44524817&tabType=recruit&Page_No={page_no}"
            try:
                soup = get_soup_from_page_with(url)
            except AttributeError:
                print(f"crawling has been blocked in job: {job}")
                break
            if not get_recruitment_links(soup, recruitment_urls):
                break
            print(f"{page_no}th page crawled in {job}, code: {job_code}")
            page_no += 1
            time.sleep(1)
        recruitment_urls.to_csv(f"{job}_recruitment_urls.info.csv")


if __name__ == "__main__":
    main()
