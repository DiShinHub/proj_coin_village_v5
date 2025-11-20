from shares.middlewares.service_options_handler import OptionHandler
from shares.middlewares.service_auto_ml_handler import AutoMlHandler
from shares.modules.log import Log
from shares.modules.redis import r as redis_single
from shares.modules.minio import MinioModule
from shares.modules.tensorflow_module import TensorflowModule
from shares.modules.sklearn_module import SklearnModule
from shares.dao.runnable_services_dao import runnableServicesDao
from shares.dao.upbit_transaction_dao import UpbitTransactionDao
from shares.dao.result_dao import ResultDao
from shares.functions.common_function import get_years_between_str, split_date_range_by_year
from shares.functions.common_function import generate_micro_date

from apscheduler.schedulers.blocking import BlockingScheduler

import pandas as pd
import datetime
import time

import os
import inspect

class CvAiTrainerS1Gen02(AutoMlHandler, OptionHandler):
    """
    Service group : AiTrainer
    Service no : 1
    Generation : 02 
    Product Name : Queen bee
    
    Role : 
    1. KRW-BTC 2일 뒤 정가대비 예측 모델 생성
    """
    slack_post_prefix = ":bee:"
    
    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.redis = redis_single
        self.minio = MinioModule()
        self.tensorflow_module = TensorflowModule()
        self.sklearn_module = SklearnModule()
        self.runnable_services_dao = runnableServicesDao()
        self.upbit_transaction_dao = UpbitTransactionDao()
        self.result_dao = ResultDao()
         
        # 옵션 오토 로드
        self.scheduler_start_day = None
        self.scheduler_start_hour = None
        self.scheduler_start_min = None
        self.auto_back_test = None
        self.auto_back_test_seq = None
        self.auto_ml_path = None
        self.ticker = None
        self.dataset_load_term = None
        self.dataset_table_prefix = None
        self.load_options(seq)
        
        self.seq = seq
        self.local_path = ""
        self.minio_path = ""
        self.train_result = {}
        
    def regist(self):
        
        self.redis.save_msg_on_Q(f"{self.slack_post_prefix} 스케쥴러 등록. {self.ticker}를 대상으로 {self.dataset_load_term}일의 데이터로 학습하며, 매월 {self.scheduler_start_day}일, {self.scheduler_start_hour}시 {self.scheduler_start_min}분에 실행.")
        scheduler = BlockingScheduler()
        scheduler.add_job(self.run, 'cron', day=self.scheduler_start_day, hour=self.scheduler_start_hour, minute=self.scheduler_start_min)
        scheduler.start()
        
    def run(self):
        
        # set path
        self.local_path = self.minio.generate_local_path("h5")
        self.minio_path = self.minio.generate_minio_model_path(folder_path=self.minio.generate_minio_folder_path(), file_name=f"{self.__class__.__name__}_{self.ticker}_{generate_micro_date()}", file_exe="h5")
        
        try:
            # --- 시작 포스트
            self.redis.save_msg_on_Q(f"{self.slack_post_prefix} 학습을 시작합니다.")
            self.redis.save_msg_on_Q(f"{self.ticker}를 대상으로 1일 뒤 가격을 예측하며 하위 실험을 기반으로 합니다.")
            self.redis.save_msg_on_Q(f"{str(self.auto_ml_path).replace('apps/scheduler/', '')}, {self.dataset_load_term}일의 데이터")
            
            # --- 데이터 조회
            df = self.get_dataframe()
            
            # --- 모델 학습 
            train_start_dt = str(datetime.datetime.now())
            self.generate_model(df)
            train_end_dt = str(datetime.datetime.now())
            
            # --- 모델 업로드, 결과 저장   
            self.upload_model()
            self.save_train_result(train_start_dt, train_end_dt)
            
            # 모델 minio 업로드
            self.train_result.get("model").save(self.local_path, save_format="h5")
            self.minio.upload_file(self.minio_path, self.local_path)
            
            # --- 결과 포스트
            self.redis.save_msg_on_Q(f"{self.slack_post_prefix} 학습 종료")
            self.redis.save_msg_on_Q(f"최종 훈련 정확도 : {self.train_result.get('history').history['accuracy'][-1]}")
            self.redis.save_msg_on_Q(f"최종 검증 정확도 : {self.train_result.get('history').history['val_accuracy'][-1]}")
            self.redis.save_msg_on_Q(f"모델 파일 위치 : {self.minio_path}")
            self.redis.save_msg_on_Q(f"모델 매트릭 실행 ID  : {self.train_result.get('run_id')}")
            
            # --- 모델 백테스팅 실행
            if self.auto_back_test == "Y":
                self.execute_back_test()
        
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
    
        finally:
            if os.path.exists(self.local_path):
                os.remove(self.local_path)
    
    def get_dataframe(self):
        
        try:
            # 변수 셋팅
            now_date = str(datetime.datetime.now())[0:19]
            n_days_ago = str(datetime.datetime.now() - datetime.timedelta(days=self.dataset_load_term))[0:19]   
            self.year_list = get_years_between_str(n_days_ago, now_date)  # 대상연도
            self.splited_year_dict = split_date_range_by_year(n_days_ago, now_date) 
            
            # 연단위 테이블 생성 (있으면 pass)
            self.upbit_transaction_dao.create_yearly_table(self.year_list)
        
            # 데이터 조회
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
            
            # 데이터프레임으로 변환
            df = pd.DataFrame(upbit_transactions_list)
            return df 
    
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise e 
    
    def generate_model(self, df):
        
        try:
            # auto ml
            self._initialize(df, self.auto_ml_path)
            self.train_result = self.execute_train_by_auto_ml()
        
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise e 
    
    def upload_model(self):
            
        try:
            # 모델 minio 업로드
            self.train_result.get("model").save(self.local_path, save_format="h5")
            self.minio.upload_file(self.minio_path, self.local_path)
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise e 
    
        finally:
            if os.path.exists(self.local_path):
                os.remove(self.local_path)
    
    def save_train_result(self, train_start_dt, train_end_dt):
        
        try:
            # 학습 결과 DB 저장 
            self.result_dao.ai_train_result(
                experiment_id=self.train_result.get("experiment_id"),
                run_id=self.train_result.get("run_id"),
                minio_path=self.minio_path,
                train_start_dt=train_start_dt,
                train_end_dt=train_end_dt,
                runnable_services_seq=self.seq
            )
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise e 
        
    def execute_back_test(self):
        
        try:
            if self.auto_back_test == "Y":
                
                #  백테스팅 옵션 생성
                self.runnable_services_dao.upsert_runnable_service_options(option_key="ticker", option_val=self.ticker, runnable_service_seq=self.auto_back_test_seq)
                self.runnable_services_dao.upsert_runnable_service_options(option_key="model_path", option_val=self.minio_path, runnable_service_seq=self.auto_back_test_seq)
                self.runnable_services_dao.upsert_runnable_service_options(option_key="auto_ml_path", option_val=self.auto_ml_path, runnable_service_seq=self.auto_back_test_seq)
                
                # 백테스팅 재시작
                params = {"activate_yn" : "N"}
                self.runnable_services_dao.update_runnable_services(params=params, seq=self.auto_back_test_seq)
                time.sleep(2.5)
                
                params = {"activate_yn" : "Y"}
                self.runnable_services_dao.update_runnable_services(params=params, seq=self.auto_back_test_seq)
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise e 
        