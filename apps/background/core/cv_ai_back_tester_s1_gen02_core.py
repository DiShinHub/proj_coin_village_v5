
from shares.modules.minio import MinioModule
from shares.modules.upbit import Upbit
from shares.modules.tensorflow_module import TensorflowModule
from shares.modules.sklearn_module import SklearnModule
from shares.modules.dataframe import DataFrame
from shares.functions.common_function import map_interval_to_interval_min
from shares.decorations.try_again import try_again
from shares.dao.ai_back_test_result_dao import AiBackTestResultDao

from tensorflow.keras.models import load_model

import numpy as np
import pandas as pd
import datetime
import time
import json

import os
import inspect


class CvAiBackTesterS1Gen02Core():
    slack_post_prefix = ":bee:"
        
    
    def __init__(self, log, seq):
        
        self.log = log
        self.minio = MinioModule()
        self.upbit = Upbit()
        self.tensorflow_module = TensorflowModule()
        self.sklearn_module = SklearnModule()
        self.dataframe = DataFrame()
        self.ai_back_test_result_dao = AiBackTestResultDao()
        
        self.seq = seq
        
    def set_feature(self, col_f):
        self.col_f = col_f
        return self.col_f
        
    def set_hyper_parameters(self, time_steps):
        self.time_steps = time_steps  # 시퀀스 길이 설정
        
    """
    biz
    """
    def back_test_model(self, df, ticker, model_path, interval, interval_prev=None, is_by_prev=False, back_test_start_dt=datetime.datetime.now()):
        
        local_path = self.minio.generate_local_path(file_exe="h5")
        self.upbit.set_ticker(ticker)
        
        try:
            interval_min = map_interval_to_interval_min(interval)
            interval_prev_min = map_interval_to_interval_min(interval_prev)
            
            self.log.info(f'model load start : {datetime.datetime.now()}')
            
            # --- 모델 셋팅 
            self.minio.download_file(model_path, local_path)
            model = load_model(local_path)    
            
            self.log.info(f'model load end : {datetime.datetime.now()}')
            
            # --- 데이터 전처리
            data = self.pre_processing_data(df)
            
            # --- 예측 전 현재가 
            current_price_before = self.get_current_price()
            
            self.log.info(f'model predict start : {datetime.datetime.now()}')
            
            # --- 예측
            up_down_side_predicted = self.execute_prediction(model, data)
            
            self.log.info(f'model predict end : {datetime.datetime.now()}')
            
            # --- 모델 파기 후 대기
            del model 
            
            # 대기할 시간 계산 (데이터 준비과정을 포함하여 interval_min만큼 대기하도록 조정)
            elapsed = (datetime.datetime.now() - back_test_start_dt).total_seconds()
            wait_time = max(interval_min * 60 - elapsed, 0)
            
            # 대기 
            time.sleep(wait_time)
            
            # --- 피대상 가격 셋팅
            target_price = None 
            
            # case 1 : 이전가 기준, 예측 전 가격을 피대상자로 
            if is_by_prev == True:
                if interval_prev_min:
                    n_minutes_ago = (datetime.datetime.now() - datetime.timedelta(minutes=interval_prev_min)).strftime('%Y-%m-%d %H:%M:%S')
                    target_price = self.get_target_price(interval_prev, n_minutes_ago)
                    #target_price = self.upbit.get_target_date_price(interval=interval_prev, date=n_minutes_ago)
                
                else:
                    target_price = current_price_before
                    
            # case 2 : 정시간 기준, 예측 전 가격을 피대상자로 
            else:
                target_price = current_price_before
                
            # --- 예측 후 현재가 조회
            current_price = self.get_current_price()
            
            # --- 실제 상승,하락,횡보여부 조회
            up_down_side_real = self.decide_up_down_side(interval_min, current_price, target_price)
                
            # --- 상승/하락여부 예측과 실제 결과 비교 
            hit_yn = "N"
            if up_down_side_real == up_down_side_predicted:
                hit_yn = "Y"
                
            # --- 백테스팅 종료 시간
            back_test_end_dt = datetime.datetime.now()
            
            # --- 결과 저장
            result_row = json.dumps({
                "back_test_start_dt" : str(back_test_start_dt),
                "back_test_end_dt" : str(back_test_end_dt),
                "current_price" : current_price,
                "target_price" : target_price,
                "up_down_side_predicted" : up_down_side_predicted,
                "up_down_side_real" : up_down_side_real,
                "interval" : interval,
                "is_by_prev" : is_by_prev,
            })
            self.ai_back_test_result_dao.insert_ai_back_test_result(
                ticker=ticker,
                model_path=model_path,
                result_row=result_row,
                hit_yn=hit_yn,
                runnable_services_seq=self.seq,
                reg_member_seq=0,
            )
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
        
        finally:
            # 모델 파일 삭제
            if os.path.exists(local_path):
                os.remove(local_path)

    """
    subs
    """
    def pre_processing_data(self, df):

        data = df.copy()
        data = self.dataframe.convert_numeric_columns(data)
        data.fillna(data.mean(), inplace=True)
        data = self.sklearn_module.standardize_fit_data(data, self.col_f)
        
        return data

    def execute_prediction(self, model, data):
        
        prediction_softmax = self.tensorflow_module.predict_by_lstm_model(model, data, self.time_steps)
        predicted_label = np.argmax(prediction_softmax, axis=1)
        prediction = int(predicted_label[0])
        
        return prediction
    
    def decide_up_down_side(self, interval_min, current_price, target_price):
        
        threshold=None
        if interval_min <= 60: 
            threshold = 0.5
        elif interval_min <= 60 * 4: 
            threshold = 1
        elif interval_min <= 60 * 24: 
            threshold = 2
            
        if threshold == None:
            raise f"no threshold for {interval_min}, {current_price}, {target_price}"

        percentage_change = ((current_price - target_price) / target_price) * 100
        
        real = None
        if percentage_change > threshold:
            real = 2
        elif percentage_change < -threshold:
            real  = 0
        else:
            real  = 1
        
        return real
    
    @try_again(num=10)
    def get_current_price(self):
        return self.upbit.get_current_price()
    
    @try_again(num=10)
    def get_target_price(self, interval_prev, n_minutes_ago):
        return self.upbit.get_target_date_price(interval=interval_prev, date=n_minutes_ago)