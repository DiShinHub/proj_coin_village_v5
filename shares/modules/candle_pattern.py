from shares.modules.log import system_module_log
import pandas as pd
import numpy as np
import inspect

import datetime
from functools import wraps

class CandlePatterns:
    
    def __init__(self):
        self.log = system_module_log
        
    def set_df(self, df):
        self.df = df
        return self.df

    # def call_all_methods(self):
        
    #     if self.df is None or len(self.df) < 35:
    #         raise ValueError("Not enough data")
        
    #     results = {}
    #     for attr_name in dir(self):
    #         attr = getattr(self, attr_name)
            
    #         # 메소드인지, 매개변수가 없는지 확인
    #         if callable(attr) and not attr_name.startswith("__"):
                
    #             # 시도해서 호출 가능하면 호출
    #             try:
    #                 sig = inspect.signature(attr)
    #                 if len(sig.parameters) == 0:
                        
    #                     self.log.info(f'{attr_name} start : {datetime.datetime.now()}')
    #                     results[attr_name] = attr()
    #                     self.log.info(f'{attr_name} end : {datetime.datetime.now()}')
                        
    #             except Exception as e:
    #                 results[attr_name] = f"Error: {e}"
                    
    #     return results
    
    # def get_all_candle_patterns(self):
        
    #     cdl_results = {}
    #     for attr in dir(self):
    #         if attr.startswith("get_cdl") and callable(getattr(self, attr)):
    #             try:
    #                 result = getattr(self, attr)()
    #                 if isinstance(result, (np.ndarray, pd.Series)):
    #                     cdl_results[attr.upper()] = int(result[-1])
                        
    #             except Exception as e:
    #                 self.log.info(f"패턴 {attr} 처리 중 오류 발생: {e}")
    #                 raise
                
    #     return cdl_results
    

    def check_df(self):
        
        if self.df is None or len(self.df) < 35:
            return False
        
        return True
    
    def get_cdl2crows(self):
        df = self.df.copy()
        signal = (
            (df['close'].shift(2) > df['open'].shift(2)) &          # 2 전 양봉
            (df['open'].shift(1) > df['close'].shift(1)) &          # 1 전 음봉
            (df['open'].shift(1) < df['close'].shift(2)) &          # 1 전 시가 < 2 전 종가
            (df['close'].shift(1) > df['open'].shift(2)) &          # 1 전 종가 > 2 전 시가
            (df['open'] > df['close']) &                            # 현재 음봉
            (df['open'] < df['close'].shift(1)) &                   # 현재 시가 < 1 전 종가
            (df['close'] < df['close'].shift(1))                    # 현재 종가 < 1 전 종가  
        )
        return signal.astype(int) * -100

    def get_cdl3blackcrows(self):
        df = self.df.copy()
        signal = (
            (df['close'] < df['open']) &
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['close'].shift(2) < df['open'].shift(2)) &
            (df['open'] < df['open'].shift(1)) &
            (df['open'].shift(1) < df['open'].shift(2)) &
            (df['close'] < df['close'].shift(1)) &
            (df['close'].shift(1) < df['close'].shift(2))
        )
        return signal.astype(int) * -100

    def get_cdl3inside(self):
        df = self.df.copy()

        up = (
            (df['high'].shift(2) > df['high'].shift(1)) &
            (df['low'].shift(2) < df['low'].shift(1)) &
            (df['high'].shift(1) > df['high']) &
            (df['low'].shift(1) < df['low']) &
            (df['close'].shift(2) < df['open'].shift(2)) &
            (df['close'] > df['open'])
        )
        down = (
            (df['high'].shift(2) > df['high'].shift(1)) &
            (df['low'].shift(2) < df['low'].shift(1)) &
            (df['high'].shift(1) > df['high']) &
            (df['low'].shift(1) < df['low']) &
            (df['close'].shift(2) > df['open'].shift(2)) &
            (df['close'] < df['open'])
        )
        signal = (up | down) & df['close'].shift(2).notna()
        return signal.astype(int) * 100
    
    def get_cdl3linestrike(self):
        df = self.df.copy()
        signal = (
            (df['close'].shift(3) > df['open'].shift(3)) &
            (df['close'].shift(2) > df['open'].shift(2)) &
            (df['close'].shift(1) > df['open'].shift(1)) &
            (df['close'] < df['open']) &
            (df['close'] < df['open'].shift(3))
        )
        return signal.astype(int) * -100

    def get_cdl3outside(self):
        df = self.df.copy()
        signal = (
            (df['high'].shift(2) < df['high'].shift(1)) &
            (df['low'].shift(2) > df['low'].shift(1)) &
            (df['high'].shift(1) < df['high']) &
            (df['low'].shift(1) > df['low']) &
            ((df['close'].shift(2) < df['open'].shift(2)) & (df['close'] > df['open'])) |
            ((df['close'].shift(2) > df['open'].shift(2)) & (df['close'] < df['open']))
        )
        return signal.astype(int) * 100

    def get_cdl3starsinsouth(self):
        df = self.df.copy()
        signal = (
            (df['close'].shift(2) < df['open'].shift(2)) &
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['close'] < df['open']) &
            (df['open'].shift(2) > df['open'].shift(1)) &
            (df['open'].shift(1) > df['open']) &
            (df['close'].shift(2) > df['close'].shift(1)) &
            (df['close'].shift(1) > df['close'])
        )
        return signal.astype(int) * 100

    def get_cdl3whitesoldiers(self):
        df = self.df.copy()
        signal = (
            (df['close'] > df['open']) &
            (df['close'].shift(1) > df['open'].shift(1)) &
            (df['close'].shift(2) > df['open'].shift(2)) &
            (df['open'] > df['open'].shift(1)) &
            (df['open'].shift(1) > df['open'].shift(2)) &
            (df['close'] > df['close'].shift(1)) &
            (df['close'].shift(1) > df['close'].shift(2))
        )
        return signal.astype(int) * 100

    def get_cdlabandonedbaby(self):
        df = self.df.copy()
        doji = (abs(df['open'] - df['close']) <= ((df['high'] - df['low']) * 0.1))
        gap_down = df['low'].shift(1) > df['high']
        gap_up = df['high'].shift(1) < df['low']
        signal = (
            (df['close'].shift(2) < df['open'].shift(2)) &
            doji.shift(1) & gap_down &
            (df['close'] > df['open']) & gap_up
        )
        return signal.astype(int) * 100

    def get_cdladvanceblock(self):
        df = self.df.copy()
        body1 = abs(df['close'].shift(2) - df['open'].shift(2))
        body2 = abs(df['close'].shift(1) - df['open'].shift(1))
        body3 = abs(df['close'] - df['open'])
        signal = (
            (df['close'].shift(2) > df['open'].shift(2)) &
            (df['close'].shift(1) > df['open'].shift(1)) &
            (df['close'] > df['open']) &
            (df['close'].shift(2) < df['close'].shift(1)) &
            (df['close'].shift(1) < df['close']) &
            (body1 > body2) & (body2 > body3)
        )
        return signal.astype(int) * -100

    def get_cdlbelthold(self):
        df = self.df.copy()
        signal = (
            (df['open'] == df['low']) & (df['close'] > df['open']) |
            (df['open'] == df['high']) & (df['close'] < df['open'])
        )
        return signal.astype(int) * np.where(df['close'] > df['open'], 100, -100)

    def get_cdlbreakaway(self):
        df = self.df.copy()
        # 단순화된 Breakaway 조건 (상승/하락 양방 가능)
        up = (
            (df['close'].shift(4) < df['open'].shift(4)) &
            (df['close'].shift(3) < df['open'].shift(3)) &
            (df['close'].shift(2) < df['open'].shift(2)) &
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['close'] > df['open'])
        )
        down = (
            (df['close'].shift(4) > df['open'].shift(4)) &
            (df['close'].shift(3) > df['open'].shift(3)) &
            (df['close'].shift(2) > df['open'].shift(2)) &
            (df['close'].shift(1) > df['open'].shift(1)) &
            (df['close'] < df['open'])
        )
        
        # signal: 1 for up, -1 for down, 0 for none
        signal = pd.Series(np.where(up, 1, np.where(down, -1, 0)), index=df.index)

        # 강도 부여: 시가 대비 양봉/음봉 여부에 따라 100 또는 -100 곱하기
        direction = np.where(df['close'] > df['open'], 100, -100)
        return signal.astype(int) * direction

    def get_cdlclosingmarubozu(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        upper_shadow = df['high'] - df[['close', 'open']].max(axis=1)
        lower_shadow = df[['close', 'open']].min(axis=1) - df['low']
        
        # 조건에 맞는 캔들: True/False Series
        signal = (upper_shadow <= (body * 0.05)) | (lower_shadow <= (body * 0.05))
        
        # True → 1, False → 0 으로 변환
        signal_int = signal.astype(int)
        
        # 봉의 방향에 따라 100 또는 -100 곱하기
        direction = np.where(df['close'] > df['open'], 100, -100)
        
        result = signal_int * direction
        
        # pandas Series로 반환 (인덱스 유지)
        return pd.Series(result, index=df.index)

    def get_cdlconcealbabyswall(self):
        df = self.df.copy()
        # 매우 드문 형태로, 조건은 아래와 같이 단순화
        signal = (
            (df['open'].shift(3) > df['close'].shift(3)) &
            (df['open'].shift(2) > df['close'].shift(2)) &
            (df['high'].shift(1) < df['open'].shift(2)) &
            (df['low'].shift(1) > df['close'].shift(2)) &
            (df['high'] < df['open'].shift(1)) &
            (df['low'] > df['close'].shift(1))
        )
        return signal.astype(int) * 100

    def get_cdlcounterattack(self):
        df = self.df.copy()
        signal = (
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['close'] > df['open']) &
            (df['close'] == df['close'].shift(1))
        )
        return signal.astype(int) * 100

    def get_cdldarkcloudcover(self):
        df = self.df.copy()
        midpoint = (df['open'].shift(1) + df['close'].shift(1)) / 2
        signal = (
            (df['close'].shift(1) > df['open'].shift(1)) &
            (df['open'] > df['close']) &
            (df['open'] > df['high'].shift(1)) &
            (df['close'] < midpoint)
        )
        return signal.astype(int) * -100

    def get_cdldoji(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        signal = (body <= (df['high'] - df['low']) * 0.1)
        return signal.astype(int) * 100

    def get_cdldojistar(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        prev_body = abs(df['close'].shift(1) - df['open'].shift(1))
        gap = df['low'] > df['high'].shift(1)
        doji = (body <= (df['high'] - df['low']) * 0.1)
        signal = (doji & gap & (prev_body > 0))
        return signal.astype(int) * 100

    def get_cdldragonflydoji(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        upper_shadow = df['high'] - df[['close', 'open']].max(axis=1)
        lower_shadow = df[['close', 'open']].min(axis=1) - df['low']
        signal = (
            (body <= (df['high'] - df['low']) * 0.1) &
            (upper_shadow <= (df['high'] - df['low']) * 0.1) &
            (lower_shadow >= (df['high'] - df['low']) * 0.5)
        )
        return signal.astype(int) * 100
    
    def get_cdlengulfing(self):
        df = self.df.copy()
        prev_bearish = df['close'].shift(1) < df['open'].shift(1)
        prev_bullish = df['close'].shift(1) > df['open'].shift(1)

        engulf_bull = (
            prev_bearish &
            (df['close'] > df['open']) &
            (df['open'] < df['close'].shift(1)) &
            (df['close'] > df['open'].shift(1))
        )
        engulf_bear = (
            prev_bullish &
            (df['close'] < df['open']) &
            (df['open'] > df['close'].shift(1)) &
            (df['close'] < df['open'].shift(1))
        )
        signal = pd.Series(np.where(engulf_bull, 100, np.where(engulf_bear, -100, 0)), index=df.index)
        return signal

    def get_cdleveningdojistar(self):
        df = self.df.copy()
        doji = abs(df['close'].shift(1) - df['open'].shift(1)) <= (df['high'].shift(1) - df['low'].shift(1)) * 0.1
        signal = (
            (df['close'].shift(2) > df['open'].shift(2)) &
            doji &
            (df['close'] < df['open']) &
            (df['close'] < (df['close'].shift(2) + df['open'].shift(2)) / 2)
        )
        return signal.astype(int) * -100

    def get_cdleveningstar(self):
        df = self.df.copy()
        body2 = abs(df['close'].shift(1) - df['open'].shift(1))
        small_body = body2 < (df['high'].shift(1) - df['low'].shift(1)) * 0.2
        signal = (
            (df['close'].shift(2) > df['open'].shift(2)) &
            small_body &
            (df['close'] < df['open']) &
            (df['close'] < (df['open'].shift(2) + df['close'].shift(2)) / 2)
        )
        return signal.astype(int) * -100

    def get_cdlgapsidesidewhite(self):
        df = self.df.copy()
        cond = (
            (df['open'].shift(2) < df['close'].shift(2)) &
            (df['open'].shift(1) > df['high'].shift(2)) &
            (df['close'].shift(1) > df['high'].shift(2)) &
            (df['open'] > df['high'].shift(2)) &
            (df['close'] > df['high'].shift(2)) &
            (df['close'].shift(1) == df['close'])
        )
        return cond.astype(int) * 100

    def get_cdlgravestonedoji(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        upper_shadow = df['high'] - df[['close', 'open']].max(axis=1)
        lower_shadow = df[['close', 'open']].min(axis=1) - df['low']
        cond = (
            (body <= (df['high'] - df['low']) * 0.1) &
            (lower_shadow <= (df['high'] - df['low']) * 0.1) &
            (upper_shadow >= (df['high'] - df['low']) * 0.5)
        )
        return cond.astype(int) * 100

    def get_cdlhammer(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        lower = df[['close', 'open']].min(axis=1) - df['low']
        upper = df['high'] - df[['close', 'open']].max(axis=1)
        
        cond = (lower > body * 2) & (upper < body)
        
        signal_int = cond.astype(int)
        direction = np.where(df['close'] > df['open'], 100, -100)
        
        result = signal_int * direction
        
        return pd.Series(result, index=df.index)

    def get_cdlhangingman(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        lower = df[['close', 'open']].min(axis=1) - df['low']
        upper = df['high'] - df[['close', 'open']].max(axis=1)
        cond = (
            (lower > body * 2) &
            (upper < body) &
            (df['close'] < df['open'])  # 음봉
        )
        return cond.astype(int) * -100

    def get_cdlharami(self):
        df = self.df.copy()
        prev_body = abs(df['close'].shift(1) - df['open'].shift(1))
        curr_body = abs(df['close'] - df['open'])

        cond = (
            (curr_body < prev_body) &
            (df['open'] > df['close'].shift(1)) &
            (df['close'] < df['open'].shift(1))
        )
        reverse = (
            (curr_body < prev_body) &
            (df['open'] < df['close'].shift(1)) &
            (df['close'] > df['open'].shift(1))
        )

        # 시그널 값: cond → -100, reverse → 100, 그 외 → 0
        signal = pd.Series(np.where(cond, -100, np.where(reverse, 100, 0)), index=df.index)
        return signal
    
    def get_cdlharamicross(self):
        df = self.df.copy()
        curr_body = abs(df['close'] - df['open'])
        prev_body = abs(df['close'].shift(1) - df['open'].shift(1))
        is_doji = curr_body <= (df['high'] - df['low']) * 0.1

        cond = (
            is_doji &
            (df['open'] > df['close'].shift(1)) &
            (df['close'] < df['open'].shift(1)) &
            (prev_body > curr_body)
        )
        reverse = (
            is_doji &
            (df['open'] < df['close'].shift(1)) &
            (df['close'] > df['open'].shift(1)) &
            (prev_body > curr_body)
        )

        signal = pd.Series(np.where(cond, -100, np.where(reverse, 100, 0)), index=df.index)
        return signal

    def get_cdlhighwave(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        shadow = (df['high'] - df['low'])
        cond = (
            (body / shadow < 0.3) &
            (shadow > df['close'] * 0.03)
        )
        return cond.astype(int) * 100

    def get_cdlhikkake(self):
        df = self.df.copy()
        inside_bar = (
            (df['high'].shift(1) < df['high'].shift(2)) &
            (df['low'].shift(1) > df['low'].shift(2))
        )
        breakout = (
            (df['high'] > df['high'].shift(1)) &
            (df['low'] > df['low'].shift(1))
        )
        cond = inside_bar & breakout
        return cond.astype(int) * 100

    def get_cdlhikkakemod(self):
        df = self.df.copy()
        inside_bar = (
            (df['high'].shift(1) < df['high'].shift(2)) &
            (df['low'].shift(1) > df['low'].shift(2))
        )
        breakout = (
            (df['high'] > df['high'].shift(1)) &
            (df['low'] > df['low'].shift(1))
        )
        confirmation = df['close'] > df['close'].shift(1)
        cond = inside_bar & breakout & confirmation
        return cond.astype(int) * 100

    def get_cdlhomingpigeon(self):
        df = self.df.copy()
        cond = (
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['close'] < df['open']) &
            (df['open'] > df['open'].shift(1)) &
            (df['close'] > df['close'].shift(1)) &
            (df['open'] < df['close'].shift(1)) &
            (df['close'] < df['open'].shift(1))
        )
        return cond.astype(int) * 100

    def get_cdlidentical3crows(self):
        df = self.df.copy()
        cond = (
            (df['close'] < df['open']) &
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['close'].shift(2) < df['open'].shift(2)) &
            (abs(df['close'] - df['close'].shift(1)) < 0.1 * df['close'].shift(1)) &
            (abs(df['close'].shift(1) - df['close'].shift(2)) < 0.1 * df['close'].shift(2))
        )
        return cond.astype(int) * -100

    def get_cdlinneck(self):
        df = self.df.copy()
        cond = (
            (df['close'].shift(1) < df['open'].shift(1)) &  # 음봉
            (df['open'] < df['low'].shift(1)) &
            (abs(df['close'] - df['low'].shift(1)) / df['low'].shift(1) < 0.003)
        )
        return cond.astype(int) * -100

    def get_cdlinvertedhammer(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        upper = df['high'] - df[['close', 'open']].max(axis=1)
        lower = df[['close', 'open']].min(axis=1) - df['low']
        cond = (
            (upper > body * 2) &
            (lower < body) &
            (body < (df['high'] - df['low']) * 0.3)
        )
        return cond.astype(int) * 100

    def get_cdlkicking(self):
        df = self.df
        cond = (
            (df['close'].shift(1) < df['open'].shift(1)) &  # 첫째 날 음봉
            (df['close'] > df['open']) &  # 둘째 날 양봉
            (df['open'] > df['close'].shift(1))  # 둘째 날 시가가 첫째 날 종가 위에서 시작
        )
        return cond.astype(int)

    def get_cdlkickingbylength(self):
        df = self.df.copy()
        body1 = abs(df['close'].shift(1) - df['open'].shift(1))
        body2 = abs(df['close'] - df['open'])
        gap = abs(df['open'] - df['close'].shift(1)) > (df['high'] - df['low']).rolling(3).mean()
        cond = (
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['close'] > df['open']) &
            (body2 > body1) &
            gap
        )
        return cond.astype(int) * 100

    def get_cdlladderbottom(self):
        df = self.df.copy()
        cond = (
            (df['close'].shift(4) < df['open'].shift(4)) &
            (df['close'].shift(3) < df['open'].shift(3)) &
            (df['close'].shift(2) < df['open'].shift(2)) &
            (df['close'].shift(1) > df['open'].shift(1)) &
            (df['close'] > df['open']) &
            (df['close'] > df['close'].shift(1))
        )
        return cond.astype(int) * 100

    def get_cdllongline(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        range_ = df['high'] - df['low']
        avg_body = body.rolling(5).mean()
        avg_range = range_.rolling(5).mean()
        cond = (
            (body > avg_body * 1.5) &
            (range_ > avg_range * 1.5)
        )
        return np.where(df['close'] > df['open'], 100, -100) * cond.astype(int)

    def get_cdlmarubozu(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        upper = df['high'] - df[['close', 'open']].max(axis=1)
        lower = df[['close', 'open']].min(axis=1) - df['low']
        cond = (
            (upper <= body * 0.05) &
            (lower <= body * 0.05)
        )
        return np.where(df['close'] > df['open'], 100, -100) * cond.astype(int)

    def get_cdlhomingpigeon(self):
        df = self.df
        body1 = abs(df['close'].shift(1) - df['open'].shift(1))
        body2 = abs(df['close'] - df['open'])
        cond = (
            (body1 > 0) & (body2 > 0) &
            (df['close'] < df['open']) & (df['close'].shift(1) < df['open'].shift(1)) &  # 둘 다 음봉
            (df['open'] >= df['open'].shift(1)) & (df['close'] <= df['close'].shift(1))  # 두번째 캔들이 첫 캔들 몸통 안에 있음
        )
        return cond.astype(int)

    def get_cdlidentical3crows(self):
        df = self.df
        cond = (
            (df['close'].shift(2) < df['open'].shift(2)) & (df['close'].shift(1) < df['open'].shift(1)) & (df['close'] < df['open']) &  # 모두 음봉
            (df['close'].shift(2) > df['close'].shift(1)) & (df['close'].shift(1) > df['close']) &  # 종가 하락 연속
            (abs(df['open'].shift(1) - df['close'].shift(2)) < (df['high'].shift(2) - df['low'].shift(2)) * 0.1) &  # 첫-둘 몸통 거의 일치
            (abs(df['open'] - df['close'].shift(1)) < (df['high'].shift(1) - df['low'].shift(1)) * 0.1)  # 둘-셋 몸통 거의 일치
        )
        return cond.astype(int)

    def get_cdlinneck(self):
        df = self.df
        cond = (
            (df['close'].shift(1) < df['open'].shift(1)) &  # 첫 음봉
            (df['close'] > df['open']) &  # 두번째 양봉
            (abs(df['open'] - df['close'].shift(1)) < (df['high'] - df['low']) * 0.1) &  # 두번째 시가 ~ 첫번째 종가 근처
            (df['close'] > df['low'].shift(1)) & (df['close'] < df['open'].shift(1))  # 두번째 종가가 첫번째 저가 근처
        )
        return cond.astype(int)

    def get_cdlinvertedhammer(self):
        df = self.df
        body = abs(df['close'] - df['open'])
        upper_shadow = df['high'] - df[['close', 'open']].max(axis=1)
        lower_shadow = df[['close', 'open']].min(axis=1) - df['low']
        cond = (
            (body <= (df['high'] - df['low']) * 0.3) &  # 몸통 작음
            (upper_shadow >= body * 2) &  # 윗꼬리 길다
            (lower_shadow <= body * 0.3)  # 아래꼬리 짧다
        )
        return cond.astype(int)

    def get_cdlkicking(self):
        df = self.df
        cond = (
            (df['close'].shift(1) < df['open'].shift(1)) &  # 첫 음봉
            (df['close'] > df['open']) &  # 두번째 양봉
            (df['open'] > df['close'].shift(1)) &  # 두번째 시가가 첫번째 종가 위에서 시작
            (df['close'].shift(1) > df['open'].shift(1))  # 첫번째 캔들 종가가 시가 위(음봉 양봉 구분에 따라 다름)
        )
        return cond.astype(int)

    def get_cdlkickingbylength(self):
        df = self.df
        body1 = abs(df['close'].shift(1) - df['open'].shift(1))
        body2 = abs(df['close'] - df['open'])
        cond = (
            (df['close'].shift(1) < df['open'].shift(1)) &  # 첫 음봉
            (df['close'] > df['open']) &  # 두번째 양봉
            (body2 > body1) &  # 두번째 몸통이 첫번째보다 길다
            (df['open'] > df['close'].shift(1))  # 두번째 시가가 첫번째 종가 위에서 시작
        )
        return cond.astype(int)

    def get_cdlladderbottom(self):
        df = self.df
        body1 = abs(df['close'].shift(3) - df['open'].shift(3))
        body2 = abs(df['close'].shift(2) - df['open'].shift(2))
        body3 = abs(df['close'].shift(1) - df['open'].shift(1))
        body4 = abs(df['close'] - df['open'])
        cond = (
            (df['close'].shift(3) > df['open'].shift(3)) &  # 양봉
            (df['close'].shift(2) < df['open'].shift(2)) &  # 음봉
            (df['close'].shift(1) > df['open'].shift(1)) &  # 양봉
            (df['close'] > df['open']) &  # 양봉
            (body2 < body1) & (body2 < body4) & (body3 < body4)  # 가운데 음봉 작음
        )
        return cond.astype(int)

    def get_cdllongleggeddoji(self):
        df = self.df
        body = abs(df['close'] - df['open'])
        upper_shadow = df['high'] - df[['close', 'open']].max(axis=1)
        lower_shadow = df[['close', 'open']].min(axis=1) - df['low']
        cond = (
            (body <= (df['high'] - df['low']) * 0.1) &  # 몸통 매우 작음 (도지)
            (upper_shadow >= body * 2) &  # 긴 윗꼬리
            (lower_shadow >= body * 2)    # 긴 아랫꼬리
        )
        return cond.astype(int)

    def get_cdllongline(self):
        df = self.df
        body = abs(df['close'] - df['open'])
        cond = (
            (body >= (df['high'] - df['low']) * 0.7)  # 몸통이 전체 캔들 길이의 70% 이상
        )
        return cond.astype(int)

    def get_cdlmarubozu(self):
        df = self.df
        body = abs(df['close'] - df['open'])
        upper = df['high'] - df[['close', 'open']].max(axis=1)
        lower = df[['close', 'open']].min(axis=1) - df['low']
        cond = (
            (upper <= body * 0.05) &
            (lower <= body * 0.05)
        )
        return np.where(df['close'] > df['open'], 100, -100) * cond.astype(int)

    def get_cdlshortline(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        range_ = df['high'] - df['low']
        cond = (
            (body < range_ * 0.25) &
            (range_ < df['close'].rolling(5).mean() * 0.02)
        )
        return np.where(df['close'] > df['open'], 100, -100) * cond.astype(int)

    def get_cdlspinningtop(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        upper = df['high'] - df[['close', 'open']].max(axis=1)
        lower = df[['close', 'open']].min(axis=1) - df['low']
        cond = (
            (body < (upper + lower)) &
            (upper > body * 0.5) &
            (lower > body * 0.5)
        )
        return np.where(df['close'] > df['open'], 100, -100) * cond.astype(int)

    def get_cdlstalledpattern(self):
        df = self.df.copy()
        cond = (
            (df['close'].shift(2) > df['open'].shift(2)) &
            (df['close'].shift(1) > df['open'].shift(1)) &
            (df['open'].shift(1) > df['open'].shift(2)) &
            (df['open'] > df['open'].shift(1)) &
            (df['close'] < df['open'])
        )
        return cond.astype(int) * -100

    def get_cdlsticksandwich(self):
        df = self.df.copy()
        cond = (
            (df['close'].shift(2) < df['open'].shift(2)) &
            (df['close'].shift(1) > df['open'].shift(1)) &
            (df['close'] < df['open']) &
            (abs(df['close'] - df['close'].shift(2)) < 0.001 * df['close'])
        )
        return cond.astype(int) * 100

    def get_cdltakuri(self):
        df = self.df.copy()
        body = abs(df['close'] - df['open'])
        lower = df[['close', 'open']].min(axis=1) - df['low']
        upper = df['high'] - df[['close', 'open']].max(axis=1)
        cond = (
            (body < lower * 0.3) &
            (lower > body * 3) &
            (upper < body * 0.1)
        )
        return cond.astype(int) * 100

    def get_cdltasukigap(self):
        df = self.df.copy()
        cond = (
            (df['close'].shift(2) < df['open'].shift(2)) &
            (df['open'].shift(1) < df['low'].shift(2)) &  # gap down
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['close'] > df['open']) &
            (df['open'] < df['close'].shift(1))
        )
        return cond.astype(int) * 100

    def get_cdlthrusting(self):
        df = self.df.copy()
        cond = (
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['open'] < df['low'].shift(1)) &
            (df['close'] > df['low'].shift(1)) &
            (df['close'] < (df['open'].shift(1) + df['close'].shift(1)) / 2)
        )
        return cond.astype(int) * -100

    def get_cdltristar(self):
        df = self.df.copy()
        is_doji = abs(df['close'] - df['open']) < (df['high'] - df['low']) * 0.1
        cond = (
            is_doji.shift(2) & is_doji.shift(1) & is_doji &
            (abs(df['open'].shift(1) - df['open'].shift(2)) > df['close'] * 0.01) &
            (abs(df['open'] - df['open'].shift(1)) > df['close'] * 0.01)
        )
        return cond.astype(int) * 100

    def get_cdlunique3river(self):
        df = self.df.copy()
        cond = (
            (df['close'].shift(2) < df['open'].shift(2)) &
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['open'] < df['low'].shift(1)) &
            (df['close'] > df['close'].shift(1))
        )
        return cond.astype(int) * 100

    def get_cdlupsidegap2crows(self):
        df = self.df.copy()
        cond = (
            (df['close'].shift(2) > df['open'].shift(2)) &
            (df['open'].shift(1) > df['high'].shift(2)) &
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['open'] > df['open'].shift(1)) &
            (df['close'] < df['close'].shift(1))
        )
        return cond.astype(int) * -100

    def get_cdlxsidegap3methods(self):
        df = self.df.copy()
        cond = (
            (df['close'].shift(4) < df['open'].shift(4)) &  # 음봉
            (df['close'].shift(3) > df['open'].shift(3)) &
            (df['close'].shift(2) > df['open'].shift(2)) &
            (df['close'].shift(1) > df['open'].shift(1)) &
            (df['open'] < df['low'].shift(1)) &  # gap down
            (df['close'] < df['open'])
        )
        return cond.astype(int) * -100