#!/usr/bin/env python3

import requests
import json
import os

def test_api_endpoints():
    base_url = "http://localhost:8000"
    
    data_file = "/Users/krust/Code/DataAnalysisFinalProject/housing_data_clean.csv"
    
    print("测试 API 端点...")
    
    try:
        print("1. 测试根路径...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ 根路径测试成功")
        else:
            print(f"❌ 根路径测试失败: {response.status_code}")
            return False
        
        print("2. 测试系统状态...")
        response = requests.get(f"{base_url}/system/status")
        if response.status_code == 200:
            print("✅ 系统状态测试成功")
        else:
            print(f"❌ 系统状态测试失败: {response.status_code}")
            return False
        
        print("3. 测试数据上传...")
        with open(data_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/data/upload", files=files)
        
        if response.status_code == 200:
            print("✅ 数据上传测试成功")
            upload_result = response.json()
        else:
            print(f"❌ 数据上传测试失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
        
        print("4. 测试获取数据信息...")
        response = requests.get(f"{base_url}/data/info")
        if response.status_code == 200:
            print("✅ 获取数据信息测试成功")
            data_info = response.json()
        else:
            print(f"❌ 获取数据信息测试失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
        
        print("5. 测试数据预览...")
        response = requests.get(f"{base_url}/data/preview")
        if response.status_code == 200:
            print("✅ 数据预览测试成功")
            preview = response.json()
        else:
            print(f"❌ 数据预览测试失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
        
        print("6. 测试数据处理...")
        response = requests.post(
            f"{base_url}/data/process",
            json={"handle_missing": "drop", "target_column": "price"}
        )
        if response.status_code == 200:
            print("✅ 数据处理测试成功")
            process_result = response.json()
        else:
            print(f"❌ 数据处理测试失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
        
        print("7. 测试模型训练...")
        response = requests.post(
            f"{base_url}/model/train",
            json={
                "model_type": "linear_regression",
                "target_column": "price",
                "test_size": 0.2,
                "tune_hyperparameters": False
            }
        )
        if response.status_code == 200:
            print("✅ 模型训练测试成功")
            train_result = response.json()
        else:
            print(f"❌ 模型训练测试失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
        
        print("8. 测试获取可用模型...")
        response = requests.get(f"{base_url}/model/available")
        if response.status_code == 200:
            print("✅ 获取可用模型测试成功")
            models = response.json()
        else:
            print(f"❌ 获取可用模型测试失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
        
        print("9. 测试预测...")
        response = requests.post(
            f"{base_url}/predict",
            json={
                "data": {"area": 120.0, "rooms": 3, "age": 10.0},
                "model_name": None
            }
        )
        if response.status_code == 200:
            print("✅ 预测测试成功")
            prediction = response.json()
        else:
            print(f"❌ 预测测试失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
        
        print("\n🎉 所有 API 端点测试通过！numpy 和 pandas 数据类型序列化问题已修复。")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 API 服务器。请确保服务器正在运行在 http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试 API 端点...")
    test_api_endpoints()