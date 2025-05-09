from shares.modules.redis import r as redis_single
from shares.modules.upbit import Upbit
from shares.modules.minio import MinioModule
from shares.modules.tensorflow_module import TensorflowModule
from shares.modules.sklearn_module import SklearnModule
from shares.functions.common_function import generate_micro_date

import pandas as pd
import datetime
import os
import inspect

class CvAiTrainerS1Gen01Core():
    slack_post_prefix = ":bee: King Bee."
    
    def __init__(self, log):
        self.log = log
        self.redis = redis_single
        self.upbit = Upbit()
        self.minio = MinioModule()
        self.tensorflow_module = TensorflowModule()
        self.sklearn_module = SklearnModule()
        
        self.model_folder_path = ""
            
        self.col_f = []
        self.col_t = []
        
    def set_feature(self, col_f):
        self.col_f = col_f
        return self.col_f
        
    def set_target(self, col_t):
        self.col_t = col_t
        return self.col_t
        
    def set_hyper_parameters(self, time_steps, batch_size, epochs, early_stop=False):
        
        self.time_steps = time_steps  # 시퀀스 길이 설정
        self.batch_size = batch_size
        self.epochs = epochs
        self.early_stop = early_stop

    def set_model_folder_path(self):
        
        self.model_folder_path = self.minio.generate_minio_folder_path()
        return self.model_folder_path
        
    def generate_model(self, ticker, df):
        
        self.redis.save_msg_on_Q(f"전체 학습 시작: {str(datetime.datetime.now())}")
        local_path_list = []
        model_path_list = []
        try:
            # 전처리
            data = df.copy()
            data.fillna(data.mean(), inplace=True)
            data = self.sklearn_module.standardize_fit_data(data, self.col_f)

            # 다단 모델 생성 후 업로드
            for idx, target in enumerate(self.col_t):
                
                # 저장경로 설정
                local_path = self.minio.generate_local_path("h5")
                local_path_list.append(local_path)
                
                minio_path = self.minio.generate_minio_model_path(folder_path=self.model_folder_path, file_name=f"{ticker}_{target}_{generate_micro_date()}", file_exe="h5")
                model_path_list.append(minio_path)
                
                # 학습 데이터 셋팅
                X, Y = data[self.col_f].values, data[target].values
                
                # 문자열 레이블을 숫자로 인코딩
                Y = self.sklearn_module.encode_labels(Y)
        
                # 모델 생성
                model = self.tensorflow_module.train_by_lstm_model(X, Y, self.time_steps, self.batch_size, self.epochs, self.early_stop)
                model.save(local_path, save_format="h5")
                self.minio.upload_file(minio_path, local_path)
            
            return model_path_list
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            self.redis.save_msg_on_Q(f"학습 중 애러: {str(datetime.datetime.now())}")
            raise
        
        finally:
            self.redis.save_msg_on_Q(f"전체 학습 종료: {str(datetime.datetime.now())}")
            
            if local_path_list:
                for local_path in local_path_list:
                    if os.path.exists(local_path):
                        os.remove(local_path)
          