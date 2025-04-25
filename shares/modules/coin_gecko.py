from shares.modules.log import system_module_log
from shares.decorations.try_again import try_again
from shares.decorations.cache_data import cache_data

import requests
import datetime

import inspect

class CoinGecko():

    def __init__(self):
        self.log = system_module_log
        self.ticker = None
        self.ticker_org = None

    def set_ticker(self, ticker):
        """
        def description : 티커 셋팅

        Parameters
        ----------
        ticker : 티커(string)

        Returns
        -------
        Boolean
        """

        self.ticker = ticker
        return True

    def get_ticker(self):
        """
        def description : 셋팅 된 티커 리턴

        Returns
        -------
        ticker : 티커(string)
        """

        return self.ticker
    
    def get_ticker_id(self, ticker):

        ticker_coin_gecko = None

        if "BTC" in ticker:
            ticker_coin_gecko = "bitcoin"
        elif "ETH" in ticker:
            ticker_coin_gecko = "ethereum"
        elif "SOL" in ticker:
            ticker_coin_gecko = "solana"
        elif "BCH" in ticker:
            ticker_coin_gecko = "bitcoin-cash"
        elif "ETC" in ticker:
            ticker_coin_gecko = "ethereum-classic"
        elif "AVAX" in ticker:
            ticker_coin_gecko = "avalanche-2"
        elif "AXS" in ticker:
            ticker_coin_gecko = "axie-infinity"
        elif "BSV" in ticker:
            ticker_coin_gecko = "bitcoin-cash-sv"
        elif "NEAR" in ticker:
            ticker_coin_gecko = "near"
        elif "LINK" in ticker:
            ticker_coin_gecko = "chainlink"
        elif "AAVE" in ticker:
            ticker_coin_gecko = "aave"
        elif "WAVES" in ticker:
            ticker_coin_gecko = "waves"

        return ticker_coin_gecko
    
    @cache_data(ttl=1)
    @try_again(num=4)
    def get_tickers(self):
        
        url = 'https://pro-api.coingecko.com/api/v3/coins/list'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()  
            return data

        else:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(response.json())}")
            raise
        
    @cache_data(ttl=1)
    @try_again(num=4)
    def get_current_price(self):
        """
        def description : 현재가 조회

        Returns
        -------
        current_price : 현재가 (float)
        """

        url = 'https://api.coingecko.com/api/v3/simple/price'
        params = {
            'ids': self.ticker,
            'vs_currencies': 'usd'
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            current_price = data.get(f'{self.ticker}').get('usd')
            return current_price

        else:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(response.json())}")
            raise

    @cache_data(ttl=1)
    @try_again(num=4)
    def get_target_date_prices(self, start=None, end=None):
        """
        def description : 특정 날짜의 가격 조회

        Parameters
        ----------
        date : 특정 날짜
        Returns
        -------
        close_price : 종가 (float)
        """

        url = f"https://api.coingecko.com/api/v3/coins/{self.ticker}/market_chart/range"

        # 날짜를 타임스탬프로 변환
        start_time = int(datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').timestamp())
        end_time = int(datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S').timestamp())

        params = {
            'from': start_time,
            'to': end_time,
            'vs_currency': 'usd'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()  
            return data['prices']

        else:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(response.json())}")
            raise
        