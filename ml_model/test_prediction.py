#!/usr/bin/env python3
"""
测试预测功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.predictor import Predictor
import json

def test_prediction():
    """测试预测功能"""
    # 创建预测器
    predictor = Predictor()
    
    # 检查可用模型
    available_models = predictor.get_available_models()
    print(f"可用模型: {available_models}")
    
    if not available_models:
        print("没有可用的模型")
        return
    
    # 加载第一个可用模型
    model_name = available_models[0]
    print(f"加载模型: {model_name}")
    
    load_result = predictor.set_current_model(model_name)
    print(f"加载结果: {load_result}")
    
    if not load_result['success']:
        print(f"模型加载失败: {load_result['message']}")
        return
    
    # 获取模型信息
    model_info = predictor.get_model_info()
    print(f"模型信息: {json.dumps(model_info, indent=2)}")
    
    # 测试预测
    test_data = {
        "area": 150,
        "rooms": 3,
        "age": 10,
        "price": 500  # 包含目标变量，应该被过滤掉
    }
    
    print(f"测试数据: {test_data}")
    result = predictor.predict(test_data)
    print(f"预测结果: {result}")

if __name__ == "__main__":
    test_prediction()