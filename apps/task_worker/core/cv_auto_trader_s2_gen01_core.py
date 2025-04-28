from shares.modules.redis import r as redis_single
from shares.modules.upbit import Upbit
from shares.decorations.transaction_lock import *
from shares.constance.upbit_constance import UpbitConst

import inspect

class CvAutoTraderS2Gen01Core():
    slack_post_prefix = ":owl: Night Owl. "
    
    def __init__(self, ticker, order_intensity, order_book, order_max, log):
        
        self.log = log
        self.redis = redis_single
        self.upbit = Upbit()
        self.upbit.set_ticker(ticker)
        
        # --- 주입 값
        self.ticker = ticker
        self.order_intensity = order_intensity
        self.order_book = order_book
        self.order_max = order_max
        
        # --- 유동 값
        self.current_price = None             # 현재가
        self.close_price_list = []            # 종가 리스트
        self.bbbb_price = None                # bbbb가격
        self.bbbb_status = None               # bbbb상태
        self.bollinger_state_prev = None      # 이전 볼린저 상태 값
        self.bollinger_state_crr = None       # 현재 볼린저 상태 값
        self.order_seed = 0                   # 주문 시드
        self.order_count = 0                  # 주문 횟수
        self.order_amount = 0                 # 주문 비중
        self.order_hurdle = 0                 # 주문 허들
        
        # --- prefixes
        self.pref_bbbb_price = f"night_owls_bundle_bbbb_price_{self.ticker}"            # bbbb 가격 
        self.pref_bbbb_status = f"night_owls_bundle_bbbb_status_{self.ticker}"          # bbbb 상태 
        self.pref_bollinger_state = f"night_owls_bundle_bollinger_state_{self.ticker}"  # 볼린저 상태 
        self.pref_order_amount = f"night_owls_bundle_order_amount_{self.ticker}"        # 주문량 
        self.pref_order_count = f"night_owls_bundle_order_count_{self.ticker}"          # 주문횟수 
        self.pref_order_hurdle = f"night_owls_bundle_order_hurdle_{self.ticker}"        # 주문 허들 
    
    @block_when_lock(lock_key=UpbitConst.TRANSACTION_BLOCK_KEY)
    def run(self):
    
        try:
            # 데이터 셋팅
            self.set_order_intensity()
            self.set_order_standard()
            self.set_current_data()

            # BBBB mornitoring 
            if self.bbbb_status != "on_bbbb":
                self.off_bbbb()
                
            else:
                self.on_bbbb()
            
        except Exception as e:
            self.log.info(f"{str(e)}")
    
    """
    pre process
    """
    @block_when_lock(lock_key=UpbitConst.TRANSACTION_BLOCK_KEY)
    def set_order_intensity(self):
        
        self.order_percent_iv = self.order_intensity["order_percent_iv"]
        self.order_percent_ir = self.order_intensity["order_percent_ir"]
        self.order_hurdle_iv = self.order_intensity["order_hurdle_iv"]
        self.order_hurdle_ir = self.order_intensity["order_hurdle_ir"]
        
        if self.order_percent_iv: self.order_percent_iv = float(self.order_percent_iv)
        else:  
            self.log.info(f"Missing options required: self.order_percent_iv")  
            raise ValueError(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : Missing options required: self.order_percent_iv")

        if self.order_percent_ir: self.order_percent_ir = float(self.order_percent_ir) 
        else: 
            self.log.info(f"Missing options required: self.order_percent_ir")  
            raise ValueError(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : Missing options required: self.order_percent_ir")

        if self.order_hurdle_iv: self.order_hurdle_iv = float(self.order_hurdle_iv)
        else: 
            raise ValueError(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : Missing options required: self.order_hurdle_iv") 

        if self.order_hurdle_ir: self.order_hurdle_ir = float(self.order_hurdle_ir)
        else: 
            raise ValueError(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : Missing options required: self.order_hurdle_ir")
        
    @block_when_lock(lock_key=UpbitConst.TRANSACTION_BLOCK_KEY)
    def set_order_standard(self):
    
        self.bbbb_price = self.redis.hget_data(self.pref_bbbb_price, self.ticker)                   # bbbb 가격
        self.bbbb_status = self.redis.hget_data(self.pref_bbbb_status, self.ticker)                 # bbbb 상태
        self.bollinger_state_prev = self.redis.hget_data(self.pref_bollinger_state, self.ticker)    # 이전 볼린저 상태
        self.order_amount = self.redis.hget_data(self.pref_order_amount, self.ticker)               # 주문량
        self.order_count = self.redis.hget_data(self.pref_order_count, self.ticker)                 # 주문횟수
        self.order_hurdle = self.redis.hget_data(self.pref_order_hurdle, self.ticker)               # 주문 허들
        
        if self.bbbb_price: self.bbbb_price = float(self.bbbb_price)
        else: self.bbbb_price = 0
        
        if self.bollinger_state_prev: self.bollinger_state_prev = int(self.bollinger_state_prev)
        else: self.bollinger_state_prev = 0

        if self.order_amount: self.order_amount = float(self.order_amount)
        else: self.order_amount = 0

        if self.order_amount < 10000: self.order_amount = 10000

        if self.order_count: self.order_count = float(self.order_count) 
        else: self.order_count = 0
        
        if self.order_hurdle: self.order_hurdle = float(self.order_hurdle)
        else:  self.order_hurdle = self.order_hurdle_iv

    @block_when_lock(lock_key=UpbitConst.TRANSACTION_BLOCK_KEY)
    def set_current_data(self):
        
        multiple_info = self.upbit.get_multiple_info(interval="minute5")
        
        self.current_price = multiple_info["CLOSE"]
        self.bollinger_state_crr = multiple_info["BOLLINGER_PARTITION"]
        self.bollinger_state_prev = multiple_info["BOLLINGER_PARTITION_PREV"]
        self.close_price_list = multiple_info["CLOSE_LIST"]

    """
    BBBB MORNITORING
    """
    @block_when_lock(lock_key=UpbitConst.TRANSACTION_BLOCK_KEY)
    def off_bbbb(self):

        # 하락세 감지, 모니터링 돌입
        if self.bollinger_state_crr == 1 and self.bollinger_state_prev == 1:
            self.pre_bbbb()
    
    @lock_transaction(lock_key=UpbitConst.TRANSACTION_BLOCK_KEY, hold=1)
    def pre_bbbb(self):
        
        # bbbb의 가격을 현재가로 잡고 bbbb 상태 변경
        self.redis.hupd_date(self.pref_bbbb_price, self.ticker, self.current_price) 
        self.redis.hupd_date(self.pref_bbbb_status, self.ticker, "on_bbbb")

        self.redis.save_msg_on_Q(f"{self.slack_post_prefix} : {self.ticker}의 하단 무너짐이 감시 되었습니다. 모니터링을 시작합니다.")

    @block_when_lock(lock_key=UpbitConst.TRANSACTION_BLOCK_KEY)
    def on_bbbb(self):
        
        # CASE 1: 매수 포인트 감지   
        if (self.bollinger_state_crr > 1 and\
            self.bollinger_state_prev > 1 and\
            self.close_price_list[-2] > self.close_price_list[-3] and\
            self.upbit.get_price_diff_rate(self.current_price, self.bbbb_price) > self.order_hurdle): 
            """
            - 현재 볼린저 상태가 1(band_lower)이상
            - 이전 볼린저 상태가 1(band_lower)이상
            - 2봉 전 종가보다 전봉 종가가 커야함
            - bbbb당시 가격과 현재가의 변화율이 order_hurdle 이하여야함
            """
            
            self.order_seed = self.upbit.get_krw_balance()

            # 시드 제한
            if self.order_seed > self.order_max:
                self.order_seed = self.order_max

            # 주문액 최초 설정 (시드의 n%만큼 매수)
            if not self.order_amount:
                self.order_amount = self.order_seed * self.order_percent_iv * 0.01

            # CASE 1-1 : 한화 없음
            if self.order_seed <= 5000:
                self.reset_order(f"{self.slack_post_prefix} : {self.ticker}를 매수하기 위한 한화가 없습니다. 초기화합니다.")

            # CASE 1-2 : 매수시도액보다 한화량 낮음. 초기화
            elif self.order_seed < self.order_amount:
                self.reset_order(f"{self.slack_post_prefix} : {self.ticker}을 매수하기 위한 한화가 부족합니다. 초기화합니다.")
            
            # CASE 1-3 : 정상 케이스, 매수
            else:
                self.log.info(f"self.upbit.get_krw_balance() : {self.upbit.get_krw_balance()}")
                self.log.info(f"self.order_percent_iv : {self.order_percent_iv}")
                self.log.info(f"self.order_seed : {self.order_seed}")
                self.log.info(f"self.order_amount : {self.order_amount}")
                self.post_bbbb()

        # CASE 2: 매수 없이 상승세 감지      
        elif self.bollinger_state_crr in ([6]) and\
            self.bollinger_state_prev in ([5, 6]):
            self.reset_bbbb(f"{self.slack_post_prefix} : {self.ticker}의 상승세를 감지하였습니다. 모니터링을 중단합니다.")

    @lock_transaction(lock_key=UpbitConst.TRANSACTION_BLOCK_KEY, hold=1)
    def post_bbbb(self):
        
        # 매매 진행
        msg = self.upbit.buy_coin(self.order_amount)

        # 매매 기록 및 강도 올림
        if self.redis.hget_data(self.pref_bbbb_price, self.ticker):
            self.redis.hupd_date(self.pref_bbbb_status, self.ticker, "off_bbbb")                  
            self.redis.hupd_date(self.pref_order_amount, self.ticker, (self.order_amount * self.order_percent_ir)) 
            self.redis.hupd_date(self.pref_order_hurdle, self.ticker, (self.order_hurdle * self.order_hurdle_ir))  
            self.redis.hupd_date(self.pref_order_count, self.ticker, (self.order_count + 1))     
            
        self.redis.save_msg_on_Q(f"{self.slack_post_prefix} : {self.ticker}의 매수를 성공하였습니다. \n {msg} \n\n")
    
    """
    BBBB reset
    """
    @lock_transaction(lock_key=UpbitConst.TRANSACTION_BLOCK_KEY, hold=1)
    def reset_bbbb(self, msg):
        
        self.redis.hdel_data(self.pref_bbbb_price, self.ticker)
        self.redis.hdel_data(self.pref_bbbb_status, self.ticker)
        self.redis.hdel_data(self.pref_bollinger_state, self.ticker)
        
        self.redis.save_msg_on_Q(msg)
    
    @lock_transaction(lock_key=UpbitConst.TRANSACTION_BLOCK_KEY, hold=1)
    def reset_order(self, msg):
        
        self.redis.hdel_data(self.pref_bbbb_price, self.ticker)
        self.redis.hdel_data(self.pref_bbbb_status, self.ticker)
        self.redis.hdel_data(self.pref_bollinger_state, self.ticker)
        self.redis.hdel_data(self.pref_order_amount, self.ticker)
        self.redis.hdel_data(self.pref_order_count, self.ticker)
        self.redis.hdel_data(self.pref_order_hurdle, self.ticker)
        
        self.redis.save_msg_on_Q(msg)
        
    
        