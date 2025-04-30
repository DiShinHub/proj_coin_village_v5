

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

import np 

class TensorflowModule():

    def create_sequences(self, X, Y, time_steps=40):
        
        Xs, Ys = [], []
        for i in range(len(X) - time_steps):
            Xs.append(X[i : i + time_steps])
            Ys.append(Y[i + time_steps])
            
        return np.array(Xs), np.array(Ys)

    def train_by_lstm_model(self, X, Y, time_steps):
        
        X, Y = self.create_sequences(X, Y, time_steps)
        
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
    
    def predict_by_lstm_model(self, model, X):
        
        model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'], run_eagerly=True)
        predict = model.predict(X)
        
        return  predict