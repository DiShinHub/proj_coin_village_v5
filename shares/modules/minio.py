from shares.modules.log import system_module_log
from shares.config.config import Config

from minio.error import S3Error

import datetime
import os, sys
import inspect

class MinioModule():

    def __init__(self):
        self.log = system_module_log
        self.external_client, self.minio_bucket, self.minio_local = Config().set_minio() 
        
        self.init_workspace()
    
    def init_workspace(self):
        """
        def description : 로컬폴더와 버켓 생성
        
        """
        
        # 로컬 폴더 여부 확인 후 없으면 생성
        if not os.path.exists(self.minio_local):
            os.makedirs(self.minio_local)
        
        # 버킷 존재 여부 확인 후 없으면 생성
        if not self.external_client.bucket_exists(self.minio_bucket):
            self.external_client.make_bucket(self.minio_bucket)

    def generate_local_path(self, file_exe):
        """
        def description : 로컬 임시 저장 경로 셋팅

        Parameters
        ----------
        file_exe : 파일 확장자 (str)

        Returns
        -------
        local_download_path : 로컬의 임시 저장 경로 (str)
        
        """
        
        now = datetime.datetime.now()
        base_path = sys.path[1]
        local_download_path = f"{base_path}/{self.minio_local}/{now.strftime('%Y%m%d_%H%M%S')}{now.microsecond}.{file_exe}" 
        
        return local_download_path

    def generate_minio_folder_path(self):
        """
        def description : minio 저장 경로 셋팅
        """
        now = datetime.datetime.now()
        folder_path = now.strftime("%Y/%m/%d")
        return folder_path
    
    def generate_minio_model_path(self, folder_path, file_name, file_exe):
        
        minio_upload_path = f"models/{folder_path}/{file_name}.{file_exe}"
        return minio_upload_path

    def generate_df_folder_path(self):
        """
        def description : df 저장 경로 셋팅
        """
        now = datetime.datetime.now()
        folder_path = now.strftime("%Y/%m/%d")
        return folder_path
    
    def generate_df_model_path(self, folder_path, file_name, file_exe):
        
        df_upload_path = f"datasets/{folder_path}/{file_name}.{file_exe}"
        return df_upload_path

    def is_file_exist(self, file_path):
        """
        def description : 파일조회
        
        Parameters
        ----------
        file_path : 파일 경로 (str)
        
        Returns
        -------
        bool
        """
        try:
            # 폴더 정보조회
            response = self.external_client.stat_object(self.minio_bucket, file_path)
            return True
            
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return False
            
            else:
                self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
                raise

        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise
    
    def upload_file(self, file_minio_path, file_local_path):
        """
        def description : 파일 업로드

        Parameters
        ----------
        file_minio_path : 파일을 저장 할 오브젝트 스토리지 경로 (str)
        file_local_path : 파일이 저장 된 로컬 경로 (str)
        
        """
        
        try:
            self.external_client.fput_object(self.minio_bucket, file_minio_path, file_local_path)
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
    
    def download_file(self, file_minio_path, file_local_path):
        """
        def description : 파일 다운로드

        Parameters
        ----------
        file_minio_path : 파일이 저장 된 오브젝트 스토리지 경로 (str)
        file_local_path : 파일을 저장 할 로컬 경로 (str)

        Returns
        -------
        file_local_path : 파일을 저장 할 로컬 경로 (str)
        """
        
        try:
            self.external_client.fget_object(self.minio_bucket, file_minio_path, file_local_path) 
            return file_local_path
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
    
    def read_file(self, file_minio_path):
        
        try:
            file = self.external_client.get_object(self.minio_bucket, file_minio_path)
            return file
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
    
    def read_files_in_folder(self, folder_minio_path, name_search=None):
        
        try:
            file_list = []

            # 폴더상에 있는 데이터 리스트를 조회
            file_minio_path_list = self.external_client.list_objects(self.minio_bucket, prefix=folder_minio_path, recursive=True)
            for file_minio_path in file_minio_path_list:
                if file_minio_path.is_dir:  # 폴더 자체는 무시
                    continue

                # 파일 가져오기
                if name_search == None:
                    file = self.read_file(file_minio_path.object_name)
                    file_list.append(file)

                else:
                    if name_search in file_minio_path.object_name:
                        file = self.read_file(file_minio_path.object_name)
                        file_list.append(file)

            return file_list
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
    
    def download_files_in_folder(self, folder_minio_path, name_search=None):
        
        try:
            file_list = []

            # 폴더상에 있는 데이터 리스트를 조회
            file_minio_path_list = self.external_client.list_objects(self.minio_bucket, prefix=folder_minio_path, recursive=True)
            for file_minio_path in file_minio_path_list:
                if file_minio_path.is_dir:  # 폴더 자체는 무시
                    continue

                # 파일 가져오기
                if name_search == None:
                    file = self.download_file(file_minio_path.object_name, f"{file_minio_path.object_name}")
                    file_list.append(file)

                else:
                    if name_search in file_minio_path.object_name:
                        file = self.download_file(file_minio_path.object_name, f"{file_minio_path.object_name}")
                        file_list.append(file)

            return file_list
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")