"""
模型训练器模块
负责机器学习模型的训练和评估
"""

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

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """模型训练器类"""
    
    def __init__(self):
        """初始化模型训练器"""
        self.models = {}
        self.trained_models = {}
        self.model_metrics = {}
        self.feature_names = []
        self.target_name = ""
        
        # 注册可用模型
        self._register_models()
        
        # 确保模型保存目录存在
        self.model_dir = "saved_models"
        os.makedirs(self.model_dir, exist_ok=True)
    
    def _register_models(self):
        """注册可用的模型"""
        self.models = {
            "linear_regression": LinearRegression(),
            "ridge": Ridge(),
            "lasso": Lasso(),
            "random_forest": RandomForestRegressor(random_state=42),
            "gradient_boosting": GradientBoostingRegressor(random_state=42),
            "svr": SVR()
        }
    
    def get_available_models(self) -> List[str]:
        """
        获取可用的模型列表
        
        Returns:
            模型名称列表
        """
        return list(self.models.keys())
    
    def get_trained_models(self) -> List[str]:
        """
        获取已训练的模型列表
        
        Returns:
            已训练模型名称列表
        """
        return list(self.trained_models.keys())
    
    def train_model(self, X: pd.DataFrame, y: pd.Series, model_type: str = "linear_regression", 
                   test_size: float = 0.2, tune_hyperparameters: bool = False) -> Dict[str, Any]:
        """
        训练模型
        
        Args:
            X: 特征DataFrame
            y: 目标Series
            model_type: 模型类型
            test_size: 测试集比例
            tune_hyperparameters: 是否调参
            
        Returns:
            训练结果字典
        """
        try:
            # 检查模型类型是否有效
            if model_type not in self.models:
                return {
                    'success': False,
                    'message': f'不支持的模型类型: {model_type}'
                }
            
            # 保存特征和目标名称
            self.feature_names = list(X.columns)
            self.target_name = y.name if y.name else "target"
            
            # 分割数据集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            # 获取模型
            model = self.models[model_type]
            
            # 如果需要调参
            if tune_hyperparameters:
                model = self._tune_hyperparameters(model, model_type, X_train, y_train)
            
            # 训练模型
            model.fit(X_train, y_train)
            
            # 预测
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
            # 计算指标
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
            
            # 交叉验证
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
            cv_metrics = {
                'mean': cv_scores.mean(),
                'std': cv_scores.std(),
                'scores': cv_scores.tolist()
            }
            
            # 生成模型名称
            model_name = f"{model_type}_{len(self.trained_models) + 1}"
            
            # 保存模型
            model_path = os.path.join(self.model_dir, f"{model_name}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            # 保存模型信息
            model_info = {
                'model_name': model_name,
                'model_type': model_type,
                'model_path': model_path,
                'feature_names': self.feature_names,
                'target_name': self.target_name,
                'train_metrics': train_metrics,
                'test_metrics': test_metrics,
                'cv_metrics': cv_metrics,
                'tuned': tune_hyperparameters
            }
            
            info_path = os.path.join(self.model_dir, f"{model_name}_info.json")
            with open(info_path, 'w') as f:
                json.dump(model_info, f, indent=2)
            
            # 保存到内存
            self.trained_models[model_name] = model
            self.model_metrics[model_name] = model_info
            
            return {
                'success': True,
                'message': f'模型 {model_name} 训练成功',
                'model_name': model_name,
                'model_path': model_path,
                'train_metrics': train_metrics,
                'test_metrics': test_metrics,
                'cv_metrics': cv_metrics,
                'feature_names': self.feature_names,
                'target_name': self.target_name
            }
            
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            return {
                'success': False,
                'message': f'模型训练失败: {str(e)}'
            }
    
    def _tune_hyperparameters(self, model, model_type: str, X: pd.DataFrame, y: pd.Series):
        """
        调整模型超参数
        
        Args:
            model: 模型实例
            model_type: 模型类型
            X: 特征DataFrame
            y: 目标Series
            
        Returns:
            调参后的模型
        """
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
        """
        获取模型评估指标
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型指标字典
        """
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
        """
        比较所有模型的性能
        
        Args:
            X: 特征DataFrame
            y: 目标Series
            test_size: 测试集比例
            
        Returns:
            模型比较结果
        """
        try:
            # 分割数据集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            comparison_results = {}
            
            for model_name, model in self.models.items():
                try:
                    # 训练模型
                    model.fit(X_train, y_train)
                    
                    # 预测
                    y_pred = model.predict(X_test)
                    
                    # 计算指标
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
            
            # 按R2分数排序
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
        """
        加载模型
        
        Args:
            model_path: 模型文件路径
            
        Returns:
            加载的模型
        """
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            return model
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            return None
    
    def load_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        加载模型信息
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型信息字典
        """
        info_path = os.path.join(self.model_dir, f"{model_name}_info.json")
        try:
            with open(info_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载模型信息失败: {str(e)}")
            return None