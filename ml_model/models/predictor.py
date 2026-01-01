"""
预测器模块
负责使用训练好的模型进行预测
"""

import os
import pickle
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from utils.helpers import serialize_numpy_pandas

class Predictor:
    """预测器类"""
    
    def __init__(self, models_dir: str = "saved_models"):
        """
        初始化预测器
        
        Args:
            models_dir: 模型目录
        """
        self.models_dir = models_dir
        self.current_model = None
        self.current_model_name = None
        self.model_info = {}
        self.available_models = {}
        
        # 加载可用的模型
        self._load_available_models()
        
    def _load_available_models(self):
        """加载可用的模型"""
        if not os.path.exists(self.models_dir):
            return
        
        # 遍历模型目录，加载模型信息
        for file in os.listdir(self.models_dir):
            if file.endswith('_info.json'):
                model_name = file.replace('_info.json', '')
                info_path = os.path.join(self.models_dir, file)
                
                try:
                    with open(info_path, 'r') as f:
                        model_info = json.load(f)
                    
                    self.available_models[model_name] = model_info
                except Exception as e:
                    print(f"加载模型信息失败 {model_name}: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """
        获取可用模型列表
        
        Returns:
            可用模型名称列表
        """
        return list(self.available_models.keys())
    
    def load_model(self, model_path: str) -> Dict[str, Any]:
        """
        加载模型
        
        Args:
            model_path: 模型文件路径
            
        Returns:
            加载结果字典
        """
        try:
            # 加载模型
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            # 获取模型名称
            model_name = os.path.basename(model_path).replace('.pkl', '')
            
            # 加载模型信息
            info_path = model_path.replace('.pkl', '_info.json')
            if os.path.exists(info_path):
                with open(info_path, 'r') as f:
                    model_info = json.load(f)
            else:
                model_info = {}
            
            # 设置当前模型
            self.current_model = model
            self.current_model_name = model_name
            self.model_info = model_info
            
            return {
                'success': True,
                'message': f'模型加载成功: {model_name}',
                'model_name': model_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'模型加载失败: {str(e)}'
            }
    
    def set_current_model(self, model_name: str) -> Dict[str, Any]:
        """
        设置当前模型
        
        Args:
            model_name: 模型名称
            
        Returns:
            设置结果字典
        """
        if model_name not in self.available_models:
            return {
                'success': False,
                'message': f'模型不存在: {model_name}'
            }
        
        model_info = self.available_models[model_name]
        model_path = os.path.join(self.models_dir, f"{model_name}.pkl")
        
        return self.load_model(model_path)
    
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        单个预测
        
        Args:
            data: 输入数据字典
            
        Returns:
            预测结果字典
        """
        if self.current_model is None:
            return {
                'success': False,
                'message': '没有加载的模型'
            }
        
        try:
            # 转换为DataFrame
            df = pd.DataFrame([data])
            
            # 确保特征顺序与训练时一致
            if 'feature_columns' in self.model_info:
                feature_columns = self.model_info['feature_columns']
                
                # 检查是否所有特征都存在
                missing_features = set(feature_columns) - set(df.columns)
                if missing_features:
                    return {
                        'success': False,
                        'message': f'缺少特征: {list(missing_features)}'
                    }
                
                # 重新排序列
                df = df[feature_columns]
            
            # 预测
            prediction = self.current_model.predict(df)[0]
            
            # 处理预测结果
            prediction = serialize_numpy_pandas(prediction)
            
            # 获取预测概率（如果是分类模型）
            prediction_proba = None
            if hasattr(self.current_model, 'predict_proba') and self.model_info.get('problem_type') == 'classification':
                prediction_proba = serialize_numpy_pandas(self.current_model.predict_proba(df)[0])
            
            return {
                'success': True,
                'prediction': prediction,
                'prediction_proba': prediction_proba,
                'model_name': self.current_model_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'预测失败: {str(e)}'
            }
    
    def batch_predict(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量预测
        
        Args:
            data: 输入数据列表
            
        Returns:
            预测结果字典
        """
        if self.current_model is None:
            return {
                'success': False,
                'message': '没有加载的模型'
            }
        
        try:
            # 转换为DataFrame
            df = pd.DataFrame(data)
            
            # 确保特征顺序与训练时一致
            if 'feature_columns' in self.model_info:
                feature_columns = self.model_info['feature_columns']
                
                # 检查是否所有特征都存在
                missing_features = set(feature_columns) - set(df.columns)
                if missing_features:
                    return {
                        'success': False,
                        'message': f'缺少特征: {list(missing_features)}'
                    }
                
                # 重新排序列
                df = df[feature_columns]
            
            # 预测
            predictions = self.current_model.predict(df)
            
            # 处理预测结果
            predictions = serialize_numpy_pandas(predictions)
            
            # 获取预测概率（如果是分类模型）
            predictions_proba = None
            if hasattr(self.current_model, 'predict_proba') and self.model_info.get('problem_type') == 'classification':
                predictions_proba = serialize_numpy_pandas(self.current_model.predict_proba(df))
            
            return {
                'success': True,
                'predictions': predictions,
                'predictions_proba': predictions_proba,
                'model_name': self.current_model_name,
                'count': len(predictions)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'批量预测失败: {str(e)}'
            }
    
    def export_predictions(self, data: List[Dict[str, Any]], output_path: str, format: str = "csv") -> Dict[str, Any]:
        """
        导出预测结果
        
        Args:
            data: 输入数据列表
            output_path: 输出文件路径
            format: 输出格式 ("csv", "json", "excel")
            
        Returns:
            导出结果字典
        """
        if self.current_model is None:
            return {
                'success': False,
                'message': '没有加载的模型'
            }
        
        try:
            # 进行预测
            result = self.batch_predict(data)
            
            if not result['success']:
                return result
            
            # 准备导出数据
            export_data = []
            
            for i, (input_data, prediction) in enumerate(zip(data, result['predictions'])):
                row = input_data.copy()
                row['prediction'] = prediction
                
                # 添加预测概率（如果有）
                if result['predictions_proba']:
                    for j, prob in enumerate(result['predictions_proba'][i]):
                        row[f'probability_class_{j}'] = serialize_numpy_pandas(prob)
                
                export_data.append(row)
            
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 导出文件
            if format == "csv":
                df.to_csv(output_path, index=False)
            elif format == "json":
                df.to_json(output_path, orient='records', indent=2)
            elif format == "excel":
                df.to_excel(output_path, index=False)
            else:
                return {
                    'success': False,
                    'message': f'不支持的导出格式: {format}'
                }
            
            return {
                'success': True,
                'message': f'预测结果已导出到: {output_path}',
                'output_path': output_path,
                'count': len(export_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'导出预测结果失败: {str(e)}'
            }
    
    def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取模型信息
        
        Args:
            model_name: 模型名称，如果为None则返回当前模型信息
            
        Returns:
            模型信息字典
        """
        if model_name is None:
            model_name = self.current_model_name
        
        if model_name is None:
            return {
                'success': False,
                'message': '没有指定的模型'
            }
        
        if model_name not in self.available_models:
            return {
                'success': False,
                'message': f'模型不存在: {model_name}'
            }
        
        return {
            'success': True,
            'model_info': serialize_numpy_pandas(self.available_models[model_name])
        }