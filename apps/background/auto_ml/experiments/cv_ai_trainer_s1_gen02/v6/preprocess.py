
from shares.modules.log import Log
from shares.middlewares.auto_ml_experiment_handler import AutoMlExperimentHandler
from scheduler.auto_ml.decorators.handle_error import handle_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder

import numpy as np
import pandas as pd
import os
import inspect
from sklearn.preprocessing import RobustScaler

class PreProcess(AutoMlExperimentHandler):
    
    def __init__(self, df, config=None):
        self.log = Log(os.path.basename(__file__)).get_logger()
        super().__init__(df, config)
        super().set_df_features()
        
    @handle_error
    def fillna(self):
        cols = self.get_defined_cols(method_name=inspect.currentframe().f_code.co_name)
        self.df_f[cols].fillna(self.df_f[cols].mean(numeric_only=True), inplace=True)
        return self.df_f
    
    @handle_error
    def cast_to_numeric(self):
        cols = self.get_defined_cols(method_name=inspect.currentframe().f_code.co_name)
        for col in self.df_f[cols].columns:
            try:
                self.df_f[col] = pd.to_numeric(self.df_f[col].astype(str).str.replace(",", "").str.strip(), errors='raise')
                
            except Exception as e:
                pass
        
        return self.df_f

    @handle_error
    def scaling(self):
        
        cols = self.get_defined_cols(method_name=inspect.currentframe().f_code.co_name)
        
        # 극단값 클립 (윈저라이즈)
        self.df[cols] = self.df[cols].clip(lower=self.df[cols].quantile(0.01),
                                        upper=self.df[cols].quantile(0.99), axis=1)
        # IQR 기반 스케일링
        self.df[cols] = RobustScaler().fit_transform(self.df[cols])
        return self.df
        
    
    
    
    
    
    
    
    # @handle_error
    # def log_transform(self, **options):
    #     cols = self.get_cols(options=options)
    #     for col in cols:
    #         self.df_f[col] = self.df_f[col].apply(lambda x: np.log1p(x) if x > 0 else 0)
            
    #     return self.df_f
    
    # @handle_error
    # def remove_outliers(self, **options):
    #     cols = self.get_cols(options=options)
    #     for col in cols:
    #         q1 = self.df_f[col].quantile(0.25)
    #         q3 = self.df_f[col].quantile(0.75)
    #         iqr = q3 - q1
    #         median = self.df_f[col].median()
    #         self.df_f[col] = self.df_f[col].apply(lambda x: x if (q1 - 1.5 * iqr <= x <= q3 + 1.5 * iqr) else median)
            
    #     return self.df_f
    
    # @handle_error
    # def minmax_scaling(self, **options):
    #     cols = self.get_cols(options=options)
    #     scaler = MinMaxScaler()
    #     self.df_f[cols] = scaler.fit_transform(self.df_f[cols])
    #     return self.df_f
    
    # @handle_error
    # def label_encoding(self, **options):
    #     cols = self.get_cols(options=options)
    #     for col in cols:
    #         if self.df_f[col].dtype == 'object':
    #             le = LabelEncoder()
    #             self.df_f[col] = le.fit_transform(self.df_f[col].astype(str))
                
    #     return self.df_f

