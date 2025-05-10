from shares.middlewares.service_options_handler import OptionHandler
from shares.modules.log import Log
from shares.modules.minio import MinioModule
from shares.modules.upbit import Upbit
from shares.modules.tensorflow_module import TensorflowModule
from shares.modules.sklearn_module import SklearnModule
from shares.functions.common_function import map_interval_to_interval_min
from shares.decorations.try_again import try_again
from shares.dao.ai_back_test_result_dao import AiBackTestResultDao

from scheduler.core.cv_ai_back_tester_s1_gen01_core import CvAiBackTesterS1Gen01Core
from scheduler.core.cv_data_collector_s1_gen01_core import CvDataCollectorS1Gen01Core

from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

import pandas as pd
import datetime
import time
import random

import os
import inspect


class CvAiBackTesterS1Gen01(OptionHandler):
    """
    Service group : AiTrainer
    Service no : 1
    Generation : 01 
    Product Name : Lab Bee
    
    Role : 
    1. KRW-BTC 예측 모델 생성
    """
    slack_post_prefix = ":bee: Lab Bee."
    
    def __init__(self, seq):
        
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.minio = MinioModule()
        self.upbit = Upbit()
        self.tensorflow_module = TensorflowModule()
        self.sklearn_module = SklearnModule()
        self.ai_back_test_result_dao = AiBackTestResultDao()
        
        self.seq = seq
         
        # service attrs : TODO auto gen by db 
        self.model_path_list = [
            'models/2025/05/07/KRW-BTC_by_ontime_change_after_15min_20250507_173104166362.h5', 
            'models/2025/05/07/KRW-BTC_by_ontime_change_after_30min_20250507_174214634777.h5', 
            'models/2025/05/07/KRW-BTC_by_ontime_change_after_1hour_20250507_175810798721.h5', 
            'models/2025/05/07/KRW-BTC_by_ontime_change_after_4hour_20250507_180317398963.h5', 
            'models/2025/05/07/KRW-BTC_by_ontime_change_after_12hour_20250507_180917352605.h5', 
            'models/2025/05/07/KRW-BTC_by_ontime_change_after_1day_20250507_181317953458.h5', 
            'models/2025/05/07/KRW-BTC_by_prev_change_after_15min_20250507_181848993081.h5', 
            'models/2025/05/07/KRW-BTC_by_prev_change_after_30min_20250507_182416527925.h5', 
            'models/2025/05/07/KRW-BTC_by_prev_change_after_1hour_20250507_183022829968.h5', 
            'models/2025/05/07/KRW-BTC_by_prev_change_after_4hour_20250507_183806032448.h5', 
            'models/2025/05/07/KRW-BTC_by_prev_change_after_12hour_20250507_184153850112.h5', 
            'models/2025/05/07/KRW-BTC_by_prev_change_after_1day_20250507_184541721808.h5'
        ]
        self.time_steps = 40
        self.col_f = ['timestamp', 'weekday',
        'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'VOLUME_MA5', 'VOLUME_MA20',
        'VOLUME_RATIO', 'OBV', 'VWAP', 'VOLUME_VOLATILITY', 'VOLUME_SPIKE',
        'RSI', 'MACD', 'MACD_SIGNAL', 'BOLLINGER_PARTITION'
        ]
        self.init_options(seq)
        
    """
    regist scheduler
    """     
    def regist(self):
        
        try:
            
            # --- 정각, 15분, 30분, 45분마다 실행하도록 조정 
            self.wait_until_next_15min()
            
            # --- 스케쥴러 등록
            for model_path in self.model_path_list:
                self.regist_scheduler(
                    ticker="KRW-BTC", 
                    model_path=model_path, 
                    interval=self.get_interval_by_model_path(model_path), 
                    interval_prev=self.get_interval_prev_by_model_path(model_path),
                    is_by_prev=self.get_is_by_prev_by_model_path(model_path)
                )
                
            # 메인 스레드는 계속 살아있어야 함
            while True:
                time.sleep(1)

        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")

    def wait_until_next_15min(self):
        
        now = datetime.datetime.now()
        next_minute = (now.minute // 15 + 1) * 15
        if next_minute == 60:
            next_time = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
            
        else:
            next_time = now.replace(minute=next_minute, second=0, microsecond=0)
            
        wait_seconds = (next_time - now).total_seconds()
        time.sleep(wait_seconds)       
        
    def regist_scheduler(self, ticker, model_path, interval, interval_prev, is_by_prev):

        executors = {
            'default': ThreadPoolExecutor(20),  # 최대 20개 스레드
        }
        # scheduler = BlockingScheduler(executors=executors)
        scheduler = BackgroundScheduler(executors=executors)
        
        if "min_" in model_path:
            scheduler.add_job(self.back_test_model, 'interval', minutes=map_interval_to_interval_min(interval), args=[ticker, model_path, interval, interval_prev, is_by_prev], max_instances=2, next_run_time=datetime.datetime.now()+datetime.timedelta(seconds=1))
            
        elif "hour_" in model_path:
            scheduler.add_job(self.back_test_model, 'interval', hours=map_interval_to_interval_min(interval)/60, args=[ticker, model_path, interval, interval_prev, is_by_prev], max_instances=2, next_run_time=datetime.datetime.now()+datetime.timedelta(seconds=2))
            
        elif "day_" in model_path:
            scheduler.add_job(self.back_test_model, 'interval', days=map_interval_to_interval_min(interval)/60/24, args=[ticker, model_path, interval, interval_prev, is_by_prev], max_instances=2, next_run_time=datetime.datetime.now()+datetime.timedelta(seconds=3))
            
        scheduler.start()
    
    def get_is_by_prev_by_model_path(self, model_path):
        
        # is_by_prev를 모델 경로를 통해 설정
        if "by_ontime" in model_path: is_by_prev = False
        else: is_by_prev = True
        
        return is_by_prev
        
    def get_interval_by_model_path(self, model_path):
        
        # interval를 모델 경로를 통해 설정
        interval = None
        if "15min_" in model_path: interval = "minute15"
        elif "30min_" in model_path: interval = "minute30"
        elif "1hour_" in model_path: interval = "hour1"
        elif "4hour_" in model_path: interval = "hour4"
        elif "12hour_" in model_path: interval = "hour12"
        elif "1day_" in model_path: interval = "day"
        
        return interval
        
    def get_interval_prev_by_model_path(self, model_path):
        
        # interval_prev를 모델 경로를 통해 설정
        interval_prev = None
        if "by_prev" in model_path:
            if "15min_" in model_path: interval_prev = None
            elif "30min_" in model_path: interval_prev = "minute15"
            elif "1hour_" in model_path: interval_prev = "minute30"
            elif "4hour_" in model_path: interval_prev = "hour1"
            elif "12hour_" in model_path: interval_prev = "hour4"
            elif "1day_" in model_path: interval_prev = "hour12"
        
        return interval_prev
    
    """
    biz
    """
    def back_test_model(self, ticker, model_path, interval, interval_prev=None, is_by_prev=False):
            
        # --- 백테스팅 시작 시간
        back_test_start_dt = datetime.datetime.now()
        self.log.info(f'back_test_start_dt : {back_test_start_dt}')
    
        # --- 예측 데이터 조회
        df = self.get_target_prediction_data(ticker)
        
        # --- 백테스팅 요청
        cv_ai_back_tester_s1_gen01_core = CvAiBackTesterS1Gen01Core(self.log, self.seq)
        cv_ai_back_tester_s1_gen01_core.back_test_model(df, ticker, model_path, interval, interval_prev, is_by_prev, back_test_start_dt)
    
    @try_again(num=10)
    def get_target_prediction_data(self, ticker):
        
        # 동시 호출로 인한 제한 완화 
        delay = random.uniform(0.1, 1.1)  
        time.sleep(delay)

        now = datetime.datetime.now()
        datetime_list = [now - datetime.timedelta(minutes=5 * i) for i in range(self.time_steps)]
        datetime_str_list = [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in datetime_list]
        
        collected_data_f_list = []
        for datetime_str in datetime_str_list:
            cv_auto_trader_s2_gen01_core = CvDataCollectorS1Gen01Core(self.log)
            cv_auto_trader_s2_gen01_core.init_upbit_ticker(ticker)
            collected_data_f = cv_auto_trader_s2_gen01_core.set_features(datetime_str)
            
            collected_data_f_list.append(collected_data_f)
        
        df = pd.DataFrame(collected_data_f_list, columns=self.col_f)
        
        return df