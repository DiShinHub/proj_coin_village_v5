
from shares.modules.log import Log
from shares.middlewares.auto_ml_experiment_handler import AutoMlExperimentHandler
from scheduler.auto_ml.decorators.handle_error import handle_error
import os

class Derived(AutoMlExperimentHandler):
    
    def __init__(self, df, config=None):
        self.log = Log(os.path.basename(__file__)).get_logger()
        super().__init__(df, config)
    
    @handle_error
    def derived_param_1(self): 
        self.df['derived_param_1'] = self.df['feature_1'].astype(float) / self.df['feature_2'].astype(float)
        return self.df
    
    @handle_error
    def derived_param_2(self): 
        self.df['derived_param_2'] = self.df['feature_1'].astype(float) * self.df['feature_2'].astype(float)
        return self.df