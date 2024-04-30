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


def get_companies_info(urls, industry):
    companies_info = pd.DataFrame(columns=[
        'industry', 'company_name', 'company_size', 'company_sales', 'company_url', 'company_logo'
    ])
    for index, row in urls.iterrows():
        try:
            company_info = get_company_info(row['company_info_url'])
        except AttributeError:
            print("기업 정보 url이 올바르지 않습니다.")
            continue
        companies_info.loc[len(companies_info)] = [
            industry,
            company_info['기업 이름'], company_info['기업구분'],
            company_info['매출액'], company_info['홈페이지']
        ]
        print(f"{index + 1}th company: {company_info['기업 이름']}")
        time.sleep(1)
    return companies_info


def get_company_info(url):
    soup = get_soup_from_page_with_query(url)
    name = get_company_name(soup)
    summary = get_company_summary(soup)
    summary['기업 이름'] = name
    return validate_company_summary(summary)

def get_company_name(soup):
    company_header = soup.find("div", "company-header-branding-body")
    return company_header.find("div", "name").text.strip()

def get_company_logo(soup):
    pass

def get_company_summary(soup):
    summary = {}
    info_table = soup.find("table", "table-basic-infomation-primary")
    table_labels = info_table.select("tr.field > th.field-label")
    table_values = info_table.select("tr.field > td.field-value")
    for title, value in zip(table_labels, table_values):
        summary[title.text.strip()] = (value.text
                                       .strip().replace(" ", "")
                                       .replace("\n", "").replace("\r", ""))
    return summary


def validate_company_summary(summary):
    if '기업구분' not in summary or summary['기업구분'] == "-":
        summary['기업구분'] = '명시되어있지않음'
    if '매출액' not in summary or summary['매출액'] == "-":
        summary['매출액'] = '명시되어있지않음'
    if '홈페이지' not in summary or summary['홈페이지'] == "-":
        summary['홈페이지'] = '명시되어있지않음'
    if '기업 로고' not in summary:
        summary['기업 로고'] = '명시되어있지않음'
    if '기업 이름' not in summary:
        summary['기업 이름'] = '명시되어있지않음'
    return summary


def main():
    industries = {
        "IT.정보통신업": ["솔루션.SI.CRM.ERP", "웹에이전시", "쇼핑몰.오픈마켓.소셜커머스",
                     "포털.컨텐츠.커뮤니티", "네트워크.통신서비스", "정보보안",
                     "컴퓨터.하드웨어.장비", "게임.애니메이션", "모바일.APP", "IT컨설팅"],
        "금융.은행업": ["은행.금융", "캐피탈.대출", "증권.보험.카드"],
    }
    company_info_urls = pd.read_csv("금융.은행업>캐피탈.대출_회사정보_링크_목록.csv")
    industry = "금융.은행업>" + industries['금융.은행업'][1]
    companies_info = get_companies_info(company_info_urls, industry)
    companies_info.to_csv("금융.은행업>캐피탈.대출_회사_목록.csv")


if __name__ == "__main__":
    main()
