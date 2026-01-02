import os
import pickle
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    
    def __init__(self):
        self.models = {}
        self.trained_models = {}
        self.model_metrics = {}
        self.feature_names = []
        self.target_name = ""
        
        self._register_models()
        
        self.model_dir = "saved_models"
        try:
            os.makedirs(self.model_dir, exist_ok=True)
            logger.info(f"模型保存目录已创建或已存在: {self.model_dir}")
        except Exception as e:
            logger.error(f"创建模型保存目录失败: {str(e)}")
            raise
    
    def _register_models(self):
        self.models = {
            "linear_regression": LinearRegression(),
            "ridge": Ridge(),
            "lasso": Lasso(),
            "random_forest": RandomForestRegressor(random_state=42),
            "gradient_boosting": GradientBoostingRegressor(random_state=42),
            "svr": SVR()
        }
    
    def get_available_models(self) -> List[str]:
        return list(self.models.keys())
    
    def get_trained_models(self) -> List[str]:
        return list(self.trained_models.keys())
    
    def train_model(self, X: pd.DataFrame, y: pd.Series, model_type: str = "linear_regression",
                   test_size: float = 0.2, tune_hyperparameters: bool = False, return_model: bool = True) -> Dict[str, Any]:
        try:
            if model_type not in self.models:
                return {
                    'success': False,
                    'message': f'不支持的模型类型: {model_type}'
                }
            
            self.feature_names = list(X.columns)
            self.target_name = y.name if y.name else "target"
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            model = self.models[model_type]
            
            if tune_hyperparameters:
                model = self._tune_hyperparameters(model, model_type, X_train, y_train)
            
            model.fit(X_train, y_train)
            
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
            train_metrics = {
                'r2': r2_score(y_train, y_train_pred),
                'rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
                'mae': mean_absolute_error(y_train, y_train_pred)
            }
            
            test_metrics = {
                'r2': r2_score(y_test, y_test_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
                'mae': mean_absolute_error(y_test, y_test_pred)
            }
            
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
            cv_metrics = {
                'mean': cv_scores.mean(),
                'std': cv_scores.std(),
                'scores': cv_scores.tolist()
            }
            
            model_name = f"{model_type}_{len(self.trained_models) + 1}"
            
            model_info = {
                'model_name': model_name,
                'model_type': model_type,
                'feature_names': self.feature_names,
                'target_name': self.target_name,
                'train_metrics': train_metrics,
                'test_metrics': test_metrics,
                'cv_metrics': cv_metrics,
                'tuned': tune_hyperparameters
            }
            
            model_data = None
            model_info_data = None
            if return_model:
                import base64
                from io import BytesIO
                
                model_bytes = BytesIO()
                pickle.dump(model, model_bytes)
                model_bytes.seek(0)
                model_data = base64.b64encode(model_bytes.read()).decode('utf-8')
                
                info_bytes = BytesIO()
                pickle.dump(model_info, info_bytes)
                info_bytes.seek(0)
                model_info_data = base64.b64encode(info_bytes.read()).decode('utf-8')
            
            self.trained_models[model_name] = model
            self.model_metrics[model_name] = model_info
            
            result = {
                'success': True,
                'message': f'模型 {model_name} 训练成功',
                'model_name': model_name,
                'train_metrics': train_metrics,
                'test_metrics': test_metrics,
                'cv_metrics': cv_metrics,
                'feature_names': self.feature_names,
                'target_name': self.target_name,
                'model_info': model_info
            }
            
            if return_model:
                result['model_data'] = model_data
                result['model_info_data'] = model_info_data
                result['model_path'] = f"memory://{model_name}"
            
            if not return_model:
                model_path = os.path.join(self.model_dir, f"{model_name}.pkl")
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
                
                model_info['model_path'] = model_path
                info_path = os.path.join(self.model_dir, f"{model_name}_info.json")
                with open(info_path, 'w') as f:
                    json.dump(model_info, f, indent=2)
                
                result['model_path'] = model_path
            
            return result
            
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            return {
                'success': False,
                'message': f'模型训练失败: {str(e)}'
            }
    
    def _tune_hyperparameters(self, model, model_type: str, X: pd.DataFrame, y: pd.Series):
        param_grids = {
            "ridge": {'alpha': [0.1, 1.0, 10.0, 100.0]},
            "lasso": {'alpha': [0.1, 1.0, 10.0, 100.0]},
            "random_forest": {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10]
            },
            "gradient_boosting": {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            },
            "svr": {
                'C': [0.1, 1, 10],
                'gamma': ['scale', 'auto', 0.1, 1]
            }
        }
        
        if model_type in param_grids:
            grid_search = GridSearchCV(
                model, param_grids[model_type], cv=5, scoring='r2', n_jobs=-1
            )
            grid_search.fit(X, y)
            return grid_search.best_estimator_
        
        return model
    
    def get_model_metrics(self, model_name: str) -> Dict[str, Any]:
        if model_name not in self.model_metrics:
            return {
                'success': False,
                'message': f'模型 {model_name} 不存在'
            }
        
        return {
            'success': True,
            'model_metrics': self.model_metrics[model_name]
        }
    
    def compare_models(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Dict[str, Any]:
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            comparison_results = {}
            
            for model_name, model in self.models.items():
                try:
                    model.fit(X_train, y_train)
                    
                    y_pred = model.predict(X_test)
                    
                    metrics = {
                        'r2': r2_score(y_test, y_pred),
                        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                        'mae': mean_absolute_error(y_test, y_pred)
                    }
                    
                    comparison_results[model_name] = metrics
                    
                except Exception as e:
                    logger.error(f"模型 {model_name} 训练失败: {str(e)}")
                    comparison_results[model_name] = {
                        'error': str(e)
                    }
            
            sorted_results = sorted(
                comparison_results.items(),
                key=lambda x: x[1].get('r2', float('-inf')),
                reverse=True
            )
            
            return {
                'success': True,
                'comparison_results': comparison_results,
                'best_model': sorted_results[0][0] if sorted_results else None,
                'sorted_results': sorted_results
            }
            
        except Exception as e:
            logger.error(f"模型比较失败: {str(e)}")
            return {
                'success': False,
                'message': f'模型比较失败: {str(e)}'
            }
    
    def load_model(self, model_path: str) -> Any:
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            return model
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            return None
    
    def load_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        info_path = os.path.join(self.model_dir, f"{model_name}_info.json")
        try:
            with open(info_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载模型信息失败: {str(e)}")
            return None