from shares.modules.log import system_module_log
from shares.config.config import Config
from shares.decorations.try_again import try_again
from shares.decorations.cache_data import cache_data

import datetime

class Binance():

    def __init__(self):
        self.log = system_module_log
        config = Config()
        self.binance = config.set_binance()
        
        self.ticker = None
        self.ticker_org = None

    def set_ticker(self, ticker):
        """
        def description : 티커 셋팅

        Parameters
        ----------
        ticker : 티커(string)

        Returns
        -------
        Boolean
        """

        self.ticker = ticker
        self.ticker_org = ticker.replace("USDT", "")
        return True

    def get_ticker(self):
        """
        def description : 셋팅 된 티커 리턴

        Returns
        -------
        ticker : 티커(string)
        """

        return self.ticker

    @cache_data(ttl=1)
    @try_again(num=4)
    def get_current_price(self):
        """
        def description : 현재가 조회

        Returns
        -------
        current_price : 현재가 (float)
        """
        res = self.binance.get_symbol_ticker(symbol=self.ticker)
        current_price = float(res.get("price"))
        return current_price
    
    @cache_data(ttl=1)
    @try_again(num=4)
    def get_target_date_price(self, start=None):
        """
        def description : 특정 날짜의 가격 조회

        Parameters
        ----------
        date : 특정 날짜
        Returns
        -------
        close_price : 종가 (float)
        """

        interval_b = self.binance.KLINE_INTERVAL_1MINUTE

        # 날짜를 타임스탬프로 변환
        start_time = int(datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

        # 캔들스틱 데이터 조회 (1일 간격)
        klines = self.binance.get_klines(symbol=self.ticker,
                                          interval=interval_b, 
                                          startTime=start_time)

        if klines:
            close_price = klines[0][4]
            return float(close_price)
    
    @cache_data(ttl=1)
    @try_again(num=4)
    def get_target_date_prices(self, interval=None,start=None, end=None):
        """
        def description : 특정 날짜의 가격 조회

        Parameters
        ----------
        date : 특정 날짜
        Returns
        -------
        close_price : 종가 (float)
        """

        interval_b = self.binance.KLINE_INTERVAL_1MINUTE
        if interval:
            if interval == "minute1":
                interval_b = self.binance.KLINE_INTERVAL_1MINUTE
            elif interval == "minute3":
                interval_b = self.binance.KLINE_INTERVAL_3MINUTE
            elif interval == "minute5":
                interval_b = self.binance.KLINE_INTERVAL_5MINUTE
            elif interval == "minute15":
                interval_b = self.binance.KLINE_INTERVAL_15MINUTE
            elif interval == "minute30":
                interval_b = self.binance.KLINE_INTERVAL_30MINUTE
            elif interval == "minute60":
                interval_b = self.binance.KLINE_INTERVAL_1HOUR
            elif interval == "minute120":
                interval_b = self.binance.KLINE_INTERVAL_2HOUR
            elif interval == "minute240":
                interval_b = self.binance.KLINE_INTERVAL_4HOUR
            elif interval == "minute360":
                interval_b = self.binance.KLINE_INTERVAL_6HOUR
            elif interval == "day":
                interval_b = self.binance.KLINE_INTERVAL_1DAY
            elif interval == "week":
                interval_b = self.binance.KLINE_INTERVAL_1WEEK
            elif interval == "month":
                interval_b = self.binance.KLINE_INTERVAL_1MONTH
    
        # 날짜를 타임스탬프로 변환
        start_time = int(datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
        end_time = int(datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

        # 캔들스틱 데이터 조회 (1일 간격)
        klines = self.binance.get_klines(symbol=self.ticker,
                                          interval=interval_b, 
                                          startTime=start_time, 
                                          endTime=end_time)

        close_price_list = []
        if klines:
            for kline in klines:
                # 캔들스틱 데이터의 첫 번째 행 (해당 날짜의 데이터)
                kline = klines[0]
                open_time = kline[0]
                open_price = kline[1]
                high_price = kline[2]
                low_price = kline[3]
                close_price = kline[4]
                close_price_list.append(close_price)

        if close_price_list:
            close_price_list.reverse()
        
        return close_price_list