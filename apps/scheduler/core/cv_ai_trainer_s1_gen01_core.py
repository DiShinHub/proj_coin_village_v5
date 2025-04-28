from shares.modules.redis import r as redis_single
from shares.modules.upbit import Upbit
from shares.modules.minio import MinioModule
from shares.functions.common_function import generate_micro_date

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import StandardScaler

import numpy as np
import pandas as pd
import datetime
import os
import inspect

class CvAiTrainerS1Gen01Core():
    slack_post_prefix = ":bee: King Bee."
    
    def __init__(self, log):
        self.log = log
        self.redis = redis_single
        self.upbit = Upbit()
        self.minio = MinioModule()
        
        self.model_folder_path = ""
    
    def set_model_folder_path(self):
        
        self.model_folder_path = self.minio.generate_minio_folder_path()
        return self.model_folder_path
        
    def set_hyper_parameters(self, time_steps, batch_size, epochs, early_stop=False):
        
        self.time_steps = time_steps  # 시퀀스 길이 설정
        self.batch_size = batch_size
        self.epochs = epochs
        if early_stop:
            self.early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True) # 조기 종료 콜백 설정
        
    def generate_model(self, ticker, df):
        
        self.redis.save_msg_on_Q(f"전체 학습 시작: {str(datetime.datetime.now())}")
            
        # 입출력 칼럼
        col_f = ['timestamp', 'weekday',
        'open', 'high', 'low', 'close', 'volume', 'volume_ma5', 'volume_ma20',
        'volume_ratio', 'obv', 'vwap', 'volume_volatility', 'volume_spike',
        'rsi', 'macd', 'macd_signal', 'bollinger_partition'
        ]
        
        col_t = ['by_ontime_change_after_15min',
        'by_ontime_change_after_30min', 'by_ontime_change_after_1hour',
        'by_ontime_change_after_4hour', 'by_ontime_change_after_12hour',
        'by_ontime_change_after_1day',
        'by_prev_change_after_15min',
        'by_prev_change_after_30min', 'by_prev_change_after_1hour',
        'by_prev_change_after_4hour', 'by_prev_change_after_12hour',
        'by_prev_change_after_1day'
        ]

        try:
            # 전처리
            data = df.copy()
            data.fillna(data.mean(), inplace=True)
            data['timestamp'] = pd.to_datetime(data['tick_datetime']).astype(int) / 10**9
            data.replace({'sideways': 1, 'up': 2, 'down': 0}, inplace=True)
        
            scaler = StandardScaler()
            data[col_f] = scaler.fit_transform(data[col_f]) # 입력과 출력 분리

            # 모델 학습 후 업로드
            local_path_list = []
            for idx, target in enumerate(col_t):
                self.log.info(f"{idx + 1}/{len(col_t)} - {target} 모델 학습 시작...")
                
                # 저장경로 설정
                local_path = self.minio.generate_local_path("h5")
                local_path_list.append(local_path)
                minio_path = self.minio.generate_minio_model_path(folder_path=self.model_folder_path, file_name=f"{ticker}_{target}_{generate_micro_date()}", file_exe="h5")
                
                # 학습 데이터 셋팅
                X, Y = data[col_f].values, data[target].values
                
                # 모델 헉습
                model = self.train_model(X, Y)
                
                # 모델 저장
                model.save(local_path, save_format="h5")
                
                # 모델 업로드
                self.minio.upload_file(minio_path, local_path)
                
                self.log.info(f"{idx + 1}/{len(col_t)} - {target} 모델 학습 종료...")
            
            return
            
        except Exception as e:
            self.log.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
        
        finally:
            self.redis.save_msg_on_Q(f"전체 학습 종료: {str(datetime.datetime.now())}")
            
            if local_path_list:
                for local_path in local_path_list:
                    if os.path.exists(local_path):
                        os.remove(local_path)
            
    """
    sub process
    """     
    def create_sequences(self, X, Y, time_steps=40):
        
        Xs, Ys = [], []
        for i in range(len(X) - time_steps):
            Xs.append(X[i : i + time_steps])
            Ys.append(Y[i + time_steps])
            
        return np.array(Xs), np.array(Ys)

    def train_model(self, X, Y):
        
        X, Y = self.create_sequences(X, Y, self.time_steps)
        
        # 모델 정의
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(self.time_steps, X.shape[2])),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(3, activation='softmax') 
        ])
        model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])
        
        # 모델 학습
        model.fit(
            X, Y,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=0.1,
            verbose=1,
            callbacks=[self.early_stopping]  # 조기 종료 추가
        )
        return model
          