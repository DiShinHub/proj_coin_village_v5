
from sklearn.preprocessing import StandardScaler

class SklearnModule():
    
    def __init__(self):
        self.scaler = StandardScaler()

    def standardize_fit_data(self, data, col_x):
        data[col_x] = self.scaler.fit_transform(data[col_x])
        return data

    def standardize_data(self, data, col_x):
        data[col_x] = self.scaler.transform(data[col_x])
        return data