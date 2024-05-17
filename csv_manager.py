import os
import pandas as pd

def get_directory_from(keyword):
    keyword = keyword.split(">")[0]
    path_map = {
        'IT.정보통신업': 'it',
        '금융.은행업': 'finance',
        '미디어.광고업': 'media',
        '문화.예술.디자인업': 'culture',
        '의료.제약업': 'medical',
        '백엔드개발자': 'backend',
        '프론트엔드개발자': 'frontend',
        '웹개발자': 'web',
        '앱개발자': 'app',
        '시스템엔지니어': 'system_engineer',
        '네트워크엔지니어': 'network_engineer',
        'DBA': 'dba',
        '데이터엔지니어': 'data_engineer',
        '데이터사이언티스트': 'data_scientist',
        '보안엔지니어': 'security_engineer',
        '소프트웨어개발자': 'software',
        '게임개발자': 'game',
        '하드웨어개발자': 'hardware',
        '머신러닝엔지니어': 'machine_learning',
        '블록체인개발자': 'blockchain',
        '클라우드엔지니어': 'cloud_engineer',
        '웹퍼블리셔': 'web_publisher',
        'IT컨설팅': 'it_consulting',
        'QA': 'qa',
    }
    target_dir_name = path_map.get(keyword, '')

    if target_dir_name == '':
        raise AttributeError("적절하지 않은 키워드")

    return f"{target_dir_name}/"


def merge_temp_files(keyword, info_type):
    path = "csv-files/temp/info-files"
    files = os.listdir(path)
    merged = pd.DataFrame()

    for file in files:
        if not file.endswith(".csv"):
            continue
        df = pd.read_csv(path + "/" + file)
        merged = pd.concat([merged, df.loc[:, (df.columns != 'Unnamed: 0')]], ignore_index=True)

    target_dir_name = get_directory_from(keyword)
    target_path = f"csv-files/{info_type}/info/" + target_dir_name
    merged.to_csv(f"{target_path}/{keyword}_{info_type}.csv")


def inner_join_table(left_table, right_table, on_column):
    return pd.merge(left=left_table, right=right_table, how='inner', on=on_column)

def left_join_table(left_table, right_table, on_column):
    return pd.merge(left=left_table, right=right_table, how='left', on=on_column)