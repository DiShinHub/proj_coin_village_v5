from shares.modules.redis import r as redis_single
from shares.modules.upbit import Upbit
from shares.modules.minio import MinioModule
from shares.modules.tensorflow_module import TensorflowModule
from shares.modules.sklearn_module import SklearnModule
from shares.modules.dataframe import DataFrame
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
        self.dataframe = DataFrame()
        
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
            data = self.pre_processing_data(df)

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
                
                # 가중치 계산 (균등화 적용)
                class_weight = self.sklearn_module.calculate_class_weight(Y)
                
                # 가중치로 인한 손실 보정 비율
                loss_balance_ratio = 2
                class_weight[0] = class_weight[0] - (class_weight[1] * loss_balance_ratio)/2
                class_weight[1] = class_weight[1] * loss_balance_ratio 
                class_weight[2] = class_weight[2] - (class_weight[1] * loss_balance_ratio)/2
                
                # # 가중치 지정 
                # class_weight = {
                #     0: 1.0,
                #     1: 2.0,
                #     2: 5.0
                # }
                # self.log.info(f'class_weight_dict : {class_weight_dict}')
                # raise
        
                # 모델 생성
                model, history = self.tensorflow_module.train_by_lstm_model(X, Y, self.time_steps, self.batch_size, self.epochs, self.early_stop, class_weight)
                
                self.log.info(f"타겟 : {target}")
                self.log.info(f"최종 훈련 정확도 : {history.history['accuracy'][-1]}")
                self.log.info(f"최종 검증 정확도 : {history.history['val_accuracy'][-1]}")
        
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
    
    """
    subs
    """
    def pre_processing_data(self, df):

        try:
            data = df.copy()
            data = self.dataframe.convert_numeric_columns(data)
            data.fillna(data.mean(), inplace=True)
            data = self.sklearn_module.standardize_fit_data(data, self.col_f)
            
            return data
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise