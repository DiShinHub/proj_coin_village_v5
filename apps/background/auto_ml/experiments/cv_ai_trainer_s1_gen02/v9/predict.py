
from tensorflow.keras.optimizers import Adam

import numpy as np
import os

class Predict():
    
    def __init__(self, df, config=None):
        self.config = config
        self.features = config.get("features")
        self.targets = config.get("targets")
        self.hyperparameters = config.get("hyperparameters")
        
        self.df = df
        self.df_f = None

    def create_sequences_for_predict(self, X, time_steps=40):
        Xs = []
        for i in range(len(X) - time_steps + 1):
            Xs.append(X[i : i + time_steps])
            
        return np.array(Xs)
    
    def predict(self, model, df):
        
        X = self.create_sequences_for_predict(df[self.features], self.hyperparameters.get("time_steps"))
        
        model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'], run_eagerly=True)
        prediction_softmax = model.predict(X)
        
        predicted_label = np.argmax(prediction_softmax, axis=1)
        prediction = int(predicted_label[0])
        return prediction
    