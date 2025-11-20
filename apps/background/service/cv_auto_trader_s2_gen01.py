from shares.middlewares.service_options_handler import OptionHandler
from shares.middlewares.service_orderbook_handler import OrderbookHandler
from shares.modules.log import Log
from shares.decorations.transaction_lock import *
from shares.constance.upbit_constance import UpbitConst
from shares.define.order_default import ORDER_INTENSITY_DEFAULT
from shares.functions.common_function import find_target_dictionary

from task_worker.core.cv_auto_trader_s2_gen01_core import CvAutoTraderS2Gen01Core

import multiprocessing
import time
import os
import inspect

class CvAutoTraderS2Gen01(OrderbookHandler, OptionHandler):
    """
    Service group : AutoTrader
    Service no : 1
    Generation : 01 
    Product Name : Night Owl
    
    Role : 
    1. 드롭 캐치하고 멈추면 매수
    2. 반복시 추가매수
    """
    slack_post_prefix = ":owl:"
    
    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        
        # service attrs
        self.order_intensities = None
        self.order_max = None
        self.load_options(seq)
        
        self.runnable_services_seq = seq
        
        # set OrderbookHandler's key
        super().__init__(orderbook_key=UpbitConst.ORDERBOOK_QUEUE_KEY)

    def run(self):
        try:
            super().monitoring_order_books()

        except Exception as e:
            self.log.info(f"호가 조회 실패, class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            
    @wait_when_lock(lock_key=UpbitConst.TRANSACTION_BLOCK_KEY)
    def execute_core_process(self, ticker, key):
        """
        def description : 코어 프로세스 실행
        """
        
        # --- 주문 강도 파싱
        order_intensity = self.order_intensities.get(ticker, ORDER_INTENSITY_DEFAULT)
        
        # --- 호가 정보 추출
        order_book = self.redis.get_json_data(key) 
        
        # --- 실행
        cv_auto_trader_s2_gen01_main = CvAutoTraderS2Gen01Core(ticker, order_intensity, order_book, self.order_max, self.log, self.runnable_services_seq)
        p = multiprocessing.Process(target=cv_auto_trader_s2_gen01_main.run)
        p.start()
        
        # --- 트래픽 제어 
        time.sleep(0.1)
        