
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder

import numpy as np
import pandas as pd
import os
import inspect
from sklearn.preprocessing import RobustScaler

class PreProcess():
    
    def __init__(self, df, config=None):
        self.config = config
        self.features = config.get("features")
        self.targets = config.get("targets")
        self.hyperparameters = config.get("hyperparameters")
        
        self.df = df
        self.df_f = None
    
    def set_df_features(self):
        self.df_f = self.df[self.features]
        
    def get_defined_cols(self, method_name):
        
        cols = self.config.get("preprocesses").get(method_name).get("cols")
        
        # cols가 정의되어 있지 않거나 all이면 모든 칼럼을 리턴
        if not cols or cols[0] == "all":
            return self.df_f.columns
        
        # 정의되어 있다면 정의된 칼럼 리턴
        else:
            return cols
        
    def fillna(self):
        cols = self.get_defined_cols(method_name=inspect.currentframe().f_code.co_name)
        self.df_f[cols].fillna(self.df_f[cols].mean(numeric_only=True), inplace=True)
        return self.df_f
    
    def cast_to_numeric(self):
        cols = self.get_defined_cols(method_name=inspect.currentframe().f_code.co_name)
        for col in self.df_f[cols].columns:
            try:
                self.df_f[col] = pd.to_numeric(self.df_f[col].astype(str).str.replace(",", "").str.strip(), errors='raise')
                
            except Exception as e:
                pass
        
        return self.df_f

    def scaling(self):
        
        cols = self.get_defined_cols(method_name=inspect.currentframe().f_code.co_name)
        
        # 극단값 클립 (윈저라이즈)
        self.df[cols] = self.df[cols].clip(lower=self.df[cols].quantile(0.01),
                                        upper=self.df[cols].quantile(0.99), axis=1)
        # IQR 기반 스케일링
        self.df[cols] = RobustScaler().fit_transform(self.df[cols])
        return self.df
        