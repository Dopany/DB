import os
import pandas as pd

def get_path_from(industry):
    target_industry = industry.split(">")[0]
    target_dir_name = ''
    if target_industry == 'IT.정보통신업':
        target_dir_name = 'it'
    elif target_industry == '금융.은행업':
        target_dir_name = 'finance'
    elif target_industry == '미디어.광고업':
        target_dir_name = 'media'
    elif target_industry == '문화.예술.디자인업':
        target_dir_name = 'culture'
    elif target_industry == '의료.제약업':
        target_dir_name = 'medical'

    if target_dir_name == '':
        raise AttributeError("적절하지 않은 산업 이름")

    return f"csv-files/{target_dir_name}/"


def merge_temp_files(industry):
    path = "csv-files/temp/info-files"
    files = os.listdir(path)
    all_company_info = pd.DataFrame()
    for file in files:
        if file in ('.DS_Store', 'merged'):
            continue
        df = pd.read_csv(path + "/" + file)

        all_company_info = pd.concat([all_company_info, df.loc[:, (df.columns != 'Unnamed: 0')]], ignore_index=True)
    industry_dir_path = get_path_from(industry)

    all_company_info.to_csv(industry_dir_path + f"info-files/{industry}_회사_목록.csv")
