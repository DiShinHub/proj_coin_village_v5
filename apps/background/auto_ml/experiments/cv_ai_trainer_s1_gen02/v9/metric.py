

from sklearn.metrics import *
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

import mlflow

import pandas as pd 
import numpy as np
import os 
import inspect


class Metric():
    
    def __init__(self, df, config=None):
        self.config = config
        self.features = config.get("features")
        self.targets = config.get("targets")
        self.hyperparameters = config.get("hyperparameters")
        
        self.df = df
        self.df_f = None
    
    def set_attr(self, train_result):
        
        self.model = train_result.get("model")
        self.history = train_result.get("history")
        self.X = train_result.get("X")
        self.Y = train_result.get("Y")
        self.X_origin = train_result.get("X_origin")
        self.Y_origin = train_result.get("Y_origin")
        self.X_train = train_result.get("X_train")
        self.X_test = train_result.get("X_test")
        self.Y_train = train_result.get("Y_train")
        self.Y_test = train_result.get("Y_test")
        self.y_true = train_result.get("y_true")
        self.y_pred = train_result.get("y_pred")
        self.y_prob = train_result.get("y_prob")
        
        if self.model is None or\
            self.history is None or\
            len(self.y_true) == 0 or\
            len(self.y_pred) == 0:
            return False

        return True
    
    def metric(self, train_result):
        
        if self.set_attr(train_result) == False:
            return 
        
        # --- 옵션 파라메터 기재
        self.log_parameters()
                    
        # --- 피쳐 임포턴스
        self.log_feature_importance()
        
        # --- 라벨 분포/정합성 로그
        self.log_dist()
        
        # --- 타입별 매트릭
        self.log_extra_by_type()
        
    def log_parameters(self):

        try:
            feature_cnt = 0 
            derived_cnt = 0 
            if self.config:
                features = self.config.get("features")
                derived_params = self.config.get("derived_params")
                if features:
                    for feature in features:
                        if feature not in derived_params:
                            feature_cnt += 1
                            mlflow.log_param(f"feature_{feature_cnt}", feature)
                        
                        else:
                            derived_cnt += 1
                            mlflow.log_param(f"derived_{derived_cnt}", feature)
                
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
        
    def log_dist(self):
        def dist(arr):
            u, c = np.unique(arr, return_counts=True)
            return {int(k): int(v) for k, v in zip(u, c)}

        y_train_labels = (
            np.argmax(self.Y_train, axis=1)
            if self.Y_train.ndim > 1 else self.Y_train
        )
        pred_distribution = dist(y_train_labels)
        for label, count in pred_distribution.items():
            mlflow.log_metric(f"pred_dist_train_class_{label}", count)
            
        # pred_distribution = dist(self.y_pred)
        # for label, count in pred_distribution.items():
        #     mlflow.log_metric(f"pred_dist_test_class_{label}", count)
            
    def log_feature_importance(self):
        
        importances = None

        # sklearn 기반 트리 모델 (e.g., RandomForest, XGBoost, LightGBM)
        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_

        # sklearn 기반 선형 모델
        elif hasattr(self.model, "coef_"):
            importances = self.model.coef_
            if importances.ndim > 1:
                importances = importances[0]  # 다중 클래스의 경우 첫 번째만 사용
        
        # lstm 기반 
        elif any('LSTM' in layer.__class__.__name__ for layer in self.model.layers):
            
            # 결측치 제외
            df = self.df.copy()
            df.fillna(df.mean(numeric_only=True), inplace=True)

            # 1. 숫자형 피처만 선택
            X = df[self.features]
            Y = df[self.targets[0]]

            #
            X = X.select_dtypes(exclude=['datetime'])

            # 2. 학습/검증 분리
            X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

            # 3. 모델 훈련
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)

            # 4. Feature Importance 추출
            importances = model.feature_importances_
            feature_importance = pd.Series(importances, index=X_train.columns).sort_values(ascending=False)
            
            # top 20 출력
            top20 = feature_importance.head(20)

            # MLflow에 로그 기록
            for feat, imp in top20.items():
                mlflow.log_metric(f"feature_importance_{feat}", float(imp))
            
        # # --- 파쳐 임포턴스 기재
        # if importances:
        #     for i, score in enumerate(importances):
        #         self.log.info(f'val : {self.config["features"][i]} : {float(score)}')
        #         mlflow.log_metric(f"feature_importance_{self.config['features'][i]}", float(score))
                
                # if i > 10:
                #     break
        
    def log_extra_by_type(self):
        
        if self.config.get("model_type") == 'binary_classification':
            mlflow.log_metric("accuracy", accuracy_score(self.y_true, self.y_pred))
            mlflow.log_metric("f1_score", f1_score(self.y_true, self.y_pred))
            mlflow.log_metric("precision", precision_score(self.y_true, self.y_pred))
            mlflow.log_metric("recall", recall_score(self.y_true, self.y_pred))
            if self.y_pred is not None and len(self.y_pred) > 0:
                mlflow.log_metric("roc_auc", roc_auc_score(self.y_true, self.y_prob))

        elif self.config.get("model_type") == 'regression':
            #mlflow.log_metric("rmse", mean_squared_error(y_true, y_pred, squared=False))
            mlflow.log_metric("mae", mean_absolute_error(self.y_true, self.y_pred))
            mlflow.log_metric("r2_score", r2_score(self.y_true, self.y_pred))

        elif self.config.get("model_type") == 'multiclass_classification':
            mlflow.log_metric("accuracy", accuracy_score(self.y_true,self.y_pred))
            mlflow.log_metric("macro_f1", f1_score(self.y_true, self.y_pred, average='macro'))
            mlflow.log_metric("log_loss", log_loss(self.y_true, self.y_prob) if self.y_prob else 0)
            
        elif self.config.get("model_type") == 'lstm_multiclass_classification':
            mlflow.log_metric("accuracy", accuracy_score(self.y_true, self.y_pred))
            mlflow.log_metric("macro_f1", f1_score(self.y_true, self.y_pred, average='macro'))
            mlflow.log_metric("micro_f1", f1_score(self.y_true, self.y_pred, average='micro'))
            mlflow.log_metric("weighted_f1", f1_score(self.y_true, self.y_pred, average='weighted'))
            mlflow.log_metric("precision_macro", precision_score(self.y_true, self.y_pred, average='macro'))
            mlflow.log_metric("recall_macro", recall_score(self.y_true, self.y_pred, average='macro'))
            if self.y_pred is not None and len(self.y_pred) > 0:
                try:
                    mlflow.log_metric("log_loss", log_loss(self.y_true, self.y_prob))
                    
                except ValueError:
                    mlflow.log_metric("log_loss", 0)