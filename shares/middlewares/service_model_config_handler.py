from shares.modules.log import system_module_log
from shares.modules.dataframe import DataFrame
    
from sklearn.preprocessing import StandardScaler

import yaml
import numpy as np
import ast
import operator as op

class ModelConfigHandler():
    """
    model_config 을 토대로 df를 정제한다 
    """
    
    def __init__(self):
        self.log = system_module_log
        self.dataframe = DataFrame()
        self.standard_scaler = StandardScaler()
        self.model_model_config = None 
        
        self.model_name = None
        self.model_type = None
        self.features = None
        self.targets = None
        self.derived_params = None
        self.preprocessing = None
        self.hyperparameters = None
        
        self.df = None

    """
    loader
    """
    def load_model_config(self, model_config_path: str):
        
        with open(model_config_path, 'r') as f:
            self.model_model_config = yaml.safe_load(f)
        
            self.model_name = self.model_model_config["model_name"]
            self.model_type = self.model_model_config["model_type"]
            self.features = self.model_model_config["features"]
            self.targets = self.model_model_config["targets"]
            self.derived_params = self.model_model_config["derived_params"]
            self.preprocessing = self.model_model_config["preprocessing"]
            self.hyperparameters = self.model_model_config["hyperparameters"]
    """
    getter
    """
    def get_model_config(self):
        model_config = {
            "model_name" : self.model_name,
            "model_type" : self.model_type,
            "features" : self.features,
            "targets" : self.targets,
            "derived_params" : self.derived_params,
            "preprocessing" : self.preprocessing,
            "hyperparameters" : self.hyperparameters,
        }
        return model_config

    def get_df(self):
        return self.df
    
    """
    preprocessor
    """
    def preprocess_df_by_model_config(self, df):
        
        # 데이터 셋팅
        derived_params = self.model_model_config["derived_params"]
        preprocessing_fillna = self.preprocessing.get("fillna") 
        preprocessing_convert_numeric = self.preprocessing.get("convert_numeric") 
        preprocessing_scaling = self.preprocessing.get("scaling") 
        
        # 파생변수 추가
        for derived_param in derived_params:
            name = derived_param.get("name")
            expression = derived_param.get("expression")
            if name:
                if expression:
                    df = self.apply_to_df(df, expression, 'CHANGE_AFTER_2DAY')

        # Fill NaNs, 결측치
        if preprocessing_fillna:
            if preprocessing_fillna == "all":
                df.fillna(df.mean(), inplace=True)
                
            else:
                df[preprocessing_fillna].fillna(df[preprocessing_fillna].mean(), inplace=True)
        
        # 수치화 변경
        if preprocessing_convert_numeric:
            if preprocessing_convert_numeric == "all":
                df[self.features] = self.dataframe.convert_numeric_columns(df[self.features])
            
            else:
                df[preprocessing_convert_numeric] = self.dataframe.convert_numeric_columns(df[preprocessing_convert_numeric])
        
        # 스케일링
        if preprocessing_scaling:
            if preprocessing_scaling == "all":
                df[self.features] = self.standard_scaler.fit_transform(df[self.features])
            
            else:
                df[preprocessing_scaling] = self.standard_scaler.fit_transform(df[preprocessing_scaling])
        
        return df

    def apply_to_df(self, df, expr, column_name):
        df[column_name] = df.apply(lambda row: self.eval_expr(expr, row.to_dict()), axis=1)
        return df

    def eval_expr(self, expr, variables):
        
        self.allowed_ops = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.Pow: op.pow,
            ast.BitXor: op.xor,
            ast.USub: op.neg,
            ast.Gt: op.gt,
            ast.Lt: op.lt,
            ast.GtE: op.ge,
            ast.LtE: op.le,
            ast.Eq: op.eq,
            ast.NotEq: op.ne,
        }
        self.allowed_funcs = {
            'int': int,
            'float': float,
            'abs': abs,
            'max': max,
            'min': min,
            'round': round, # 필요시 함수 작성 후 추가
        }
        def _eval(node):
            try:
                if isinstance(node, ast.Constant):
                    return node.value
                elif isinstance(node, ast.Name):
                    return variables[node.id]
                elif isinstance(node, ast.BinOp):
                    return self.allowed_ops[type(node.op)](_eval(node.left), _eval(node.right))
                elif isinstance(node, ast.UnaryOp):
                    return self.allowed_ops[type(node.op)](_eval(node.operand))
                elif isinstance(node, ast.Compare):
                    left = _eval(node.left)
                    for op_, comp in zip(node.ops, node.comparators):
                        if not self.allowed_ops[type(op_)](left, _eval(comp)):
                            return False
                        left = _eval(comp)
                    return True
                elif isinstance(node, ast.IfExp):
                    return _eval(node.body) if _eval(node.test) else _eval(node.orelse)
                elif isinstance(node, ast.Call):
                    func_name = node.func.id
                    if func_name not in self.allowed_funcs:
                        raise ValueError(f"Function '{func_name}' is not allowed")
                    args = [_eval(arg) for arg in node.args]
                    return self.allowed_funcs[func_name](*args)
                else:
                    raise ValueError(f"Unsupported expression: {type(node)}")
            
            except Exception as e:
                raise ValueError(f"Exception on expression: {str(e)}")
                
        tree = ast.parse(expr, mode='eval').body
        return _eval(tree)