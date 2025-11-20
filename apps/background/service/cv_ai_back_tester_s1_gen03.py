from shares.middlewares.service_options_handler import OptionHandler
from shares.middlewares.service_auto_ml_handler import AutoMlHandler
from shares.modules.log import Log
from shares.modules.redis import r as redis_single
from shares.modules.minio import MinioModule
from shares.modules.upbit import Upbit
from shares.decorations.try_again import try_again
from shares.dao.result_dao import ResultDao

from tensorflow.keras.models import load_model

from scheduler.core.cv_data_collector_s1_gen02_core import CvDataCollectorS1Gen02Core

from apscheduler.schedulers.blocking import BlockingScheduler

import pandas as pd
import numpy as np
import datetime
import time
import random
import json

import os
import inspect


class CvAiBackTesterS1Gen03(AutoMlHandler, OptionHandler):
    """
    Service group : AiTrainer
    Service no : 1
    Generation : 02
    Product Name : Back Lab Bee
    
    Role : 
    1. KRW-BTC 예측 모델 백테스트
    """
    slack_post_prefix = ":bee:"
    
    def __init__(self, seq):
        
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.redis = redis_single
        self.minio = MinioModule()
        self.upbit = Upbit()
        # self.tensorflow_module = TensorflowModule()
        # self.sklearn_module = SklearnModule()
        self.result_dao = ResultDao()
        
        self.seq = seq
         
        # 옵션 오토 로드
        self.ticker = None
        self.model_path = None
        self.auto_ml_path = None
        self.load_options(seq)
        
    """
    regist scheduler
    """     
    def regist(self):
        
        try:
            # --- 정각에 실행하도록 조정 
            self.redis.save_msg_on_Q(f"{self.slack_post_prefix} 백테스팅 대기. {self.ticker}를 대상으로 정각에 맞춰 실행.")
            self.wait_until_next_noon()
        
            self.redis.save_msg_on_Q(f"{self.slack_post_prefix} 백테스팅 시작.")
            scheduler = BlockingScheduler()
            
            scheduler_interval = 30 
            scheduler_max_instances = int(1440/scheduler_interval) + 1000
            scheduler.add_job(self.run, 'interval', minutes=scheduler_interval, max_instances=scheduler_max_instances)
            scheduler.start()
            
            # executors = {
            #     'default': ThreadPoolExecutor(20),  # 최대 20개 스레드
            # }
            #scheduler = BackgroundScheduler(executors=executors)

        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")

    def wait_until_next_noon(self):
        
        now = datetime.datetime.now()
        next_minute = (now.minute // 60 + 1) * 60
        if next_minute == 60:
            next_time = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
            
        else:
            next_time = now.replace(minute=next_minute, second=0, microsecond=0)
            
        wait_seconds = (next_time - now).total_seconds()
        time.sleep(wait_seconds)      
        
    """
    biz
    """
    def run(self):
        
        model_info_list = []
        model_info_list.append({
                "model_path" : "models/2025/08/21/CvAiTrainerS1Gen02_KRW-BTC_20250821_131510950046.h5",
                "auto_ml_path" : "/apps/scheduler/auto_ml/experiments/cv_ai_trainer_s1_gen02/v7",
                "threshhold" : 0.1,
        })
        model_info_list.append({
                "model_path" : "models/2025/08/21/CvAiTrainerS1Gen02_KRW-BTC_20250821_133702093520.h5",
                "auto_ml_path" : "/apps/scheduler/auto_ml/experiments/cv_ai_trainer_s1_gen02/v7",
                "threshhold" : 0.2,
        })
        model_info_list.append({
                "model_path" : "models/2025/08/21/CvAiTrainerS1Gen02_KRW-BTC_20250821_142401953335.h5",
                "auto_ml_path" : "/apps/scheduler/auto_ml/experiments/cv_ai_trainer_s1_gen02/v7",
                "threshhold" : 0.3,
        })
        model_info_list.append({
                "model_path" : "models/2025/08/21/CvAiTrainerS1Gen02_KRW-BTC_20250821_145632413369.h5",
                "auto_ml_path" : "/apps/scheduler/auto_ml/experiments/cv_ai_trainer_s1_gen02/v7",
                "threshhold" : 0.4,
        })
        model_info_list.append({
                "model_path" : "models/2025/08/21/CvAiTrainerS1Gen02_KRW-BTC_20250821_152422651356.h5",
                "auto_ml_path" : "/apps/scheduler/auto_ml/experiments/cv_ai_trainer_s1_gen02/v7",
                "threshhold" : 0.5,
        })
        model_info_list.append({
                "model_path" : "models/2025/08/21/CvAiTrainerS1Gen02_KRW-BTC_20250821_160109788079.h5",
                "auto_ml_path" : "/apps/scheduler/auto_ml/experiments/cv_ai_trainer_s1_gen02/v7",
                "threshhold" : 0.6,
        })
        model_info_list.append({
                "model_path" : "models/2025/08/21/CvAiTrainerS1Gen02_KRW-BTC_20250821_162543953959.h5",
                "auto_ml_path" : "/apps/scheduler/auto_ml/experiments/cv_ai_trainer_s1_gen02/v7",
                "threshhold" : 0.7,
        })
        model_info_list.append({
                "model_path" : "models/2025/08/21/CvAiTrainerS1Gen02_KRW-BTC_20250821_165101953113.h5",
                "auto_ml_path" : "/apps/scheduler/auto_ml/experiments/cv_ai_trainer_s1_gen02/v7",
                "threshhold" : 0.8,
        })
        model_info_list.append({
                "model_path" : "models/2025/08/22/CvAiTrainerS1Gen02_KRW-BTC_20250822_091808190365.h5",
                "auto_ml_path" : "/apps/scheduler/auto_ml/experiments/cv_ai_trainer_s1_gen02/v7",
                "threshhold" : 1.0,
        })
        model_info_list.append({
                "model_path" : "models/2025/08/22/CvAiTrainerS1Gen02_KRW-BTC_20250822_093942377432.h5",
                "auto_ml_path" : "/apps/scheduler/auto_ml/experiments/cv_ai_trainer_s1_gen02/v7",
                "threshhold" : 2.0,
        })
        model_info_list.append({
                "model_path" : "models/2025/08/22/CvAiTrainerS1Gen02_KRW-BTC_20250822_100457990872.h5",
                "auto_ml_path" : "/apps/scheduler/auto_ml/experiments/cv_ai_trainer_s1_gen02/v7",
                "threshhold" : 3.0,
        })

        try:
            # --- 백테스팅 시작 시간
            back_test_start_dt = datetime.datetime.now()
            
            # --- 예측 전 현재가 
            current_price_before = self.get_current_price()
            
            # --- 예측 
            for i, model_info in enumerate(model_info_list):
                
                # 모델 파일 다운로드
                local_path = self.minio.generate_local_path(file_exe="h5")
                self.minio.download_file(model_info["model_path"], local_path)
                 
                # 모델 로드
                model = load_model(local_path)    
            
                # 예측에 쓰일 데이터 조회
                self._initialize(None, model_info["auto_ml_path"])
                
                self.load_auto_ml()
                self.hyperparameters = self.get_hyperparameters()
                df = self.get_data_for_prediction()
                
                # 예측 by auto ml
                self._initialize(df, self.auto_ml_path)
                prediction = self.execute_predict_by_auto_ml(model)
                
                model_info_list[i]["local_path"] = local_path
                model_info_list[i]["prediction"] = prediction
                
                # 모델 파기
                del model 
            
            # --- 대기 
            elapsed = (datetime.datetime.now() - back_test_start_dt).total_seconds()
            wait_time = max(24*60*60 - elapsed, 0) # 1days
            time.sleep(wait_time)   
            
            # --- 예측 후 현재가 조회
            current_price_after = self.get_current_price()
            
            # --- 실제 결과 비교 
            for i, model_info in enumerate(model_info_list):
                
                # 실제 결과
                change = (current_price_after - current_price_before) / current_price_before * 100
                
                if change > model_info["threshhold"]:
                    real = 2
                else:
                    real = 0

                # --- 상승/하락여부 예측과 실제 결과 비교 
                hit_yn = "N"
                if real == model_info["prediction"]:
                    hit_yn = "Y"
                    
                # --- 백테스팅 종료 시간
                back_test_end_dt = datetime.datetime.now()
                
                # --- 결과 DB에 저장
                result_row = json.dumps({
                    "back_test_start_dt" : str(back_test_start_dt),
                    "back_test_end_dt" : str(back_test_end_dt),
                    "current_price_after" : current_price_after,
                    "current_price_before" : current_price_before,
                    "prediction" : prediction,
                    "real" : real
                })
                self.result_dao.insert_ai_back_test_result(
                    ticker=self.ticker,
                    model_path=model_info["model_path"],
                    result_row=result_row,
                    hit_yn=hit_yn,
                    runnable_services_seq=self.seq,
                    reg_member_seq=0,
                )
            
            # # --- 모델 로드
            # model = load_model(local_path)    
            
            # # --- 예측에 쓰일 데이터 조회
            # self._initialize(None, self.auto_ml_path)
            # self.load_auto_ml()
            # self.hyperparameters = self.get_hyperparameters()
            # df = self.get_data_for_prediction()
            
            # # --- 예측 전 현재가 
            # current_price_before = self.get_current_price()
            
            # # 예측 by auto ml
            # self._initialize(df, self.auto_ml_path)
            # prediction = self.execute_predict_by_auto_ml(model)
                
            # # --- 모델 파기 후 대기
            # del model 
            
            # elapsed = (datetime.datetime.now() - back_test_start_dt).total_seconds()
            # wait_time = max(24*60*60 - elapsed, 0) # 1days
            # time.sleep(wait_time)
                    
            # # --- 예측 후 현재가 조회
            # current_price_after = self.get_current_price()
            
            # # 실제 결과
            # change = (current_price_after - current_price_before) / current_price_before * 100
            # if change > 1:
            #     real = 2
            # elif change < -1:
            #     real = 0
            # else:
            #     real = 1

            # # --- 상승/하락여부 예측과 실제 결과 비교 
            # hit_yn = "N"
            # if real == prediction:
            #     hit_yn = "Y"
                
            # # --- 백테스팅 종료 시간
            # back_test_end_dt = datetime.datetime.now()
            
            # # --- 결과 DB에 저장
            # result_row = json.dumps({
            #     "back_test_start_dt" : str(back_test_start_dt),
            #     "back_test_end_dt" : str(back_test_end_dt),
            #     "current_price_after" : current_price_after,
            #     "current_price_before" : current_price_before,
            #     "prediction" : prediction,
            #     "real" : real
            # })
            # self.result_dao.insert_ai_back_test_result(
            #     ticker=self.ticker,
            #     model_path=self.model_path,
            #     result_row=result_row,
            #     hit_yn=hit_yn,
            #     runnable_services_seq=self.seq,
            #     reg_member_seq=0,
            # )
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
        
        finally:
            for i, model_info in enumerate(model_info_list):
                # 모델 파일 삭제
                if model_info.get("local_path"):
                    if os.path.exists(model_info["local_path"]):
                        os.remove(model_info["local_path"])

    def get_data_for_prediction(self):
        
        try:
            # 동시 호출로 인한 API 호출 제한 완화 
            delay = random.uniform(0.1, 2.1)  
            time.sleep(delay)

            now = datetime.datetime.now()
            datetime_list = [now - datetime.timedelta(minutes=5 * i) for i in range(self.hyperparameters.get("time_steps"))]
            datetime_str_list = [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in datetime_list]
            
            collected_data_list = []
            for datetime_str in datetime_str_list:
                collected_data = self.get_collected_data(datetime_str)
                collected_data_list.append(collected_data)
                
                # 동시 호출로 인한 API 호출 제한 완화 
                delay = random.uniform(0.1, 1.1)  
                time.sleep(delay)
            
            #df = pd.DataFrame(collected_data_list, columns=self.features)
            df = pd.DataFrame(collected_data_list)
            return df
        
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise

    # def execute_prediction(self, model, df):
        
    #     try:
    #         prediction_softmax = self.tensorflow_module.predict_by_lstm_model(model, df[self.features], self.hyperparameters.get("time_steps"))
    #         predicted_label = np.argmax(prediction_softmax, axis=1)
    #         prediction = int(predicted_label[0])
    #         return prediction
        
    #     except Exception as e:
    #         self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
    #         raise
    
    """
    sub
    """
    @try_again(num=10)
    def get_collected_data(self, datetime_str):
        
        cv_auto_trader_s2_gen01_core = CvDataCollectorS1Gen02Core(self.log)
        cv_auto_trader_s2_gen01_core.set_ticker(self.ticker)
        cv_auto_trader_s2_gen01_core.set_tick_datetime(datetime_str)
        collected_data = cv_auto_trader_s2_gen01_core.collect_data()
        return collected_data
    
    @try_again(num=10)
    def get_current_price(self):
        self.upbit.set_ticker(self.ticker)
        return self.upbit.get_current_price()