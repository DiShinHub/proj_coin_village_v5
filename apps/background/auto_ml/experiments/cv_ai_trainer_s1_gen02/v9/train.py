

from sklearn.utils.class_weight import compute_class_weight
from sklearn.model_selection import train_test_split

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

from collections import Counter
import numpy as np
import os

class Train():
    
    def __init__(self, df, config=None):
        self.config = config
        self.features = config.get("features")
        self.targets = config.get("targets")
        self.hyperparameters = config.get("hyperparameters")
        
        self.df = df
        self.df_f = None
    
    """
    train
    """
    def undersample(self, X, Y):

        # 다수 클래스(0) 인덱스 추출
        idx_majority = np.where(Y == 0)[0]
        idx_minority = np.where(Y == 1)[0]

        # 다수 클래스 랜덤 선택 (소수 클래스 수와 맞춤)
        np.random.seed(42)
        idx_majority_downsampled = np.random.choice(idx_majority, size=len(idx_minority), replace=False)

        # 선택된 인덱스 합치기
        idx_resampled = np.concatenate([idx_majority_downsampled, idx_minority])

        # 리샘플링된 X, y
        X_resampled = X[idx_resampled]
        Y_resampled = Y[idx_resampled]
        
        return X_resampled, Y_resampled
    
    def create_sequences(self, X, Y, time_steps=40):
        Xs, Ys = [], []
        for i in range(len(X) - time_steps):
            Xs.append(X[i : i + time_steps])
            Ys.append(Y[i + time_steps])
            
        return np.array(Xs), np.array(Ys)
    
    def train(self):
        
        # feature target 셀렉션
        X, Y = self.df[self.features].values, self.df[self.targets[0]].values
        X_origin = X.copy
        Y_origin = Y.copy
        
        X, Y = self.undersample(X, Y)
        
        # # 클래스 가중치 계산
        class_weight = None
        # class_weights = compute_class_weight(
        #     class_weight='balanced',
        #     classes=np.unique(Y),
        #     y=Y
        # )
        # class_weight = dict(enumerate(class_weights))

        # 시퀀스 생성
        X, Y = self.create_sequences(X, Y, self.hyperparameters.get("time_steps"))

        # train/val 분리 
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.1, random_state=42, stratify=Y)

        # 모델 정의
        early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(self.hyperparameters.get("time_steps"), X.shape[2])),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(2, activation='softmax')
        ])
        model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=0.0005), metrics=['accuracy'])

        # 학습
        history = model.fit(
            X_train, Y_train,
            epochs=self.hyperparameters.get("epochs"),
            batch_size=self.hyperparameters.get("batch_size"),
            validation_data=(X_test, Y_test),
            verbose=0,
            class_weight=class_weight,
            callbacks=[early_stopping]
        )

        # 예측
        y_prob = model.predict(X_test, verbose=0)
        y_pred = np.argmax(y_prob, axis=1)
        y_true = Y_test
        
        return {
            "model" : model,
            "history" : history,
            "df" : self.df,
            "X": X,
            "Y": Y,
            "X_origin": X_origin,
            "Y_origin": Y_origin,
            "X_train": X_train,
            "X_test": X_test,
            "Y_train": Y_train,
            "Y_test": Y_test,
            "y_true": y_true,
            "y_pred": y_pred,
            "y_prob": y_prob,
        }
        
