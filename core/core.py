from utils.conf import Config
from database.db_option import DB
from utils.log import Logos

DEFAULT_CONFIG = {
    "name":"KP-license",
    "work_dir":"./",
    "log":{
        "log_level":"info",
        "output_path":"data/",
        "output_file":"log.txt"
    },
    "api":{
        "route_root":"/",
        "port":19810,
        "host":"0.0.0.0",
        "token":"",
        "domain":"www.example.com"
    },
    "database":{
        "path":"data/database/",
        "file":"license.db"
    },
    "QQ_API":{
        "url":"",
        "token":""
    }
}

conf = Config(default=DEFAULT_CONFIG)
db = DB(db_path=conf.get()["work_dir"]+conf.get()["database"]["path"],file=conf.get()["database"]["file"])
log = Logos(name=conf.get()["name"], level=conf.get()["log"]["log_level"].upper(),output_path= conf.get()["work_dir"]+conf.get()["log"]["output_path"],output_file=conf.get()["log"]["output_file"])


