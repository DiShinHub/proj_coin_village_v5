from shares.modules.log import system_module_log
from shares.config.config import Config
from shares.decorations.try_again import try_again
from shares.decorations.cache_data import cache_data
from shares.decorations.reuse_data import reuse_data

import pyupbit

from datetime import datetime, timedelta
import math

import inspect

class Upbit():

    def __init__(self):
        self.log = system_module_log
        config = Config()

        self.upbit = config.set_upbit()
        
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
        self.ticker_org = ticker.replace("KRW-", "")
        return True

    def get_ticker(self):
        """
        def description : 셋팅 된 티커 리턴

        Returns
        -------
        ticker : 티커(string)
        """
        return self.ticker
    
    
    
    """
    No Auth
    """
    @cache_data(ttl=1)
    @try_again(num=4)
    def get_KRW_tickers(self):
        """
        def description : 원화로 매매 가능한 코인 리스트

        Returns
        -------
        tickers : 티커 배열 (float)
        """
        tickers = pyupbit.get_tickers(fiat="KRW")
        return tickers

    @cache_data(ttl=1)
    @try_again(num=4)
    def get_current_price(self):
        """
        def description : 현재가 조회

        Returns
        -------
        current_price : 현재가 (float)
        """
        df = pyupbit.get_ohlcv(self.ticker, interval="minute1", count=1)

        current_price = float(df["close"].iloc[0])
        return current_price
        
    @cache_data(ttl=1)
    @try_again(num=4)
    def get_target_date_price(self, interval, date):
        """
        def description : 특정 날짜의 가격 조회

        Parameters
        ----------
        date : 특정 날짜
        Returns
        -------
        close_price : 종가 (float)
        """
        df = pyupbit.get_ohlcv(self.ticker, interval=interval, to=self.adjust_date(date, interval), count=1)

        close_price = float(df["close"].iloc[0])
        return close_price
        
    @cache_data(ttl=1)
    @try_again(num=4)
    def get_current_ohlcv(self):
        """
        def description : 현재가 조회

        Returns
        -------
        ohlcv : ohlcv (dict)
        """
        df = pyupbit.get_ohlcv(self.ticker, interval="minute1", count=1)

        ohlcv = {}
        ohlcv["open"] = float(df["open"].iloc[0])
        ohlcv["high"] = float(df["high"].iloc[0])
        ohlcv["low"] = float(df["low"].iloc[0])
        ohlcv["close"] = float(df["close"].iloc[0])
        ohlcv["volume"] = float(df["volume"].iloc[0])

        return ohlcv

    @cache_data(ttl=1)
    @try_again(num=4)
    def get_target_date_ohlcv(self, date, interval="minute1"):
        """
        def description : 특정 날짜의 가격 조회

        Parameters
        ----------
        date : 특정 날짜
        Returns
        -------
        close_price : 종가 (float)
        """
        df = pyupbit.get_ohlcv(
            self.ticker, interval="minute1", to=self.adjust_date(date, interval), count=1)

        ohlcv = {}
        ohlcv["open"] = float(df["open"].iloc[0])
        ohlcv["high"] = float(df["high"].iloc[0])
        ohlcv["low"] = float(df["low"].iloc[0])
        ohlcv["close"] = float(df["close"].iloc[0])
        ohlcv["volume"] = float(df["volume"].iloc[0])

        return ohlcv
    
    @cache_data(ttl=1)
    @try_again(num=4)
    def get_target_date_prices(self, interval, date, count=2):
        """
        def description : 특정 기간의 가격 조회

        Parameters
        ----------
        interval : 특정 인터벌

        minute1
        minute3
        minute5
        minute10
        minute15
        minute30
        minute60
        minute240
        day
        week
        month

        date : 조회 시작 날짜
        count : 데이터 갯수
        
        Returns
        -------
        close_price : 종가 (float)
        """
        df = pyupbit.get_ohlcv(
            self.ticker, interval=interval, to=self.adjust_date(date, interval), count=count)

        price_list = []
        for close in df["close"]:
            price_list.append(float(close))

        if price_list:
            price_list.reverse()

        return price_list

    @cache_data(ttl=1)
    @try_again(num=4)
    def get_target_interval_price(self, interval):
        """
        def description : 특정 인터벌의 가격 조회

        Parameters
        ----------
        interval : 특정 인터벌

        minute1
        minute3
        minute5
        minute10
        minute15
        minute30
        minute60
        minute240
        day
        week
        month

        Returns
        -------
        close_price : 종가 (float)
        """
        df = pyupbit.get_ohlcv(self.ticker, interval=interval, count=2)

        close_price = float(df["close"].iloc[0])
        return close_price

    @cache_data(ttl=1)
    @try_again(num=4)
    def get_target_interval_prices(self, interval, count=2):
        """
        def description : 특정 인터벌의 가격 조회

        Parameters
        ----------
        interval : 특정 인터벌

        minute1
        minute3
        minute5
        minute10
        minute15
        minute30
        minute60
        minute240
        day
        week
        month

        count : 데이터 갯수
        
        Returns
        -------
        close_price : 종가 (float)
        """
        df = pyupbit.get_ohlcv(self.ticker, interval=interval, count=count)

        price_list = []
        for close in df["close"]:
            price_list.append(float(close))

        if price_list:
            price_list.reverse()

        return price_list
    
    #@cache_data(ttl=1)
    #@reuse_data(required_keys=['date'])
    @try_again(num=4)
    def get_multiple_info(self, interval="day", date=None):
        """
        def description : 
        
        Parameters
        ----------
        interval : 특정 인터벌
        date : 타겟 날짜

        Returns
        -------
        ohlcv : ohlcv (dict)
        """
            
        if date:
            df = pyupbit.get_ohlcv(self.ticker, interval=interval, to=self.adjust_date(date, interval), count=100)
            
        else:
            df = pyupbit.get_ohlcv(self.ticker, interval=interval, count=100)
            
        if df is None:
            raise

        # 2. 거래량 이동 평균 (5분, 20분)
        df["volume_ma5"] = df["volume"].rolling(window=5).mean()  # 5분 이동 평균
        df["volume_ma20"] = df["volume"].rolling(window=20).mean()  # 20분 이동 평균

        # 3. 거래량 비율 (VR)
        df["volume_ratio"] = df["volume"] / df["volume_ma20"]

        # 4. On-Balance Volume (OBV)
        df["obv"] = (df["close"].diff() > 0).astype(int) * df["volume"]
        df["obv"] = df["obv"].cumsum()

        # 5. 볼륨 가중 평균 가격 (VWAP)
        df["cum_volume"] = df["volume"].cumsum()
        df["cum_vwap"] = (df["volume"] * (df["high"] + df["low"] + df["close"]) / 3).cumsum()
        df["vwap"] = df["cum_vwap"] / df["cum_volume"]

        # 6. 거래량 변동성 (표준편차)
        df["volume_volatility"] = df["volume"].rolling(window=10).std()

        # 7. 거래량 스파이크 탐지 (평균 대비 2배 이상)
        df["volume_spike"] = df["volume"] > (df["volume_ma20"] * 2)

        # 8. RSI 계산 (14일 기준)
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))

        # 9. MACD 계산 (12일, 26일 EMA, 9일 Signal Line)
        df["macd"] = df["close"].ewm(span=12, adjust=False).mean() - df["close"].ewm(span=26, adjust=False).mean()
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

        # 10. Bollinger Bands (20일 기준, 표준편차 2배)
        df["band_mid"] = df["close"].rolling(window=20).mean()
        df["stddev"] = df["close"].rolling(window=20).std()
        df["band_upper"] = df["band_mid"] + (df["stddev"] * 2)
        df["band_lower"] = df["band_mid"] - (df["stddev"] * 2)

        # Bollinger Band 위치를 8개 구간으로 나누기
        def bollinger_band_partition(row):
            if row["close"] >= row["band_upper"]:
                return 6
            elif row["close"] >= row["band_upper"] - row["stddev"]:
                return 5
            elif row["close"] >= row["band_mid"]:
                return 4
            elif row["close"] >= row["band_mid"] - row["stddev"]:
                return 3
            elif row["close"] >= row["band_lower"]:
                return 2
            elif row["close"] < row["band_lower"]:
                return 1
            else:
                return 0 # error

        df["bollinger_partition"] = df.apply(bollinger_band_partition, axis=1)
        
        # 11. 종가 리스트 10개
        close_list_df = df["close"].iloc[-10:].tolist()
        close_list = [float(c) for c in close_list_df]

        # 마지막 값을 딕셔너리로 변환
        result_dict = {
            "OPEN": float(df["open"].iloc[-1]),
            "HIGH": float(df["high"].iloc[-1]),
            "LOW": float(df["low"].iloc[-1]),
            "CLOSE": float(df["close"].iloc[-1]),
            "VOLUME": float(df["volume"].iloc[-1]),
            "VOLUME_MA5": float(df["volume_ma5"].iloc[-1]),
            "VOLUME_MA20": float(df["volume_ma20"].iloc[-1]),
            "VOLUME_RATIO": float(df["volume_ratio"].iloc[-1]),
            "OBV": float(df["obv"].iloc[-1]),
            "VWAP": float(df["vwap"].iloc[-1]),
            "VOLUME_VOLATILITY": float(df["volume_volatility"].iloc[-1]),
            "VOLUME_SPIKE": float(df["volume_spike"].iloc[-1]),
            "RSI": float(df["rsi"].iloc[-1]),
            "MACD": float(df["macd"].iloc[-1]),
            "MACD_SIGNAL": float(df["macd_signal"].iloc[-1]),
            "BOLLINGER_PARTITION": int(df["bollinger_partition"].iloc[-1]),
            "BOLLINGER_PARTITION_PREV": int(df["bollinger_partition"].iloc[-2]),
            "CLOSE_LIST": close_list,
        }
        return result_dict
    
    def get_multiple_infos(self, interval="day", date=None):
        """
        def description : 
        
        Parameters
        ----------
        interval : 특정 인터벌
        date : 타겟 날짜

        Returns:
            result_list: 최대 165개의 인터벌별 분석 결과 (dict 리스트 형태)
        """
        
        if date:
            df = pyupbit.get_ohlcv(self.ticker, interval=interval, to=self.adjust_date(date, interval), count=200)
            
        else:
            df = pyupbit.get_ohlcv(self.ticker, interval=interval, count=200)

        if df is None or len(df) < 50:
            raise ValueError("Not enough data")

        # 지표 계산
        df["volume_ma5"] = df["volume"].rolling(window=5).mean()
        df["volume_ma20"] = df["volume"].rolling(window=20).mean()
        df["volume_ratio"] = df["volume"] / df["volume_ma20"]
        df["obv"] = (df["close"].diff() > 0).astype(int) * df["volume"]
        df["obv"] = df["obv"].cumsum()
        df["cum_volume"] = df["volume"].cumsum()
        df["cum_vwap"] = (df["volume"] * (df["high"] + df["low"] + df["close"]) / 3).cumsum()
        df["vwap"] = df["cum_vwap"] / df["cum_volume"]
        df["volume_volatility"] = df["volume"].rolling(window=10).std()
        df["volume_spike"] = df["volume"] > (df["volume_ma20"] * 2)

        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))

        df["macd"] = df["close"].ewm(span=12, adjust=False).mean() - df["close"].ewm(span=26, adjust=False).mean()
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

        df["band_mid"] = df["close"].rolling(window=20).mean()
        df["stddev"] = df["close"].rolling(window=20).std()
        df["band_upper"] = df["band_mid"] + (df["stddev"] * 2)
        df["band_lower"] = df["band_mid"] - (df["stddev"] * 2)

        def bollinger_band_partition(row):
            if row["close"] >= row["band_upper"]:
                return 6
            elif row["close"] >= row["band_upper"] - row["stddev"]:
                return 5
            elif row["close"] >= row["band_mid"]:
                return 4
            elif row["close"] >= row["band_mid"] - row["stddev"]:
                return 3
            elif row["close"] >= row["band_lower"]:
                return 2
            elif row["close"] < row["band_lower"]:
                return 1
            else:
                return 0

        df["bollinger_partition"] = df.apply(bollinger_band_partition, axis=1)

        result_list = []
        for i in range(35, len(df)):
            close_list_df = df["close"].iloc[i - 10 + 1: i + 1]
            if len(close_list_df) < 10:
                continue

            result_dict = {
                "OPEN": float(df["open"].iloc[i]),
                "HIGH": float(df["high"].iloc[i]),
                "LOW": float(df["low"].iloc[i]),
                "CLOSE": float(df["close"].iloc[i]),
                "VOLUME": float(df["volume"].iloc[i]),
                "VOLUME_MA5": float(df["volume_ma5"].iloc[i]),
                "VOLUME_MA20": float(df["volume_ma20"].iloc[i]),
                "VOLUME_RATIO": float(df["volume_ratio"].iloc[i]),
                "OBV": float(df["obv"].iloc[i]),
                "VWAP": float(df["vwap"].iloc[i]),
                "VOLUME_VOLATILITY": float(df["volume_volatility"].iloc[i]),
                "VOLUME_SPIKE": float(df["volume_spike"].iloc[i]),
                "RSI": float(df["rsi"].iloc[i]),
                "MACD": float(df["macd"].iloc[i]),
                "MACD_SIGNAL": float(df["macd_signal"].iloc[i]),
                "BOLLINGER_PARTITION": int(df["bollinger_partition"].iloc[i]),
                "CLOSE_LIST": [float(c) for c in close_list_df],
            }
            result_list.append(result_dict)

        return result_list
            
    @cache_data(ttl=1)
    #@reuse_data(required_keys=['date', 'days', 'interval'])
    @try_again(num=4)
    def get_target_date_future_prices(self, date, days, interval):

        # 기준 시점 datetime으로 변환
        start_time = datetime.fromisoformat(date)

        # n일 뒤 날짜 계산
        end_date = (start_time + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

        # pyupbit에서 필요한 데이터를 분 단위로 가져오기 (최소 데이터 확보)
        if interval == "minute5":
            count = int((1440/5)*days)

        elif interval == "minute15":
            count = int((1440/15)*days)

        elif interval == "minute30":
            count = int((1440/30)*days)

        elif interval == "minute60":
            count = int((1440/60)*days)

        else:
            self.log.info(f"{inspect.currentframe().f_code.co_name}, error : not allowd")
            return

        df = pyupbit.get_ohlcv(
            self.ticker, interval=interval, to=self.adjust_date(end_date, interval), count=count
        )

        # 기준 시점 이후 필요한 시간 간격 정의
        intervals = {
            "on_time": start_time,
            "after_15min": start_time + timedelta(minutes=15),
            "after_30min": start_time + timedelta(minutes=30),
            "after_1hour": start_time + timedelta(hours=1),
            "after_4hour": start_time + timedelta(hours=4),
            "after_12hour": start_time + timedelta(hours=12),
            "after_1day": start_time + timedelta(days=1),
            "after_2day": start_time + timedelta(days=2),
            "after_3day": start_time + timedelta(days=3),
            "after_4day": start_time + timedelta(days=4),
            "after_5day": start_time + timedelta(days=5),
            "after_6day": start_time + timedelta(days=6),
        }

        # 미래 종가 데이터를 저장할 딕셔너리
        future_prices = {}

        # 기준 시간 이후 데이터 필터링
        for label, target_time in intervals.items():
            try:
                # 가장 가까운 타임스탬프 찾기
                nearest_idx = df.index.get_indexer([target_time], method='backfill')[0]
                nearest_time = df.index[nearest_idx]
                future_prices[label] = df.loc[nearest_time, 'close']

            except KeyError:
                # 타임스탬프가 데이터 범위에 없을 경우 처리
                future_prices[label] = None

        return future_prices

    @cache_data(ttl=1)
    @try_again(num=4)
    def get_ma(self, target_term, interval="day"):
        """
        def description : 이동 평균선 조회

        Parameters
        ----------
        target_term : 이동평균선 타겟 텀 (int)

        Returns
        -------
        없음

        explain sample
        -------

        df["close"].rolling(5).mean().iloc[-1] :
        종가 중 5개를 추출하여 각 평균을 내고 마지막 항목을 추출 ==> 5일 이동평균선

        - df["close"].rolling(5)
        종가 시리즈 객체에서 rolling(windows=5) 메서드를 통해 위에서부터 5개의 데이터 묶음을 추출

        - .mean()
        평균 계산

        - .iloc[-1] - 마지막 항목 추출
        """
        df = pyupbit.get_ohlcv(self.ticker, interval=interval, count=target_term)
        ma = df["close"].rolling(target_term).mean().iloc[-1]
        return ma

    @cache_data(ttl=1)
    @try_again(num=4)
    def get_bollinger_bands(self, interval="day"):
        """
        def description : 볼린저밴드 조회

        Parameters
        ----------
        interval : 특정 인터벌

        minute1
        minute3
        minute5
        minute10
        minute15
        minute30
        minute60
        minute240
        day
        week
        month

        Returns
        -------
        response_obj : 결과 (dict)
        """
        # 20개 종가 조회
        df = pyupbit.get_ohlcv(self.ticker, interval=interval, count=20)
        close_price_list = df["close"]

        # 평균
        mean = sum(close_price_list) / len(close_price_list)

        # 분산
        vsum = 0
        for val in close_price_list:
            vsum = vsum + (val - mean)**2

        variance = vsum / len(close_price_list)

        # 표준편차
        std = math.sqrt(variance)

        # 볼린저 상중하단 계산
        top = mean + (std * 2)
        q3 = mean + (std)
        mid = mean
        q1 = mean - (std)
        bot = mean - (std * 2)

        response_obj = {
            "top": top,
            "q3": q3,
            "mid": mid,
            "q1": q1,
            "bot": bot
        }
        return response_obj

    @cache_data(ttl=1)
    def get_bollinger_state(self, interval="day", current_price=None):
        """
        def description : 볼린져 스테이트 계산

        Parameters
        ----------
        interval : 특정 인터벌

        minute1
        minute3
        minute5
        minute10
        minute15
        minute30
        minute60
        minute240
        day
        week
        month

        Returns
        -------
        bollinger_state : 볼린저 상태 (str)

        over_top : 상단 볼린저 위
        over_mid : 중단 볼린저 위
        below_mid : 중단 볼린저 아래
        below_bot : 하단 볼린저 아래
        """

        # 볼린저 값 및 현재가 산출
        bollinger_bands = self.get_bollinger_bands(interval=interval)

        if not current_price:
            current_price = self.get_current_price()

        # 상태 계산
        bollinger_state = None
        if current_price >= bollinger_bands["top"]:
            bollinger_state = "over_top"

        elif current_price > bollinger_bands["q3"]  and current_price < bollinger_bands["top"]:
            bollinger_state = "over_qtr_3"

        elif current_price > bollinger_bands["mid"] and current_price <= bollinger_bands["top"]:
            bollinger_state = "over_mid"

        elif current_price < bollinger_bands["q1"] and current_price > bollinger_bands["bot"]:
            bollinger_state = "below_qtr_1"

        elif current_price < bollinger_bands["mid"] and current_price >= bollinger_bands["bot"]:
            bollinger_state = "below_mid"

        elif current_price <= bollinger_bands["bot"]:
            bollinger_state = "below_bot"

        response = {
            "bollinger_state": bollinger_state,
            "top": bollinger_bands["top"],
            "mid": bollinger_bands["mid"],
            "bot": bollinger_bands["bot"]
        }
        return response


    """
    Auth 
    """
    @try_again(num=4)
    def get_krw_balance(self):
        """
        def description : 원화 잔고 조회

        Returns
        -------
        krw_balances : 원화
        """
        
        balances = self.upbit.get_balances()

        krw_balance = 0
        for balance in balances:
            if balance['currency'] == 'KRW':
                krw_balance = float(balance['balance'])

        return krw_balance

    @try_again(num=4)
    def get_ticker_balance(self):
        """
        def description : 특정 잔고 정보 조회

        Returns
        -------
        my_target_balance : 타겟 티커에 대한 잔고 정보
        """
        all_my_balance = self.get_all_my_balance()

        my_target_balance = 0
        for my_balance in all_my_balance:
            if my_balance["ticker"] == self.ticker_org:
                my_target_balance = float(my_balance["balance"])
                break

        return my_target_balance
    
    @try_again(num=4)
    def get_all_my_balance(self):
        """
        def description : 전체 잔고 정보 조회

        Returns
        -------
        balance_list : 잔고 딕셔너리 array
        """
        
        balances = self.upbit.get_balances()

        balance_dict = {}
        balance_list = []
        for b in balances:
            if b["balance"] is not None:
                balance_dict = {
                    "ticker": b["currency"],
                    "balance": float(b["balance"])
                }
                balance_list.append(balance_dict)

        return balance_list
    
    @try_again(num=4)
    def get_avg_price(self):
        """
        def description : 티커 평단 조회

        Returns
        -------
        avg_price : 평단
        """
        avg_price = self.upbit.get_avg_buy_price(self.ticker)
        return avg_price
        
    def buy_coin(self, krw_order):
        """
        def description : 코인 매수

        Parameters
        ----------
        krw_order : 코인 원화 주문 가격

        Returns
        -------
        boolean
        """
        
        fees = 0.0005
        buy_result = self.upbit.buy_market_order(
            self.ticker, krw_order * (1-fees))
        
        # 성공
        if "uuid" in buy_result:
            if "price" in buy_result:
                if "reserved_fee" in buy_result: 
                    return buy_result

        # 실패
        self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(buy_result)}")
        raise

    def sell_coin(self, krw_order="All", current_price=None):
        """
        def description : 코인 매도
        

        Parameters
        ----------
        krw_order : 코인 원화 주문 가격

        Returns
        -------
        response_object : 결과 오브젝트(dict)
        """
        
        org_ticker = self.ticker

        # 전액 매도
        if krw_order == "all":
            self.ticker = self.ticker.replace("KRW-", "")
            ticker_balance = self.get_ticker_balance()
            self.ticker = org_ticker

            # 예외처리
            if krw_order > ticker_balance:
                self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : ticker 보유량이 부족합니다.")
                raise

        # 분할 매도
        else:
            ticker_balance = krw_order

        sell_result = self.upbit.sell_market_order(self.ticker, ticker_balance)

        # 매매 성공
        if "uuid" in sell_result:
            if "volume" in sell_result:
                if "reserved_fee" in sell_result: 
                    return sell_result

        # 실패
        self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(sell_result)}")
        raise
    
    """
    Calculates 
    """
    def adjust_date(self, date: str, interval: str) -> str:
        """
        def description : 날짜 보정
        upbit ohlcv 호출 시 날짜가 지정되는 경우 당일(당시간)의 데이터를 제외하기 때문에 인터벌 만큼 시간을 추가
        
        Parameters
        ----------
        
        date : 날짜
        interval : 인터벌
        
        Returns
        -------
        date_adjusted : 보정 된 날짜
        """
        
        dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

        if interval == "minute1":
            dt += timedelta(minutes=1)
        elif interval == "minute3":
            dt += timedelta(minutes=3)
        elif interval == "minute5":
            dt += timedelta(minutes=5)
        elif interval == "minute10":
            dt += timedelta(minutes=10)
        elif interval == "minute15":
            dt += timedelta(minutes=15)
        elif interval == "minute30":
            dt += timedelta(minutes=30)
        elif interval == "minute60":
            dt += timedelta(hours=1)
        elif interval == "minute240":
            dt += timedelta(hours=4)
        elif interval == "day":
            dt += timedelta(days=1)
        elif interval == "week":
            dt += timedelta(weeks=1)
        elif interval == "month":
            year = dt.year + (dt.month // 12)
            month = dt.month % 12 + 1
            dt = datetime(year, month, 1)
        else:
            raise ValueError(f"Unknown interval: {interval}")

        date_adjusted = dt.strftime("%Y-%m-%d %H:%M:%S")
        return date_adjusted

    def get_rsi(self, close_prices, window=14):

        if len(close_prices) < window + 1:
            return
        
        gains = []
        losses = []
        
        # 첫 번째 윈도우에서 평균 상승과 평균 하락을 계산
        for i in range(1, window + 1):
            change = close_prices[i] - close_prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / window
        avg_loss = sum(losses) / window
        
        # RS와 RSI 초기화
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        
        rsi_values = [None] * window  # 첫 윈도우 동안은 RSI 값을 None으로 설정
        rsi_values.append(rsi)
        
        # 이후의 RSI 값들을 계산
        for i in range(window + 1, len(close_prices)):
            change = close_prices[i] - close_prices[i - 1]
            gain = max(change, 0)
            loss = max(-change, 0)
            
            avg_gain = (avg_gain * (window - 1) + gain) / window
            avg_loss = (avg_loss * (window - 1) + loss) / window
            
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        return rsi_values[-1]

    def calculate_ema(self, close_prices, days):
        """Calculate Exponential Moving Average (EMA)"""
        ema = [sum(close_prices[:days]) / days]  # 초기 EMA는 단순 이동 평균(SMA)로 시작
        multiplier = 2 / (days + 1)
        
        for price in close_prices[days:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema

    def get_macd(self, close_prices, short_window=12, long_window=26, signal_window=9):
        """Calculate MACD, Signal Line, and Histogram"""
        if len(close_prices) < long_window:
            return

        short_ema = self.calculate_ema(close_prices, short_window)
        long_ema = self.calculate_ema(close_prices, long_window)
        
        # 두 EMA의 차이로 MACD 라인을 계산
        macd_line = [short - long for short, long in zip(short_ema[-len(long_ema):], long_ema)]
        
        # 시그널 라인 계산
        signal_line = self.calculate_ema(macd_line, signal_window)
        
        # 히스토그램 계산
        histogram = [m - s for m, s in zip(macd_line[-len(signal_line):], signal_line)]
        
        return macd_line[-1]
    
    def get_minimum_price(self, price_list):
        """
        def description : 최저가 계산

        Parameters
        ----------
        price_list : 대상 가격 리스트

        Returns
        -------
        minimum_price : 최저가
        """

        minimum_price = price_list[0]
        for i in range(1,len(price_list)):
            if minimum_price > price_list[i]:
                minimum_price = price_list[i]

        return minimum_price
    
    def get_maximum_price(self, price_list):
        """
        def description : 최고가 계산

        Parameters
        ----------
        price_list : 대상 가격 리스트

        Returns
        -------
        maximum_price : 최고가
        """

        maximum_price = price_list[0]
        for i in range(1,len(price_list)):
            if maximum_price < price_list[i]:
                maximum_price = price_list[i]

        return maximum_price
    
    def get_price_diff_rate(self, from_price, to_price):
        """
        def description :가격 변화율 계산


        Parameters
        ----------
        from_price : 시작점 종가
        to_price : 종료점 종가

        Returns
        -------
        change_rate : 현재변화율 (float)
        """
        if from_price == 0 : 
            self.log.info(f"from_price가 0입니다.")
            raise
            
        if to_price == 0 : 
            self.log.info(f"to_price가 0입니다.")
            raise

        change_rate = ((to_price - from_price) / from_price) * 100
        change_rate = round(change_rate, 4)
        return change_rate
    
upbit_module = Upbit()
