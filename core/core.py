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
    "resource":{
        "kp_license_background_path":"resource/bg_kp_2r6.png",
        "pl_license_background_path":"resource/bg_pl_2r6.png",
        "ob_license_background_path":"resource/bg_ob_2r6.png",
        "dice_license_background_path":"resource/bg_dice_2r6.png",
        "default_avatar_path":"resource/default_avatar.jpg",
        "chinese_font_path":"resource/fonts/FangSong.ttf",
        "english_font_path":"resource/fonts/Times New Roman.ttf"
    }
}

conf = Config(default=DEFAULT_CONFIG)
db = DB(db_path=conf.get()["work_dir"]+conf.get()["database"]["path"],file=conf.get()["database"]["file"])
log = Logos(name=conf.get()["name"], level=conf.get()["log"]["log_level"].upper(),output_path= conf.get()["work_dir"]+conf.get()["log"]["output_path"],output_file=conf.get()["log"]["output_file"])


