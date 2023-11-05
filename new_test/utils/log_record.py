#coding=utf-8
import logging
from logging import handlers
import os
import time

class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射


    def __init__(self,filename,level='info',when='MIDNIGHT',backCount=7,fmt='%(asctime)s-[line:%(lineno)d] - %(levelname)s: %(message)s'):
        code_path = os.getcwd()
        log_path = rf'{code_path}\log'
        if not os.path.exists(log_path):
            print(f"创建目录{log_path}")
            os.makedirs(log_path)
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get(level))#设置日志级别
        sh = logging.StreamHandler()#往控制台输出
        sh.setFormatter(format_str) #设置控制台上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename,interval=1,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.suffix = "%Y-%m-%d.log" #设置文件后缀
        th.setFormatter(format_str)#设置文件里写入的格式
        self.logger.addHandler(sh) #把对象加到logger里
        self.logger.addHandler(th)

# logger =Logger(os.getcwd()+f'/log/rec_{time.strftime("%Y%m%d", time.localtime())}.log',level='debug').logger
logger =Logger(os.getcwd()+f'/log/acc_{time.strftime("%Y%m%d", time.localtime())}.log',level='debug').logger
