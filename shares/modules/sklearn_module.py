
from sklearn.preprocessing import StandardScaler

class SklearnModule():

    def standardize_fit_data(self, data, col_x):
        scaler = StandardScaler()
        data[col_x] = scaler.fit_transform(data[col_x])
        return data

    def standardize_data(self, data, col_x):
        scaler = StandardScaler()
        data[col_x] = scaler.transform(data[col_x])
        return data