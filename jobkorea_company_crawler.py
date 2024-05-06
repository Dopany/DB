"""
잡코리아의 산업마다 구분된 기업별 연봉 정보 페이지들로부터 기업들의 정보들을 추출하는 크롤러
결과적으로 얻을 수 있는 정보는
1.잡코리아 상의 산업구분, 2. 기업이름, 3.기업규모, 4.매출액, 5.기업 홈페이지
"""
import requests
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime
import pandas as pd
from csv_manager import merge_temp_files, get_path_from

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
        'industry',
        'company_name', 'company_size',
        'company_sales', 'company_url',
        'company_img_url', 'company_addr'
    ])
    for index, row in urls.iterrows():
        try:
            company_info = get_company_info(row['company_info_url'])
        except AttributeError:
            print("기업 정보 url이 올바르지 않습니다.")
            continue
        if not company_info:
            return companies_info, index
        companies_info.loc[len(companies_info)] = [
            industry,
            company_info['기업 이름'], company_info['기업구분'],
            company_info['매출액'], company_info['홈페이지'],
            company_info['로고'], company_info['주소']
        ]
        print(f"{index + 1}th company: {company_info['기업 이름']}")
        time.sleep(1.5)
    return companies_info, -1


def get_company_info(url):
    soup = get_soup_from_page_with_query(url)
    if isBlocked(soup):
        return
    name = get_company_name(soup)
    logo = get_company_logo(soup)
    summary = get_company_summary(soup)
    summary['기업 이름'] = name
    summary['로고'] = logo
    return validate_company_summary(summary)

def get_company_name(soup):
    company_header = soup.find("div", "company-header-branding-body")
    return company_header.find("div", "name").text.strip()

def get_company_logo(soup):
    company_logo = soup.select_one(
        "div.company-header-branding-container > "
        "div.logo > a > img")
    if not company_logo or not company_logo['src']:
        return "명시되어있지않음"
    return "https" + company_logo['src']

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
    if '주소' not in summary:
        summary['주소'] = '명시되어있지않음'
    return summary

def isBlocked(soup):
    if soup.select_one("#step1_1"):
        return True
    return False


def main():
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
    industry = "미디어.광고업>" + industries['미디어.광고업'][5]
    industry_dir_path = get_path_from(industry)
    company_info_urls = pd.read_csv(industry_dir_path + "url-files/" + industry + "_회사정보_링크_목록.csv")
    # company_info_urls = pd.read_csv("csv-files/temp/url-files/" + industry + "_회사정보_수집안된_링크_목록.csv")
    companies_info, idx = get_companies_info(company_info_urls, industry)
    if idx >= 0:
        sliced_urls = company_info_urls.loc[idx:]
        sliced_urls.to_csv(f"csv-files/temp/url-files/{industry}_회사정보_수집안된_링크_목록.csv")
        companies_info.to_csv(f"csv-files/temp/info-files/{industry}_회사_수집_덜된_목록_{datetime.now()}.csv")
        print("서버로부터 차단됨.")
        return
    companies_info.to_csv("csv-files/temp/info-files/" + industry + "_회사_수집_완료_목록.csv")
    print("회사 정보 수집 완료")
    merge_temp_files(industry)

if __name__ == "__main__":
    main()
