import logging
import os


class Logos:
    def __init__(self,name:str="KP-license", output_path:str ="./data/log.txt",output_file:str ="log.txt",level:int=logging.INFO):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        # 检查输出路径是否存在，如果不存在则创建
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        self.handler = logging.FileHandler(output_path+output_file)
        self.handler.setLevel(level)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def info(self, message:str):
        self.logger.info(message)

    def error(self, message:str):
        self.logger.error(message)

    def warning(self, message:str):
        self.logger.warning(message)

    def debug(self, message:str):
        self.logger.debug(message)

    def critical(self, message:str):
        self.logger.critical(message)