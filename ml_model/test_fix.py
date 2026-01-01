#!/usr/bin/env python3
"""
测试 numpy 和 pandas 数据类型序列化修复
"""

import numpy as np
import pandas as pd
import json
from utils.helpers import serialize_numpy_pandas

def test_data_processor():
    """测试数据处理器"""
    print("测试数据处理器...")
    
    from data.data_processor import DataProcessor
    
    # 使用实际的数据文件
    data_path = '/Users/krust/Code/DataAnalysisFinalProject/housing_data_clean.csv'
    
    # 测试数据处理器
    processor = DataProcessor()
    result = processor.load_csv(data_path)
    
    if result['success']:
        print("数据加载成功，开始测试序列化...")
        
        # 测试获取数据信息
        data_info = processor.get_data_info()
        
        # 检查数据类型
        print("检查数据类型...")
        for key, value in data_info.items():
            print(f"  {key}: {type(value)}")
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {type(sub_value)}")
        
        try:
            # 尝试 JSON 序列化
            json_str = json.dumps(data_info)
            print("✅ 数据处理器测试成功！数据信息可以正确序列化。")
            return True
        except Exception as e:
            print(f"❌ 数据处理器测试失败: {str(e)}")
            
            # 尝试找出问题所在
            print("尝试逐个序列化字段...")
            for key, value in data_info.items():
                try:
                    json.dumps({key: value})
                    print(f"  {key}: OK")
                except Exception as e:
                    print(f"  {key}: ERROR - {str(e)}")
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            try:
                                json.dumps({sub_key: sub_value})
                                print(f"    {sub_key}: OK")
                            except Exception as e:
                                print(f"    {sub_key}: ERROR - {str(e)}")
            
            return False
    else:
        print(f"❌ 数据加载失败: {result['message']}")
        return False

if __name__ == "__main__":
    print("开始测试 numpy 和 pandas 数据类型序列化修复...")
    
    # 运行测试
    result = test_data_processor()
    
    # 总结
    print("\n测试总结:")
    if result:
        print("🎉 测试通过！numpy 和 pandas 数据类型序列化问题已修复。")
    else:
        print("⚠️ 测试失败，需要进一步检查。")