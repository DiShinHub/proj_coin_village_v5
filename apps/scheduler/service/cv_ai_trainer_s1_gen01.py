from shares.middlewares.service_options_handler import OptionHandler
from scheduler.dao.upbit_transaction_dao import UpbitTransactionDao
from shares.modules.log import Log
from shares.functions.common_function import get_years_between_str, split_date_range_by_year, generate_micro_date

from scheduler.core.cv_ai_trainer_s1_gen01_core import CvAiTrainerS1Gen01Core

from apscheduler.schedulers.blocking import BlockingScheduler

import numpy as np
import pandas as pd
import datetime

import os
import inspect


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
        self.upbit_transaction_dao = UpbitTransactionDao()
        self.cv_ai_trainer_s1_gen01_core = CvAiTrainerS1Gen01Core(self.log)
         
        # service attrs
        self.ticker_list = None
        self.dataset_load_term = None
        self.time_steps = None  
        self.batch_size = None
        self.epochs = None
        self.early_stop = None
         
        self.init_options(seq)
        
    def regist(self):
        
        # TEST Block
        # scheduler = BlockingScheduler()
        # scheduler.add_job(self.run, 'cron', hour=self.scheduler_start_hour, minute=self.scheduler_start_min)
        # scheduler.start()
        # self.log.info(f"스케쥴러는 매일 {self.ticker_list}를 대상으로 {self.dataset_generate_term}일의 데이터를 수집하며, {self.scheduler_start_hour}시 {self.scheduler_start_min}분에 실행됩니다.")
        
        # TEST
        self.run()
        
    def run(self):
        
        try:
            # set model folder 
            model_folder_path = self.cv_ai_trainer_s1_gen01_core.set_model_folder_path()
            
            # loop - generate models
            for ticker in self.ticker_list:
                df = self.get_dataframe(ticker)
                model_path_list = self.generate_model(ticker, df)
            
            # TODO regist back tester or execute
            self.log.info(f"model_folder_path : {model_folder_path}")
            self.log.info(f"model_path_list : {model_path_list}")
    
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
        df['tick_datetime_'] = df['tick_datetime_'].dt.tz_localize(None)
        
        return df 
    
    def generate_model(self, ticker, df):
        
        # option 
        self.cv_ai_trainer_s1_gen01_core.set_hyper_parameters(
            time_steps=self.time_steps,
            batch_size=self.batch_size,
            epochs=self.epochs,
            early_stop=self.early_stop
        )
        
        # gen
        model_path_list = self.cv_ai_trainer_s1_gen01_core.generate_model(
            df=df,
            ticker=ticker
        )
        return model_path_list