from shares.modules.log import Log
from shares.modules.slack import *
from shares.modules.redis import r as redis_single

import time
import os

class CvMessengerS1Gen01():
    """
    Service group : Messenger
    Service no : 1
    Generation : 01 
    Product Name : Baby Chick
    
    Role : 큐 메세지를 취합하여 슬랙 포스트
    """
    slack_post_prefix = ":chick: Baby Chick. "

    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.redis = redis_single
        self.slack = Slack(channel="#coinvillage")
        
        self.pref_slack_msg_box = "slack_msg_box"
    
    def run(self):
        
        while True:
            try:
                data_list = self.get_msg_from_queue()
                if data_list:
                    self.post_msg_from_queue(data_list)
                    
                else:
                    time.sleep(1)

            except Exception as e:
                self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
                time.sleep(1)
                    
    def get_msg_from_queue(self):
        
        data_list = self.redis.lrange_all(self.pref_slack_msg_box)
        return data_list
                
    def post_msg_from_queue(self, data_list):

        msg = ""
        for item in reversed(data_list):
            self.redis.lpop(self.pref_slack_msg_box)
            item = item.decode("utf-8")

            if msg:
                msg += f"\n{item}"
            
            else:
                msg = f"{item}" 

        if msg:
            self.slack.post_msg(msg)
