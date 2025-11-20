from shares.modules.log import Log
from shares.modules.slack import *
from shares.modules.redis import r as redis_single
from shares.modules.notion import NontionModule
from shares.functions.common_function import generate_weekday_kor, generate_now_time

import datetime
import time
import os

class CvReminderS1Gen01():
    """
    Service group : Reminder
    Service no : 1
    Generation : 01 
    
    Role : 리마인더
    """
    slack_post_prefix = ":cv_secretary_kitty:"

    def __init__(self, seq):
        self.log = Log(os.path.basename(__file__)).get_logger()
        self.redis = redis_single
        self.notion = NontionModule()
    
    def run(self):
        
        self.wait_until_next_full_second()
        
        while True:
            try:
                remind_msgs = self.get_remind_msgs()
                if remind_msgs:
                    remind_msgs = f"{remind_msgs}"
                    self.redis.save_msg_on_Q(remind_msgs)
                
                time.sleep(60)

            except Exception as e:
                self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
                time.sleep(1)


    def wait_until_next_full_second(self):
        
        # 초정각에 실행 되도록 조정 
        now = datetime.datetime.now()
        next_time = now.replace(microsecond=0) + datetime.timedelta(seconds=1)
        wait_seconds = (next_time - now).total_seconds()
        time.sleep(wait_seconds)
    
    def get_remind_msgs(self):
        
        remind_msgs = ""
        
        # datetimes
        weekday_kor = generate_weekday_kor() 
        now_time = generate_now_time()[0:5]
        now_time = datetime.datetime.strptime(now_time, "%H:%M")
        min5_before = (now_time - datetime.timedelta(minutes=5))
        
        # Routine 페이지에서 데이터 조회
        page_id="24b22a980c46807a9d26d989758c7d64"
        response = self.notion.get_page(page_id=page_id)
        data = response.json()
        
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
                    created_time = result.get('created_time')
                    last_edited_time = result.get('last_edited_time')
                    created_by_user_id = result.get('created_by', {}).get('id')
                    last_edited_by_user_id = result.get('last_edited_by', {}).get('id')
                    parent_database_id = result.get('parent', {}).get('database_id')
                    archived = result.get('archived')
                    in_trash = result.get('in_trash')
                    page_url = result.get('url')
                    properties = result.get('properties', {})

                    # properties 파싱
                    if properties:
                        # '이름' title 필드 추출
                        title = ""
                        if properties.get('이름', {}).get('type') == 'title':
                            title_texts = properties['이름'].get('title', [])
                            title = "".join([t.get('plain_text', '') for t in title_texts])
                            title = title.strip()

                        # '요일' multi_select 필드 추출 (이름 리스트)
                        days = []
                        if properties.get('요일', {}).get('type') == 'multi_select':
                            days = [item.get('name', '') for item in properties['요일'].get('multi_select', [])]

                        # '알림 시간' rich_text 필드 추출
                        alerm_time = ""
                        if properties.get('알림 시간', {}).get('type') == 'rich_text':
                            alerm_time_texts = properties['알림 시간'].get('rich_text', [])
                            alerm_time = "".join([t.get('plain_text', '') for t in alerm_time_texts])
                            alerm_time = alerm_time.strip()

                        # '태그' multi_select 필드 추출 (이름 리스트)
                        tags = []
                        if properties.get('태그', {}).get('type') == 'multi_select':
                            tags = [item.get('name', '') for item in properties['태그'].get('multi_select', [])]
                    
                    # # 표 내부 상세 파싱
                    # if page_id:
                    #     response = self.notion.get_page(page_id=page_id)
                    #     data = response.json()
                    #     if data.get("results"):
                    #         content = data.get("results")
                    
                    if "매일" in days or weekday_kor in days:
                        if "," in alerm_time:
                            alerm_times = alerm_time.split(",")
                            for alerm_time in alerm_times:
                                key = f"{page_id}_{title}_{weekday_kor}_{alerm_time}"
                                remind_msg = self.get_remind_msg_if_alerm_time(key, title, page_url, min5_before, alerm_time, now_time)
                                if remind_msg:
                                    remind_msgs += f"{remind_msg}\n"
                               
                        else:
                            key = f"{page_id}_{title}_{weekday_kor}_{alerm_time}"
                            remind_msg = self.get_remind_msg_if_alerm_time(key, title, page_url, min5_before, alerm_time, now_time)
                            if remind_msg:
                                remind_msgs += f"{remind_msg}\n"

        return remind_msgs
    
    def get_remind_msg_if_alerm_time(self, key, title, page_url, min5_before, alerm_time, now_time):
        
                            
        remind_msg = None
        
        alerm_time = alerm_time.strip()
        if alerm_time:
            alerm_time = datetime.datetime.strptime(alerm_time, "%H:%M")
            if now_time >= alerm_time and min5_before < alerm_time:
                if not self.redis.get_data(key=key):
                    remind_msg = f"""{title}
{page_url}
                    """
                    
                    self.redis.set_data(
                        key=key,
                        val=1,
                        expire=43200
                    )

            return remind_msg
            
