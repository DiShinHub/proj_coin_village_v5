from shares.modules.redis import r as redis_single
from shares.modules.upbit import Upbit
from shares.functions.common_function import cal_weekday_code

import datetime
import inspect

class CvDataCollectorS1Gen01Core():
    slack_post_prefix = ":bee: Honey Bee. "
    
    def __init__(self, log):
        self.log = log
        self.redis = redis_single
        self.upbit = Upbit()
        
        # system attrs
        self.feature = {}    
        self.target = {}      
    
    def reset_attr(self):

        # system attrs
        self.feature = {}    
        self.target= {}    
    
    def init_upbit_ticker(self, ticker):
        self.reset_attr()
        self.upbit.set_ticker(ticker)
        
    def collect_data(self, ticker, tick_datetime):
        
        try:
            self.init_upbit_ticker(ticker)
            
            # -- 피쳐 조회
            self.set_features(tick_datetime)
            
            # -- 타겟 조회
            self.set_targets(tick_datetime)
            
            # -- 결과 리턴
            return self.feature, self.target
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise
            
    def set_features(self, tick_datetime):
        
        # 기본 값
        self.feature["tick_datetime"] = tick_datetime
        self.feature["timestamp"] = str(datetime.datetime.strptime(tick_datetime, "%Y-%m-%d %H:%M:%S").timestamp())
        self.feature["weekday"] = cal_weekday_code(tick_datetime[0:10])
        
        # 거래 정보
        multiple_info = self.upbit.get_multiple_info("minute5", tick_datetime)
        for key, value in multiple_info.items():
            self.feature[key] = value
        
        return self.feature
            
    def set_targets(self, tick_datetime):
        
        target_by_prev = {}
        target_by_ontime = {}
        
        # tick_datetime 기준으로 미래 값 조회 
        future_prices = self.upbit.get_target_date_future_prices(
            date = tick_datetime,
            days = 7, 
            interval = "minute5", 
        )
    
        # 이전가격 기준대비 상승/하락/횡보
        target_by_prev = self.decide_up_down_side(future_prices, True)
        
        # 최초가격 기준대비 상승/하락/횡보
        target_by_ontime = self.decide_up_down_side(future_prices)
        
        self.target = {
            "by_prev" : target_by_prev,
            "by_ontime" : target_by_ontime,
        }
        return self.target
        
    def decide_up_down_side(self, future_prices, is_by_prev=False):
        
        res = {}
        
        # 첫 타겟은 정시간
        target_price = future_prices["on_time"]

        # 미래가격 산출
        for key, future_price in future_prices.items():
            if key != "on_time":
                if future_price:
                    if isinstance(future_price, float) or isinstance(future_price, int): 
                        res[f"price_{key}"] = future_price
                        res[f"price_{key}"] = future_price
        
        # 상승/하락/횡보 산출
        for key, future_price in future_prices.items():
            if key != "on_time":
                if future_price:
                    if isinstance(future_price, float) or isinstance(future_price, int): 

                        threshold = None
                        if "min" in key: 
                            threshold = 0.5
                        elif "hour" in key: 
                            threshold = 1
                        elif "day" in key: 
                            threshold = 2

                        percentage_change = ((future_price - target_price) / target_price) * 100
                        if percentage_change > threshold:
                            res[f"change_{key}"] = 2

                        elif percentage_change < -threshold:
                            res[f"change_{key}"]  = 0

                        else:
                            res[f"change_{key}"]  = 1
                        
                        if is_by_prev: 
                            target_price = future_price 
        
        return res