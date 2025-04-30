from shares.middlewares.service_options_handler import OptionHandler
from shares.modules.log import Log
from shares.modules.minio import MinioModule

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import save_model, load_model

from apscheduler.schedulers.blocking import BlockingScheduler

import numpy as np
import pandas as pd
import datetime

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
         
        # service attrs
        self.model_folder_path = "models/2025/04/28"
        self.init_options(seq)
        
    def run(self):
        
        # 모델 다운로드
        local_file_list = self.minio.download_files_in_folder(f"{self.model_folder_path}")
        
        # 모델 로드
        models={}
        for idx, local_file in enumerate(local_file_list):
            try:
                model = load_model(local_file)      # 🔹 로컬 경로에서 직접 로드
                #model.compile(run_eagerly=True)    # 즉시 실행 모드 활성화
                models[local_file] = model
            
            except Exception as e:
                self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            
            finally:
                # 로컬 파일 삭제
                if os.path.exists(local_file):
                    os.remove(local_file)
        
        # split by predict time  
        
        # predict 
        
        # real 
        
        return 
    
    def load_model_from_local(self):
        return
    
    def delete_model_on_local(self):
        return 
    
    def back_test_model(self, model, interval):
        
        # 현재가 조회
        
        # 예측가 조회
        
        # interval 만큼 대기
        
        # interval 이후 현재가 조회
        
        # 예측 <> 실제 결과 비교 
        
        pass