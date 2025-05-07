from shares.middlewares.service_options_handler import OptionHandler
from shares.modules.log import Log
from shares.modules.minio import MinioModule
from shares.modules.upbit import Upbit
from shares.modules.tensorflow_module import TensorflowModule
from shares.modules.sklearn_module import SklearnModule
from scheduler.core.cv_data_collector_s1_gen01_core import CvDataCollectorS1Gen01Core

from apscheduler.schedulers.blocking import BlockingScheduler
from tensorflow.keras.models import load_model

import numpy as np
import pandas as pd
import datetime
import time

import os
import inspect


class CvAiBackTesterS1Gen01(OptionHandler):
    """
    Service group : AiTrainer
    Service no : 1
    Generation : 01 
    Product Name : Scholar bee
    
    Role : 
    1. KRW-BTC 예측 모델 생성
    """
    slack_post_prefix = ":bee: Scholar Bee."
    
    def __init__(self, seq):
        
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.minio = MinioModule()
        self.upbit = Upbit()
        self.tensorflow_module = TensorflowModule()
        self.sklearn_module = SklearnModule()
         
        # service attrs : TODO auto gen by db 
        self.model_folder_path = "models/2025/04/28"
        self.model_path_list = [
            "models/2025/04/28/KRW-BTC_by_ontime_change_after_15min_20250428_175355291689.h5",
            "models/2025/04/28/KRW-BTC_by_ontime_change_after_30min_20250428_181140369661.h5",
            "models/2025/04/28/KRW-BTC_by_ontime_change_after_1hour_20250428_182843866979.h5",
            "models/2025/04/28/KRW-BTC_by_ontime_change_after_4hour_20250428_183620206381.h5",
            "models/2025/04/28/KRW-BTC_by_ontime_change_after_12hour_20250428_184056863529.h5",
            "models/2025/04/28/KRW-BTC_by_ontime_change_after_1day_20250428_184436767909.h5",
            "models/2025/04/28/KRW-BTC_by_prev_change_after_15min_20250428_184820389211.h5",
            "models/2025/04/28/KRW-BTC_by_prev_change_after_30min_20250428_190159898172.h5",
            "models/2025/04/28/KRW-BTC_by_prev_change_after_1hour_20250428_191244513511.h5",
            "models/2025/04/28/KRW-BTC_by_prev_change_after_4hour_20250428_191722060110.h5",
            "models/2025/04/28/KRW-BTC_by_prev_change_after_12hour_20250428_192402067674.h5",
            "models/2025/04/28/KRW-BTC_by_prev_change_after_1day_20250428_192749191385.h5"
        ]
        self.time_steps = 40
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
            ticker="KRW-BTC"
            model_path="models/2025/05/07/KRW-BTC_by_ontime_change_after_15min_20250507_161809346519.h5"
            interval = 15 * 60
            self.back_test_model(ticker, model_path, interval)
    
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
        
        return 
        
        # 현재가 대비
        model=None
        interval = 15 * 60
        scheduler = BlockingScheduler()
        scheduler.add_job(self.back_test_model, 'interval', minutes=15, args=[model, interval])
        
        # model=None
        # interval = 30 * 60
        # scheduler = BlockingScheduler()
        # scheduler.add_job(self.back_test_model, 'interval', minutes=30, args=[model, interval])
        
        # model=None
        # interval = 1 * 60 * 60
        # scheduler = BlockingScheduler()
        # scheduler.add_job(self.back_test_model, 'interval', hours=1, args=[model, interval])
        
        # model=None
        # interval = 4 * 60 * 60
        # scheduler = BlockingScheduler()
        # scheduler.add_job(self.back_test_model, 'interval', hours=4, args=[model, interval])
        
        # model=None
        # interval = 12 * 60 * 60
        # scheduler = BlockingScheduler()
        # scheduler.add_job(self.back_test_model, 'interval', hours=12, args=[model, interval])
        
        # model=None
        # interval = 24 * 60 * 60
        # scheduler = BlockingScheduler()
        # scheduler.add_job(self.back_test_model, 'interval', days=1, args=[model, interval])
        
        # 이전가 대비
  
    
    def back_test_model(self, ticker, model_path, interval):
        
        # 입출력 칼럼
        col_f = ['tick_datetime', 'weekday',
        'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'VOLUME_MA5', 'VOLUME_MA20',
        'VOLUME_RATIO', 'OBV', 'VWAP', 'VOLUME_VOLATILITY', 'VOLUME_SPIKE',
        'RSI', 'MACD', 'MACD_SIGNAL', 'BOLLINGER_PARTITION'
        ]
        
        # 모델 다운
        local_path = self.minio.generate_local_path(file_exe="h5")
        self.minio.download_file(model_path, local_path)
        
        # 모델 로드 
        model = load_model(local_path)    
        
        # 예측 데이터 준비
        now = datetime.datetime.now()
        datetime_list = [now - datetime.timedelta(minutes=5 * i) for i in range(self.time_steps)]
        datetime_str_list = [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in datetime_list]
        
        collected_data_f_list = []
        for datetime_list_ in datetime_str_list:
            cv_auto_trader_s2_gen01_core = CvDataCollectorS1Gen01Core(self.log)
            
            collected_data_f, collected_data_t = cv_auto_trader_s2_gen01_core.collect_data(ticker, str(datetime_list_))
            collected_data_f_list.append(collected_data_f)
        
        df = pd.DataFrame(collected_data_f_list, columns=col_f)
        
        # 전처리
        data = df.copy()
        data['timestamp'] = pd.to_datetime(data['tick_datetime']).astype(int) / 10**9
        data.replace({'sideways': 1, 'up': 2, 'down': 0}, inplace=True)
        data.fillna(data.mean(), inplace=True)
        data.pop('tick_datetime')
        
        # 입력 칼럼
        col_f = ['timestamp', 'weekday',
        'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'VOLUME_MA5', 'VOLUME_MA20',
        'VOLUME_RATIO', 'OBV', 'VWAP', 'VOLUME_VOLATILITY', 'VOLUME_SPIKE',
        'RSI', 'MACD', 'MACD_SIGNAL', 'BOLLINGER_PARTITION'
        ]
        data[col_f] = self.sklearn_module.standardize_fit_data(data, col_f) 
        
        # 예측 전 현재가 조회
        self.upbit.set_ticker(ticker)
        current_price_before = self.upbit.get_current_price()
        
        # 예측
        prediction_softmax = self.tensorflow_module.predict_by_lstm_model(model, data[col_f], self.time_steps)
        predicted_label = np.argmax(prediction_softmax, axis=1)
        prediction = int(predicted_label[0])
        
        # 모델 파기
        del model
        
        # interval만큼 대기 
        time.sleep(interval)
        
        # 예측 후 현재가 조회
        self.upbit.set_ticker(ticker)
        current_price_after = self.upbit.get_current_price()
        
        # --- 상승/하락여부 예측과 실제 결과 비교 
        if interval < 60 * 60: 
            percentage_standard = 0.5
        elif interval < 60 * 60 * 4: 
            percentage_standard = 1
        elif interval < 60 * 60 * 24: 
            percentage_standard = 2

        percentage_change = ((current_price_after - current_price_before) / current_price_before) * 100
        
        real = None
        if percentage_change > percentage_standard:
            real = 2
        elif percentage_change < -percentage_standard:
            real  = 0
        else:
            real  = 1
            
        if real == prediction:
            self.log.info(f"예측 성공")
        
        else:
            self.log.info(f'예측 실패')
        
        # 모델 파일 삭제
        if os.path.exists(local_path):
            os.remove(local_path)
        
        
        
          
    
