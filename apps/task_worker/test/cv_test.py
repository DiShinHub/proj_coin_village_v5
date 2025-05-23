from shares.modules.log import Log
from shares.modules.postgres import *
from shares.modules.redis import *
from shares.modules.slack import *
from shares.modules.upbit import *
from shares.modules.binance import *
from shares.modules.minio import *
from shares.modules.candle_pattern import *

from shares.dao.trade_result_dao import TradeResultDao
from shares.dao.upbit_transaction_dao import UpbitTransactionDao
from shares.functions.common_function import *

from collections import defaultdict
        
import pandas as pd

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
        self.minio = MinioModule()
        self.candle_pattern = CandlePatterns()
        
        self.trade_result_dao = TradeResultDao()
        self.upbit_transaction_dao = UpbitTransactionDao()
        
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

    def wait_until_next_15min(self):
        
        now = datetime.datetime.now()
        next_minute = (now.minute // 15 + 1) * 15
        if next_minute == 60:
            next_time = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        else:
            next_time = now.replace(minute=next_minute, second=0, microsecond=0)
        wait_seconds = (next_time - now).total_seconds()
        
        self.log.info(f"Waiting {int(wait_seconds)} seconds until {next_time.time()} to start.")
        
        time.sleep(wait_seconds)    
            
    def get_dataframe(self, ticker):
        
        # --- 데이터 셋팅
        now_date = str(datetime.datetime.now())[0:19]
        n_days_ago = str(datetime.datetime.now() - datetime.timedelta(days=730))[0:19]   
        self.year_list = get_years_between_str(n_days_ago, now_date)  # 대상연도
        self.splited_year_dict = split_date_range_by_year(n_days_ago, now_date) 
        
        # --- 연단위 테이블 생성 (있으면 pass)
        self.upbit_transaction_dao.create_yearly_table(self.year_list)
    
        # --- 데이터 조회
        upbit_transactions_list = []
        for year in self.year_list:
            
            table_name_f, table_name_t = self.upbit_transaction_dao.get_yearly_table_name(year)
            splited_year = self.splited_year_dict[year]
            start = splited_year[0]
            end = splited_year[1]
            
            upbit_transactions = self.upbit_transaction_dao.get_upbit_transactions_between(table_name_f, table_name_t, ticker, start, end)
            upbit_transactions_list += upbit_transactions
        
        # --- 데이터프레임으로 변환
        df = pd.DataFrame(upbit_transactions_list)     
        
        df['tick_datetime_'] = df['tick_datetime_'].dt.tz_localize(None)
        return df
    
    def run(self):
        
        
        local_path = "./my_data.xlsx"
        minio_path = "/datasets/2025/05/21/2025-05-21 10:30:00.xlsx"
        
        df = self.get_dataframe("KRW-BTC")
        
        # Excel 파일로 저장
        df.to_excel(local_path, index=False)  # 현재 작업 디렉토리에 저장

        self.minio.upload_file(minio_path, local_path)
        
        os.remove(local_path)
        
        return 
        
        # 전체 테스트
        
        self.datetime_list = generate_datetimes_by_min(terms=30, interval=5, n_days_ago=7) # 수집 구간 datetime 리스트 생성
        
        self.log.info(f' start : {datetime.datetime.now()}')
        
        for date_ in self.datetime_list:
        
            self.upbit.set_ticker("KRW-BTC")
            df_ohlcv = self.upbit.get_df_ohlcv(interval="minute5", date=date_, count=50)
            
            self.candle_pattern.set_df(df_ohlcv)
            get_cdl2crows = self.candle_pattern.get_cdl2crows()
            cdl2crows_key = get_cdl2crows.index[-1]
            cdl2crows_val = get_cdl2crows.iloc[-1]
            
            # 2025-03-25 20:50:00
            if cdl2crows_val != 0:
                self.log.info(f'key : {cdl2crows_key}')
                self.log.info(f'val : {cdl2crows_val}')
                
            time.sleep(0.1)
        self.log.info(f' end : {datetime.datetime.now()}')
        
        # for idx, row in get_cdl2crows['signal'].iterrows():
        #     self.log.info(f'idx : {idx}')
        #     self.log.info(f'row : {row}')
        #     self.log.info(f'row : {type(row)}')
            # if row['some_column'] == 1:
            #     print(f"Index {idx}에서 값이 1인 행 발견:", row)
            #     # 필요한 작업 수행
        
        # last_row = get_cdl2crows.iloc[-1]
        # self.log.info(f'last_row : {last_row}')
        # # self.log.info(f'candle_pattern_all : {candle_pattern_all}')
        
        return 
        # res = self.upbit_transaction_dao.create_upbit_transaction_table(table_name="dataset_upbit_transaction_2023")
        
        query = """
            SELECT
                data_row->>'tick_datetime' AS tick_datetime,
                data_row->>'timestamp' AS timestamp,
                data_row->>'weekday' AS weekday,
                data_row->>'OPEN' AS OPEN,
                data_row->>'HIGH' AS HIGH,
                data_row->>'LOW' AS LOW,
                data_row->>'CLOSE' AS CLOSE,
                data_row->>'VOLUME' AS VOLUME,
                data_row->>'VOLUME_MA5' AS VOLUME_MA5,
                data_row->>'VOLUME_MA20' AS VOLUME_MA20,
                data_row->>'VOLUME_RATIO' AS VOLUME_RATIO,
                data_row->>'OBV' AS OBV,
                data_row->>'VWAP' AS VWAP,
                data_row->>'VOLUME_VOLATILITY' AS VOLUME_VOLATILITY,
                data_row->>'VOLUME_SPIKE' AS VOLUME_SPIKE,
                data_row->>'RSI' AS RSI,
                data_row->>'MACD' AS MACD,
                data_row->>'MACD_SIGNAL' AS MACD_SIGNAL,
                data_row->>'BOLLINGER_PARTITION' AS BOLLINGER_PARTITION,
                data_row->>'CLOSE_LIST' AS CLOSE_LIST
            FROM
                dataset_upbit_transaction_feature_2023
            WHERE ticker = 'KRW-BTC'
            ORDER BY tick_datetime desc
        """
        res_f = self.postgres.read_all(query)
        self.log.info(f'len res_f : {len(res_f)}')
        
        query = """
            SELECT
            EXTRACT(EPOCH FROM tick_datetime)::bigint AS timestamp,
            data_row->'by_prev'->>'price_after_15min' AS price_after_15min,
            data_row->'by_prev'->>'price_after_30min' AS price_after_30min,
            data_row->'by_prev'->>'price_after_1hour' AS price_after_1hour,
            data_row->'by_prev'->>'price_after_4hour' AS price_after_4hour,
            data_row->'by_prev'->>'price_after_12hour' AS price_after_12hour,
            data_row->'by_prev'->>'price_after_1day' AS price_after_1day,
            data_row->'by_prev'->>'price_after_2day' AS price_after_2day,
            data_row->'by_prev'->>'price_after_3day' AS price_after_3day,
            data_row->'by_prev'->>'price_after_4day' AS price_after_4day,
            data_row->'by_prev'->>'price_after_5day' AS price_after_5day,
            data_row->'by_prev'->>'price_after_6day' AS price_after_6day
            FROM
            dataset_upbit_transaction_target_2023
            WHERE ticker = 'KRW-BTC'
            ORDER BY tick_datetime DESC;
        """
        res_t = self.postgres.read_all(query)
        self.log.info(f'len res_t : {len(res_t)}')
        
        merged_list = []
        for val_t in res_t:
            
            merged_dict = {}
            for val_f in res_f:
                if float(val_f['timestamp']) == float(val_t['timestamp']):
                    merged_dict = {**val_f, **val_t}
                    merged_list.append(merged_dict)
        
        self.log.info(f'len merged_list : {len(merged_list)}')
        return 
        
        df = self.get_dataframe("KRW-BTC")
        data = df.copy()
        
        
        for col in data.columns:
            try:
                data[col] = pd.to_numeric(data[col].astype(str).str.replace(",", "").str.strip(), errors='raise')
                
            except Exception as e:
                pass
                
        for col in data.columns:
            self.log.info(type(data[col].iloc[0]))  # 첫 번째 값 타입
            self.log.info(repr(data[col].iloc[0]))  # 숨은 공백 등 포함해서 확인
            self.log.info("")
        
        return 
        
        data['LOW'] = pd.to_numeric(data['LOW'], errors='raise')
        self.log.info(data['LOW'].head(5).tolist())
        self.log.info(type(data['LOW'].iloc[0]))  # 첫 번째 값 타입
        self.log.info(repr(data['LOW'].iloc[0]))  # 숨은 공백 등 포함해서 확인
        self.log.info("")
        
        return 

        for col in data.columns:
            
            # 날짜형 변환 시도
            try:
                data[col] = pd.to_datetime(data[col], errors='raise')
                continue
            except Exception:
                pass

            # 수치형 변환 시도
            try:
                data[col] = pd.to_numeric(data[col].str.replace(",", "").str.strip(), errors='coerce')
            except Exception:
                pass
        
        for col in data.columns:
            self.log.info(f"{col}: {df[col].dtype}")
        
  
        return 
        
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