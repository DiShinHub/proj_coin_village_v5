from shares.middlewares.service_options_handler import OptionHandler
from shares.middlewares.service_orderbook_handler import OrderbookHandler
from shares.modules.log import Log
from shares.constance.upbit_constance import UpbitConst
from shares.functions.common_function import find_target_dictionary

#from task_worker.core.cv_auto_trader_s2_gen01_core import CvAutoTraderS2Gen01Core

import multiprocessing
import inspect
import os

class CvAutoTraderS3Gen01(OrderbookHandler, OptionHandler):
    """
    Service group : AutoTrader
    Service no : 1
    Generation : 01 
    Product Name : Highnoon Eagle
    
    Role : 
    1. 돌파파 캐치하고 멈추면 매도
    2. 반복시 추가매도
    """
    slack_post_prefix = ":eagle: Highnoon Eagle. "
    
    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        
        # service attrs
        self.order_intensities = None
        self.order_max = None
        self.init_options(seq)
        
        # set OrderbookHandler's key
        super().__init__(orderbook_key=UpbitConst.ORDERBOOK_QUEUE_KEY)

    def run(self):
        super().run()

    def execute_core_process(self, ticker, key):
        """
        def description : 코어 프로세스 실행
        """
        pass