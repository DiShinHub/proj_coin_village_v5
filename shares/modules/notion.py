from shares.modules.log import system_module_log
from shares.config.config import Config
import requests
import os, sys
import inspect

class NontionModule():

    def __init__(self):
        self.log = system_module_log
        self.notion_key = Config().set_notion()
        
        self.headers = None
        
        self.set_header()
    
    def set_header(self):
        self.headers = {
            "Authorization": f"Bearer {self.notion_key}",
            "Notion-Version": "2022-06-28"
        }
        return self.headers
    
    def get_page(self, page_id):
        url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response

        else:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(response)}")
            raise
    
    def post_db(self, db_id):
        
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        response = requests.post(url, headers=self.headers, json={})
        if response.status_code == 200:
            return response
        
        else:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(response)}")
            raise