from shares.modules.log import system_module_log
from shares.config.config import Config
from shares.decorations.try_again import try_again
from shares.decorations.cache_data import cache_data

import requests
import inspect

class ExchangeRate():
        
    def __init__(self):
        self.log = system_module_log
        self.exchage_rate_key = Config().set_exchange_rate() 

    @cache_data(ttl=1)
    @try_again(num=4)
    def get_exchange_rate_by_usd(self, target="KRW"):
        """
        def description : 현재가 조회

        Returns
        -------
        current_price : 현재가 (float)
        """

        url = f'https://v6.exchangerate-api.com/v6/{self.exchage_rate_key}/latest/USD'
        response = requests.get(url)
        exchange_rate_data = response.json()

        if response.status_code == 200:
            if target == "KRW":
                usd_to_krw = exchange_rate_data['conversion_rates']['KRW']
                return usd_to_krw

        else:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(response.json())}")
            raise
    
    @cache_data(ttl=1)
    @try_again(num=4)
    def get_target_date_exchange_rate_by_usd(self, date, base_currency="USD", target_currency="KRW"):
        """
        def description : 현재가 조회

        Returns
        -------
        current_price : 현재가 (float)
        """


        url = f'https://v6.exchangerate-api.com/v6/{self.exchage_rate_key}/latest/{base_currency}'
        response = requests.get(url)
        exchange_rate_data = response.json()
        self.log.info(f"exchange_rate_data : {exchange_rate_data}")

        if response.status_code == 200:
            return exchange_rate_data.get('conversion_rates').get(target_currency)
        
        else:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(response.json())}")
            raise
            
        return
    
        # 유료 플랜에서만 지원하여 나중에 프리트라이얼 해서 일자별로 쮹 땡겨와 mysql에 넣을 꺼임

        y = date[0:4]
        m = date[5:7].replace("0","")
        d = date[8:10]
        # print(f"y : {y}")
        # print(f"m : {m}")
        # print(f"d : {d}")

        url = f"https://v6.exchangerate-api.com/v6/{self.exchage_rate_key}/history/USD/{y}/{m}/{d}"
        
    
        response = requests.get(url)
        print(response.status_code)
        if response.status_code == 200:
            data = response.json()
            print(data)
            rates = data.get('conversion_rates')
            if rates and target_currency in rates:
                return rates[target_currency]

