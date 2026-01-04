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
import redis

from data.data_processor import DataProcessor
from models.model_trainer import ModelTrainer
from models.predictor import Predictor
from utils.helpers import serialize_numpy_pandas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="机器学习数据分析与统计系统",
    description="基于机器学习的数据分析与统计系统API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局DataProcessor实例，每个worker进程一个
data_processor = DataProcessor()
model_trainer = ModelTrainer()
predictor = Predictor()

# 定期清理任务
import asyncio
import threading
import time

def cleanup_idle_data():
    """定期清理长时间未使用的数据"""
    while True:
        try:
            data_processor.check_and_cleanup()
            time.sleep(300)  # 每5分钟检查一次
        except Exception as e:
            logger.error(f"清理任务出错: {str(e)}")
            time.sleep(60)  # 出错时1分钟后重试

# 启动清理线程
cleanup_thread = threading.Thread(target=cleanup_idle_data, daemon=True)
cleanup_thread.start()

# Redis连接
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    redis_available = True
except:
    redis_available = False
    logging.warning("Redis不可用，将使用内存存储状态（多进程环境下可能不一致）")

# 默认系统状态
default_system_status = {
    "data_uploaded": False,
    "model_trained": False,
    "current_step": "数据上传",
    "current_model": "线性回归模型（默认）",
    "available_models": model_trainer.get_available_models()
}

# 使用内存存储，不再创建临时目录
# temp_dir = tempfile.mkdtemp()  # 注释掉，改用Redis存储文件

def get_system_status():
    """获取系统状态"""
    if redis_available:
        try:
            status = redis_client.get("system_status")
            if status:
                return json.loads(status)
        except:
            pass
    return default_system_status.copy()

def set_system_status(status):
    """设置系统状态"""
    if redis_available:
        try:
            redis_client.set("system_status", json.dumps(status))
            return
        except:
            pass
    # 如果Redis不可用，更新默认状态（仅在单进程环境下有效）
    global default_system_status
    default_system_status.update(status)

def get_current_data_file():
    """获取当前数据文件内容"""
    if redis_available:
        try:
            # 获取当前活跃的文件ID
            current_file_id = redis_client.get("current_file_id")
            if current_file_id:
                # 每次访问后更新过期时间，延长活跃数据的生命周期
                content = redis_client.get(f"file_content:{current_file_id}")
                if content:
                    redis_client.expire(f"file_content:{current_file_id}", 1800)  # 重置30分钟过期时间
                    redis_client.expire(f"file_info:{current_file_id}", 1800)
                return content
        except:
            pass
    return None

def set_current_data_file(file_content, filename):
    """设置当前数据文件内容到Redis，并设置30分钟过期时间"""
    if redis_available:
        try:
            import uuid
            # 生成唯一的文件ID
            file_id = str(uuid.uuid4())
            
            # 存储文件内容和信息，设置30分钟(1800秒)过期时间
            redis_client.setex(f"file_content:{file_id}", 1800, file_content)
            redis_client.setex(f"file_info:{file_id}", 1800, json.dumps({"filename": filename}))
            
            # 设置为当前活跃文件
            redis_client.set("current_file_id", file_id)
            
            return file_id
        except:
            pass
    # 如果Redis不可用，无法在多进程环境下共享状态
    return None

def get_current_data_filename():
    """获取当前数据文件名"""
    if redis_available:
        try:
            current_file_id = redis_client.get("current_file_id")
            if current_file_id:
                file_info = redis_client.get(f"file_info:{current_file_id}")
                if file_info:
                    info = json.loads(file_info)
                    return info.get("filename")
        except:
            pass
    return None

def get_all_files():
    """获取所有存储的文件信息"""
    if redis_available:
        try:
            # 获取所有文件信息的键
            keys = redis_client.keys("file_info:*")
            files = []
            for key in keys:
                file_info = redis_client.get(key)
                if file_info:
                    file_id = key.split(":", 1)[1]
                    info = json.loads(file_info)
                    info["file_id"] = file_id
                    files.append(info)
            return files
        except:
            pass
    return []

def switch_to_file(file_id):
    """切换到指定的文件"""
    if redis_available:
        try:
            # 检查文件是否存在
            if redis_client.exists(f"file_content:{file_id}"):
                redis_client.set("current_file_id", file_id)
                return True
        except:
            pass
    return False

def delete_file(file_id):
    """删除指定的文件"""
    if redis_available:
        try:
            redis_client.delete(f"file_content:{file_id}")
            redis_client.delete(f"file_info:{file_id}")
            
            # 如果删除的是当前文件，清除当前文件ID
            current_file_id = redis_client.get("current_file_id")
            if current_file_id == file_id:
                redis_client.delete("current_file_id")
            return True
        except:
            pass
    return False

class PredictionRequest(BaseModel):
    data: Dict[str, Any]
    model_name: Optional[str] = None
    model_data: Optional[str] = None
    model_info_data: Optional[str] = None

class ModelTrainRequest(BaseModel):
    model_type: str = "linear_regression"
    target_column: Optional[str] = None
    test_size: float = 0.2
    tune_hyperparameters: bool = False
    return_model: bool = True

class DataProcessRequest(BaseModel):
    handle_missing: str = "drop"
    target_column: Optional[str] = None

class BatchPredictionRequest(BaseModel):
    data: List[Dict[str, Any]]
    model_name: Optional[str] = None
    model_data: Optional[str] = None
    model_info_data: Optional[str] = None

class ExportPredictionsRequest(BaseModel):
    data: List[Dict[str, Any]]
    format: str = "csv"
    model_name: Optional[str] = None
    model_data: Optional[str] = None
    model_info_data: Optional[str] = None

@app.get("/")
async def root():
    return {
        "message": "机器学习数据分析与统计系统API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/system/status")
async def get_system_status_endpoint():
    return {
        "success": True,
        "status": get_system_status()
    }

@app.post("/data/upload")
async def upload_data(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="只支持CSV文件")
        
        # 读取文件内容到内存
        file_content = await file.read()
        file_text = file_content.decode('utf-8')
        
        # 保存文件内容到Redis，设置30分钟过期
        set_current_data_file(file_text, file.filename)
        
        # 直接从内存加载CSV
        result = data_processor.load_csv_from_content(file_text, file.filename)
        
        if result['success']:
            # 更新系统状态
            status = get_system_status()
            status["data_uploaded"] = True
            status["current_step"] = "模型训练"
            set_system_status(status)
            
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
    try:
        # 检查是否有上传的数据
        current_data = get_current_data_file()
        current_filename = get_current_data_filename()
        if not current_data:
            raise HTTPException(status_code=400, detail="没有上传的数据")
        
        # 如果当前进程没有加载数据，尝试从内存加载
        if not data_processor.data_content or data_processor.data_file != current_filename:
            data_processor.load_csv_from_content(current_data, current_filename)
        
        # 更新访问时间
        data_processor.update_access_time()
        
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
    try:
        # 检查是否有上传的数据
        current_data = get_current_data_file()
        current_filename = get_current_data_filename()
        if not current_data:
            raise HTTPException(status_code=400, detail="没有上传的数据")
        
        # 如果当前进程没有加载数据，尝试从内存加载
        if not data_processor.data_content or data_processor.data_file != current_filename:
            data_processor.load_csv_from_content(current_data, current_filename)
        
        # 更新访问时间
        data_processor.update_access_time()
        
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
    try:
        status = get_system_status()
        if not status["data_uploaded"]:
            raise HTTPException(status_code=400, detail="没有上传的数据")
        
        # 检查是否有上传的数据
        current_data = get_current_data_file()
        current_filename = get_current_data_filename()
        if not current_data:
            raise HTTPException(status_code=400, detail="没有上传的数据")
        
        # 如果当前进程没有加载数据，尝试从内存加载
        if not data_processor.data_content or data_processor.data_file != current_filename:
            data_processor.load_csv_from_content(current_data, current_filename)
        
        # 更新访问时间
        data_processor.update_access_time()
        
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
    import tempfile
    import os
    import pickle
    import base64
    
    try:
        status = get_system_status()
        if not status["data_uploaded"]:
            raise HTTPException(status_code=400, detail="没有上传的数据")
        
        if request.model_type not in model_trainer.get_available_models():
            raise HTTPException(status_code=400, detail=f"不支持的模型类型: {request.model_type}")
        
        try:
            os.makedirs(model_trainer.model_dir, exist_ok=True)
            logger.info(f"模型保存目录已确认存在: {model_trainer.model_dir}")
        except Exception as e:
            logger.error(f"创建模型保存目录失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"创建模型保存目录失败: {str(e)}")
        
        # 检查是否有上传的数据
        current_data = get_current_data_file()
        current_filename = get_current_data_filename()
        if not current_data:
            raise HTTPException(status_code=400, detail="没有上传的数据")
        
        # 如果当前进程没有加载数据，尝试从内存加载
        if not data_processor.data_content or data_processor.data_file != current_filename:
            data_processor.load_csv_from_content(current_data, current_filename)
        
        X, y = data_processor.preprocess_data(
            handle_missing='drop',
            target_column=request.target_column
        )
        
        result = model_trainer.train_model(
            X=X,
            y=y,
            model_type=request.model_type,
            test_size=request.test_size,
            tune_hyperparameters=request.tune_hyperparameters,
            return_model=True
        )
        
        if result['success']:
            # 更新系统状态
            status["model_trained"] = True
            status["current_step"] = "预测"
            status["current_model"] = request.model_type
            set_system_status(status)
            
            model_name = result['model_name']
            
            if 'model_data' in result:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as temp_file:
                    model_bytes = base64.b64decode(result['model_data'])
                    temp_file.write(model_bytes)
                    temp_file_path = temp_file.name
                
                try:
                    predictor.load_model(temp_file_path)
                    predictor.set_current_model(model_name)
                finally:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
            else:
                predictor.load_model(result['model_path'])
                predictor.set_current_model(model_name)
            
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
    return {
        "success": True,
        "models": model_trainer.get_available_models()
    }

@app.get("/model/trained")
async def get_trained_models():
    return {
        "success": True,
        "models": model_trainer.get_trained_models()
    }

@app.get("/model/metrics/{model_name}")
async def get_model_metrics(model_name: str):
    try:
        result = model_trainer.get_model_metrics(model_name)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['message'])
        
        return serialize_numpy_pandas(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模型指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模型指标失败: {str(e)}")

@app.post("/model/compare")
async def compare_models(test_size: float = 0.2):
    try:
        status = get_system_status()
        if not status["data_uploaded"]:
            raise HTTPException(status_code=400, detail="没有上传的数据")
        
        # 检查是否有上传的数据
        current_data = get_current_data_file()
        current_filename = get_current_data_filename()
        if not current_data:
            raise HTTPException(status_code=400, detail="没有上传的数据")
        
        # 如果当前进程没有加载数据，尝试从内存加载
        if not data_processor.data_content or data_processor.data_file != current_filename:
            data_processor.load_csv_from_content(current_data, current_filename)
        
        X, y = data_processor.preprocess_data(handle_missing='drop')
        
        result = model_trainer.compare_models(X, y, test_size)
        
        if result['success']:
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
    try:
        if request.model_data:
            import tempfile
            import os
            import pickle
            import base64
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as temp_file:
                model_bytes = base64.b64decode(request.model_data)
                temp_file.write(model_bytes)
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    model = pickle.load(f)
                
                temp_predictor = Predictor()
                temp_predictor.current_model = model
                temp_predictor.current_model_name = request.model_name or "temp_model"
                
                if request.model_info_data:
                    try:
                        model_info_bytes = base64.b64decode(request.model_info_data)
                        model_info = pickle.loads(model_info_bytes)
                        temp_predictor.model_info = model_info
                    except Exception as e:
                        logger.error(f"加载模型信息失败: {str(e)}")
                        if request.model_name:
                            for model_name, model_info in model_trainer.model_metrics.items():
                                if request.model_name in model_name or model_name in request.model_name:
                                    temp_predictor.model_info = model_info
                                    break
                else:
                    if request.model_name:
                        for model_name, model_info in model_trainer.model_metrics.items():
                            if request.model_name in model_name or model_name in request.model_name:
                                temp_predictor.model_info = model_info
                                break
                
                result = temp_predictor.predict(request.data)
                
                if result['success']:
                    return serialize_numpy_pandas(result)
                else:
                    raise HTTPException(status_code=400, detail=result['message'])
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        else:
            status = get_system_status()
            if not status["model_trained"]:
                raise HTTPException(status_code=400, detail="没有训练的模型")
            
            if request.model_name and request.model_name in predictor.get_available_models():
                predictor.set_current_model(request.model_name)
            
            result = predictor.predict(request.data)
            
            if result['success']:
                return serialize_numpy_pandas(result)
            else:
                raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"预测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")

@app.post("/predict/batch")
async def batch_predict(request: BatchPredictionRequest):
    try:
        if request.model_data:
            import tempfile
            import os
            import pickle
            import base64
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as temp_file:
                model_bytes = base64.b64decode(request.model_data)
                temp_file.write(model_bytes)
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    model = pickle.load(f)
                
                temp_predictor = Predictor()
                temp_predictor.current_model = model
                temp_predictor.current_model_name = request.model_name or "temp_model"
                
                if request.model_info_data:
                    try:
                        model_info_bytes = base64.b64decode(request.model_info_data)
                        model_info = pickle.loads(model_info_bytes)
                        temp_predictor.model_info = model_info
                    except Exception as e:
                        logger.error(f"加载模型信息失败: {str(e)}")
                        if request.model_name:
                            for model_name, model_info in model_trainer.model_metrics.items():
                                if request.model_name in model_name or model_name in request.model_name:
                                    temp_predictor.model_info = model_info
                                    break
                else:
                    if request.model_name:
                        for model_name, model_info in model_trainer.model_metrics.items():
                            if request.model_name in model_name or model_name in request.model_name:
                                temp_predictor.model_info = model_info
                                break
                
                result = temp_predictor.batch_predict(request.data)
                
                if result['success']:
                    return serialize_numpy_pandas(result)
                else:
                    raise HTTPException(status_code=400, detail=result['message'])
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        else:
            status = get_system_status()
            if not status["model_trained"]:
                raise HTTPException(status_code=400, detail="没有训练的模型")
            
            if request.model_name and request.model_name in predictor.get_available_models():
                predictor.set_current_model(request.model_name)
            
            result = predictor.batch_predict(request.data)
            
            if result['success']:
                return serialize_numpy_pandas(result)
            else:
                raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量预测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量预测失败: {str(e)}")

@app.post("/predict/export")
async def export_predictions(request: ExportPredictionsRequest):
    try:
        if request.model_data:
            import tempfile
            import os
            import pickle
            import base64
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as temp_file:
                model_bytes = base64.b64decode(request.model_data)
                temp_file.write(model_bytes)
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    model = pickle.load(f)
                
                temp_predictor = Predictor()
                temp_predictor.current_model = model
                temp_predictor.current_model_name = request.model_name or "temp_model"
                
                if request.model_info_data:
                    try:
                        model_info_bytes = base64.b64decode(request.model_info_data)
                        model_info = pickle.loads(model_info_bytes)
                        temp_predictor.model_info = model_info
                    except Exception as e:
                        logger.error(f"加载模型信息失败: {str(e)}")
                        if request.model_name:
                            for model_name, model_info in model_trainer.model_metrics.items():
                                if request.model_name in model_name or model_name in request.model_name:
                                    temp_predictor.model_info = model_info
                                    break
                else:
                    if request.model_name:
                        for model_name, model_info in model_trainer.model_metrics.items():
                            if request.model_name in model_name or model_name in request.model_name:
                                temp_predictor.model_info = model_info
                                break
                
                output_filename = f"predictions.{request.format}"
                output_path = os.path.join(tempfile.gettempdir(), output_filename)
                
                result = temp_predictor.export_predictions(request.data, output_path, request.format)
                
                if result['success']:
                    return FileResponse(
                        path=output_path,
                        filename=output_filename,
                        media_type='application/octet-stream'
                    )
                else:
                    raise HTTPException(status_code=400, detail=result['message'])
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        else:
            status = get_system_status()
            if not status["model_trained"]:
                raise HTTPException(status_code=400, detail="没有训练的模型")
            
            if request.model_name and request.model_name in predictor.get_available_models():
                predictor.set_current_model(request.model_name)
            
            output_filename = f"predictions.{request.format}"
            output_path = os.path.join(tempfile.gettempdir(), output_filename)
            
            result = predictor.export_predictions(request.data, output_path, request.format)
            
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
    try:
        result = predictor.get_model_info(model_name)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['message'])
        
        return serialize_numpy_pandas(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模型信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模型信息失败: {str(e)}")

def run_api(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    uvicorn.run(
        "api.ml_api:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

if __name__ == "__main__":
    run_api(debug=True)