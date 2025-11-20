
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight

import numpy as np
from sklearn.metrics import accuracy_score

class SklearnModule():
    
    def __init__(self):
        self.scaler = StandardScaler()

    def standardize_fit_data(self, data, col_x):
        data[col_x] = self.scaler.fit_transform(data[col_x])
        return data

    def standardize_data(self, data, col_x):
        data[col_x] = self.scaler.transform(data[col_x])
        return data
    
    def encode_labels(self, col):
        encoder = LabelEncoder()
        col = encoder.fit_transform(col) 
        return col
    
    def calculate_class_weight(self, Y):
        
        # 클래스 가중치 계산 (Y는 정수 인코딩된 라벨)
        class_weights = compute_class_weight(
            class_weight='balanced',
            classes=np.unique(Y),
            y=Y
        )
        class_weight_dict = dict(enumerate(class_weights))
        
        return class_weight_dict
    
    def calculate_permutation_importance(self, model, X, Y, time_steps, n_repeats=3):

        base_preds = model.predict(X.reshape(-1, time_steps, X.shape[1]))
        base_score = accuracy_score(Y, base_preds.argmax(axis=1))
        
        feature_importances = []
        
        for i in range(X.shape[1]):
            scores = []
            for _ in range(n_repeats):
                X_permuted = X.copy()
                np.random.shuffle(X_permuted[:, i])  # i번째 feature만 셔플
                preds = model.predict(X_permuted.reshape(-1, time_steps, X.shape[1]))
                score = accuracy_score(Y, preds.argmax(axis=1))
                scores.append(base_score - score)  # 성능 하락
            feature_importances.append(np.mean(scores))
        
        return feature_importances