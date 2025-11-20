from shares.modules.log import Log
from shares.modules.slack import *
from shares.modules.redis import r as redis_single
from shares.modules.notion import NontionModule

import time
import os

class CvSystemS3Gen01():
    """
    Service group : system
    Service no : 1
    Generation : 01 
    
    Role : 간이 UI
    """
    slack_post_prefix = ""

    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.redis = redis_single
        self.notion = NontionModule()
    
    def run(self):
        
        while True:
            try:
                ui_changes = self.get_ui_changes()
                if ui_changes:
                    pass
   
                time.sleep(1)

            except Exception as e:
                self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
                time.sleep(1)
                
    def get_ui_changes(self):
        
        # 데이터 조회
        page_id="25122a980c468001b8c2f3311b5443a6"
        response = self.notion.get_page(page_id=page_id)
        data = response.json()
        return 
        
        # 데이터 베이스 인라인 파싱
        for block in data['results']:
            block_type = block.get("type")
            
            # 자식 데이터 베이스 파싱
            if block_type == "child_database":
                response = self.notion.post_db(db_id=block['id']  )
                data = response.json()
                results = data.get("results")
                
                # 표 내부 데이터 루프 
                for result in results:
                    page_id = result.get('id')
                    page_url = result.get('url')
                    properties = result.get('properties', {})

                    # properties 파싱
                    if properties:
                        
                        # '이름' title 필드 추출
                        title = ""
                        if properties.get('이름', {}).get('type') == 'title':
                            title_texts = properties['이름'].get('title', "")
                            title = "".join([t.get('plain_text', '') for t in title_texts])
                            title = title.strip()
                            self.log.info(f'title : {title}')

                        # '설명' 필드 추출 
                        desc = ""
                        if properties.get('설명', {}).get('type') == 'rich_text':
                            desc_texts = properties['알림 시간'].get('rich_text', "")
                            desc = "".join([t.get('plain_text', '') for t in desc_texts])
                            desc = desc.strip()
                            self.log.info(f'desc : {desc}')
                            
                        # '실행방식'  필드 추출 
                        execution_method = ""
                        if properties.get('실행방식', {}).get('type') == 'select':
                            execution_method_texts = properties['실행방식'].get('select', "")
                            
                            self.log.info(f'execution_method_texts : {execution_method_texts}')
                            self.log.info(f'execution_method_texts : {type(execution_method_texts)}')
                            
                            execution_method = "".join([t.get('plain_text', '') for t in execution_method_texts])
                            execution_method = execution_method.strip()
                            self.log.info(f'execution_method : {execution_method}')
                            
                        # '실행'  필드 추출 
                        activate_yn = ""
                        if properties.get('실행', {}).get('type') == 'select':
                            activate_yn_texts = properties['실행'].get('select', "")
                            
                            self.log.info(f'activate_yn_texts : {activate_yn_texts}')
                            self.log.info(f'activate_yn_texts : {type(activate_yn_texts)}')
                            activate_yn = "".join([t.get('plain_text', '') for t in activate_yn_texts])
                            activate_yn = activate_yn.strip()
                            self.log.info(f'activate_yn : {activate_yn}')
                            
    