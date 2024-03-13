import logging
from pathlib import Path


class Logger:
    rootPath=Path(__file__).parent.parent.absolute()

    def __init__(self,log_name:str) -> None:
        self.logPath = Logger.rootPath.joinpath('log')
        self.logPath.mkdir(exist_ok=True)
        self.log_name = log_name+'.log' if not log_name.endswith('.log') else log_name
        self.logFile = self.logPath.joinpath(self.log_name)
        self.logger = logging.getLogger(self.log_name.replace(".log",""))
        self.logger.setLevel(logging.INFO)
        fileHandler = self.createFHandler()
        self.logger.addHandler(fileHandler)
        
    def createFHandler(self):
        handler = logging.FileHandler(self.logFile, encoding='utf8')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        return handler

    def log(self,msg:str):
        self.logger.info(msg)