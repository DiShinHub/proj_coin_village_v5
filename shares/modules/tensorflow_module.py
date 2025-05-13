from shares.modules.log import system_module_log

from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

import numpy as np 

class TensorflowModule():

    def create_sequences(self, X, Y, time_steps=40):
        
        Xs, Ys = [], []
        for i in range(len(X) - time_steps):
            Xs.append(X[i : i + time_steps])
            Ys.append(Y[i + time_steps])
            
        return np.array(Xs), np.array(Ys)
    
    def create_sequences_for_predict(self, X, time_steps=40):
        """
        학습할 때는 정답을 주고, 예측할 때는 가장 마지막 시퀀스로 미래를 예측**
        - 학습용 시퀀스:
        `X = [t0, t1, ..., t39]` → `Y = t40`

        - 예측용 시퀀스:
        `X = [t0, t1, ..., t39]` → 모델이 `t40`을 예측
        """
        
        Xs = []
        for i in range(len(X) - time_steps + 1):  # 범위 조정
            Xs.append(X[i : i + time_steps])
            
        return np.array(Xs)

    def train_by_lstm_model(self, X, Y, time_steps, batch_size, epochs, early_stop=False, class_weight=None):
        
        X, Y = self.create_sequences(X, Y, time_steps)
        
        if early_stop:
            self.early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True) # 조기 종료 콜백 설정
        
        # 모델 정의
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(time_steps, X.shape[2])),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(3, activation='softmax') 
        ])
        model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])
        
        # 모델 학습
        model.fit(
            X, Y,
            epochs=epochs,                      # 전체 데이터셋을 몇 번 반복해서 학습할지
            batch_size=batch_size,              # 한 번에 학습에 사용할 데이터의 개수
            validation_split=0.1,               # 학습 데이터 중 10%를 검증용(validation) 으로 사용
            verbose=0,                          # 출력 레벨 설정: 0: 아무 출력 없음, 1: progress bar로 출력, 2: 에포크마다 한 줄 요약
            class_weight=class_weight,          # 가중치 
            callbacks=[self.early_stopping]     # 조기 종료 추가
        )
        return model
    
    def predict_by_lstm_model(self, model, X, time_steps):
        
        X = self.create_sequences_for_predict(X, time_steps)
        
        model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'], run_eagerly=True)
        predict = model.predict(X)
        
        return  predict