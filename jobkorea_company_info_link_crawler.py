"""
잡코리아의 산업마다 구분된 기업별 연봉 정보 페이지들로부터 기업들의 정보들을 추출하는 크롤러
결과적으로 얻을 수 있는 정보는
1.잡코리아 상의 산업구분, 2. 기업이름, 3.기업규모, 4.매출액, 5.기업 홈페이지
"""
import requests
from bs4 import BeautifulSoup as bs
import time
import pandas as pd

"""
need to install "lxml"
-> "pip install lxml" 
"""


def get_soup_from_page_with_query(url):
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    })
    return bs(response.text, 'lxml')


def get_company_info_urls(soup, urls):
    """
    잡코리아의 기업별 연봉 정보 "한 페이지"에서 기업 정보를 열람할 수 있는 url들을 가져옴
    :param 기업별 연봉 정보 페이지의 soup:
    :return 기업 정보 url들:
    """
    companies_tag = soup.find(attrs={'id': 'listCompany'})
    companies = companies_tag.find_all("li")
    for company in companies:
        url = "https://www.jobkorea.co.kr"
        try:
            a = company.find("a")
        except AttributeError:
            print("기업 정보 링크를 찾을 수 없음")
            continue
        href = a['href'].replace("salary", "")
        url += (href + "?tabType=I")
        urls.loc[len(urls)] = url
    return companies


def main():
    industries = {
        "IT.정보통신업": ["솔루션.SI.CRM.ERP", "웹에이전시", "쇼핑몰.오픈마켓.소셜커머스",
                     "포털.컨텐츠.커뮤니티", "네트워크.통신서비스", "정보보안",
                     "컴퓨터.하드웨어.장비", "게임.애니메이션", "모바일.APP", "IT컨설팅"],
        "금융.은행업": ["은행.금융", "캐피탈.대출", "증권.보험.카드"],
    }
    page_no = 1
    company_info_urls = pd.DataFrame(columns=['company_info_url'])
    while True:
        urls = {
            "IT.정보통신업>솔루션.SI.CRM.ERP": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10007&indsCode=1000038&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "금융.은행업>은행.금융": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10002&indsCode=1000011&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "금융.은행업>캐피탈.대출": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10002&indsCode=1000012&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "금융.은행업>증권.보험.카드": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10002&indsCode=1000013&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
        }
        industry = "금융.은행업>" + industries['금융.은행업'][1]
        soup = get_soup_from_page_with_query(urls[industry])
        if not get_company_info_urls(soup, company_info_urls):
            break
        print(f"Crawling from {page_no}th page")
        page_no += 1
        time.sleep(1)
    company_info_urls.to_csv("금융.은행업>캐피탈.대출_회사정보_링크_목록.csv")


if __name__ == "__main__":
    main()
