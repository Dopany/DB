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


def get_recruitment_links(soup):
    recruitments = soup.find_all("li", "list-post")
    hrefs = []
    for idx, recruitment in enumerate(recruitments):
        # 공고 20개까지만 가져옴, 21개째부터는 쿼리랑 연관 없는 인기 채용 공고들
        if idx == 20:
            break
        a = recruitment.find("div", "post-list-info").find("a")
        hrefs.append("https://www.jobkorea.co.kr/" + a['href'])
    return hrefs

def get_company_info(article):
    company_name = article.find("span", "coName").text.strip()
    tb_list = article.find_all("dl", "tbList")
    company_info_titles = tb_list[2].find_all("dt")
    company_info_values = tb_list[2].find_all("dd")
    temp_info = {}
    for title, value in zip(company_info_titles, company_info_values):
        temp_info[title.text] = " ".join(value.text.strip().replace(" ", "").replace("\r", "").split("\n"))
    if '산업(업종)' in temp_info:
        domain = temp_info['산업(업종)']
    else:
        domain = "명시되어있지않음"
    if '사원수' in temp_info:
        employee_count = temp_info['사원수']
    else:
        employee_count = "명시되어있지않음"
    if '설립년도' in temp_info:
        build_year = temp_info['설립년도']
    else:
        build_year = "명시되어있지않음"
    if '기업형태' in temp_info:
        company_size = temp_info['기업형태']
    else:
        company_size = "명시되어있지않음"

    return {'기업 이름': company_name, '도메인': domain, '기업 규모': company_size, '사원수': employee_count, '설립 연도': build_year}

def get_requirement(article):
    tb_list = article.find_all("dl", "tbList")
    requirement_title = tb_list[0].find_all("dt")
    requirement_value = tb_list[0].find_all("dd")
    temp_info = {}
    for title, value in zip(requirement_title, requirement_value):
        temp_info[title.text] = " ".join(value.text.strip().replace(" ", "").replace("\r", "").split("\n"))
    if '경력' in temp_info:
        career = temp_info['경력']
    else:
        career = "명시되어있지않음"
    if '학력' in temp_info:
        education = temp_info['학력']
    else:
        education = "명시되어있지않음"
    if '스킬' in temp_info:
        skills = temp_info['스킬']
    else:
        skills = "명시되어있지않음"

    return {'요구 경력': career, '요구 학력': education, '스킬': skills}

def get_working_conditions(article):
    tb_list = article.find_all("dl", "tbList")
    working_condition_titles = tb_list[1].find_all("dt")
    working_condition_value = tb_list[1].find_all("dd")
    temp_info = {}
    for title, value in zip(working_condition_titles, working_condition_value):
        temp_info[title.text] = " ".join(value.text.strip().replace(" ", "").replace("\r", "").split("\n"))
    if '고용형태' in temp_info:
        employment_type = temp_info['고용형태']
    else:
        employment_type = "명시되어있지않음"
    if '급여' in temp_info:
        salary = temp_info['급여']
    else:
        salary = "명시되어있지않음"
    if '지역' in temp_info:
        location = " ".join(temp_info['지역'].split(" ")[:-1])
    else:
        location = "명시되어있지않음"

    return {'고용 형태': employment_type, '급여': salary, '지역': location}

def get_recruitment_infos(hrefs):
    infos = pd.DataFrame(columns=[
        '공고 제목', '기업 이름', '도메인', '기업 규모', '사원수', '설립 연도',
        '요구 경력', '요구 학력', '스킬',
        '고용 형태', '급여', '지역'
    ])
    for idx, url in enumerate(hrefs, start=1):
        soup = get_soup_from_page_with_query(url)
        print(idx)
        article = soup.find("article", "artReadJobSum")
        recruitment_title = article.find("h3").text.split("\n")[-2].strip()
        # 기업 정보
        company_info = get_company_info(article)
        # 지원 자격
        requirement = get_requirement(article)
        # 근무 조건
        working_conditions = get_working_conditions(article)
        infos.loc[len(infos)] = [
            recruitment_title,
            company_info['기업 이름'], company_info['도메인'], company_info['기업 규모'],
            company_info['사원수'], company_info['설립 연도'],
            requirement['요구 경력'], requirement['요구 학력'], requirement['스킬'],
            working_conditions['고용 형태'], working_conditions['급여'], working_conditions['지역']
        ]
        # 시간 간격 1초보다 많이 줘야 블록 당할 확률 낮아짐
        time.sleep(3)

    return infos




def main():
    query = "데이터엔지니어"
    hrefs = []
    """
    원하는 페이지까지 채용공고 링크 크롤링, 검색어: query, 직무 필터링: 데이터엔지니어 직무로 URL 상에 걸려있음
    """
    for page_no in range(1, 2):
        """
        데이터 직무 필터링 안한 url
        """
        # url = f"https://www.jobkorea.co.kr/Search/?stext={query}&tabType=recruit&Page_No={page_no}"
        """
        데이터 직무 필터링 한 url
        """
        url = f"https://www.jobkorea.co.kr/Search/?stext={query}&duty=1000236&tabType=recruit&Page_No={page_no}"
        soup = get_soup_from_page_with_query(url)
        hrefs += get_recruitment_links(soup)
        time.sleep(0.5)
    # page_no = 1
    # url = f"https://www.jobkorea.co.kr/Search/?stext={query}&tabType=recruit&Page_No={page_no}"
    # soup = get_soup_from_page_with_query(url)
    # hrefs += get_recruitment_links(soup)
    # print(hrefs)
    # print(len(hrefs))
    """
    가져온 채용공고 URL들을 하나씩 방문하여 기업 정보 수집 
    """
    recruitment_infos = get_recruitment_infos(hrefs)

    recruitment_infos.to_csv("recruitment_info.csv")


if __name__ == "__main__":
    main()
