import logging
import os

root = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))))
log_path = root + r'/logs'


class LoggerHandler(logging.Logger):
    # 继承Logger类
    def __init__(self, name='root', level="DEBUG", file=None, formats=None):
        # 设置收集器
        super().__init__(name)
        # 设置收集器级别
        self.setLevel(level)
        # 设置日志格式
        fmt = logging.Formatter(formats)
        # 如果存在文件，就设置文件处理器，日志输出文件
        if file:
            file_handler = logging.FileHandler(file, mode="w", encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(fmt)
            self.addHandler(file_handler)
        # 设置StreamHandler,输出日志到控制台
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(fmt)
        self.addHandler(stream_handler)


# 目录不存在新建
if not os.path.exists(log_path):
    os.makedirs(log_path)
# logging相关配置
logger = LoggerHandler(
    name="Logger",
    level="INFO",
    file=log_path + r"/error.log",
    formats="%(asctime)s--%(levelname)s--%(filename)s--%(funcName)s--%(message)s"
)
