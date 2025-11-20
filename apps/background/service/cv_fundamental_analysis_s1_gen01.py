from shares.middlewares.service_options_handler import OptionHandler
from shares.modules.log import Log
from shares.modules.redis import r as redis_single
from shares.dao.trade_transaction_dao import TradeTransactionDao

from apscheduler.schedulers.blocking import BlockingScheduler

import json
import os
import inspect

class CvFundamentalAalysisS1Gen01(OptionHandler):
    """
    Service group : FundamentalAalysis
    Service no : 1
    Generation : 01
    Product Name : 
    
    Role : 
    1. kis 거래 데이터 수집 
    2. kis 차트 데이터 수집 
    
    Desc : 
    
    
    """
    slack_post_prefix = ":bee:"
    
    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.redis = redis_single
        self.trade_transaction_dao = TradeTransactionDao()
        
        # service attrs
        self.scheduler_start_hour = None
        self.scheduler_start_min = None
        self.ticker_list = None
        self.dataset_generate_term = None
        self.dataset_table_prefix = None
        self.load_options(seq)
        
        # system attrs
        self.ticker = ""
        self.datetime_list = []
        self.year_list = []
        
    def regist(self):
        
        redis_single.save_msg_on_Q(f"{self.slack_post_prefix} 스케쥴러 등록. {self.ticker_list}를 대상으로 {self.dataset_generate_term}일의 데이터를 수집하며, 매일 {self.scheduler_start_hour}시 {self.scheduler_start_min}분에 실행.")
        scheduler = BlockingScheduler()
        scheduler.add_job(self.run, 'cron', hour=self.scheduler_start_hour, minute=self.scheduler_start_min)
        scheduler.start()
        
    def run(self):
        
        try:
            # ---데이터 셋팅
            self.datetime_list = generate_datetimes_by_min(terms=self.dataset_generate_term, interval=5, n_days_ago=7) # 수집 구간 datetime 리스트 생성
            self.year_list = get_years_between_str(self.datetime_list[0], self.datetime_list[-1])  # 대상연도
            
            # --- 연단위 테이블 생성 
            for year in self.year_list:
                table_name = f"{self.dataset_table_prefix}_{year}"
                if self.trade_transaction_dao.is_exist_table(table_name) == False:
                    self.trade_transaction_dao.create_transaction_table(table_name=table_name)  
                    self.trade_transaction_dao.create_index(index_cols=["ticker", "tick_datetime"], table_name=table_name)  
                    
            # --- 티커별 데이터 수집
            for ticker in self.ticker_list:
                self.ticker = ticker
                self.redis.save_msg_on_Q(f"{self.slack_post_prefix} : {self.ticker} 의 데이터를 수집합니다.")
                
                # -- 수집구간에 해당하는 데이터 중 수집되지 않은 구간 조회
                collectable_datetime_list = self.get_collectable_datetime_list()
                
                # -- 데이터 수집
                self.collect_kis_transaction(collectable_datetime_list)
                
                self.redis.save_msg_on_Q(f"{self.slack_post_prefix} : {self.ticker} 의 데이터를 수집을 완료하였습니다.")
                
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
    