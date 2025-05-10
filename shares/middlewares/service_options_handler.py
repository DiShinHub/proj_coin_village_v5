from shares.dao.runnable_services_dao import *
from shares.functions.common_function import convert_eval_safe

class OptionHandler():
    
    def init_options(self, seq):
        """
        def description : 옵션 이닛
        
        - 클래스의 속성을 DB를 토대로 자동으로 채움
        
        Parameters
        ----------
        seq : 서비스 시퀀스
        """
        
        # --- 자식 클래스의 속성 중 None 값인 속성 조회
        required_options = {
            key for key in self.__dict__
            if self.__dict__[key] is None and not callable(self.__dict__[key])
        }
        if not required_options:
            return True # pass
        
        # --- DB에서 서비스 옵션 조회 
        service_options = runnableServicesDao().get_runnable_service_options(seq)
        incoming_options = {opt["option_key"] for opt in service_options}
        
        # --- 시스템을 기준으로 DB에 누락 된 옵션이 있으면 raise
        missing_options = list(required_options - incoming_options)  
        if missing_options:
            raise ValueError(f"Missing options required: {missing_options}")
        
        # --- 속성에 DB에서 조회한 서비스 옵션 값을 채워 넣음
        for service_option in service_options:
            setattr(self, service_option["option_key"], convert_eval_safe(service_option["option_val"]))