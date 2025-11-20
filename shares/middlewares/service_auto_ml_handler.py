from shares.modules.log import system_module_log
from shares.functions.common_function import *
    
import mlflow
import inspect
import os 

import yaml
import numpy as np
import ast
import operator as op
from functools import wraps

class AutoMlHandler():
    
    def __init__(self, df, auto_ml_path):
        self._initialized = False
        self.df = None
        self.auto_ml_path= None
        
        self.config = None 
        self.config_path = None
        self.features = None 
        self.targets = None 
        self.hyperparameters = None
        
        self.derived_path = None
        self.preprocess_path = None
        self.train_path = None
        self.metric_path = None
        
        self.derived_class = None
        self.preprocess_class = None
        self.train_class = None
        self.metric_class = None
        self.predict_class = None
        
        self.train_result = {}
        
        self._initialize(df, auto_ml_path)
        
    def _initialize(self, df, auto_ml_path):
        self.log = system_module_log
        self.df = df
        self.auto_ml_path = auto_ml_path
        
        self.config = None 
        self.config_path = None
        self.features = None 
        self.targets = None 
        self.hyperparameters = None
        
        self.derived_path = None
        self.preprocess_path = None
        self.train_path = None
        self.predict_path = None
        self.metric_path = None
        
        self.derived_class = None
        self.preprocess_class = None
        self.train_class = None
        self.predict_class = None
        self.metric_class = None
        
        self._initialized = True
        
        self.train_result = {}
    
    def get_df(self):
        return self.df
    
    def set_df(self, df):
        self.df = df
        return self.df
    
    def get_auto_ml_path(self):
        return self.auto_ml_path
    
    def set_auto_ml_path(self, auto_ml_path):
        self.auto_ml_path= auto_ml_path
        return self.auto_ml_path
    
    def get_features(self):
        return self.features
        
    def get_targets(self):
        return self.targets
    
    def get_hyperparameters(self):
        return self.hyperparameters

    """
    executer
    """
    def execute_train_by_auto_ml(self):

        try:
            mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))  
            mlflow.set_experiment(self.set_experiment_name())
            with mlflow.start_run():
                self.load_auto_ml()
                self.apply_dervied_params()
                self.apply_preprocess()
                self.train_model()
                self.metric_model()
                
                run = mlflow.active_run()
                self.train_result["experiment_id"] = run.info.experiment_id
                self.train_result["run_id"] = run.info.run_id
                return self.train_result

        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
    
    def execute_predict_by_auto_ml(self, model):
        self.load_auto_ml()
        self.apply_dervied_params()
        self.apply_preprocess()
        return self.predict_model(model)
        
    """
    auto ml
    """
    def load_auto_ml(self):
        self.config_path = f"{self.auto_ml_path}/config.yaml"
        self.derived_path = f"{self.auto_ml_path}/derived.py"
        self.preprocess_path = f"{self.auto_ml_path}/preprocess.py"
        self.train_path = f"{self.auto_ml_path}/train.py"
        self.metric_path = f"{self.auto_ml_path}/metric.py"
        self.predict_path = f"{self.auto_ml_path}/predict.py"
        
        # yaml 파싱
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            self.features = self.config.get("features")
            self.targets = self.config.get("targets")
            self.hyperparameters = self.config.get("hyperparameters")
            
    def apply_dervied_params(self):
        
        derived_params = self.config.get("derived_params")
        if not derived_params:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : no derived_params on config")
            raise
        
        df = self.df.copy()
        derived_class = self.load_class_from_file(self.derived_path, f"Derived")
        derived_obj = derived_class(df, self.config)
        
        for derived_param in derived_params:
            self.run_method_dynamic(obj=derived_obj, method_name=f"{derived_param}")
        
        self.df = derived_obj.df
        return self.df
    
    def apply_preprocess(self):
        
        preprocesses = self.config.get("preprocesses")
        if not preprocesses:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : no preprocesses on config")
            raise
        
        df = self.df.copy()
        preprocess_class = self.load_class_from_file(self.preprocess_path, f"PreProcess")
        preprocess_obj = preprocess_class(df, self.config)
        
        for preprocess, options in preprocesses.items():
            self.run_method_dynamic(obj=preprocess_obj, method_name=f"{preprocess}")
        
        self.df[self.features] = preprocess_obj.df_f
        return self.df
    
    def train_model(self):
        
        df = self.df.copy()
        train_class = self.load_class_from_file(self.train_path, f"Train")
        train_obj = train_class(df, self.config)
        self.train_result = self.run_method_dynamic(obj=train_obj, method_name=f"train")
        return self.train_result
    
    def metric_model(self):
        
        df = self.df.copy()
        metric_class = self.load_class_from_file(self.metric_path, f"Metric")
        metric_obj = metric_class(df, self.config)
        if self.train_result:
            self.run_method_dynamic(obj=metric_obj, method_name=f"metric", train_result=self.train_result)
        
        return 
    
    def predict_model(self, model):
        
        df = self.df.copy()
        predict_class = self.load_class_from_file(self.predict_path, f"Predict")
        predict_obj = predict_class(df, self.config)
        return self.run_method_dynamic(obj=predict_obj, method_name=f"predict", df=self.df, model=model)
    
    """
    helper
    """
    def load_class_from_file(self, file_path: str, class_name: str):
        
        # 파일 이름에서 모듈 이름 생성 (확장자 제외)
        module_name = os.path.splitext(os.path.basename(file_path))[0]

        # 모듈 스펙 로드
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            raise ImportError(f"Cannot find spec for {file_path}")
        
        # 모듈 객체 생성 및 실행
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  

        # 클래스 가져오기
        cls = getattr(module, class_name, None)
        if cls is None:
            raise AttributeError(f"Class '{class_name}' not found in {file_path}")
        
        return cls

    def run_method_dynamic(self, obj, method_name, **options):
        method = getattr(obj, method_name)
        result = method(**options)
        return result
    
    def set_experiment_name(self):
        
        auto_ml_path_splited = self.auto_ml_path.split("/")
        experiment_name = f"{auto_ml_path_splited[-2]}_{auto_ml_path_splited[-1]}"
        return experiment_name
        