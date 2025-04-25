from shares.middlewares.service_options_handler import OptionHandler
from shares.modules.log import Log
from shares.modules.redis import r as redis_single
from shares.constance.upbit_constance import UpbitConst

import websocket
import json
import time
import os

class CvAutoTraderS1Gen01(OptionHandler):
    """
    Service group : AutoTrader
    Service no : 1
    Generation : 01 
    Product Name : Orderbook Woodpecker
    
    Role : 업비트 소켓 구독
    """
    slack_post_prefix = ":wood: :bird: Orderbook Woodpecker. "
    
    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.redis = redis_single
        
        # service attrs
        self.ticker_list = None
        self.ttl_orderbook = None
        self.init_options(seq)
        
        # system attrs
        self.socket_url = "wss://api.upbit.com/websocket/v1"
         
    def run(self):
        
        ws = websocket.WebSocketApp(self.socket_url,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        
        ws.on_open = self.on_open
        ws.run_forever()

    """
    socks
    """
    def on_open(self, ws):
        params = [{"ticket": "test"}, {"type": "ticker", "codes": self.ticker_list}]
        ws.send(json.dumps(params))
        self.log.info(f"WebSocket opened. Subscribed: {self.ticker_list}")
        return 

    def on_close(self, ws, close_status_code, close_msg):
        self.log.info(f"WebSocket closed, close_status_code : {close_status_code}, close_msg : {close_msg}")
        self.reconnect()
        return 

    def on_error(self, ws, error):
        self.log.info(f"Error:", error)
        self.reconnect()
        return 

    def on_message(self, ws, message):
        data = json.loads(message)
    
        ticker = data.get('code')
        timestamp = time.time()
        key=f"{UpbitConst.ORDERBOOK_QUEUE_KEY}_{ticker}_{timestamp}"
        self.push_to_queue(key, message)
        return data
    
    def reconnect(self):
        
        self.log.info("Reconnecting in 5 seconds...")
        time.sleep(5)
        try:
            self.run()
            
        except Exception as e:
            self.log.error(f"Reconnect failed: {e}")
            time.sleep(10)

    """
    biz
    """
    def push_to_queue(self, key, message):
        
        # 호가를 큐에 저장, 각 서비스에서 돌려 씀
        self.redis.set_data(
            key=key,
            val=message, 
            expire=self.ttl_orderbook
        )