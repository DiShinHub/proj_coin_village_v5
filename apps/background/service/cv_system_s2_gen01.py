
from shares.middlewares.service_options_handler import OptionHandler
from shares.middlewares.service_auto_ml_handler import AutoMlHandler
from shares.modules.log import Log
from shares.modules.redis import r as redis_single
from shares.modules.minio import MinioModule
from shares.modules.tensorflow_module import TensorflowModule
from shares.modules.sklearn_module import SklearnModule
from shares.dao.runnable_services_dao import runnableServicesDao
from shares.dao.upbit_transaction_dao import UpbitTransactionDao
from shares.dao.result_dao import ResultDao
from shares.functions.common_function import get_years_between_str, split_date_range_by_year
from shares.functions.common_function import generate_micro_date

import pandas as pd
import datetime
import time

import os
import inspect

class CvSystemS2Gen01(AutoMlHandler, OptionHandler):
    """
    Service group : DfGenerator
    Service no : 2
    Generation : 01
    Product Name : 
    
    Role : 
    1. 
    """
    slack_post_prefix = ":bee:"
    
    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.redis = redis_single
        self.minio = MinioModule()
        self.tensorflow_module = TensorflowModule()
        self.sklearn_module = SklearnModule()
        self.runnable_services_dao = runnableServicesDao()
        self.upbit_transaction_dao = UpbitTransactionDao()
        self.result_dao = ResultDao()
         
        # 옵션 오토 로드
        self.ticker = None
        self.auto_ml_path = None
        self.dataset_load_term = None
        self.dataset_table_prefix = None
        self.load_options(seq)
        
        self.seq = seq
        self.local_path = ""
        self.minio_path = ""
        self.train_result = {}
        
    def run(self):
        
        try:
            self.log.info("엑셀을 만듭니다.")
            
            # Excel 업로드
            self.df_local_path = self.minio.generate_local_path("xlsx")
            self.df_minio_path = self.minio.generate_df_model_path(folder_path=self.minio.generate_df_folder_path(), file_name=f"{self.__class__.__name__}_{self.ticker}_{generate_micro_date()}", file_exe="xlsx")
            
            # --- df 조회
            df = self.get_dataframe()
            
            # auto ml
            self._initialize(df, self.auto_ml_path)
            self.load_auto_ml()
            self.apply_dervied_params()
            #self.apply_preprocess()
            df = self.get_df()
            
            # --- df 업로드
            df['tick_datetime'] = df['tick_datetime'].dt.tz_localize(None)
            self.upload_dataframe(df)
            
            self.log.info("엑셀을 만들었습니다.")
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
    
        finally:
            if os.path.exists(self.df_local_path):
                os.remove(self.df_local_path)
                
            # --- 서비스 오프
            params = {
                "activate_yn" : "N"
            }
            self.runnable_services_dao.update_runnable_services(
                params=params,
                seq=self.seq
            )
    
    def get_dataframe(self):
        
        try:
            # 변수 셋팅
            now_date = str(datetime.datetime.now())[0:19]
            n_days_ago = str(datetime.datetime.now() - datetime.timedelta(days=self.dataset_load_term))[0:19]   
            self.year_list = get_years_between_str(n_days_ago, now_date)  # 대상연도
            self.splited_year_dict = split_date_range_by_year(n_days_ago, now_date) 
            
            # 연단위 테이블 생성 (있으면 pass)
            self.upbit_transaction_dao.create_yearly_table(self.year_list)
        
            # 데이터 조회
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
            
            # 데이터프레임으로 변환
            df = pd.DataFrame(upbit_transactions_list)
            return df 
    
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise e 
        
    
    def upload_dataframe(self, df):
        
        try:
            df.to_excel(self.df_local_path, index=False)  # 현재 작업 디렉토리에 저장
            self.minio.upload_file(self.df_minio_path, self.df_local_path)
    
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise e 
        