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


def get_soup_from_page_with(url):
    """
    :param url:
    :return soup object of web page:
    """
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
    """
    industries에 해당하는 모든 산업군의 기업정보 url주소들을 가져와서
    산업마다 csv파일로 저장
    :return:
    """
    industries = {
        "IT.정보통신업": ["솔루션.SI.CRM.ERP", "웹에이전시", "쇼핑몰.오픈마켓.소셜커머스",
                     "포털.컨텐츠.커뮤니티", "네트워크.통신서비스", "정보보안",
                     "컴퓨터.하드웨어.장비", "게임.애니메이션", "모바일.APP", "IT컨설팅"],
        "금융.은행업": ["은행.금융", "캐피탈.대출", "증권.보험.카드"],
        "미디어.광고업" : ["방송.케이블.프로덕션", "신문.잡지.언론사", "광고.홍보.전시",
                     "영화.음반.배급", "연예.엔터테인먼트", "출판.인쇄.사진"],
        "문화.예술.디자인업": ["문화.공연.예술", "디자인.CAD"],
        "의료.제약업": ["제약.보건.바이오"],
    }
    page_no = 1
    company_info_urls = pd.DataFrame(columns=['company_info_url'])
    industry = "IT.정보통신업>" + industries['IT.정보통신업'][7]
    while True:
        urls = {
            "IT.정보통신업>솔루션.SI.CRM.ERP": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10007&indsCode=1000038&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "IT.정보통신업>웹에이전시" :f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10007&indsCode=1000039&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "IT.정보통신업>쇼핑몰.오픈마켓.소셜커머스": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10007&indsCode=1000040&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "IT.정보통신업>포털.컨텐츠.커뮤니티": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10007&indsCode=1000041&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "IT.정보통신업>네트워크.통신서비스": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10007&indsCode=1000042&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "IT.정보통신업>정보보안": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10007&indsCode=1000043&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "IT.정보통신업>컴퓨터.하드웨어.장비": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10007&indsCode=1000044&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "IT.정보통신업>게임.애니메이션": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10007&indsCode=1000045&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "IT.정보통신업>모바일.APP": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10007&indsCode=1000046&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "IT.정보통신업>IT컨설팅": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10007&indsCode=1000047&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "금융.은행업>은행.금융": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10002&indsCode=1000011&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "금융.은행업>캐피탈.대출": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10002&indsCode=1000012&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "금융.은행업>증권.보험.카드": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10002&indsCode=1000013&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "미디어.광고업>방송.케이블.프로덕션": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10005&indsCode=1000030&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "미디어.광고업>신문.잡지.언론사": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10005&indsCode=1000031&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "미디어.광고업>광고.홍보.전시": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10005&indsCode=1000032&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "미디어.광고업>영화.음반.배급": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10005&indsCode=1000033&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "미디어.광고업>연예.엔터테인먼트": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10005&indsCode=1000034&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "미디어.광고업>출판.인쇄.사진": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10005&indsCode=1000035&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "문화.예술.디자인업>문화.공연.예술": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10006&indsCode=1000036&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "문화.예술.디자인업>디자인.CAD": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10006&indsCode=1000037&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
            "의료.제약업>제약.보건.바이오": f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10004&indsCode=1000028&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany",
        }
        soup = get_soup_from_page_with(urls[industry])
        if not get_company_info_urls(soup, company_info_urls):
            break
        print(f"Crawling from {page_no}th page")
        page_no += 1
        time.sleep(1)
    company_info_urls.to_csv("csv-files/medical/url-files/" + industry + "_회사정보_링크_목록2.csv")


if __name__ == "__main__":
    main()
