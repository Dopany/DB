import requests
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
from datetime import datetime
from csv_manager import merge_temp_files
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

def get_requirement(article):
    """
    채용 요구 조건 정보들을 수집
    1. 요구 경력, 2. 요구 학력, 3. 필요 스킬
    :param article: 채용공고 게시글의 article 태그 요소
    :return: 1. 요구 경력, 2. 요구 학력, 3. 필요 스킬을 포함하는 딕셔너리
    """
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
        skills = temp_info['스킬'].lower()
    else:
        skills = "명시되어있지않음"

    return {'경력': career, '학력': education, '스킬': skills}

def get_company_name(article):
    """
    기업 이름 수집
    :param article: 채용공고 게시글의 article 태그 요소
    :return: 공백 제거한 기업 이름
    """
    return (article.find("span", "coName").text.replace("기업정보", "")
            .replace("\r", "").replace("\n", "").strip())

def get_recruitment_infos(recruitment_urls, job):
    """
    채용공고 게시글 url들로부터 다음 정보들을 추출
    1. 제목, 2. 게시글 url, 3. 요구 경력, 4. 요구 학력,
    5. 마감기한, 6. 채용 기업, 7. 채용 직무, 8. 요구 스킬

    :param recruitment_urls:
    :param job:
    :return:
    """
    infos = pd.DataFrame(columns=[
        'recruitment_title', 'url',
        'career', 'education', 'due_date', 'company_name',
        'job', 'skill',
    ])

    for idx, row in recruitment_urls.iterrows():
        url = row['recruitment_url']
        due_date = row['due_date'].replace("~", "")
        soup = get_soup_from_page_with(url)
        if isBlocked(soup):
            return infos, idx
        try:
            if is_head_hunting(soup):
                print(f"헤드헌팅, 생략, {idx + 1}")
                time.sleep(1)
                continue
            article = soup.find("article", "artReadJobSum")
            recruitment_title = article.find("h3").text.split("\n")[-2].strip()
            # 지원 자격
            requirement = get_requirement(article)
            # 기업 이름
            company_name = get_company_name(article)
        except AttributeError:
            print(f"잘못된 채용공고 링크, {idx + 1}")
            time.sleep(1)
            continue
        infos.loc[len(infos)] = [
            recruitment_title, url,
            requirement['경력'], requirement['학력'], due_date, company_name,
            job, requirement['스킬']
        ]
        print(f'{idx + 1}th recruitment scraped in {job}, title: {recruitment_title}')
        # 시간 간격 1초보다 많이 줘야 블록 당할 확률 낮아짐
        time.sleep(1.5)

    return infos, -1

def isBlocked(soup):
    """
    서버로부터 차단됐는지 확인 후 boolean 반환
    :param 채용공고 게시글 soup:
    :return 차단 여부 boolean:
    """
    if soup.select_one("#step1_1"):
        return True
    return False

def is_head_hunting(soup):
    """
    헤드헌팅 공고인지 확인 후 boolean 반환
    :param 채용공고 게시글 soup:
    :return 헤드헌팅 공고 여부 boolean:
    """
    if "헤드헌팅" in soup.select_one("h1.tpl_hd_1").text:
        return True
    return False

def main():
    """
    industries에 해당하는 모든 산업의 채용공고 게시글 url주소들을 가져와서
    산업마다 csv파일로 저장
    서버로부터 차단시 스크랩한 내용까지 csv파일로 저장하고,
    아직 방문하지 못한 url들부터 slice하여 별도의 url csv파일로 저장
    -> 사용자가 차단해제 후 이 파일로 수집 못한 부분부터 다시 진행
    :return:
    """
    jobs = ['백엔드개발자', '프론트엔드개발자', '웹개발자', '앱개발자',
            '시스템엔지니어', '네트워크엔지니어','DBA', '데이터엔지니어', '데이터사이언티스트',
            '보안엔지니어', '소프트웨어개발자', '게임개발자', '하드웨어개발자',
            '머신러닝엔지니어', '블록체인개발자', '클라우드엔지니어', '웹퍼블리셔', 'IT컨설팅', 'QA']
    job = jobs[18]
    recruitment_urls = pd.read_csv(f"csv-files/recruitments/urls/{job}_recruitment_urls.info.csv")

    # restart urls
    # recruitment_urls = pd.read_csv(f"csv-files/temp/url-files/{job}_채용공고_수집안된_링크_목록.csv")
    """
    가져온 채용공고 URL들을 하나씩 방문하여 기업 정보 수집
    """
    recruitments_info, idx = get_recruitment_infos(recruitment_urls, job)
    if idx >= 0:
        sliced_urls = recruitment_urls.loc[idx:]
        sliced_urls.to_csv(f"csv-files/temp/url-files/{job}_채용공고_수집안된_링크_목록.csv")
        recruitments_info.to_csv(f"csv-files/temp/info-files/{job}_채용공고_수집_덜된_목록_{datetime.now()}.csv")
        print("서버로부터 차단됨")
        return
    recruitments_info.to_csv(f"csv-files/temp/info-files/{job}_채용공고_수집_완료_목록.csv")
    print("채용 공고 수집 완료")
    merge_temp_files(job, "recruitments")



if __name__ == "__main__":
    main()
