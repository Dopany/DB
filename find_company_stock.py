import os
import csv
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote

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
  company_in_stock = []
  for company in extract_company_name():
    encode_str = quote(company, encoding='euc-kr')
    response = requests.get(root_url + encode_str, headers={'User-agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    if soup.select('.result_area > p > em') == []:
      company_in_stock.append(company)
  return company_in_stock

def extract_company_name():
  company_list = []
  for company in find_unmatched_company():
    if company[0] == '(':
      company_list.append(company.split(')')[1].strip())
    elif company[-1] == ')':
      company_list.append(company.split('(')[0].strip())
    elif company[-1] == '㈜':
      company_list.append(company[:-1].strip())
    elif company[0] == '㈜':
      company_list.append(company[1:].strip())
    else:
      company_list.append(company)
  return company_list

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for row in data:
            writer.writerow(row)

def main():
  find_company_in_market()

if __name__ == '__main__':
   main()