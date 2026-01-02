#!/usr/bin/env python3

import requests
import json
import pandas as pd
import numpy as np
from io import StringIO

BASE_URL = "http://localhost:8000"

def test_prediction_workflow():
    print("开始测试预测功能修复...")
    
    print("\n1. 创建测试数据...")
    np.random.seed(42)
    data_size = 100
    feature1 = np.random.normal(0, 1, data_size)
    feature2 = np.random.normal(0, 1, data_size)
    feature3 = np.random.normal(0, 1, data_size)
    target = 2 * feature1 + 3 * feature2 + np.random.normal(0, 0.5, data_size)
    
    df = pd.DataFrame({
        'feature1': feature1,
        'feature2': feature2,
        'feature3': feature3,
        'target': target
    })
    
    csv_data = df.to_csv(index=False)
    
    print("\n2. 上传数据...")
    files = {'file': ('test_data.csv', csv_data, 'text/csv')}
    response = requests.post(f"{BASE_URL}/data/upload", files=files)
    result = response.json()
    
    if not result.get('success'):
        print(f"上传数据失败: {result.get('message')}")
        return False
    
    print("数据上传成功")
    
    print("\n3. 处理数据...")
    process_data = {
        "handle_missing": "drop",
        "target_column": "target"
    }
    response = requests.post(f"{BASE_URL}/data/process", json=process_data)
    result = response.json()
    
    if not result.get('success'):
        print(f"数据处理失败: {result.get('message')}")
        return False
    
    print("数据处理成功")
    
    print("\n4. 训练模型...")
    train_data = {
        "model_type": "linear_regression",
        "target_column": "target",
        "test_size": 0.2,
        "tune_hyperparameters": False,
        "return_model": True
    }
    response = requests.post(f"{BASE_URL}/model/train", json=train_data)
    result = response.json()
    
    if not result.get('success'):
        print(f"模型训练失败: {result.get('message')}")
        return False
    
    model_name = result.get('model_name')
    model_data = result.get('model_data')
    model_info_data = result.get('model_info_data')
    
    print(f"模型训练成功: {model_name}")
    print(f"模型数据长度: {len(model_data) if model_data else 0}")
    print(f"模型信息数据长度: {len(model_info_data) if model_info_data else 0}")
    
    print("\n5. 测试单个预测...")
    predict_data = {
        "data": {
            "feature1": 1.0,
            "feature2": 2.0,
            "feature3": 0.5
        },
        "model_name": model_name,
        "model_data": model_data,
        "model_info_data": model_info_data
    }
    response = requests.post(f"{BASE_URL}/predict", json=predict_data)
    result = response.json()
    
    if not result.get('success'):
        print(f"单个预测失败: {result.get('message')}")
        return False
    
    prediction = result.get('prediction')
    print(f"单个预测成功: {prediction}")
    
    print("\n6. 测试批量预测...")
    batch_predict_data = {
        "data": [
            {"feature1": 1.0, "feature2": 2.0, "feature3": 0.5},
            {"feature1": -1.0, "feature2": 1.5, "feature3": -0.5},
            {"feature1": 0.5, "feature2": 0.0, "feature3": 1.0}
        ],
        "model_name": model_name,
        "model_data": model_data,
        "model_info_data": model_info_data
    }
    response = requests.post(f"{BASE_URL}/predict/batch", json=batch_predict_data)
    result = response.json()
    
    if not result.get('success'):
        print(f"批量预测失败: {result.get('message')}")
        return False
    
    predictions = result.get('predictions')
    print(f"批量预测成功: {predictions}")
    
    print("\n7. 测试导出预测结果...")
    export_data = {
        "data": [
            {"feature1": 1.0, "feature2": 2.0, "feature3": 0.5},
            {"feature1": -1.0, "feature2": 1.5, "feature3": -0.5},
            {"feature1": 0.5, "feature2": 0.0, "feature3": 1.0}
        ],
        "format": "csv",
        "model_name": model_name,
        "model_data": model_data,
        "model_info_data": model_info_data
    }
    response = requests.post(f"{BASE_URL}/predict/export", json=export_data)
    
    if response.status_code != 200:
        print(f"导出预测结果失败: {response.text}")
        return False
    
    print("导出预测结果成功")
    
    print("\n8. 测试不使用模型信息数据的预测...")
    predict_data_no_info = {
        "data": {
            "feature1": 1.0,
            "feature2": 2.0,
            "feature3": 0.5
        },
        "model_name": model_name,
        "model_data": model_data
    }
    response = requests.post(f"{BASE_URL}/predict", json=predict_data_no_info)
    result = response.json()
    
    if not result.get('success'):
        print(f"不使用模型信息数据的预测失败（预期）: {result.get('message')}")
    else:
        print(f"不使用模型信息数据的预测成功（意外）: {result.get('prediction')}")
    
    print("\n测试完成！")
    return True

if __name__ == "__main__":
    try:
        success = test_prediction_workflow()
        if success:
            print("\n✅ 所有测试通过！预测功能修复成功。")
        else:
            print("\n❌ 测试失败，需要进一步检查。")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()