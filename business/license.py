import uuid
import time
import json
import base58

from database.db_option import DB

class License:
    def __init__(self,db:DB):
        self.namespace = uuid.NAMESPACE_DNS
        self.db = db
    def generate_lid(self, role:str, name:str,QQ:str):
        name = f"{role}_{name}_{QQ}"
        uuid_value = uuid.uuid5(self.namespace, name)
        # 将UUID转换为bytes然后base58编码
        uuid_bytes = uuid_value.bytes
        return base58.b58encode(uuid_bytes).decode('utf-8')
    def register_kp_license(self, name:str, QQ:str, level:int):
        try:
            lid = self.generate_lid("KP", name, QQ)
            record = self.db.get_record(lid)
            if record is None:
                # 确保所有传入值都是字符串或可转换为字符串的类型
                self.db.add_record(
                    lid=str(lid),
                    license_type="KP",
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


