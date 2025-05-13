
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight

import numpy as np

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