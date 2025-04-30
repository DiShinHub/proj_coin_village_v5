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
        
        # 
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
        
    def run(self):
        
        
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
        col_f = ['timestamp', 'weekday',
        'open', 'high', 'low', 'close', 'volume', 'volume_ma5', 'volume_ma20',
        'volume_ratio', 'obv', 'vwap', 'volume_volatility', 'volume_spike',
        'rsi', 'macd', 'macd_signal', 'bollinger_partition'
        ]
        
        # 모델 다운
        local_path = self.minio.generate_local_path(file_exe="h5")
        self.minio.download_file(model_path, local_path)
        
        # 모델 로드 
        model = load_model(local_path)      
        
        # 예측 데이터 준비
        now = datetime.datetime.now()
        datetime_list = [now - datetime.timedelta(minutes=5 * i) for i in range(self.time_steps)]
        
        for datetime_list_ in datetime_list:
            cv_auto_trader_s2_gen01_core = CvDataCollectorS1Gen01Core()
            collected_data_f, collected_data_t = cv_auto_trader_s2_gen01_core.collect_data(ticker, datetime_list_)
        
        df = pd.DataFrame(collected_data_f, columns=col_f)
        
        # 전처리
        data = df.copy()
        data['timestamp'] = pd.to_datetime(data['tick_datetime']).astype(int) / 10**9
        data.replace({'sideways': 1, 'up': 2, 'down': 0}, inplace=True)
        data.fillna(data.mean(), inplace=True)
        
        data = self.sklearn_module.standardize_data(data, col_f)
        X = self.tensorflow_module.create_sequences(data[col_f].values, self.time_steps)
        
        # 예측 전 현재가 조회
        self.upbit.set_ticker(ticker)
        current_price = self.upbit.get_current_price()
        
        # 예측
        predicttion = self.tensorflow_module.predict_by_lstm_model(model, X)
        
        # softmax 확률을 라벨로 변환
        predicted_label = np.argmax(predicttion, axis=1)
        
        # 모델 파기
        del model
        
        # interval만큼 대기 
        time.sleep(interval)
        
        # 예측 후 현재가 조회
        self.upbit.set_ticker(ticker)
        current_price = self.upbit.get_current_price()
        
        # 상승/하락여부 예측과 실제 결과 비교 
        
        # 모델 파일 삭제
        if os.path.exists(local_path):
            os.remove(local_path)
        
        
        
          
    
