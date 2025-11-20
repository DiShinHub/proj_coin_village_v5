
from shares.modules.log import Log
from shares.middlewares.auto_ml_experiment_handler import AutoMlExperimentHandler
from scheduler.auto_ml.decorators.handle_error import handle_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder

import numpy as np
import pandas as pd
import os
import inspect

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
        self.df_f[cols] = StandardScaler().fit_transform(self.df_f[cols])
        return self.df_f