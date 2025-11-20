from shares.modules.log import Log
from shares.modules.redis import Redis
from shares.dao.runnable_services_dao import runnableServicesDao

import inspect
import os

class CvSystemS1Gen01():
    """
    Service group : System
    Service no : 1
    Generation : 01 
    Product Name : Redis Cleaner
    
    Role : 
    1. redis flusher
    """
    
    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.seq = seq
        
        self.redis = Redis()
        self.runnable_service_dao = runnableServicesDao()

    def run(self):
        
        try:
            self.log.info("레디스를 청소합니다.")
            
            # 레디스 플러시시
            self.redis.flushall()
            
            # 스스로를 종료
            params = {
                "activate_yn" : "N"
            }
            self.runnable_service_dao.update_runnable_services(
                params=params,
                seq=self.seq
            )
            
            self.log.info("레디스를 청소하였습니다.")
    
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
        
            
        
        