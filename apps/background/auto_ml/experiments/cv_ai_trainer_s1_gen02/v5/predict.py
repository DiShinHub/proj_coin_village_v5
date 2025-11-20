
from shares.modules.log import Log
from shares.middlewares.auto_ml_experiment_handler import AutoMlExperimentHandler
from tensorflow.keras.optimizers import Adam

import numpy as np
import os

class Predict(AutoMlExperimentHandler):
    
    def __init__(self, df, config=None):
        self.log = Log(os.path.basename(__file__)).get_logger()
        super().__init__(df, config)

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
    