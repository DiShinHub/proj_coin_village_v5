
from shares.modules.log import Log
from shares.middlewares.auto_ml_experiment_handler import AutoMlExperimentHandler
from scheduler.auto_ml.decorators.handle_error import handle_error
import os

class Derived(AutoMlExperimentHandler):
    
    def __init__(self, df, config=None):
        self.log = Log(os.path.basename(__file__)).get_logger()
        super().__init__(df, config)
    
    @handle_error
    def high_low_ratio(self): 
        self.df['high_low_ratio'] = self.df['high'].astype(float) / self.df['low'].astype(float)
        return self.df

    @handle_error
    def close_open_ratio(self):
        self.df['close_open_ratio'] = self.df['close'].astype(float) / self.df['open'].astype(float)
        return self.df

    @handle_error
    def daily_range(self):
        self.df['daily_range'] = (self.df['high'].astype(float) - self.df['low'].astype(float)) / self.df['close'].astype(float)
        return self.df

    @handle_error
    def price_change_ratio(self):
        self.df['price_change_ratio'] = (self.df['close'].astype(float) - self.df['open'].astype(float)) / self.df['open'].astype(float)
        return self.df

    @handle_error
    def rolling_volatility(self):
        self.df['rolling_volatility'] = self.df['close'].astype(float).pct_change().rolling(10).std()
        return self.df

    @handle_error
    def close_above_ma5(self):
        self.df['close_above_ma5'] = (self.df['close'].astype(float) > self.df['close'].rolling(5).mean()).astype(int)
        return self.df

    @handle_error
    def candle_body_size(self):
        self.df['candle_body_size'] = (self.df['close'].astype(float) - self.df['open'].astype(float)).abs()
        return self.df

    @handle_error
    def upper_wick(self):
        self.df['upper_wick'] = self.df['high'].astype(float) - self.df[['open', 'close']].astype(float).max(axis=1)
        return self.df

    @handle_error
    def lower_wick(self):
        self.df['lower_wick'] = self.df[['open', 'close']].astype(float).min(axis=1) - self.df['low'].astype(float)
        return self.df

    @handle_error
    def wick_ratio(self):
        high = self.df['high'].astype(float)
        low = self.df['low'].astype(float)
        open_ = self.df['open'].astype(float)
        close = self.df['close'].astype(float)
        upper = high - open_.combine(close, max)
        lower = open_.combine(close, min) - low
        self.df['wick_ratio'] = (upper + lower) / (high - low + 1e-6)
        return self.df

    @handle_error
    def volatility_1h(self):
        self.df['volatility_1h'] = self.df['close'].astype(float).pct_change().rolling(12).std()
        return self.df

    @handle_error
    def gap_vs_30min_avg(self):
        shifted_close = self.df['close'].astype(float).shift(1)
        self.df['gap_vs_30min_avg'] = (self.df['open'].astype(float) - shifted_close) / shifted_close.rolling(6).mean()
        return self.df

    @handle_error
    def bollinger_width(self):
        ma = self.df['close'].astype(float).rolling(20)
        std = ma.std()
        self.df['bollinger_width'] = 4 * std / ma.mean()
        return self.df

    @handle_error
    def close_vs_ma12(self):
        self.df['close_vs_ma12'] = self.df['close'].astype(float) / self.df['close'].astype(float).rolling(12).mean()
        return self.df

    @handle_error
    def close_vs_ma36(self):
        self.df['close_vs_ma36'] = self.df['close'].astype(float) / self.df['close'].astype(float).rolling(36).mean()
        return self.df
    
    @handle_error
    def ema_diff_12_36(self):
        self.df['ema_diff_12_36'] = self.df['close'].astype(float).rolling(12).mean() - \
                                    self.df['close'].astype(float).rolling(36).mean()
        return self.df

    @handle_error
    def momentum_5_20(self):
        self.df['momentum_5_20'] = self.df['close'].astype(float).pct_change(5) - \
                                   self.df['close'].astype(float).pct_change(20)
        return self.df

    @handle_error
    def rsi_change(self):
        self.df['rsi_change'] = self.df['rsi'].astype(float).diff()
        return self.df

    @handle_error
    def volatility_10_30_ratio(self):
        vol10 = self.df['close'].astype(float).pct_change().rolling(10).std()
        vol30 = self.df['close'].astype(float).pct_change().rolling(30).std()
        self.df['volatility_10_30_ratio'] = vol10 / (vol30 + 1e-6)
        return self.df

    @handle_error
    def atr_ratio(self):
        self.df['atr_ratio'] = self.df['atr'].astype(float) / self.df['close'].astype(float)
        return self.df

    @handle_error
    def bullish_engulfing_flag(self):
        self.df['bullish_engulfing_flag'] = ((self.df['cdlengulfing'].astype(float)==1) & (self.df['momentum'].astype(float)>0)).astype(int)
        return self.df

    @handle_error
    def bearish_engulfing_flag(self):
        self.df['bearish_engulfing_flag'] = ((self.df['cdlengulfing'].astype(float)==-1) & (self.df['momentum'].astype(float)<0)).astype(int)
        return self.df

    @handle_error
    def change_after_1day(self):
        price_after_1day = self.df['price_after_1day'].astype(float)
        price_on_time = self.df['price_on_time'].astype(float)
        change = (price_after_1day - price_on_time) / price_on_time * 100

        def label(val):
            if val > 1:
                return 2
            elif val < -1:
                return 0
            else:
                return 1

        self.df['change_after_1day'] = change.apply(label)
        return self.df