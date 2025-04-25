from shares.modules.log import system_module_log
import pandas as pd

import inspect

class DataFrame():

    def __init__(self):
        self.log = system_module_log
    
    def concatenate_dataset(self, dataset_local_path_list, direction="row-wise"):
        """
        def description : 데이터 셋 콘켓

        Parameters
        ----------
        dataset_local_path_list : 데이터 셋 리스트 (list[str])

        Returns
        -------
        dataset_concatenated : 콘켓 된 데이터셋 (df)
        """
        
        # 데이터 프레임 조회 및 배열에 추가
        df_list = []
        for dataset_local_path in dataset_local_path_list:
            df = self.read_dataframe(dataset_local_path)
            df_list.append(df)
        
        try:
            # CASE 1 : 행 방향으로 병합
            if direction == "row-wise":
                dataset_concatenated = pd.concat(df_list, ignore_index=True)
                
            # CASE 2 : 열 방향으로 병합
            else:
                dataset_concatenated = pd.concat(df_list, axis=1)
                dataset_concatenated = self.replace_overlab_columns(dataset_concatenated)
            
            return dataset_concatenated
                
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise 

    def replace_overlab_columns(self, df):
        """
        def description : 칼럼 중복 치환

        Parameters
        ----------
        df : 데이터 프레임 (df)

        Returns
        -------
        df : 칼럼 중복 치환 된 데이터 프레임 (df)
        """
        
        columns_overlab_cnt = {}

        column_names_list = []
        for col in df.columns:
            if col in columns_overlab_cnt:
                # 열 이름이 이미 존재하는 경우 카운트를 증가시키고 새로운 이름 생성
                columns_overlab_cnt[col] += 1
                column_name = f"{col}_{columns_overlab_cnt[col]}"
                
            else:
                # 처음 발견된 열 이름인 경우 카운트를 1로 설정
                columns_overlab_cnt[col] = 1
                column_name = col
            
            # 새로운 열 이름 목록에 추가
            column_names_list.append(column_name)

        # 데이터프레임의 열 이름 변경
        df.columns = column_names_list
        
        return df
    
    def read_dataframe(self, file_path, exe="xlsx"):
        """
        def description : 데이터프레임 리드

        Parameters
        ----------
        file_path : 파일 경로 (str)
        exe : 확장자 (str)

        Returns
        -------
        df : 데이터 프레임 (df)
        """
        
        # 데이터프레임 조회
        try:
            if exe == "csv":
                df = pd.read_csv(file_path)
            
            elif exe == "xlsx":
                df = pd.read_excel(file_path)
                
            elif exe == "parquet":
                df = pd.read_parquet(file_path)
            
            else:
                df = pd.read_excel(file_path)
        
            return df
                
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise 
    
    def write_dataset(self, dataset, dataset_path, dataset_exe="xlsx"):
        """
        def description : 데이터프레임 작성

        Parameters
        ----------
        dataset : 데이터 셋 (df)
        dataset_path : 데이터 셋 경로 (str)
        dataset_exe : 데이터 셋 확장자 (str)
        """
        
        try:
            if dataset_exe == "parquet":
                # 결과를 Parquet 파일로 저장
                dataset.to_parquet(dataset_path, index=False)
            
            elif dataset_exe == "csv":
                # 결과를 새 CSV 파일로 저장
                dataset.to_csv(dataset_path, index=False)
            
            elif dataset_exe == "xlsx":
                # 결과를 새 xlsx 파일로 저장
                dataset.to_excel(dataset_path, index=False)
            
            else:
                dataset.to_excel(dataset_path, index=False)
                
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")    
            raise