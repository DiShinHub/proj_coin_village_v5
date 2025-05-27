from shares.middlewares.service_options_handler import OptionHandler
from shares.middlewares.service_model_config_handler import ModelConfigHandler
from shares.modules.log import Log
from shares.modules.redis import Redis
from shares.dao.runnable_services_dao import runnableServicesDao
from shares.dao.upbit_transaction_dao import UpbitTransactionDao

from shares.functions.common_function import get_years_between_str, split_date_range_by_year

import pandas as pd
import datetime
import inspect
import os

class CvSystemS1Gen01(ModelConfigHandler, OptionHandler):
    """
    Service group : System
    Service no : 2
    Generation : 01 
    Product Name : Excel Maker
    
    Role : 
    1. make excel from transaction table
    2. upload to minio
    """
    
    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.seq = seq
        
        self.redis = Redis()
        self.runnable_services_dao = runnableServicesDao()
        self.upbit_transaction_dao = UpbitTransactionDao()
         
        # 옵션 오토 로드
        self.start_date = None
        self.dataset_load_term = None
        self.dataset_table_prefix = None
        self.model_config_path = None
        self.load_options(seq)
        
        # 모델 구성 로드
        super().__init__()
        self.load_model_config(self.model_config_path)

    def run(self):
        
        try:
            self.log.info("엑셀을 만듭니다.")
            
            # 데이터 조회
            df = self.get_dataframe()
            
            # 데이터 전처리
            df = self.preprocess_df_by_model_config(df)
            
            # local_path = "./my_data.xlsx"
            # minio_path = "/datasets/2025/05/23/2025-05-23 14:30:00_2.xlsx"
            # df['tick_datetime'] = df['tick_datetime'].dt.tz_localize(None)
                
            # # Excel 파일로 저장
            # df.to_excel(local_path, index=False)  # 현재 작업 디렉토리에 저장

            # self.minio.upload_file(minio_path, local_path)
            # os.remove(local_path)
            
            # 스스로를 종료
            params = {
                "use_yn" : "N"
            }
            self.runnable_services_dao.update_runnable_services(
                params=params,
                seq=self.seq
            )
            
            self.log.info("엑셀을 만들었습니다.")
    
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
        
    def get_dataframe(self):
        
        # --- TODO
        self.start_date = "2024-11-11 00:00:00"
        self.dataset_load_term = 0
        self.dataset_table_prefix = ""
        
        # --- 데이터 셋팅
        n_days_ago = str(datetime.datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=self.dataset_load_term))[0:19]   
        self.year_list = get_years_between_str(n_days_ago, self.start_date )  # 대상연도
        self.splited_year_dict = split_date_range_by_year(n_days_ago, self.start_date ) 
        
        # --- 데이터 조회
        upbit_transactions_list = []
        for year in self.year_list:
            
            table_name = f"{self.dataset_table_prefix}_{year}"
            
            splited_year = self.splited_year_dict[year]
            start = splited_year[0]
            end = splited_year[1]
            
            upbit_transactions = self.upbit_transaction_dao.get_upbit_transactions_between(table_name, self.ticker, start, end)
            upbit_transactions_list += upbit_transactions
        
        if len(upbit_transactions_list) == 0:
            self.log.info(f'no dataset found')
            raise 
        
        df = pd.DataFrame(upbit_transactions_list)
        return df 