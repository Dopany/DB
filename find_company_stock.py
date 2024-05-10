import os
import csv
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import json

def find_unmatched_company():
  loaded_company_list = get_loaded_company_list()
  company_list = get_company_list()
  unmatched_company_list = []
  for company in company_list:
    if company not in loaded_company_list:
      unmatched_company_list.append(company)
  return unmatched_company_list

def get_loaded_company_list():
  directory = 'original_csv/stock'
  file_list = os.listdir(directory)
  file_name_list = []
  for file_name in file_list:
    file_name_list.append(file_name.split('_')[0])
  return file_name_list

def get_company_list():
  company_list = []
  root_directory = 'companies_info/'
  for industry_type in os.listdir(root_directory):
    if industry_type == '.DS_Store':
      continue
    for company_csv in os.listdir(root_directory + industry_type):
      with open(root_directory + industry_type + '/' + company_csv, newline='', encoding='utf-8') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
          company_list.append(row[2])
  return company_list

def find_company_in_market():
  root_url = "https://finance.naver.com/search/search.naver?query="
  company_in_stock = {}
  for trans_company, origin_company in extract_company_name().items():
    encode_str = quote(trans_company, encoding='euc-kr')
    response = requests.get(root_url + encode_str, headers={'User-agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    if soup.select('.result_area > p > em') == []:
      company_in_stock[trans_company] = origin_company
  return company_in_stock

def extract_company_name():
  company_list = {}
  for company in find_unmatched_company():
    if company[0] == '(':
      original_company = company
      company_list[company.split(')')[1].strip()] = original_company
    elif company[-1] == ')':
      original_company = company
      company_list[company.split('(')[0].strip()] = original_company
    elif company[-1] == '㈜':
      original_company = company
      company_list[company[:-1].strip()] = original_company
    elif company[0] == '㈜':
      original_company = company
      company_list[company[1:].strip()] = original_company
    else:
      company_list[company] = company
  return company_list

def rename_files(directory, name_dict):
    for filename in os.listdir(directory):
        company_name = filename.split('_')[0]
        company_num = filename.split('_')[1].split('.')[0]
        if company_name in name_dict:
            os.rename(os.path.join(directory, filename), os.path.join(directory, name_dict[company_name] + '_' + company_num + '.csv'))

def save_dict_to_file(dict_obj, file_name):
    with open(file_name, 'w') as file:
        json.dump(dict_obj, file)

def load_dict_from_file(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def main():
  name_dict = load_dict_from_file("company_in_stock.json")
  rename_files("original_csv/stock/", name_dict)

if __name__ == '__main__':
   main()