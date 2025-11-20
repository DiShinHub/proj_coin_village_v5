
import numpy as np
import pandas as pd 
import os

class Derived():
    
    def __init__(self, df, config=None):
        self.config = config
        self.features = config.get("features")
        self.targets = config.get("targets")
        self.hyperparameters = config.get("hyperparameters")
        
        self.df = df
        self.df_f = None
    
    def high_low_ratio(self): 
        self.df['high_low_ratio'] = self.df['high'].astype(float) / self.df['low'].astype(float)
        return self.df

    def close_open_ratio(self):
        self.df['close_open_ratio'] = self.df['close'].astype(float) / self.df['open'].astype(float)
        return self.df

    def daily_range(self):
        self.df['daily_range'] = (self.df['high'].astype(float) - self.df['low'].astype(float)) / self.df['close'].astype(float)
        return self.df

    def price_change_ratio(self):
        self.df['price_change_ratio'] = (self.df['close'].astype(float) - self.df['open'].astype(float)) / self.df['open'].astype(float)
        return self.df

    def rolling_volatility(self):
        self.df['rolling_volatility'] = self.df['close'].astype(float).pct_change().rolling(10).std()
        return self.df

    def close_above_ma5(self):
        self.df['close_above_ma5'] = (self.df['close'].astype(float) > self.df['close'].rolling(5).mean()).astype(int)
        return self.df

    def candle_body_size(self):
        self.df['candle_body_size'] = (self.df['close'].astype(float) - self.df['open'].astype(float)).abs()
        return self.df

    def upper_wick(self):
        self.df['upper_wick'] = self.df['high'].astype(float) - self.df[['open', 'close']].astype(float).max(axis=1)
        return self.df

    def lower_wick(self):
        self.df['lower_wick'] = self.df[['open', 'close']].astype(float).min(axis=1) - self.df['low'].astype(float)
        return self.df

    def wick_ratio(self):
        high = self.df['high'].astype(float)
        low = self.df['low'].astype(float)
        open_ = self.df['open'].astype(float)
        close = self.df['close'].astype(float)
        upper = high - open_.combine(close, max)
        lower = open_.combine(close, min) - low
        self.df['wick_ratio'] = (upper + lower) / (high - low + 1e-6)
        return self.df

    def volatility_1h(self):
        self.df['volatility_1h'] = self.df['close'].astype(float).pct_change().rolling(12).std()
        return self.df

    def gap_vs_30min_avg(self):
        shifted_close = self.df['close'].astype(float).shift(1)
        self.df['gap_vs_30min_avg'] = (self.df['open'].astype(float) - shifted_close) / shifted_close.rolling(6).mean()
        return self.df

    def bollinger_width(self):
        ma = self.df['close'].astype(float).rolling(20)
        std = ma.std()
        self.df['bollinger_width'] = 4 * std / ma.mean()
        return self.df

    def close_vs_ma12(self):
        self.df['close_vs_ma12'] = self.df['close'].astype(float) / self.df['close'].astype(float).rolling(12).mean()
        return self.df

    def close_vs_ma36(self):
        self.df['close_vs_ma36'] = self.df['close'].astype(float) / self.df['close'].astype(float).rolling(36).mean()
        return self.df
    
    def ema_diff_12_36(self):
        self.df['ema_diff_12_36'] = self.df['close'].astype(float).rolling(12).mean() - \
                                    self.df['close'].astype(float).rolling(36).mean()
        return self.df

    def momentum_5_20(self):
        self.df['momentum_5_20'] = self.df['close'].astype(float).pct_change(5) - \
                                   self.df['close'].astype(float).pct_change(20)
        return self.df

    def rsi_change(self):
        self.df['rsi_change'] = self.df['rsi'].astype(float).diff()
        return self.df

    def volatility_10_30_ratio(self):
        vol10 = self.df['close'].astype(float).pct_change().rolling(10).std()
        vol30 = self.df['close'].astype(float).pct_change().rolling(30).std()
        self.df['volatility_10_30_ratio'] = vol10 / (vol30 + 1e-6)
        return self.df

    def atr_ratio(self):
        self.df['atr_ratio'] = self.df['atr'].astype(float) / self.df['close'].astype(float)
        return self.df

    def bullish_engulfing_flag(self):
        self.df['bullish_engulfing_flag'] = ((self.df['cdlengulfing'].astype(float)==1) & (self.df['momentum'].astype(float)>0)).astype(int)
        return self.df

    def bearish_engulfing_flag(self):
        self.df['bearish_engulfing_flag'] = ((self.df['cdlengulfing'].astype(float)==-1) & (self.df['momentum'].astype(float)<0)).astype(int)
        return self.df
    
    def datetime(self):
        self.df['datetime'] = pd.to_datetime(self.df['timestamp'], unit='s')
        return self.df
    
    def hour_sin(self):
        self.df['hour'] = self.df['datetime'].dt.hour
        self.df['hour_sin'] = np.sin(2 * np.pi * self.df['hour'] / 24)
        return self.df
    
    def hour_cos(self):
        self.df['hour'] = self.df['datetime'].dt.hour
        self.df['hour_cos'] = np.cos(2 * np.pi * self.df['hour'] / 24)
        return self.df
    
    def weekday_sin(self):
        self.df['weekday'] = self.df['datetime'].dt.weekday
        self.df['weekday_sin'] = np.sin(2 * np.pi * self.df['weekday'] / 7)
        return self.df
    
    def weekday_cos(self):
        self.df['weekday'] = self.df['datetime'].dt.weekday
        self.df['weekday_cos'] = np.cos(2 * np.pi * self.df['weekday'] / 7)
        return self.df
    
    def day_of_month_sin(self):
        self.df['day'] = self.df['datetime'].dt.day
        self.df['day_of_month_sin'] = np.sin(2 * np.pi * self.df['day'] / 31)
        return self.df

    def day_of_month_cos(self):
        self.df['day'] = self.df['datetime'].dt.day
        self.df['day_of_month_cos'] = np.cos(2 * np.pi * self.df['day'] / 31)
        return self.df

    def month_sin(self):
        self.df['month'] = self.df['datetime'].dt.month
        self.df['month_sin'] = np.sin(2 * np.pi * self.df['month'] / 12)
        return self.df

    def month_cos(self):
        self.df['month'] = self.df['datetime'].dt.month
        self.df['month_cos'] = np.cos(2 * np.pi * self.df['month'] / 12)
        return self.df

    def minute_of_day_sin(self):
        self.df['minute_of_day'] = self.df['datetime'].dt.hour * 60 + self.df['datetime'].dt.minute
        self.df['minute_of_day_sin'] = np.sin(2 * np.pi * self.df['minute_of_day'] / 1440)
        return self.df

    def minute_of_day_cos(self):
        self.df['minute_of_day'] = self.df['datetime'].dt.hour * 60 + self.df['datetime'].dt.minute
        self.df['minute_of_day_cos'] = np.cos(2 * np.pi * self.df['minute_of_day'] / 1440)
        return self.df
    
    def price_zscore_20(self):
        close = self.df['close'].astype(float)
        mean20 = close.rolling(20).mean()
        std20  = close.rolling(20).std()
        self.df['price_zscore_20'] = (close - mean20) / (std20 + 1e-6)
        return self.df

    def volume_zscore_20(self):
        vol = self.df['volume'].astype(float)
        mean20 = vol.rolling(20).mean()
        std20  = vol.rolling(20).std()
        self.df['volume_zscore_20'] = (vol - mean20) / (std20 + 1e-6)
        return self.df

    def return_1_zscore_20(self):
        ret1 = self.df['close'].astype(float).pct_change(1)
        mean20 = ret1.rolling(20).mean()
        std20  = ret1.rolling(20).std()
        self.df['return_1_zscore_20'] = (ret1 - mean20) / (std20 + 1e-6)
        return self.df

    def ma36_slope_norm(self):
        ma36 = self.df['close'].astype(float).rolling(36).mean()
        slope = ma36.diff(5)  # 5-스텝 기울기
        atr = self.df['atr'].astype(float).replace(0, np.nan)
        self.df['ma36_slope_norm'] = slope / (atr + 1e-6)
        return self.df

    def trend_over_vol(self):
        # 단기-장기 차이를 변동성으로 정규화 (추세 대비 변동성)
        ema12 = self.df['close'].astype(float).ewm(span=12, adjust=False).mean()
        ema36 = self.df['close'].astype(float).ewm(span=36, adjust=False).mean()
        atr = self.df['atr'].astype(float)
        self.df['trend_over_vol'] = (ema12 - ema36) / (atr + 1e-6)
        return self.df

    def obv_ma_ratio_20(self):
        obv = self.df['obv'].astype(float)
        self.df['obv_ma_ratio_20'] = obv / (obv.rolling(20).mean() + 1e-6)
        return self.df

    def return_1d(self):
        self.df['return_1d'] = self.df['close'].astype(float).pct_change(288)
        
        # 5분봉 기준 288개 = 1일
        self.df['return_1d'] = self.df['close'].astype(float).pct_change(288)

        # 1. NaN 제거/보정
        self.df['return_1d'] = self.df['return_1d'].astype(float).replace([np.inf, -np.inf], np.nan)
        self.df['return_1d'] = self.df['return_1d'].astype(float).fillna(0)

        # 2. 극단값 클리핑 (예: -20% ~ +20% 범위)
        self.df['return_1d'] = self.df['return_1d'].astype(float).clip(lower=-0.2, upper=0.2)

        # 3. 표준화 (z-score)
        mean = self.df['return_1d'].astype(float).mean()
        std = self.df['return_1d'].astype(float).std() + 1e-6
        self.df['return_1d'] = (self.df['return_1d'].astype(float) - float(mean)) / float(std)
        
        return self.df

    def return_1h(self):
        self.df['return_1h'] = self.df['close'].astype(float).pct_change(12)
        return self.df

    def return_5h_mean(self):
        self.df['return_5h_mean'] = self.df['return_1h'].astype(float).rolling(5).mean()
        return self.df

    def volume_change(self):
        self.df['volume_change'] = self.df['volume'].astype(float).pct_change(288)
        return self.df

    def volume_ma_ratio(self):
        self.df['volume_ma_ratio'] = self.df['volume'].astype(float) / self.df['volume_ma20'].astype(float)
        return self.df
    
    def daily_close_price_at_9(self):
        
        # 일자만 추출
        self.df['date'] = self.df['datetime'].dt.date
        self.df['time'] = self.df['datetime'].dt.time
        
        time_based = "09:00:00"
        
        # 해당 시각의 종가를 가져오기
        daily_close = (
            self.df[self.df['datetime'].dt.strftime('%H:%M:%S') == time_based]
            .groupby('date')['close']
            .first()   # 해당 시각 종가
        )
        
        # 원래 df에 merge
        self.df = self.df.merge(
            daily_close.rename("daily_close_price_at_9"),
            left_on='date',
            right_index=True,
            how='left'
        )
            
        # float 변환
        self.df["daily_close_price_at_9"] = self.df["daily_close_price_at_9"].astype(float)
        return self.df
    
    def daily_close_price_at_22_30(self):
        
        # 일자만 추출
        self.df['date'] = self.df['datetime'].dt.date
        self.df['time'] = self.df['datetime'].dt.time
        
        time_based = "22:30:00"
        
        # 해당 시각의 종가를 가져오기
        daily_close = (
            self.df[self.df['datetime'].dt.strftime('%H:%M:%S') == time_based]
            .groupby('date')['close']
            .first()   # 해당 시각 종가
        )
        
        # 원래 df에 merge
        self.df = self.df.merge(
            daily_close.rename("daily_close_price_at_22_30"),
            left_on='date',
            right_index=True,
            how='left'
        )
        self.df["daily_close_price_at_22_30"] = self.df["daily_close_price_at_22_30"].astype(float)
        return self.df
    
    def change_after_1day(self):
        price_after_1day = self.df['price_after_1day'].astype(float)
        price_on_time = self.df['price_on_time'].astype(float)
        change = (price_after_1day - price_on_time) / price_on_time * 100

        def label(val):
            if val > 0.1: 
                return 1
            else:
                return 0

        self.df['change_after_1day'] = change.apply(label)
        return self.df
    