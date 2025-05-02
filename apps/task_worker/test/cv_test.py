from shares.modules.log import Log
from shares.modules.postgres import *
from shares.modules.redis import *
from shares.modules.slack import *
from shares.modules.upbit import *
from shares.modules.binance import *

from shares.dao.trade_result_dao import TradeResultDao
from shares.functions.common_function import *

import os
import time
import datetime



class Test():

    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.postgres = Postgres()
        self.redis = Redis()
        self.slack = Slack(channel="#coinvillage")
        self.upbit = Upbit()
        self.binance = Binance()
        
        self.trade_result_dao = TradeResultDao()
        
        self.pref_slack_msg_box = "slack_msg_box"
    
        
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

                        percentage_standard = None
                        if "min" in key: 
                            percentage_standard = 0.5
                        elif "hour" in key: 
                            percentage_standard = 1
                        elif "day" in key: 
                            percentage_standard = 2

                        percentage_change = ((future_price - target_price) / target_price) * 100
                        if percentage_change > percentage_standard:
                            res[f"change_{key}"] = "up"

                        elif percentage_change < -percentage_standard:
                            res[f"change_{key}"]  = "down"

                        else:
                            res[f"change_{key}"]  = "sideways"
                        
                        if is_by_prev: 
                            target_price = future_price 
        
        return res
                            
    def run(self):
        
        # order_dt = str(generate_now_date())
        # self.ticker = "KRW-TEST"
        # self.pref_order_last = "testsestse"
        
        # self.redis.hupd_date(self.pref_order_last, self.ticker, order_dt) 
        
        # time.sleep(1)
        
        # self.order_last = self.redis.hget_data(self.pref_order_last, self.ticker)   
        
        # self.log.info(f"self.order_last : {self.order_last}")
        # self.log.info(f"self.order_last : {type(self.order_last)}")
        
        # self.order_last = datetime.datetime.strptime(self.order_last, "%Y-%m-%d %H:%M:%S")
        
        # self.log.info(f"self.order_last : {self.order_last}")
        # self.log.info(f"self.order_last : {type(self.order_last)}")
        
                
        # now = datetime.datetime.now()
        # elapsed = now - self.order_last
        # n = 3
        # if elapsed >= timedelta(hours=n):
        
        
        return 
        
        self.runnable_services_seq = 1 
        
        # 매매 진행
        order_dt = str(generate_now_date())
        self.upbit.set_ticker("KRW-BTC")
        
        msg = None
        try:
            buy_result = self.upbit.buy_coin(10000)
                    
            self.trade_result_dao.insert_trade_result(
                trade_exchange="upbit",
                trade_ticker="KRW-BTC",
                uuid=buy_result.get("uuid"),
                ord_side=buy_result.get("side"),
                ord_type=buy_result.get("ord_type"),
                price=buy_result.get("price"),
                reserved_fee=buy_result.get("reserved_fee"),
                remaining_fee=buy_result.get("remaining_fee"),
                paid_fee=buy_result.get("paid_fee"),
                state=buy_result.get("state"),
                locked=buy_result.get("locked"),
                executed_volume=buy_result.get("executed_volume"),
                order_dt=order_dt,
                trade_dt=str(buy_result.get("created_at")),
                runnable_services_seq=self.runnable_services_seq
            )
            
            msg = f"매수에 성공하였습니다, \n 티커 : {self.ticker} ,\n 주문가 : {round(float(buy_result['price']), 2)}, 수수료 : {round(float(buy_result['reserved_fee']))}"
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
          
        
        self.redis.save_msg_on_Q(f"{self.slack_post_prefix} : {self.ticker}의 매수를 성공하였습니다. \n {msg} \n\n")
        return 
        
        
        return 
        
        # current_price = 2554000.0
        # bbbb_price = 2628000.0
        
        # self.log.info(f"price_diff_rate : {self.upbit.get_price_diff_rate(current_price, bbbb_price)}")
            
        # return 
        # datetime_list = generate_datetimes_by_min(terms=90, interval=5, n_days_ago=7) # 수집 구간 datetime 리스트 생성
        # self.log.info(f"datetime_list0 : {datetime_list[0]}")
        # self.log.info(f"datetime_list-1 : {datetime_list[-1]}")
        
        """
282536	KRW-BTC	2025-04-21 15:10:00.000 +0900	125350000.0	125092000.0	125200000.0	125157000.0	125093000.0	127044000.0	134194000.0	132779000.0	134386000.0	136600000.0	136102000.0	sideways	sideways	sideways	sideways	sideways	sideways	up	sideways	sideways	sideways	sideways	125350000.0	125092000.0	125200000.0	125157000.0	125093000.0	127044000.0	134194000.0	132779000.0	134386000.0	136600000.0	136102000.0	sideways	sideways	sideways	sideways	sideways	sideways	up	up	up	up	up
282534	KRW-BTC	2025-04-21 15:05:00.000 +0900	125296000.0	125181000.0	125406000.0	125190000.0	124989000.0	127110000.0	134180000.0	132789000.0	134427000.0	136522000.0	136112000.0	sideways	sideways	sideways	sideways	sideways	sideways	up	sideways	sideways	sideways	sideways	125296000.0	125181000.0	125406000.0	125190000.0	124989000.0	127110000.0	134180000.0	132789000.0	134427000.0	136522000.0	136112000.0	sideways	sideways	sideways	sideways	sideways	sideways	up	up	up	up	up
282532	KRW-BTC	2025-04-21 15:00:00.000 +0900	125309000.0	125301000.0	125417000.0	125300000.0	124936000.0	127271000.0	133968000.0	132805000.0	134216000.0	136508000.0	135996000.0	sideways	sideways	sideways	sideways	sideways	sideways	up	sideways	sideways	sideways	sideways	125309000.0	125301000.0	125417000.0	125300000.0	124936000.0	127271000.0	133968000.0	132805000.0	134216000.0	136508000.0	135996000.0	sideways	sideways	sideways	sideways	sideways	sideways	up	up	up	up	up
282530	KRW-BTC	2025-04-21 14:55:00.000 +0900	125259000.0	125350000.0	125400000.0	125411000.0	124835000.0	127250000.0	133840000.0	132667000.0	134159000.0	136584000.0	135970000.0	sideways	sideways	sideways	sideways	sideways	sideways	up	sideways	sideways	sideways	sideways	125259000.0	125350000.0	125400000.0	125411000.0	124835000.0	127250000.0	133840000.0	132667000.0	134159000.0	136584000.0	135970000.0	sideways	sideways	sideways	sideways	sideways	sideways	up	up	up	up	up
        """
        
        # # tick_datetime 기준으로 미래 값 조회 
        
        # self.upbit.set_ticker("KRW-BTC")
        
        # tick_datetime = "2025-04-17 15:40:00"
        # future_prices = self.upbit.get_target_date_future_prices(
        #     date = tick_datetime,
        #     days = 7, 
        #     interval = "minute5", 
        # )
        
        # ontime_price = future_prices["on_time"]
        # self.log.info(f"ontime_price : {ontime_price}")
        
        # updown = self.decide_up_down_side(future_prices, is_by_prev = False)
        
        # self.log.info(f"updown : {updown}")
        
        a = 125350000
        b = 125092000
        
        change_rate = ((b - a) / a) * 100
        change_rate = round(change_rate, 4)
        self.log.info(f"change_rate : {change_rate}")
        
        return 
        # """
        # {
        # ontime_price : 122435000.0
        # updown : {
        # 'price_after_15min': 122528000.0, 
        # 'price_after_30min': 122344000.0, 
        # 'price_after_1hour': 122400000.0, 
        # 'price_after_4hour': 121967000.0, 
        # 'price_after_12hour': 123013000.0, 
        # 'price_after_1day': 122527000.0, 
        # 'price_after_2day': 122823000.0, 
        # 'price_after_3day': 122850000.0, 
        # 'price_after_4day': 125092000.0, 
        # 'price_after_5day': 126892000.0, 
        # 'price_after_6day': 134047000.0, 
        # 'change_after_15min': 'sideways', 
        # 'change_after_30min': 'sideways', 
        # 'change_after_1hour': 'sideways', 
        # 'change_after_4hour': 'sideways', 
        # 'change_after_12hour': 'sideways', 
        # 'change_after_1day': 'sideways', 
        # 'change_after_2day': 'sideways', 
        # 'change_after_3day': 'sideways', 
        # 'change_after_4day': 'up', 
        # 'change_after_5day': 'up', 
        # 'change_after_6day': 'up'}
        # """
        # return
         
        
        
        # import pyupbit
        # df = pyupbit.get_ohlcv("KRW-BTC", interval="minute5", to="2025-04-18 09:50:00", count=100)
        
        # a = float(df["close"].iloc[0])
        # b = float(df["close"].iloc[-1])
        
        # 122490000.0
        
        # target_date_price : 122490000.0
        
        # self.log.info(f"a : {a}")
        # self.log.info(f"b : {b}")
        
        
        # 'CLOSE_LIST': [122665000.0, 122728000.0, 122782000.0, 122731000.0, 122610000.0, 122569000.0, 122557000.0, 122532000.0, 122502000.0, 122490000.0]
        
        # """
        # 2025-04-17 01:45:00	3	122985000.0	123199000.0	122942000.0	123045000.0	1.81167007	3.098011808	6.364101659	0.28467019652930403	263.93505918000005	122293826.63531724	1.844446578242326	0.0	46.71953857245854	119978.5028654635	156661.696308399	4	[123104000.0, 123119000.0, 123136000.0, 123000000.0, 122911000.0, 122911000.0, 123015000.0, 122826000.0, 122985000.0, 123045000.0]
        # 2025-04-17 01:40:00	3	122823000.0	122997000.0	122768000.0	122985000.0	7.32633383	3.3427319580000003	6.4682256595	1.1326651566708532	273.57870922000006	122274715.52361616	2.539262372195025	0.0	49.65940054495913	121725.3575567007	166028.814256741	4	[122811000.0, 123104000.0, 123119000.0, 123136000.0, 123000000.0, 122911000.0, 122911000.0, 123015000.0, 122826000.0, 122985000.0]
        # 2025-04-17 01:35:00	3	123015000.0	123016000.0	122777000.0	122826000.0	2.80593189	2.4069588580000003	6.280383249	0.4467771756519441	280.5160733700001	122257725.38337067	2.3622502276819786	0.0	37.01298701298702	128262.36817130446	177290.89333473204	3	[122817000.0, 122811000.0, 123104000.0, 123119000.0, 123136000.0, 123000000.0, 122911000.0, 122911000.0, 123015000.0, 122826000.0]
        # 2025-04-17 01:30:00	3	122911000.0	123017000.0	122911000.0	123015000.0	0.67934046	2.330441738	6.390114469999999	0.10631115658245792	285.42145645000005	122237412.78217044	2.3620956634600465	0.0	42.741935483870975	150839.63608172536	189636.0797346857	4	[122942000.0, 122817000.0, 122811000.0, 123104000.0, 123119000.0, 123136000.0, 123000000.0, 122911000.0, 122911000.0, 123015000.0]
        # """
        
        
        # self.upbit.set_ticker("KRW-BTC")
        # target_date_price = self.upbit.get_target_date_price("minute5", "2025-04-24 11:30:00")
        # self.log.info(f"target_date_price : {target_date_price}")
        
        
        # multiple_info = self.upbit.get_multiple_info("minute5", "2025-04-17 01:45:00")
        # self.log.info(f"multiple_info : {multiple_info}")
        
        #eturn 
        
        # import pyupbit
        
        
        # date = "2025-01-01 00:00:00"
        # df = pyupbit.get_ohlcv("KRW-BTC", interval="minute5", to=date, count=1)
        
        # df_dict = df.to_dict(orient='records')  # 각 row를 dict로
        # for row in df_dict:
        #     self.log.info(row)
        # return 
        
        
        self.upbit.set_ticker("KRW-BTC")
        
        date = "2025-01-01 00:00:00"
        
        multiple_info = self.upbit.get_multiple_info(interval="minute5", date=date)
        self.log.info(f"multiple_info : {multiple_info}")
        
        
        multiple_infos = self.upbit.get_multiple_infos(interval="minute5", date=date)
        self.log.info(f"multiple_infos : {multiple_infos}")
        pass
        
        # import websocket
        # import json

        # def on_open(ws):
        #     # 요청할 티커 정보 설정 (예: BTC/KRW, ETH/KRW)
        #     params = [{"ticket": "test"},
        #             {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH", "KRW-SOL",  "KRW-LINK",  "KRW-SUI"]}]

        #     ws.send(json.dumps(params))

        # def on_close(ws, close_status_code, close_msg):
        #     self.log.info("WebSocket closed")
            
        # def on_error(ws, error):
        #     self.log.info("Error:", error)
                
        # def on_message(ws, message):
        #     data = json.loads(message)
        #     self.log.info(data)  # 받은 데이터 출력
            
        #     # check_remaining_req()
                
        # def handle_ticker(self):
        #     return

        # # def check_remaining_req():
        # #     url = "https://api.upbit.com/v1/ticker?markets=KRW-BTC"
        # #     response = requests.get(url)
        # #     remaining_req = response.headers.get("Remaining-Req")
            
        # #     # 남은 수가 적으면 대기
        # #     if int(remaining_req) < 1:
        # #         self.log.info(f"잔여 요청 수: {remaining_req}")
        # #         time.sleep(1.5)  # 초당 제한 리셋을 기다림
        # #     return


        # # WebSocket 연결 URL
        # socket_url = "wss://api.upbit.com/websocket/v1"

        # ws = websocket.WebSocketApp(socket_url,
        #                             on_message=on_message,
        #                             on_error=on_error,
        #                             on_close=on_close)
        # ws.on_open = on_open
        
        # # WebSocket 실행
        # ws.run_forever()
        
        # self.log.info("TEST START")
        
        # # --- POSTGRES TEST
        # query = "SELECT 1 as TEST"
        # res = self.postgres.read_all(query) 
        # self.log.info(f"POSTGRES TEST : {res}")
        
        # # --- REDIS TEST
        # self.redis.set_data("test", "test", 1)
        # res = self.redis.get_data("test")
        # self.log.info(f"REDIS TEST : {res}")
        
        # # --- SLACK TEST
        # self.slack.post_msg("SLACK TEST")
        # self.log.info(f"SLACK TEST : {True}")
        
        # # --- UPBIT TEST, NO AUTH 
        # self.upbit.set_ticker("KRW-BTC")
        # current_price = self.upbit.get_current_price()
        # self.log.info(f"UPBIT TEST, NO AUTH : {current_price}")
        
        # # --- UPBIT TEST, AUTH
        # all_my_balance = self.upbit.get_all_my_balance()
        # self.log.info(f"UPBIT TEST, AUTH : {all_my_balance}")
        
        # # --- BINANCE TEST
        # self.binance.set_ticker("BTCUSDT")
        # current_price = self.binance.get_current_price()
        # self.log.info(f"BINANCE TEST, NO AUTH: {current_price}")
        
        # self.log.info("TEST END")
        
        
        
        # # --- UPBIT STRESS TEST
        # self.upbit.set_ticker("KRW-BTC")
        # multiple_info = self.upbit.get_multiple_info(date='2025-04-03 00:00:00') 
        # self.log.info(f"multiple_info : {multiple_info}")
        
        # multiple_info = self.upbit.get_multiple_info() 
        # self.log.info(f"multiple_info : {multiple_info}")
        # time.sleep(1)
        
        # multiple_info = self.upbit.get_multiple_info()
        # self.log.info(f"multiple_info : {multiple_info}")
        
        # multiple_info = self.upbit.get_multiple_info() 
        # self.log.info(f"multiple_info : {multiple_info}")
        # time.sleep(1)
        
        # self.upbit.set_ticker("KRW-BTC")
        # multiple_info = self.upbit.get_multiple_info(date='2025-04-03 00:00:00') 
        # self.log.info(f"multiple_info : {multiple_info}")
        
                
        # import pyupbit
        # import pandas as pd
        # import numpy as np

        # def analysis(ticker="KRW-BTC", interval="minute60", weeks=8):
            
        #     def weekly_stats(week_df):
        #         if week_df.empty:
        #             return {
        #                 "전체 평균 거래량": pd.Series(dtype=float),
        #                 "양봉 평균 거래량": pd.Series(dtype=float),
        #                 "음봉 평균 거래량": pd.Series(dtype=float)
        #             }

        #         weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
        #         return {
        #             "전체 평균 거래량": week_df.groupby("weekday")["volume"].mean().rename(index=lambda x: weekday_names[x]),
        #             "양봉 평균 거래량": week_df[week_df["is_bullish"]].groupby("weekday")["volume"].mean().rename(index=lambda x: weekday_names[x]),
        #             "음봉 평균 거래량": week_df[~week_df["is_bullish"]].groupby("weekday")["volume"].mean().rename(index=lambda x: weekday_names[x])
        #         }

        #     def hourly_stats(data):
        #         bullish_volumes = data[data["is_bullish"]].groupby("hour")["volume"].mean()
        #         bearish_volumes = data[~data["is_bullish"]].groupby("hour")["volume"].mean()
        #         total = data.groupby("hour")["volume"].mean()

        #         return {
        #             "전체 거래량 상위 4개": total.nlargest(4).to_dict(),
        #             "전체 거래량 하위 4개": total.nsmallest(4).to_dict(),
        #             "양대 거래량 상위 4개": bullish_volumes.nlargest(4).to_dict(),
        #             "양대 거래량 하위 4개": bullish_volumes.nsmallest(4).to_dict(),
        #             "음대 거래량 상위 4개": bearish_volumes.nlargest(4).to_dict(),
        #             "음대 거래량 하위 4개": bearish_volumes.nsmallest(4).to_dict(),
        #         }

        #     count = weeks * 7 * 24  # 8주치 60분봉 데이터 (1344개)
        #     df = pyupbit.get_ohlcv(ticker, interval=interval, count=count)
        
        #     # # 1주일(168시간) 동안의 OHLCV 데이터 가져오기
        #     # df = pyupbit.get_ohlcv(ticker, interval=interval, count=168)

        #     if df is None:
        #         raise ValueError("데이터를 가져올 수 없습니다.")

        #     df["hour"] = df.index.hour  # 시간대 추출
        #     df["is_bullish"] = df["close"] > df["open"]  # 양대 여부 (True: 양대, False: 음대)

        #     df = df.copy()
        #     df["date"] = df.index.date
        #     df["weekday"] = df.index.dayofweek  # 0=월 ~ 6=일
        #     weekday_map = {
        #         0: "월", 1: "화", 2: "수", 3: "목",
        #         4: "금", 5: "토", 6: "일"
        #     }
        #     df["weekday_name"] = df["weekday"].map(weekday_map)
        #     df["is_bullish"] = df["close"] > df["open"]  # 양봉 여부 (True: 양봉, False: 음봉)

        #     # 날짜 기준으로 몇 주차인지 계산 (최근 날짜 기준 역순)
        #     df["week_num"] = ((df.index - df.index[-1]).days // 7) * -1
            
        #     # 주별 평균 거래량 계산
        #     # weekly_volume = df.groupby("week_num")["volume"].mean()

        #     # # 📆 이상치 탐지 (IQR 방법 사용)
        #     # Q1 = weekly_volume.quantile(0.25)
        #     # Q3 = weekly_volume.quantile(0.75)
        #     # IQR = Q3 - Q1
        #     # outlier_threshold = Q3 + 1.5 * IQR  # 이상치 기준값
        #     # outlier_weeks = weekly_volume[weekly_volume > outlier_threshold]  # 이상치 주차 필터링

        #     # 📊 상승(양봉) / 하락(음봉) 캔들 별도 집계
        #     bullish_pivot = df[df["is_bullish"]].groupby(["week_num", "weekday"])["volume"].mean().reset_index()
        #     bearish_pivot = df[~df["is_bullish"]].groupby(["week_num", "weekday"])["volume"].mean().reset_index()

        #     # 요일 이름 매핑
        #     weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
        #     bullish_pivot["weekday_name"] = bullish_pivot["weekday"].map(lambda x: weekday_names[x])
        #     bearish_pivot["weekday_name"] = bearish_pivot["weekday"].map(lambda x: weekday_names[x])

        #     # 전체 요일별 평균 (양봉 & 음봉)
        #     total_overall = df.groupby("weekday_name")["volume"].mean().sort_values(ascending=False)
        #     bullish_overall = bullish_pivot.groupby("weekday_name")["volume"].mean().sort_values(ascending=False)
        #     bearish_overall = bearish_pivot.groupby("weekday_name")["volume"].mean().sort_values(ascending=False)

        #     # 날짜 기준 계산
        #     today = datetime.datetime.now().date()
        #     monday_this_week = today - timedelta(days=today.weekday())  # 이번주 월요일
        #     last_week_start = monday_this_week - timedelta(weeks=1)
        #     last_week_end = monday_this_week - timedelta(seconds=1)

        #     prev_week_start = monday_this_week - timedelta(weeks=2)
        #     prev_week_end = last_week_start - timedelta(seconds=1)

        #     # 필터링
        #     last_week_df = df[(df.index.date >= last_week_start) & (df.index.date <= last_week_end)]
        #     prev_week_df = df[(df.index.date >= prev_week_start) & (df.index.date <= prev_week_end)]
                
        #     # 날짜 기준 주차 계산
        #     df["hour"] = df.index.hour  # 시간대 추출
        #     df["is_bullish"] = df["close"] > df["open"]  # 양봉 여부 (True: 양대, False: 음대)
        #     monday_this_week = today - timedelta(days=today.weekday())  # 이번 주 월요일
        #     last_week_start = monday_this_week - timedelta(weeks=1)
        #     last_week_end = monday_this_week - timedelta(seconds=1)
        #     prev_week_start = monday_this_week - timedelta(weeks=2)
        #     prev_week_end = last_week_start - timedelta(seconds=1)
        #     full_8_weeks_df = df
        #     last_week_df = df[(df.index.date >= last_week_start) & (df.index.date <= last_week_end)]
        #     prev_week_df = df[(df.index.date >= prev_week_start) & (df.index.date <= prev_week_end)]
            
        #     return {
        #         #"📆 이상치 주차 (평균 거래량 튄 주)": outlier_weeks,
        #         "📊 주별 요일 거래량 평균 (양봉)": bullish_pivot,
        #         "📊 주별 요일 거래량 평균 (음봉)": bearish_pivot,
        #         "🔄 전체 요일별 평균 거래량": total_overall,
        #         "🔄 전체 요일별 평균 거래량 (양봉)": bullish_overall,
        #         "🔄 전체 요일별 평균 거래량 (음봉)": bearish_overall,
        #         "📆 지난주 (-1주) 거래량": weekly_stats(last_week_df),
        #         "📆 지지난주 (-2주) 거래량": weekly_stats(prev_week_df),
        #         "📊 최근 8주 전체": hourly_stats(full_8_weeks_df),
        #         "📆 지난주 (-1주)": hourly_stats(last_week_df),
        #         "📆 지지난주 (-2주)": hourly_stats(prev_week_df),
        #     }

        # # 사용 예시
        # result = analysis()
        # print("📆 이상치 주차 (거래량이 튄 주):\n", result["📆 이상치 주차 (평균 거래량 튄 주)"])
        # print("\n🔄 전체 요일별 평균 거래량:\n", result["🔄 전체 요일별 평균 거래량"])
        # print("\n🔄 전체 요일별 평균 거래량 (양봉):\n", result["🔄 전체 요일별 평균 거래량 (양봉)"])
        # print("\n🔄 전체 요일별 평균 거래량 (음봉):\n", result["🔄 전체 요일별 평균 거래량 (음봉)"])
        # print("\n📆 지지난주 (-2주) 거래량:\n", result["📆 지지난주 (-2주) 거래량"])
        # print("📆 지난주 (-1주) 거래량:\n", result["📆 지난주 (-1주) 거래량"])
        
        # print("\n📊 최근 8주 전체:\n", result["📊 최근 8주 전체"])
        # print("\n📆 지지난주 (-2주):\n", result["📆 지지난주 (-2주)"])
        # print("\n📆 지난주 (-1주):\n", result["📆 지난주 (-1주)"])
        
                
        # class UpbitSocket():

        #     def __init__(self):
        #         self.socket_url = "wss://api.upbit.com/websocket/v1"
        #         self.ticker_list = []
            
        #     def set_ticker_list(self, ticker_list):
        #         self.ticker_list = ticker_list
        #         return self.ticker_list
                
        #     # def on_message(self, ws, message):
        #     #     data = json.loads(message)
        #     #     return data

        #     def on_open(self, ws):
                
        #         # 요청할 티커 정보 설정 (예: BTC/KRW, ETH/KRW)
        #         params = [{"ticket": "test"},
        #                 {"type": "ticker", "codes": self.ticker_list}]

        #         ws.send(json.dumps(params))

        #     def on_close(self, ws, close_status_code, close_msg):
        #         self.log.info("WebSocket closed")

        #     def on_error(self, ws, error):
        #         self.log.info("Error:", error)
        #         self.reconnect()

        #     def reconnect(self):
        #         time.sleep(5)
        #         self.run()
                    
        #     def run(self, business_service):
                
        #         # WebSocket 연결 URL
        #         ws = websocket.WebSocketApp(self.socket_url,
        #                                     on_message=business_service,
        #                                     on_error=self.on_error,
        #                                     on_close=self.on_close)
        #         ws.on_open = self.on_open
                
        #         # WebSocket 실행
        #         ws.run_forever()