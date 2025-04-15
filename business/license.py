import uuid
import time
import json

from database.db_option import DB

class License:
    def __init__(self,db:DB):
        self.namespace = uuid.NAMESPACE_DNS
        self.db = db
    def generate_lid(self, role:str, name:str,QQ:str,level:int):
        name = f"{role}{name}{QQ}{level}"
        uuid_value = uuid.uuid5(self.namespace, name)
        # 将UUID转换为bytes然后base62编码
        uuid_bytes = uuid_value.bytes
        lid = bytes_to_base62(uuid_bytes)
        # 去掉末尾的'='
        lid = lid.rstrip('=')
        return lid
    def register_license(self, role:str, name:str, QQ:str, level:int):
        try:
            lid = self.generate_lid(role, name, QQ,level)
            record = self.db.get_record(lid)
            if record is None:
                # 确保所有传入值都是字符串或可转换为字符串的类型
                self.db.add_record(
                    lid=str(lid),
                    license_type=role,
                    info=json.dumps({
                        "name": str(name),
                        "QQ": QQ,
                        "level": str(level)
                    }),
                    time=str(int(time.time()))
                )
                record = self.db.get_record(lid)

            # 将返回的tuple转为dict
            if isinstance(record, tuple):
                return {
                    'lid': record[0],
                    'license_type': record[1],
                    'info': record[2],
                    'time': record[3]
                }
            return record
        except Exception as e:
            raise e
    def confirm_kp_license(self, lid:str):
        try:
            record = self.db.get_record(lid)
            if record is None:
                return False
            if isinstance(record, tuple):
                record = {
                    'lid': record[0],
                    'license_type': record[1],
                    'info': record[2],
                    'time': record[3]
                }
            if record.get("license_type") != "KP":
                return False
            return True
        except Exception as e:
            raise e


BASE62_CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def bytes_to_base62(b):
    # 将bytes转换为整数
    num = int.from_bytes(b, byteorder='big')
    if num == 0:
        return BASE62_CHARSET[0]
    result = ""
    while num > 0:
        num, remainder = divmod(num, 62)
        result = BASE62_CHARSET[remainder] + result
    return result