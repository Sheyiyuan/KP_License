import asyncio
from fastapi import FastAPI,Response,Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import sys
import threading
import time
import os
import json
from datetime import datetime
from pathlib import Path

from fastapi.responses import FileResponse

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))
from core.core import db,conf,log
from business.license import License
from drawer.kp_license_draw import CertificateGenerator

def timestamp_to_date(timestamp: int, fmt: str = "%Y-%m-%d") -> str:
    """将秒级时间戳转为日期字符串
    Args:
        timestamp: 秒级时间戳
        fmt: 日期格式字符串，默认为"%Y-%m-%d %H:%M:%S"
    Returns:
        格式化后的日期字符串
    """
    return datetime.fromtimestamp(timestamp).strftime(fmt)

license_app = FastAPI()
license_obj = License(db)
kp_bg_path = conf.get()["resource"]["kp_license_background_path"]
pl_bg_path = conf.get()["resource"]["pl_license_background_path"]
ob_bg_path = conf.get()["resource"]["ob_license_background_path"]
dice_bg_path = conf.get()["resource"]["dice_license_background_path"]
default_avatar_path = conf.get()["resource"]["default_avatar_path"]
chinese_font_path = conf.get()["resource"]["chinese_font_path"]
english_font_path = conf.get()["resource"]["english_font_path"]
KpDrawer = CertificateGenerator(
    log=log,
    kp_background_path=kp_bg_path,
    ob_background_path=ob_bg_path,
    dice_background_path=dice_bg_path,
    pl_background_path=pl_bg_path,
    output_folder = "data/certificates",
    default_avatar_path=default_avatar_path,
    chinese_font_path=chinese_font_path,
    english_font_path=english_font_path
)

file = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(file, "../")
IMAGE_FOLDER = path + "data/certificates"
DOMAIN = conf.get()["api"]["domain"]
PORT = conf.get()["api"]["port"]

@license_app.post("/license/")
async def license_deal(request: Request):
    try:
        form_data = await request.json()
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "请求体必须包含有效的JSON数据",
                "data": {}
            }
        )

    # 检查必需字段是否存在
    if not all(key in form_data for key in ["role", "option"]):
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "请求必须包含role和option字段",
                "data": {}
            }
        )

    role = form_data.get("role")
    option = form_data.get("option")
    lid = form_data.get("lid")
    name = form_data.get("name")
    QQ = form_data.get("qq")
    level = int(form_data.get("level"))

    # 此处option为register时，p为name，option为confirm时，p为lid
    if option == "register":
        license_dict = license_obj.register_license(role=role,name=name,QQ=QQ,level=level)
        # 解析info字段中的JSON字符串
        info = json.loads(license_dict["info"])
        url = f"http://q2.qlogo.cn/headimg_dl?dst_uin={QQ}&spec=5"
        try:
            KpDrawer.generate_certificate(
                certificate_id=license_dict["lid"],
                name=info["name"],
                avatar_url=url,
                role=role,
                level=info["level"],
                date=timestamp_to_date(license_dict["time"])
            )
        except Exception as e:
            log.error(f"生成证书{license_dict['lid']}时出错: {e}")
            print(f"生成证书{license_dict['lid']}时出错: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "code": 400,
                    "message":f"请求出错：{e}",
                    "data": {}
                }
            )
        create_image_and_start_deletion(f"certificate_{license_dict['lid']}.jpg")
        return JSONResponse(
        status_code=200,
        content={
            "code": 200,
            "message": "success",
            "data": {
                "img_url": f"http://{DOMAIN}:{PORT}/images/certificate_{license_dict['lid']}.jpg",
            }
        }
    )
    elif option == "confirm":
        if role == "kp":
            res = license_obj.confirm_kp_license(lid=lid)
            return JSONResponse(
                status_code=200,
                content={
                    "code": 200,
                    "message": "success",
                    "data": {
                        "result": res,
                    }
                }
            )
        elif role == "dice":
            pass
        elif role == "pl":
            pass
        else:
            pass
    else:
        pass
    return JSONResponse(
        status_code=404,
        content={
            "code": 404,
            "message": "not found",
            "data": {}
                }
    )


# 挂载静态目录
license_app.mount("/images", StaticFiles(directory=IMAGE_FOLDER), name="images")

# 启动定时删除线程
def delete_file(path):
    time.sleep(300)  # 等待300秒
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"已删除图片: {path}")
    except Exception as e:
        print(f"删除图片失败: {e}")


# 模拟文件创建时启动删除线程
def create_image_and_start_deletion(image_name):
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    threading.Thread(target=delete_file, args=(image_path,)).start()


# 添加全局异常处理中间件
@license_app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        # 设置全局超时
        return await asyncio.wait_for(call_next(request), timeout=30)
    except asyncio.TimeoutError:
        return JSONResponse({"error": "请求超时"}, status_code=504)
