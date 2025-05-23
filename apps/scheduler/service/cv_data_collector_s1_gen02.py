from shares.middlewares.service_options_handler import OptionHandler
from shares.modules.log import Log
from shares.modules.redis import r as redis_single
from shares.dao.upbit_transaction_dao import UpbitTransactionDao
from shares.functions.common_function import get_years_between_str, generate_datetimes_by_min

from scheduler.core.cv_data_collector_s1_gen02_core import CvDataCollectorS1Gen02Core

from apscheduler.schedulers.blocking import BlockingScheduler

import json
import os
import inspect

class CvDataCollectorS1Gen02(OptionHandler):
    """
    Service group : DataCollector
    Service no : 1
    Generation : 02
    Product Name : Honey Bee
    
    Role : 
    1. 업비트 거래 데이터 수집 
    2. 업비트 차트 데이터 수집 
    """
    slack_post_prefix = ":bee: Honey Bee. "
    
    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.redis = redis_single
        self.upbit_transaction_dao = UpbitTransactionDao()
        self.cv_auto_trader_s2_gen01_core = CvDataCollectorS1Gen02Core(self.log)
        
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
                if self.upbit_transaction_dao.is_exist_table(table_name) == False:
                    self.upbit_transaction_dao.create_upbit_transaction_table(table_name=table_name)  
                    self.upbit_transaction_dao.create_index(index_cols=["ticker", "tick_datetime"], table_name=table_name)  
                    
            # --- 티커별 데이터 수집
            for ticker in self.ticker_list:
                self.ticker = ticker
                self.redis.save_msg_on_Q(f"{self.slack_post_prefix} : {self.ticker} 의 데이터를 수집합니다.")
                
                # -- 수집구간에 해당하는 데이터 중 수집되지 않은 구간 조회
                collectable_datetime_list = self.get_collectable_datetime_list()
                
                # -- 데이터 수집
                self.collect_upbit_transaction(collectable_datetime_list)
                
                self.redis.save_msg_on_Q(f"{self.slack_post_prefix} : {self.ticker} 의 데이터를 수집을 완료하였습니다.")
                
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
    
    """
    pre processing
    """     
    def get_collectable_datetime_list(self):
        """
        def description : 수집해야할 대상 데이터 추출
        """
        
        # --- DB에서 대상 기간 내 이미 수집 된 데이터의 datetime 리스트  
        already_collected_list = self.get_already_collected_datetime_list()
            
        # --- 수집 대상 외 datetime 리스트 파싱
        collectable_datetime_list = self.parse_collectable_datetime_list(already_collected_list)
        return collectable_datetime_list
    
    def get_already_collected_datetime_list(self):
        """
        def description : 이미 수집 된 데이터의 datetime_list
        """
        
        already_collected_list = []
        for year in self.year_list:
            table_name = f"{self.dataset_table_prefix}_{year}"
            
            already_collected_list_obj = self.upbit_transaction_dao.get_upbit_transaction_with_tick_datetime_list(table_name, self.ticker, self.datetime_list)
            
            for tick_datetime_already in already_collected_list_obj:
                tick_datetime = str(tick_datetime_already["tick_datetime"])[0:19]
                already_collected_list.append(tick_datetime)
            
        return already_collected_list
        
    def parse_collectable_datetime_list(self, already_collected_list):
        """
        def description : 수집해야할 datetime을 분류
        """
        
        target_datetime_list = []
        for datetime_ in self.datetime_list:
            if datetime_ not in already_collected_list:
                target_datetime_list.append(datetime_)
        
        return target_datetime_list
           
    """
    biz
    """     
    def collect_upbit_transaction(self, collectable_datetime_list):
        """
        def description : 데이터 수집 후 DB 인서트
        """
        
        try:
            for tick_datetime in collectable_datetime_list:
                
                # 데이터 수집
                self.cv_auto_trader_s2_gen01_core.set_ticker(self.ticker)
                self.cv_auto_trader_s2_gen01_core.set_tick_datetime(tick_datetime)
                collected_data = self.cv_auto_trader_s2_gen01_core.collect_data()
                
                # 데이터 저장
                table_name = f"{self.dataset_table_prefix}_{tick_datetime[0:4]}"
                self.upbit_transaction_dao.insert_upbit_transaction(table_name, self.ticker, tick_datetime, json.dumps(collected_data))
        
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, ticker : {self.ticker} ,tick_datetime : {tick_datetime}, error : {str(e)}")