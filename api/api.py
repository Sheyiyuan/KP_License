from fastapi import FastAPI,Response,Request
from fastapi.responses import JSONResponse
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
KpDrawer = CertificateGenerator(log=log,background_path="./resource/bg_kp_2r6.png",output_folder = "data/certificates",default_avatar_path="./resource/default_avatar.jpg")

IMAGE_FOLDER = "data/certificates"
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
        if role == "kp":
            license_dict = license_obj.register_kp_license(name=name,QQ=QQ,level=level)
            print(license_dict)
            # 解析info字段中的JSON字符串
            info = json.loads(license_dict["info"])
            url = f"http://q2.qlogo.cn/headimg_dl?dst_uin={QQ}&spec=5"
            KpDrawer.generate_certificate(
                certificate_id=license_dict["lid"],
                name=info["name"],
                avatar_url=url,
                level=info["level"],
                date=timestamp_to_date(license_dict["time"])
            )
            return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "message": "success",
                "data": {
                    "img_url": f"{DOMAIN}:{PORT}/images/certificate_{license_dict['lid']}.jpg",
                }
            }
        )
        elif role == "dice":
            pass
        elif role == "pl":
            pass
        else:
            pass
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


@license_app.get("/images/{image_path:path}")
async def get_image(image_path: str):
    image_path = os.path.join(IMAGE_FOLDER, image_path)
    # 检查图片文件是否存在
    if not os.path.exists(image_path):
        return {"error": "图片文件不存在"}

    # 读取图片内容
    with open(image_path, "rb") as f:
        image_data = f.read()

    # 启动定时删除线程
    def delete_file(path):
        time.sleep(60)  # 等待60秒
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"已删除图片: {path}")
        except Exception as e:
            print(f"删除图片失败: {e}")

    threading.Thread(target=delete_file, args=(image_path,)).start()

    # 返回图片数据
    return Response(content=image_data, media_type="image/jpeg")
