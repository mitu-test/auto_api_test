# -*- coding: utf-8 -*-
"""
@Time ： 2024/3/4 10:09
@Auth ： jun.guo
@File ：database.py
@IDE ：PyCharm
"""
import os
import configparser
import pymysql
import pymongo
import pandas as pd
from contextlib import closing
from commons.files import file_handler
# 配置文件路径
CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))),
                           'config/test', 'db.ini')


# print(CONFIG_PATH)


class DBC:
    """
    数据库操作类，支持MySQL、MongoDB数据库的增删改查操作。
    实例化时自动建立连接，析构时自动关闭连接。
    """

    def __init__(self, path,section):
        self.section = section
        # self.config = configparser.ConfigParser()
        # self.config.read(CONFIG_PATH, encoding='utf-8')
        self.config = file_handler.read_file(path)
        self.connection = None

    def get_connection(self):
        """
        根据配置文件中的数据库类型创建连接。
        """
        db_config = self.config[self.section]
        db_type = db_config.get('dbtype').upper()
        # print(db_type)
        try:
            if db_type == 'MYSQL':
                return pymysql.connect(
                    host=db_config['host'],
                    user=db_config['user'],
                    password=db_config['password'],
                    db=db_config['db'],
                    port=int(db_config['port']),
                    use_unicode=True,
                    charset="utf8",
                    autocommit=True
                )
            elif db_type == 'MONGODB':
                client = pymongo.MongoClient(
                    host=db_config['host'],
                    port=int(db_config['port'])
                )
                return client
            else:
                raise NotImplementedError(f"Unsupported database type: {db_type}")
        except Exception as e:
            print(f"Connection to database '{self.section}' failed!\n", e)
            return None

    def __enter__(self):
        """
        使用with语句时自动建立数据库连接。
        """
        if self.connection is None:
            self.connection = self.get_connection()
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        使用with语句时自动关闭数据库连接。
        """
        if self.connection:
            self.connection.close()

    def query(self, query: str, return_type: str = 'dataframe'):
        """
        执行SQL查询并返回结果。
        """
        if not query.upper().startswith('SELECT'):
            raise ValueError("需要执行查询语句")
        db_type = self.config[self.section].get('dbtype').upper()
        if return_type.lower() in ('df', 'dataframe'):
            try:
                if db_type in ('MYSQL',):
                    with self as conn:
                        # 返回字典列表
                        return pd.read_sql(query, conn).to_dict(orient='records')
            except Exception as e:
                print(e)
                raise EnvironmentError("查询数据库失败")
        else:
            raise NotImplementedError("还没有实现其他返回类型")

    def not_query(self, sql: str):
        """
        执行SQL插入、更新、删除语句。
        """
        with self as conn:
            with closing(conn.cursor()) as cursor:
                try:
                    cursor.execute(sql)
                    return True
                except Exception as e:
                    # print(e)
                    raise EnvironmentError(f"执行语句失败：{sql}")

    def mgb_sql(self, action: str, query: dict, update_query=None):
        """
        MongoDB 数据库操作。
        :param action: 操作类型，如 'insert', 'find', 'delete', 'update'
        :param query: 查询条件
        :param update_query: 更新条件（仅用于 'update' 操作）
        :return: 操作结果
        """
        if action not in ('insert', 'find', 'delete', 'update'):
            raise ValueError("Invalid action. Must be one of 'insert', 'find', 'delete', 'update'.")

        try:
            with self as conn:
                db_config = self.config[self.section]
                conn = conn[db_config['db']][db_config['cn']]
                if action == 'insert':
                    result = conn.insert_one(query)
                    return result.inserted_id
                elif action == 'find':
                    return pd.DataFrame(list(conn.find(query))).to_dict(orient='records')
                elif action == 'delete':
                    result = conn.delete_one(query)
                    return result.deleted_count
                elif action == 'update':
                    result = conn.update_one(query, {'$set': update_query})
                    return result.modified_count
        except Exception as e:
            print(e)
            raise EnvironmentError(f"执行 MongoDB 语句失败：{action}")

# user_post_sql = "SELECT * FROM lifestyle_test.content where id = '100991'"

# db_info = DBC(CONFIG_PATH,"mysql_test")
# print(db_info.query(user_post_sql))
# db = DBC("mysql_test")

# sql_q = "SELECT * FROM lifestyle_test.csd_content limit 10"
# sql_d_1 = "DELETE FROM lifestyle_test.csd_content WHERE id = '%s'" % '100769'
# sql_d_2 = "DELETE FROM table_name WHERE id = %d" % 1
# sql_d_u = "UPDATE `lifestyle_test`.`csd_content` SET `title` = '0331222播测试-299999999' WHERE (`id` = '100991');"
# results_1 = db.query(sql_q)
# results_2 = db.not_query(sql_d_1)
# results_3 = db.not_query(sql_d_u)
# print("是否查询成功", results_1)
# print("是否删除成功", results_2)
# print("是否更新成功", results_3)

# db_1 = DBC("nio_mongodb")
# query = {
#     "title": 'MongoDB 教程678',
#     "description": 'MongoDB 是一个 Nosql 数据库',
#     "by": '菜鸟教程',
#     "url": 'http://www.runoob.com',
#     "tags": ['mongodb', 'database', 'NoSQL'],
#     "likes": 100
# }
# results_4 = db_1.mgb_sql("insert", query)
# print(results_4)
# query_1 ={
#     "title": 'MongoDB 教程3',
# }
# query_2 = {
#     "title": 'MongoDB 教程22222222222222',
# }
# results_5 = db_1.mgb_sql("find", query_2)
# print("find", results_5)
# for i in results_5:
#     print(i)
# results_6 = db_1.mgb_sql("delete", query_1)
# print("delele",results_6)
# results_7 = db_1.mgb_sql("update", query_1,query_2)
# print("update",results_7)
