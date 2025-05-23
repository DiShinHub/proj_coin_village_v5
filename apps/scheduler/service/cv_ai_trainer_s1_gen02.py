from shares.middlewares.service_options_handler import OptionHandler
from shares.middlewares.service_model_config_handler import ModelConfigHandler
from shares.modules.log import Log
from shares.modules.redis import r as redis_single
from shares.modules.minio import *
from shares.modules.tensorflow_module import TensorflowModule
from shares.modules.sklearn_module import SklearnModule
from shares.dao.runnable_services_dao import runnableServicesDao
from shares.dao.upbit_transaction_dao import UpbitTransactionDao
from shares.functions.common_function import get_years_between_str, split_date_range_by_year
from shares.functions.common_function import generate_micro_date

from apscheduler.schedulers.blocking import BlockingScheduler

import pandas as pd
import datetime

import os
import inspect

class CvAiTrainerS1Gen02(ModelConfigHandler, OptionHandler):
    """
    Service group : AiTrainer
    Service no : 1
    Generation : 02 
    Product Name : Queen bee
    
    Role : 
    1. KRW-BTC 2일 뒤 정가대비 예측 모델 생성
    """
    slack_post_prefix = ":bee: Queen Bee."
    
    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.redis = redis_single
        self.minio = MinioModule()
        self.tensorflow_module = TensorflowModule()
        self.sklearn_module = SklearnModule()
        self.runnable_services_dao = runnableServicesDao()
        self.upbit_transaction_dao = UpbitTransactionDao()
         
        # 옵션 오토 로드
        self.scheduler_start_day = None
        self.scheduler_start_hour = None
        self.scheduler_start_min = None
        self.auto_back_test = None
        self.auto_back_test_seq = None
        self.model_config_path = None
        self.ticker = None
        self.dataset_load_term = None
        self.dataset_table_prefix = None
        self.load_options(seq)
        
        # 모델 구성 로드
        super().__init__()
        self.load_model_config(self.model_config_path)
        
        self.seq = seq
        self.model_path = ""
        
    def regist(self):
        
        self.redis.save_msg_on_Q(f"{self.slack_post_prefix} 스케쥴러 등록. {self.ticker}를 대상으로 {self.dataset_load_term}일의 데이터로 학습하며, 매월 {self.scheduler_start_day}일, {self.scheduler_start_hour}시 {self.scheduler_start_min}분에 실행.")
        scheduler = BlockingScheduler()
        scheduler.add_job(self.run, 'cron', day=self.scheduler_start_day, hour=self.scheduler_start_hour, minute=self.scheduler_start_min)
        scheduler.start()
        
    def run(self):
        
        try:
            # 데이터 조회
            df = self.get_dataframe()
            
            # 모델 생성
            self.model_path = self.generate_model(df)
            
            # local_path = "./my_data.xlsx"
            # minio_path = "/datasets/2025/05/23/2025-05-23 14:30:00_2.xlsx"
            # df['tick_datetime'] = df['tick_datetime'].dt.tz_localize(None)
                
            # # Excel 파일로 저장
            # df.to_excel(local_path, index=False)  # 현재 작업 디렉토리에 저장

            # self.minio.upload_file(minio_path, local_path)
            # os.remove(local_path)
        
            # # 자동 백테스팅
            # if self.auto_back_test == "Y":
            #     self.execute_back_test()
        
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
        
    def get_dataframe(self):
        
        # --- 데이터 셋팅
        now_date = str(datetime.datetime.now())[0:19]
        n_days_ago = str(datetime.datetime.now() - datetime.timedelta(days=self.dataset_load_term))[0:19]   
        self.year_list = get_years_between_str(n_days_ago, now_date)  # 대상연도
        self.splited_year_dict = split_date_range_by_year(n_days_ago, now_date) 
        
        # --- 연단위 테이블 생성 (있으면 pass)
        self.upbit_transaction_dao.create_yearly_table(self.year_list)
    
        # --- 데이터 조회
        upbit_transactions_list = []
        for year in self.year_list:
            
            table_name = f"{self.dataset_table_prefix}_{year}"
            
            splited_year = self.splited_year_dict[year]
            start = splited_year[0]
            end = splited_year[1]
            
            upbit_transactions = self.upbit_transaction_dao.get_upbit_transactions_between(table_name, self.ticker, start, end)
            upbit_transactions_list += upbit_transactions
        
        if len(upbit_transactions_list) == 0:
            self.log.info(f'no dataset found')
            raise 
        
        # --- 데이터프레임으로 변환
        self.log.info(f'upbit_transactions_list : {upbit_transactions_list[0]}')
        df = pd.DataFrame(upbit_transactions_list)
        
        # --- 데이터 전처리
        df = self.preprocess_df_by_model_config(df)
        
        return df 
    
    def generate_model(self, df):
        
        try:
            self.redis.save_msg_on_Q(f"학습 시작, {minio_path}")
            
            # df 카피
            data = df.copy()
            
            # 모덜 구성 셋팅
            model_config = self.get_model_config()
            features = model_config.get("features")
            target = model_config.get("targets")[0]
            hyperparameters = model_config.get("hyperparameters")
            
            #
            X, Y = data[features].values, data[target].values
            
            # 클래스 가중치 계산 (Y는 정수 인코딩된 라벨)
            class_weight = self.sklearn_module.calculate_class_weight(Y)
            
            # # 가중치로 인한 손실 보정 비율
            # loss_balance_ratio = 8
            # class_weight[0] = class_weight[0] - (class_weight[1] * loss_balance_ratio)/2
            # class_weight[1] = class_weight[1] * loss_balance_ratio 
            # class_weight[2] = class_weight[2] - (class_weight[1] * loss_balance_ratio)/2
                
            # # 가중치 지정 
            # class_weight = {
            #     0: 1.0,
            #     1: 2.0,
            #     2: 5.0
            # }
            # self.log.info(f'class_weight_dict : {class_weight_dict}')
            # raise
        
            # 모델 생성
            model, history = self.tensorflow_module.train_by_lstm_model(
                X, Y, 
                hyperparameters.get("time_steps"), 
                hyperparameters.get("batch_size"), 
                hyperparameters.get("epochs"), 
                hyperparameters.get("early_stop"), 
                class_weight
            )

            # 모델 저장
            local_path = self.minio.generate_local_path("h5")
            minio_path = self.minio.generate_minio_model_path(folder_path=self.minio.generate_minio_folder_path(), file_name=f"{self.ticker}_{target}_{generate_micro_date()}", file_exe="h5")
            
            model.save(local_path, save_format="h5")
            self.minio.upload_file(minio_path, local_path)
                
            # 결과 post    
            self.redis.save_msg_on_Q(f"학습 종료, {minio_path}")
            self.redis.save_msg_on_Q(f"최종 훈련 정확도 : {history.history['accuracy'][-1]}")
            self.redis.save_msg_on_Q(f"최종 훈련 정확도 : {history.history['val_accuracy'][-1]}")
        
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            self.redis.save_msg_on_Q(f"학습 중 애러: {str(datetime.datetime.now())}")
            raise
    
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)
            
            self.redis.save_msg_on_Q(f"학습 죵료: {str(datetime.datetime.now())}")
                    
    

    
        