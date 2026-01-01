"""
模型训练模块
负责训练各种机器学习模型
"""

import pickle
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """模型训练器类，负责训练各种机器学习模型"""
    
    def __init__(self, model_dir: str = "ml_model/saved_models"):
        self.model_dir = model_dir
        self.models = {}
        self.trained_models = {}
        self.model_metrics = {}
        self.feature_names = []
        self.target_name = ""
        
        # 确保模型目录存在
        os.makedirs(model_dir, exist_ok=True)
        
        # 初始化可用模型
        self._initialize_models()
    
    def _initialize_models(self):
        """初始化可用的模型"""
        self.models = {
            'linear_regression': LinearRegression(),
            'ridge': Ridge(),
            'lasso': Lasso(),
            'elastic_net': ElasticNet(),
            'random_forest': RandomForestRegressor(random_state=42),
            'gradient_boosting': GradientBoostingRegressor(random_state=42),
            'svr': SVR(),
            'decision_tree': DecisionTreeRegressor(random_state=42),
            'knn': KNeighborsRegressor()
        }
    
    def train_model(self, X: pd.DataFrame, y: pd.Series, model_type: str = 'linear_regression', 
                   test_size: float = 0.2, tune_hyperparameters: bool = False) -> Dict[str, Any]:
        """
        训练指定类型的模型
        
        Args:
            X: 特征数据
            y: 目标数据
            model_type: 模型类型
            test_size: 测试集比例
            tune_hyperparameters: 是否进行超参数调优
            
        Returns:
            包含训练结果的字典
        """
        try:
            # 检查模型类型是否有效
            if model_type not in self.models:
                return {
                    'success': False,
                    'message': f'不支持的模型类型: {model_type}'
                }
            
            # 保存特征名称和目标名称
            self.feature_names = list(X.columns)
            self.target_name = y.name if y.name else 'target'
            
            # 分割训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            # 获取模型
            model = self.models[model_type]
            
            # 超参数调优
            if tune_hyperparameters:
                model = self._tune_hyperparameters(model, model_type, X_train, y_train)
            
            # 训练模型
            model.fit(X_train, y_train)
            
            # 预测
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
            # 计算评估指标
            train_metrics = self._calculate_metrics(y_train, y_train_pred)
            test_metrics = self._calculate_metrics(y_test, y_test_pred)
            
            # 交叉验证
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
            
            # 保存模型和指标
            model_name = f"{model_type}_{len(self.trained_models)}"
            self.trained_models[model_name] = model
            self.model_metrics[model_name] = {
                'train_metrics': train_metrics,
                'test_metrics': test_metrics,
                'cv_scores': {
                    'mean': cv_scores.mean(),
                    'std': cv_scores.std(),
                    'scores': cv_scores.tolist()
                },
                'model_type': model_type,
                'feature_names': self.feature_names,
                'target_name': self.target_name
            }
            
            # 保存模型到文件
            model_path = os.path.join(self.model_dir, f"{model_name}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            logger.info(f"模型训练成功: {model_name}, 测试集R²: {test_metrics['r2']:.4f}")
            
            return {
                'success': True,
                'message': '模型训练成功',
                'model_name': model_name,
                'model_type': model_type,
                'train_metrics': train_metrics,
                'test_metrics': test_metrics,
                'cv_scores': {
                    'mean': cv_scores.mean(),
                    'std': cv_scores.std()
                },
                'model_path': model_path
            }
            
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            return {
                'success': False,
                'message': f'模型训练失败: {str(e)}'
            }
    
    def _tune_hyperparameters(self, model, model_type: str, X_train: pd.DataFrame, y_train: pd.Series):
        """超参数调优"""
        param_grids = {
            'ridge': {'alpha': [0.1, 1.0, 10.0, 100.0]},
            'lasso': {'alpha': [0.1, 1.0, 10.0, 100.0]},
            'elastic_net': {'alpha': [0.1, 1.0, 10.0], 'l1_ratio': [0.1, 0.5, 0.9]},
            'random_forest': {'n_estimators': [50, 100, 200], 'max_depth': [None, 10, 20]},
            'gradient_boosting': {'n_estimators': [50, 100, 200], 'learning_rate': [0.01, 0.1, 0.2]},
            'svr': {'C': [0.1, 1, 10], 'kernel': ['linear', 'rbf']},
            'decision_tree': {'max_depth': [None, 10, 20], 'min_samples_split': [2, 5, 10]},
            'knn': {'n_neighbors': [3, 5, 7], 'weights': ['uniform', 'distance']}
        }
        
        if model_type in param_grids:
            grid_search = GridSearchCV(
                model, param_grids[model_type], cv=5, scoring='r2', n_jobs=-1
            )
            grid_search.fit(X_train, y_train)
            logger.info(f"最佳参数: {grid_search.best_params_}")
            return grid_search.best_estimator_
        
        return model
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """计算评估指标"""
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2
        }
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型类型"""
        return list(self.models.keys())
    
    def get_trained_models(self) -> List[str]:
        """获取已训练的模型名称"""
        return list(self.trained_models.keys())
    
    def get_model_metrics(self, model_name: str) -> Dict[str, Any]:
        """获取指定模型的评估指标"""
        if model_name not in self.model_metrics:
            return {
                'success': False,
                'message': f'模型 {model_name} 不存在'
            }
        
        return {
            'success': True,
            'metrics': self.model_metrics[model_name]
        }
    
    def load_model(self, model_path: str) -> Dict[str, Any]:
        """
        从文件加载模型
        
        Args:
            model_path: 模型文件路径
            
        Returns:
            包含加载结果的字典
        """
        try:
            if not os.path.exists(model_path):
                return {
                    'success': False,
                    'message': f'模型文件不存在: {model_path}'
                }
            
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            model_name = os.path.basename(model_path).replace('.pkl', '')
            self.trained_models[model_name] = model
            
            logger.info(f"模型加载成功: {model_name}")
            
            return {
                'success': True,
                'message': '模型加载成功',
                'model_name': model_name
            }
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            return {
                'success': False,
                'message': f'模型加载失败: {str(e)}'
            }
    
    def compare_models(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Dict[str, Any]:
        """
        比较所有模型的性能
        
        Args:
            X: 特征数据
            y: 目标数据
            test_size: 测试集比例
            
        Returns:
            包含所有模型比较结果的字典
        """
        comparison_results = {}
        
        for model_type in self.models.keys():
            result = self.train_model(X, y, model_type, test_size)
            if result['success']:
                comparison_results[model_type] = {
                    'r2': result['test_metrics']['r2'],
                    'rmse': result['test_metrics']['rmse'],
                    'mae': result['test_metrics']['mae'],
                    'cv_mean': result['cv_scores']['mean']
                }
        
        # 按R²分数排序
        sorted_models = sorted(comparison_results.items(), key=lambda x: x[1]['r2'], reverse=True)
        
        return {
            'success': True,
            'comparison_results': comparison_results,
            'best_model': sorted_models[0][0] if sorted_models else None,
            'sorted_models': sorted_models
        }