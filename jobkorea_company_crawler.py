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


def get_company_info_urls(soup):
    """
    잡코리아의 기업별 연봉 정보 "한 페이지"에서 기업 정보를 열람할 수 있는 url들을 가져옴
    :param 기업별 연봉 정보 페이지의 soup:
    :return 기업 정보 url들:
    """
    companies_tag = soup.find(attrs={'id': 'listCompany'})
    companies = companies_tag.find_all("li")
    urls = []
    for company in companies:
        url = "https://www.jobkorea.co.kr"
        a = company.find("a")
        href = a['href'].replace("salary", "")
        url += href
        urls.append(url)
    return urls


def get_companies_info(urls, industry):
    companies_info = pd.DataFrame(columns=[
        'industry', 'company_name', 'company_size', 'company_sales', 'company_url'
    ])
    for index, company_info_url in enumerate(urls, start=1):
        try:
            company_info = get_company_info(company_info_url)
        except AttributeError:
            return companies_info
        companies_info.loc[len(companies_info)] = [
            industry,
            company_info['기업 이름'], company_info['기업구분'],
            company_info['매출액'], company_info['홈페이지']
        ]
        print(f"{index}th company: {company_info['기업 이름']}")
        time.sleep(1)
    return companies_info


def get_company_info(url):
    soup = get_soup_from_page_with_query(url)
    name = get_company_name(soup)
    summary = get_company_summary(soup)
    summary['기업 이름'] = name
    return summary


def get_company_summary(soup):
    info_table = soup.find("table", "table-basic-infomation-primary")
    table_labels = info_table.select("tr.field > th.field-label")
    table_values = info_table.select("tr.field > td.field-value")
    summary = {}
    for title, value in zip(table_labels, table_values):
        summary[title.text.strip()] = (value.text
                                       .strip().replace(" ", "")
                                       .replace("\n", "").replace("\r", ""))
    return validate_company_summary(summary)


def validate_company_summary(summary):
    if '기업구분' not in summary or summary['기업구분'] == "-":
        summary['기업구분'] = '명시되어있지않음'
    if '매출액' not in summary or summary['매출액'] == "-":
        summary['매출액'] = '명시되어있지않음'
    if '홈페이지' not in summary or summary['홈페이지'] == "-":
        summary['홈페이지'] = '명시되어있지않음'
    return summary


def get_company_name(soup):
    company_header = soup.find("div", "company-header-branding-body")
    return company_header.find("div", "name").text.strip()


def main():
    page_no = 1
    url = f"https://www.jobkorea.co.kr/Salary/Index?coKeyword=&tabindex=1&indsCtgrCode=10007&indsCode=1000038&jobTypeCode=&haveAGI=0&orderCode=2&coPage={page_no}#salarySearchCompany"
    soup = get_soup_from_page_with_query(url)
    company_info_urls = get_company_info_urls(soup)
    companies_info = get_companies_info(company_info_urls, "IT.정보통신업>솔루션.SI.CRM.ERP")
    companies_info.to_csv("companies_info.csv")


if __name__ == "__main__":
    main()
