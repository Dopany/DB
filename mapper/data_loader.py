import pandas as pd
from datetime import datetime
from django.db import transaction
from app.models import Company, Industry, Domain, Etf, Job, Skill, Recruitment, Requirement, News, Stock, ProsReview, ConsReview, ProsWord, ConsWord

from utils.decorator import singleton

domain_list = {
    'domain_name': [
        '메타버스',
        'IT',
        '금융', 
        '바이오/헬스', 
        '게임', 
        'e커머스', 
        '방송/통신'
    ]
}

# 추가 예정
industry_list = {
    'industry_name': [
        'IT.정보통신업>게임.애니메이션', 
        '미디어.광고업', 
        '문화.예술.디자인업', 
        'Manufacturing', 
        'Retail'
    ]
}

# 추가 예정
job_list = {}

@singleton
class DataLoader:
    def load_domain_from_dataframe(self, domains_df):
        for _, row in domains_df.iterrows():
            Domain.objects.update_or_create(
                domain_name=row['domain_name']
            )

    def load_industry_from_dataframe(self, industries_df):
        try:
            for _, row in industries_df.iterrows():
                domain = Domain.objects.get(domain_name=row['domain_name'])
                Industry.objects.update_or_create(
                    industry_name=row['industry_name'],
                    defaults={
                        'domain': domain
                    }
                )
        except Domain.DoesNotExist:
            print(f"Domain not found for {row['domain_name']}, skipping industry {row['industry_name']}")
    
    def load_company_from_dataframe(self, companies_df):
        try:
            for _, row in companies_df.iterrows():
                industry = Industry.objects.get(industry_name=row['industry_name'])
                Company.objects.update_or_create(
                    company_name=row['company_name'],
                    defaults={
                        'company_size': row['company_size'],
                        'company_introduction': row['company_introduction'],
                        'industry': industry
                    }
                )
        except Industry.DoesNotExist:
            print(f"Industry not found for {row['industry_name']}, skipping company {row['company_name']}")

    # def load_news_from_dataframe(self, news_df):
    #     try:
    #         for _, row in news_df.iterrows():
    #             company = Company.objects.get(company_id=row['company_id'])
    #             News.objects.create(
    #                 news_title=row['news_title'],
    #                 news_text=row['news_text'],
    #                 company=company
    #             )
    #     except Company.DoesNotExist:
    #         print(f"Company not found for {row['company_name']}, skipping company {row['news_title']}")

    # def load_stock_from_dataframe(self, news_df):
    #         for _, row in stocks_df.iterrows():
    #             company = Company.objects.get(company_id=row['company_id'])
    #             Stock.objects.update_or_create(
    #                 transaction_date=pd.to_datetime(row['transaction_date']),
    #                 defaults={
    #                     'stock_id': row['stock_id'],
    #                     'created_at': pd.to_datetime(row['created_at']),
    #                     'updated_at': pd.to_datetime(row['updated_at']),
    #                     'closing_price': row['closing_price'],
    #                     'trading_volume': row['trading_volume'],
    #                     'change': row['change'],
    #                     'company': company
    #                 }
    #             )

            # Load other tables similarly...
            # For ProsWord, ConsWord, Etf, Domain, Job, Skill, Recruitment, Requirement, ProsReview, ConsReview

# 적재 순서 절대 유지_무결성 영향
def preload(companies_df):
    loader = DataLoader()
    with transaction.atomic():
        loader.load_domain_from_dataframe(pd.DataFrame(domain_list))
        loader.load_industry_from_dataframe(pd.DataFrame(industry_list))
        loader.load_company_from_dataframe(companies_df)

if __name__ == "__main__":
    preload()
