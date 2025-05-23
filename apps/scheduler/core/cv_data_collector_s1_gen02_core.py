from shares.modules.redis import r as redis_single
from shares.modules.upbit import Upbit
from shares.modules.candle_pattern import CandlePatterns
from shares.functions.common_function import cal_weekday_code

import datetime
import inspect

class CvDataCollectorS1Gen02Core():
    slack_post_prefix = ":bee: Honey Bee. "
    
    def __init__(self, log):
        self.log = log
        self.redis = redis_single
        self.upbit = Upbit()
        self.candle_pattern = CandlePatterns()
        
        # system attrs
        self.data_collected = {}    
        self.ticker = ""
        self.df = None
    
    def set_ticker(self, ticker):
        self.upbit.set_ticker(ticker)
        self.ticker = ticker
        return self.ticker
    
    def set_tick_datetime(self, tick_datetime):
        self.tick_datetime = tick_datetime
        return self.tick_datetime
    
    def reset_attr(self):
        self.data_collected = {}    
        self.ticker = ""
        
    def collect_data(self):
        
        try:
            self.df = self.upbit.get_df_ohlcv(interval="minute5", date=self.tick_datetime)
            
            self.put_date_info()
            self.put_technical_indicators()
            self.put_candle_pattern()
            self.put_future_info()
            
            return self.data_collected
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise
    
    def put_date_info(self):
        """
        def description : 날짜 정보 수집
        """
        
        self.data_collected["tick_datetime"] = self.tick_datetime
        self.data_collected["timestamp"] = str(datetime.datetime.strptime(self.tick_datetime, "%Y-%m-%d %H:%M:%S").timestamp())
        self.data_collected["weekday"] = cal_weekday_code(self.tick_datetime[0:10])
    
    def put_technical_indicators(self):
        """
        def description : 기술지표 수집
        """
        res = self.upbit.get_technical_indicator(self.df)
        self.data_collected.update(res)
        
    def put_candle_pattern(self):
        """
        def description : 차트지표 수집
        """
        
        # self.candle_pattern에 있는 모든 조회 함수를 실행하여 담음
        self.candle_pattern.set_df(self.df)
        for name in dir(self.candle_pattern):
            attr = getattr(self.candle_pattern, name)
            if callable(attr):
                if "get_" in name:
                    try:
                        self.data_collected[name.replace("get_", "")] = float(attr().iloc[-1])
                        
                    except Exception as e:
                        self.data_collected[name.replace("get_", "")] = 999
        
    def put_future_info(self):
        """
        def description : 미래가격 수집
        """
        
        future_prices = self.upbit.get_target_date_future_prices(
            date = self.tick_datetime,
            days = 7, 
            interval = "minute5", 
        )
        for key, future_price in future_prices.items():
            if future_price:
                if isinstance(future_price, float) or isinstance(future_price, int): 
                    self.data_collected[f"price_{key}"] = future_price
    
            