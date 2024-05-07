import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date

"""
    get_finance_itemlist: root_url을 기준으로 페이지를 1까지 가져와서 날짜, 종가, 거래량, 변동률을 가져옵니다.
    root_url: 종목 코드를 포함한 url
    time: 가져오고 싶은 시간을 기준으로 가져오고 싶으면 사용, 형식은 ''YYYY.MM.DD'
"""
def get_finance_itemlist(root_url: str, time: str):

    # 이 부분은 페이지를 1까지 가져오는걸 가정하고 작성되었습니다.
    # 만약 페이지를 더 가져오고 싶다면 page_num을 더 늘리면 됩니다.
    page_num = 1
    output = []
    
    for n in range(1, page_num + 1):
        response = requests.get(root_url + str(n),  headers={'User-agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in range(3, 16):
            if i in [8, 9, 10]:
                continue
            date = soup.select_one('body > table.type2 > tr:nth-child({}) > td:nth-child(1) > span'.format(i)).text
            date = pd.to_datetime(date)

            # 시간을 기준으로 가져오고 싶으면 아래 주석을 해제하면 됩니다.
            """
            time = pd.to_datetime(time)
            if date >= time:
               return output
            """
            closing_price = int(soup.select_one('body > table.type2 > tr:nth-child({}) > td:nth-child(2) > span'.format(i)).text.replace(',', ''))
            trading_volume = int(soup.select_one('body > table.type2 > tr:nth-child({}) > td:nth-child(7) > span'.format(i)).text.replace(',', ''))
            diff = int(soup.select_one('body > table.type2 > tr:nth-child({}) > td:nth-child(3) > span'.format(i)).text.replace(',', ''))
            diff_state = soup.select_one('body > table.type2 > tr:nth-child({}) > td:nth-child(3) > em > span'.format(i)).text

            if diff_state == '하락':
                diff = (-1) * diff

            elif diff_state == '상승':
                diff = diff

            else:
                diff = 0

            change = round( ((closing_price + diff) / closing_price * 100) - 100, 2)
            output.append({'transaction_date': date, 'closing_price': closing_price, 'trading_volume': trading_volume, 'change': change})

    return output

"""
get_root_url: 종목 코드를 포함한 url을 가져옵니다.
finance_num: 종목 코드
"""
def get_root_url(finance_num: str):
    return 'https://finance.naver.com/item/sise_day.naver?code={}&page='.format(finance_num)

"""
get_finance_dictlist: etf, stock 디렉토리에 있는 파일 리스트를 가져와서 딕셔너리 리스트로 만들어줍니다.
만약 디렉토리의 경로가 바뀌었다면 root_directory를 바꿔주면 됩니다.
필요한 디렉토리 구조는 다음과 같습니다.
original_csv/
    etf/
        etf_종목명_종목코드.csv
    stock/
        stock_종목명_종목코드.csv
"""
def get_finance_dictlist():
    root_directory = 'original_csv/'
    type_list = ['etf', 'stock']
    finance_dictlist = []
    for type_name in type_list:
        directory = root_directory + type_name
        file_list = os.listdir(directory)
        for file_name in file_list:
            finance_dict = {}
            finance_dict['type'] = type_name
            finance_dict['finance_name'] = file_name.split('_')[0]
            finance_dict['finance_num'] = file_name.split('_')[1][0:6]
            finance_dictlist.append(finance_dict)
    return finance_dictlist

"""
refine_finance_dict_to_df: finance_itemlist과 finance_dict를 받아서 데이터 프레임으로 만들어줍니다.
finance_itemlist: get_finance_itemlist 메서드에서 가져온 리스트
finance_dict: get_finance_dictlist 메서드로 생성된 리스트에서 가져온 딕셔너리 원소
"""
def refine_finance_dict_to_df(finance_itemlist: list, finance_dict: dict):
    df = pd.DataFrame(finance_itemlist)
    df['finance_type'] = finance_dict['type']
    df['finance_item_name'] = finance_dict['finance_name']
    return df

"""
최신 데이터를 데이터 프레임으로 가져오려면 main 메서드와 같은 형식으로 작성하면 됩니다.

1. get_finance_dictlist 메서드를 통해 etf, stock 디렉토리에 있는 파일 리스트를 가져와서 각 종목의 정보를 딕셔너리 리스트로 만들어줍니다.
2. get_root_url 메서드를 통해 종목 코드를 포함한 url을 가져옵니다.
3. get_finance_itemlist 메서드를 통해 root_url을 기준으로 페이지를 1까지 가져와서 날짜, 종가, 거래량, 변동률을 가져옵니다.
4. refine_finance_dict_to_df 메서드를 통해 finance_itemlist과 finance_dict를 받아서 데이터 프레임으로 만들어줍니다.
"""
def main():
    # 시간을 기준으로 가져오고 싶으면 time을 데이터 베이스의 가장 최근의 날짜로 설정하면 됩니다.
    time = date.today().strftime('%Y.%m.%d')

    finance_dictlist = get_finance_dictlist()
    for finance_dict in finance_dictlist:
        root_url = get_root_url(finance_dict['finance_num'])
        finance_itemlist = get_finance_itemlist(root_url, time)
        df = refine_finance_dict_to_df(finance_itemlist, finance_dict)
        print(df)

if __name__ == "__main__":
    main()