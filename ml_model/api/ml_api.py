"""
机器学习API接口模块
提供RESTful API供后端调用
"""

import os
import json
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import logging

# 导入自定义模块
from data.data_processor import DataProcessor
from models.model_trainer import ModelTrainer
from models.predictor import Predictor
from utils.helpers import serialize_numpy_pandas

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="机器学习数据分析与统计系统",
    description="基于机器学习的数据分析与统计系统API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
data_processor = DataProcessor()
model_trainer = ModelTrainer()
predictor = Predictor()

# 系统状态
system_status = {
    "data_uploaded": False,
    "model_trained": False,
    "current_step": "数据上传",
    "current_model": "线性回归模型（默认）",
    "available_models": model_trainer.get_available_models()
}

# 临时文件存储
temp_dir = tempfile.mkdtemp()
current_data_file = None

# Pydantic模型
class PredictionRequest(BaseModel):
    """预测请求模型"""
    data: Dict[str, Any]
    model_name: Optional[str] = None

class ModelTrainRequest(BaseModel):
    """模型训练请求模型"""
    model_type: str = "linear_regression"
    target_column: Optional[str] = None
    test_size: float = 0.2
    tune_hyperparameters: bool = False

class DataProcessRequest(BaseModel):
    """数据处理请求模型"""
    handle_missing: str = "drop"
    target_column: Optional[str] = None

# API路由
@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "机器学习数据分析与统计系统API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/system/status")
async def get_system_status():
    """获取系统状态"""
    return {
        "success": True,
        "status": system_status
    }

@app.post("/data/upload")
async def upload_data(file: UploadFile = File(...)):
    """上传CSV数据文件"""
    global current_data_file
    
    try:
        # 检查文件类型
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="只支持CSV文件")
        
        # 保存上传的文件
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        current_data_file = file_path
        
        # 加载数据
        result = data_processor.load_csv(file_path)
        
        if result['success']:
            # 更新系统状态
            system_status["data_uploaded"] = True
            system_status["current_step"] = "模型训练"
            
            # 序列化结果
            return serialize_numpy_pandas(result)
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传数据失败: {str(e)}")

@app.get("/data/info")
async def get_data_info():
    """获取数据信息"""
    try:
        data_info = data_processor.get_data_info()
        
        if not data_info['file_name']:
            raise HTTPException(status_code=400, detail="没有上传的数据")
        
        return {
            "success": True,
            "data_info": serialize_numpy_pandas(data_info)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取数据信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取数据信息失败: {str(e)}")

@app.get("/data/preview")
async def get_data_preview(rows: int = 20):
    """获取数据预览"""
    try:
        preview = data_processor.get_data_preview(rows)
        
        if not preview:
            raise HTTPException(status_code=400, detail="没有上传的数据")
        
        return {
            "success": True,
            "preview": serialize_numpy_pandas(preview)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取数据预览失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取数据预览失败: {str(e)}")

@app.post("/data/process")
async def process_data(request: DataProcessRequest):
    """处理数据"""
    try:
        if not system_status["data_uploaded"]:
            raise HTTPException(status_code=400, detail="没有上传的数据")
        
        # 预处理数据
        X, y = data_processor.preprocess_data(
            handle_missing=request.handle_missing,
            target_column=request.target_column
        )
        
        return {
            "success": True,
            "message": "数据处理成功",
            "feature_count": len(X.columns),
            "sample_count": len(X),
            "target_column": data_processor.get_data_info()['target_column']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"数据处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"数据处理失败: {str(e)}")

@app.post("/model/train")
async def train_model(request: ModelTrainRequest, background_tasks: BackgroundTasks):
    """训练模型"""
    try:
        if not system_status["data_uploaded"]:
            raise HTTPException(status_code=400, detail="没有上传的数据")
        
        # 检查模型类型是否有效
        if request.model_type not in model_trainer.get_available_models():
            raise HTTPException(status_code=400, detail=f"不支持的模型类型: {request.model_type}")
        
        # 确保模型保存目录存在
        try:
            os.makedirs(model_trainer.model_dir, exist_ok=True)
            logger.info(f"模型保存目录已确认存在: {model_trainer.model_dir}")
        except Exception as e:
            logger.error(f"创建模型保存目录失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"创建模型保存目录失败: {str(e)}")
        
        # 预处理数据
        X, y = data_processor.preprocess_data(
            handle_missing='drop',
            target_column=request.target_column
        )
        
        # 训练模型
        result = model_trainer.train_model(
            X=X,
            y=y,
            model_type=request.model_type,
            test_size=request.test_size,
            tune_hyperparameters=request.tune_hyperparameters
        )
        
        if result['success']:
            # 更新系统状态
            system_status["model_trained"] = True
            system_status["current_step"] = "预测"
            system_status["current_model"] = request.model_type
            
            # 加载模型到预测器
            model_name = result['model_name']
            predictor.load_model(result['model_path'])
            predictor.set_current_model(model_name)
            
            # 序列化结果
            return serialize_numpy_pandas(result)
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"模型训练失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"模型训练失败: {str(e)}")

@app.get("/model/available")
async def get_available_models():
    """获取可用的模型类型"""
    return {
        "success": True,
        "models": model_trainer.get_available_models()
    }

@app.get("/model/trained")
async def get_trained_models():
    """获取已训练的模型"""
    return {
        "success": True,
        "models": model_trainer.get_trained_models()
    }

@app.get("/model/metrics/{model_name}")
async def get_model_metrics(model_name: str):
    """获取模型评估指标"""
    try:
        result = model_trainer.get_model_metrics(model_name)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['message'])
        
        # 序列化结果
        return serialize_numpy_pandas(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模型指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模型指标失败: {str(e)}")

@app.post("/model/compare")
async def compare_models(test_size: float = 0.2):
    """比较所有模型的性能"""
    try:
        if not system_status["data_uploaded"]:
            raise HTTPException(status_code=400, detail="没有上传的数据")
        
        # 预处理数据
        X, y = data_processor.preprocess_data(handle_missing='drop')
        
        # 比较模型
        result = model_trainer.compare_models(X, y, test_size)
        
        if result['success']:
            # 序列化结果
            return serialize_numpy_pandas(result)
        else:
            raise HTTPException(status_code=400, detail="模型比较失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"模型比较失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"模型比较失败: {str(e)}")

@app.post("/predict")
async def predict(request: PredictionRequest):
    """使用模型进行预测"""
    try:
        if not system_status["model_trained"]:
            raise HTTPException(status_code=400, detail="没有训练的模型")
        
        # 如果指定了模型名称，设置当前模型
        if request.model_name and request.model_name in predictor.get_available_models():
            predictor.set_current_model(request.model_name)
        
        # 进行预测
        result = predictor.predict(request.data)
        
        if result['success']:
            # 序列化结果
            return serialize_numpy_pandas(result)
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"预测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")

@app.post("/predict/batch")
async def batch_predict(data: List[Dict[str, Any]], model_name: Optional[str] = None):
    """批量预测"""
    try:
        if not system_status["model_trained"]:
            raise HTTPException(status_code=400, detail="没有训练的模型")
        
        # 如果指定了模型名称，设置当前模型
        if model_name and model_name in predictor.get_available_models():
            predictor.set_current_model(model_name)
        
        # 进行批量预测
        result = predictor.batch_predict(data)
        
        if result['success']:
            # 序列化结果
            return serialize_numpy_pandas(result)
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量预测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量预测失败: {str(e)}")

@app.post("/predict/export")
async def export_predictions(
    data: List[Dict[str, Any]], 
    format: str = "csv",
    model_name: Optional[str] = None
):
    """导出预测结果"""
    try:
        if not system_status["model_trained"]:
            raise HTTPException(status_code=400, detail="没有训练的模型")
        
        # 如果指定了模型名称，设置当前模型
        if model_name and model_name in predictor.get_available_models():
            predictor.set_current_model(model_name)
        
        # 生成输出文件路径
        output_filename = f"predictions.{format}"
        output_path = os.path.join(temp_dir, output_filename)
        
        # 导出预测结果
        result = predictor.export_predictions(data, output_path, format)
        
        if result['success']:
            return FileResponse(
                path=output_path,
                filename=output_filename,
                media_type='application/octet-stream'
            )
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出预测结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导出预测结果失败: {str(e)}")

@app.get("/model/info")
async def get_model_info(model_name: Optional[str] = None):
    """获取模型信息"""
    try:
        result = predictor.get_model_info(model_name)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['message'])
        
        # 序列化结果
        return serialize_numpy_pandas(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模型信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模型信息失败: {str(e)}")

def run_api(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """运行API服务器"""
    uvicorn.run(
        "api.ml_api:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

if __name__ == "__main__":
    run_api(debug=True)