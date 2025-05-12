from shares.middlewares.service_options_handler import OptionHandler
from shares.modules.log import Log
from shares.modules.redis import r as redis_single
from shares.dao.runnable_services_dao import runnableServicesDao
from shares.functions.common_function import get_years_between_str, split_date_range_by_year

from scheduler.dao.upbit_transaction_dao import UpbitTransactionDao
from scheduler.core.cv_ai_trainer_s1_gen01_core import CvAiTrainerS1Gen01Core

from apscheduler.schedulers.blocking import BlockingScheduler

import pandas as pd
import datetime

import os
import inspect
import time

class CvAiTrainerS1Gen01(OptionHandler):
    """
    Service group : AiTrainer
    Service no : 1
    Generation : 01 
    Product Name : King bee
    
    Role : 
    1. KRW-BTC 예측 모델 생성
    """
    slack_post_prefix = ":bee: King Bee."
    
    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.redis = redis_single
        self.runnable_services_dao = runnableServicesDao()
        self.upbit_transaction_dao = UpbitTransactionDao()
        self.cv_ai_trainer_s1_gen01_core = CvAiTrainerS1Gen01Core(self.log)
         
        # service attrs
        self.scheduler_start_day = None
        self.scheduler_start_hour = None
        self.scheduler_start_min = None
        self.auto_back_test = None
        self.auto_back_test_seq = None
        
        self.ticker_list = None
        self.dataset_load_term = None
        
        self.time_steps = None  
        self.batch_size = None
        self.epochs = None
        self.early_stop = None
  
        self.col_f = None
        self.col_t = None
         
        self.init_options(seq)
        self.seq = seq
        self.model_path_list = []
        
    def regist(self):
        
        self.redis.save_msg_on_Q(f"{self.slack_post_prefix} 스케쥴러 등록. {self.ticker_list}를 대상으로 {self.dataset_load_term}일의 데이터로 학습하며, 매월 {self.scheduler_start_day}일, {self.scheduler_start_hour}시 {self.scheduler_start_min}분에 실행.")
        scheduler = BlockingScheduler()
        scheduler.add_job(self.run, 'cron', day=self.scheduler_start_day, hour=self.scheduler_start_hour, minute=self.scheduler_start_min)
        scheduler.start()
        
    def run(self):
        
        try:
            # loop - models 생성
            for ticker in self.ticker_list:
                df = self.get_dataframe(ticker)
                self.model_path_list = self.model_path_list + self.generate_model(ticker, df)
            
            # 자동 백테스팅
            if self.auto_back_test == "Y":
                self.execute_back_test()
        
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            
    def get_dataframe(self, ticker):
        
        # --- 데이터 셋팅
        now_date = str(datetime.datetime.now())[0:19]
        n_days_ago = str(datetime.datetime.now() - datetime.timedelta(days=self.dataset_load_term))[0:19]   
        self.year_list = get_years_between_str(n_days_ago, now_date)  # 대상연도
        self.splited_year_dict = split_date_range_by_year(n_days_ago, now_date) 
        
        # --- 연단위 테이블 생성 (있으면 pass)
        self.upbit_transaction_dao.create_yearly_table(self.year_list)
    
        # --- 데이터 조회
        upbit_transactions_list = []
        for year in self.year_list:
            
            table_name_f, table_name_t = self.upbit_transaction_dao.get_yearly_table_name(year)
            splited_year = self.splited_year_dict[year]
            start = splited_year[0]
            end = splited_year[1]
            
            upbit_transactions = self.upbit_transaction_dao.get_upbit_transactions_between(table_name_f, table_name_t, ticker, start, end)
            upbit_transactions_list += upbit_transactions
        
        # --- 데이터프레임으로 변환
        df = pd.DataFrame(upbit_transactions_list)
        
        return df 
    
    def generate_model(self, ticker, df):
        
        # 옵션 셋팅
        self.cv_ai_trainer_s1_gen01_core.set_feature(self.col_f)
        self.cv_ai_trainer_s1_gen01_core.set_target(self.col_t)
        self.cv_ai_trainer_s1_gen01_core.set_hyper_parameters(
            time_steps=self.time_steps,
            batch_size=self.batch_size,
            epochs=self.epochs,
            early_stop=self.early_stop
        )
        self.cv_ai_trainer_s1_gen01_core.set_model_folder_path()
        
        # 모델 생성
        model_path_list = self.cv_ai_trainer_s1_gen01_core.generate_model(
            ticker=ticker,
            df=df
        )
        return model_path_list

    def execute_back_test(self):
        
        #  백테스팅 옵션 생성
        self.runnable_services_dao.upsert_runnable_service_options(option_key="ticker_list", option_val=str(self.ticker_list).replace("'", "\""), runnable_service_seq=self.auto_back_test_seq)
        self.runnable_services_dao.upsert_runnable_service_options(option_key="model_path_list", option_val=str(self.model_path_list).replace("'", "\""), runnable_service_seq=self.auto_back_test_seq)
        self.runnable_services_dao.upsert_runnable_service_options(option_key="col_f", option_val=str(self.col_f).replace("'", "\""), runnable_service_seq=self.auto_back_test_seq)
        self.runnable_services_dao.upsert_runnable_service_options(option_key="time_steps", option_val=self.time_steps, runnable_service_seq=self.auto_back_test_seq)
        
        # 백테스팅 재시작
        params = {"use_yn" : "N"}
        self.runnable_services_dao.update_runnable_services(params=params, seq=self.auto_back_test_seq)
        time.sleep(5)
        params = {"use_yn" : "Y"}
        self.runnable_services_dao.update_runnable_services(params=params, seq=self.auto_back_test_seq)