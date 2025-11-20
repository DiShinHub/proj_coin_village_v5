from shares.modules.log import system_module_log
from shares.config.config import Config
from shares.decorations.try_again import try_again
from shares.decorations.cache_data import cache_data
from shares.decorations.reuse_data import reuse_data

import requests
import pandas as pd
import datetime
import time

class Kis():

    def __init__(self):
        self.log = system_module_log
        config = Config()
        self.kis_app_key, self.kis_secret_key = config.set_kis()
        
        self.access_token = ""
        self.token_expire_time = 0  
        self.tr_id = ""

    def set_tr_id(self, tr_id):
        """
        def description : tr_id 셋팅

        Parameters
        ----------
        tr_id : tr_id(string), e.g.) FHKST01010100

        Returns
        -------
        tr_id : tr_id(string)
        """
        self.tr_id = tr_id
        return self.tr_id

    def get_tr_id(self):
        """
        def description : 셋팅 된 tr_id 리턴

        Returns
        -------
        tr_id : tr_id(string)
        """
        return self.tr_id
    
    def set_access_token(self):
        
        try:
            URL = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
            data = {
                "grant_type": "client_credentials",
                "appkey": self.kis_app_key,
                "appsecret": self.kis_secret_key
            }
            response = requests.post(URL, json=data)
            response.raise_for_status()  
            
            response = response.json()
            expires_in = response.get("expires_in", 0) 
            if expires_in >= 0:
                self.access_token = response.get("access_token")
                self.token_expire_time = time.time() + int(expires_in) - 60  
                
            return self.access_token
        
        except Exception as e:
            self.log.error(f"Access token 발급 실패: {e}")
            raise
    
    def ensure_access_token(self):
        if not self.access_token or time.time() >= self.token_expire_time:
            self.set_access_token()

    def get_df_ohlcv(self, interval="D", date=None, count=100):
        
        self.ensure_access_token()
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "appkey": self.kis_app_key,
            "appsecret": self.kis_secret_key,
            "tr_id": self.tr_id
        }
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",   # J: 주식
            "FID_INPUT_ISCD": "005930"       # 삼성전자 종목코드
        }
        url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  
        self.log.info(response.json())
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",  # J: 주식
            "FID_INPUT_ISCD": self.tr_id,
            "FID_INPUT_DATE_1": date if date else datetime.datetime.today().strftime("%Y%m%d"),
            "FID_INPUT_DATE_2": "",             # 종료일 (빈값: 오늘)
            "FID_INPUT_VOL_ATND_CODE": "",      # 거래량 구분
            "FID_PERIOD_DIV_CODE": interval,    
            "FID_OUTPUT_ROWS": count
        }
        res = requests.get(url, headers=headers, params=params)
        data = res.json().get("output", [])

        # DataFrame으로 변환
        df = pd.DataFrame(data)
        if df.empty:
            return df

        # 컬럼명 맞추기
        df = df.rename(columns={
            "stck_bsop_date": "date",
            "stck_oprc": "open",
            "stck_hgpr": "high",
            "stck_lwpr": "low",
            "stck_prpr": "close",
            "acml_vol": "volume"
        })
        df["date"] = pd.to_datetime(df["date"])
        df = df[["date", "open", "high", "low", "close", "volume"]]
        return df
    
kis_module = Kis()
    