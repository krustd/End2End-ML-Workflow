"""
预测模块
负责使用训练好的模型进行预测
"""

import pickle
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional, Union
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Predictor:
    """预测器类，负责使用训练好的模型进行预测"""
    
    def __init__(self, model_dir: str = "ml_model/saved_models"):
        self.model_dir = model_dir
        self.loaded_models = {}
        self.model_metadata = {}
        self.current_model = None
        self.current_model_name = ""
        
        # 确保模型目录存在
        os.makedirs(model_dir, exist_ok=True)
        
        # 加载目录中的所有模型
        self._load_all_models()
    
    def _load_all_models(self):
        """加载目录中的所有模型"""
        if not os.path.exists(self.model_dir):
            return
        
        for file_name in os.listdir(self.model_dir):
            if file_name.endswith('.pkl'):
                model_path = os.path.join(self.model_dir, file_name)
                self.load_model(model_path)
    
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
                model_data = pickle.load(f)
            
            model_name = os.path.basename(model_path).replace('.pkl', '')
            self.loaded_models[model_name] = model_data
            
            # 尝试加载模型元数据
            metadata_path = model_path.replace('.pkl', '_metadata.json')
            if os.path.exists(metadata_path):
                import json
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                self.model_metadata[model_name] = metadata
            
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
    
    def set_current_model(self, model_name: str) -> Dict[str, Any]:
        """
        设置当前使用的模型
        
        Args:
            model_name: 模型名称
            
        Returns:
            包含设置结果的字典
        """
        if model_name not in self.loaded_models:
            return {
                'success': False,
                'message': f'模型 {model_name} 不存在'
            }
        
        self.current_model = self.loaded_models[model_name]
        self.current_model_name = model_name
        
        logger.info(f"当前模型设置为: {model_name}")
        
        return {
            'success': True,
            'message': f'当前模型设置为: {model_name}',
            'model_name': model_name
        }
    
    def predict(self, input_data: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]) -> Dict[str, Any]:
        """
        使用当前模型进行预测
        
        Args:
            input_data: 输入数据，可以是字典、字典列表或DataFrame
            
        Returns:
            包含预测结果的字典
        """
        try:
            if self.current_model is None:
                return {
                    'success': False,
                    'message': '没有设置当前模型'
                }
            
            # 转换输入数据为DataFrame
            if isinstance(input_data, dict):
                df = pd.DataFrame([input_data])
            elif isinstance(input_data, list):
                df = pd.DataFrame(input_data)
            elif isinstance(input_data, pd.DataFrame):
                df = input_data.copy()
            else:
                return {
                    'success': False,
                    'message': '不支持的输入数据类型'
                }
            
            # 检查特征数量是否匹配
            if hasattr(self.current_model, 'n_features_in_'):
                if df.shape[1] != self.current_model.n_features_in_:
                    return {
                        'success': False,
                        'message': f'特征数量不匹配，模型需要 {self.current_model.n_features_in_} 个特征，输入数据有 {df.shape[1]} 个特征'
                    }
            
            # 进行预测
            predictions = self.current_model.predict(df)
            
            # 准备结果
            if len(predictions) == 1:
                result = {
                    'success': True,
                    'prediction': float(predictions[0]),
                    'model_name': self.current_model_name,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                result = {
                    'success': True,
                    'predictions': [float(p) for p in predictions],
                    'model_name': self.current_model_name,
                    'timestamp': datetime.now().isoformat()
                }
            
            logger.info(f"预测成功，模型: {self.current_model_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"预测失败: {str(e)}")
            return {
                'success': False,
                'message': f'预测失败: {str(e)}'
            }
    
    def batch_predict(self, input_data: Union[List[Dict[str, Any]], pd.DataFrame], 
                      batch_size: int = 100) -> Dict[str, Any]:
        """
        批量预测
        
        Args:
            input_data: 输入数据
            batch_size: 批处理大小
            
        Returns:
            包含预测结果的字典
        """
        try:
            if self.current_model is None:
                return {
                    'success': False,
                    'message': '没有设置当前模型'
                }
            
            # 转换输入数据为DataFrame
            if isinstance(input_data, list):
                df = pd.DataFrame(input_data)
            elif isinstance(input_data, pd.DataFrame):
                df = input_data.copy()
            else:
                return {
                    'success': False,
                    'message': '不支持的输入数据类型'
                }
            
            # 分批处理
            predictions = []
            total_samples = len(df)
            
            for i in range(0, total_samples, batch_size):
                batch_df = df.iloc[i:i+batch_size]
                batch_predictions = self.current_model.predict(batch_df)
                predictions.extend(batch_predictions)
            
            result = {
                'success': True,
                'predictions': [float(p) for p in predictions],
                'model_name': self.current_model_name,
                'total_samples': total_samples,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"批量预测成功，样本数: {total_samples}，模型: {self.current_model_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"批量预测失败: {str(e)}")
            return {
                'success': False,
                'message': f'批量预测失败: {str(e)}'
            }
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        return list(self.loaded_models.keys())
    
    def get_current_model(self) -> str:
        """获取当前模型名称"""
        return self.current_model_name
    
    def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取模型信息
        
        Args:
            model_name: 模型名称，如果为None则获取当前模型信息
            
        Returns:
            包含模型信息的字典
        """
        if model_name is None:
            model_name = self.current_model_name
        
        if model_name not in self.loaded_models:
            return {
                'success': False,
                'message': f'模型 {model_name} 不存在'
            }
        
        model = self.loaded_models[model_name]
        model_info = {
            'model_name': model_name,
            'model_type': type(model).__name__,
            'is_current': model_name == self.current_model_name
        }
        
        # 添加模型特有属性
        if hasattr(model, 'n_features_in_'):
            model_info['n_features'] = model.n_features_in_
        
        if hasattr(model, 'feature_names_in_'):
            model_info['feature_names'] = list(model.feature_names_in_)
        
        # 添加元数据
        if model_name in self.model_metadata:
            model_info['metadata'] = self.model_metadata[model_name]
        
        return {
            'success': True,
            'model_info': model_info
        }
    
    def export_predictions(self, input_data: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame], 
                          output_path: str, format: str = 'csv') -> Dict[str, Any]:
        """
        导出预测结果到文件
        
        Args:
            input_data: 输入数据
            output_path: 输出文件路径
            format: 输出格式 ('csv', 'excel', 'json')
            
        Returns:
            包含导出结果的字典
        """
        try:
            # 进行预测
            result = self.predict(input_data)
            
            if not result['success']:
                return result
            
            # 转换输入数据为DataFrame
            if isinstance(input_data, dict):
                df = pd.DataFrame([input_data])
            elif isinstance(input_data, list):
                df = pd.DataFrame(input_data)
            elif isinstance(input_data, pd.DataFrame):
                df = input_data.copy()
            else:
                return {
                    'success': False,
                    'message': '不支持的输入数据类型'
                }
            
            # 添加预测结果
            if 'prediction' in result:
                df['prediction'] = result['prediction']
            else:
                df['prediction'] = result['predictions']
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 导出文件
            if format.lower() == 'csv':
                df.to_csv(output_path, index=False)
            elif format.lower() == 'excel':
                df.to_excel(output_path, index=False)
            elif format.lower() == 'json':
                df.to_json(output_path, orient='records', indent=2)
            else:
                return {
                    'success': False,
                    'message': f'不支持的输出格式: {format}'
                }
            
            logger.info(f"预测结果导出成功: {output_path}")
            
            return {
                'success': True,
                'message': f'预测结果导出成功: {output_path}',
                'output_path': output_path,
                'format': format,
                'samples_count': len(df)
            }
            
        except Exception as e:
            logger.error(f"导出预测结果失败: {str(e)}")
            return {
                'success': False,
                'message': f'导出预测结果失败: {str(e)}'
            }