import pandas as pd
import os

def handle_volume(volume):
    try:
        if pd.isna(volume):
            return 0
        elif 'K' in volume:
            return float(volume.replace('K', '')) * 1000
        elif 'M' in volume:
            return float(volume.replace('M', '')) * 1000000
        else:
            return float(volume)
    except TypeError:
        print(f"TypeError occurred with value: {volume}")
        return volume

def handle_close_price(price):
    try:
        if pd.isna(price):
            return 0
        if isinstance(price, str) and ',' in price:
            price = price.replace(',', '')
        if isinstance(price, str) and '.' in price:
            price = price.split('.')[0]
        return int(price)
    except TypeError:
        print(f"TypeError occurred with value: {price}")
        return price

def transform_columns(file_name: str):
    df = pd.read_csv('original_csv/{}'.format(file_name), encoding='UTF-8')
    df = df.drop(df.columns[[2, 3, 4]], axis=1)
    df.rename(
        columns={'날짜': 'transaction_date', '종가': 'closing_price', '거래량': 'trading_volume', '변동 %': 'change'},
        inplace=True,
        )
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['closing_price'] = df['closing_price'].apply(handle_close_price)

    df['trading_volume'] = df['trading_volume'].apply(handle_volume).astype(int)
    df['change'] = df['change'].str.replace('%', '').astype(float)

    df.to_csv('transform_csv/{}'.format(file_name), index=False, encoding='UTF-8')

def get_file_list(directory: str):
    return os.listdir(directory)

def main():
    root_directory = 'original_csv/'
    type_list = ['etf', 'stock']
    for type_name in type_list:
        directory = root_directory + type_name
        file_list = get_file_list(directory)
        for file_name in file_list:
            transform_columns(type_name + '/' + file_name)

if __name__ == "__main__":
    main()