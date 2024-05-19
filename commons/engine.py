# -*- coding: utf-8 -*-
"""
@Time ： 2024/3/18 19:49
@Auth ： jun.guo
@File ：engine.py
@IDE ：PyCharm
"""
import json
import os
import re
import random
import requests
import jmespath
import allure
from commons.files import file_handler
from collections import defaultdict
from commons.db import DBC
from commons.asst import *

# 配置文件路径
config_path = os.path.join(os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))),
                           'config/test', 'csd_content_config.yaml')
case_path = os.path.join(os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))),
                         'data/test/csd_content', 'data_api_demo.yaml')
config_data = file_handler.read_file(config_path)
case_data = file_handler.read_file(case_path)
db_path = os.path.join(os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))),
                       'config/test', 'db.ini')


# user_post_sql = "SELECT * FROM lifestyle_test.content where id = '100991'"

# db_info = DBC(db_path,"mysql_test")
# print(db_info.query(user_post_sql))
# # print("search:", jmespath.search("tests[?case=='GET请求 - 提取参数']", case_data))


# 生成随机数
def generate_random_number():
    return random.randint(1, 10000)  # 假设我们需要一个1到10000之间的随机数


# 提取关联接口响应数据
def extra_api_data(extract_str, data):
    request_params = make_input_data(data)[0]
    # 使用请求参数字典发送请求
    response = requests.request(**request_params).json()
    return jmespath.search(extract_str, response)


# 构造用例入参数据
def make_input_data(raw_data):
    # print("测试数据：", raw_data)
    # extract_str = 'users[?id == `1`].tokens."10001"'
    # print(case_data["tests"][0]["input"]["params"])
    # print(config_data)
    input_data_list = []
    input_data = defaultdict()
    # print(case_data)
    for case in raw_data:
        for key, value in case["input"].items():
            # print(value)
            if isinstance(value, str) and "{{$" in value:
                obj_1 = re.search(r"{{.*}}", value)
                # print(obj_1.start(),obj_1.end())
                # print(obj_1.group())
                extract_str = obj_1.group().replace("{{$.", "").replace("}}", "")
                # print(extract_str)
                # extract_str = value.replace("{{","").replace("}}","").split(".")
                # print(extract_str)

                if "random_number" not in extract_str:
                    res_name = jmespath.search(extract_str, config_data)
                else:
                    res_name = str(generate_random_number())
                # print(res_name)
                # temp_data = config_data
                # for s in extract_str[1:]:
                #     if not isinstance(temp_data[s], str):
                #         temp_data = temp_data[s]
                #         continue
                #     if obj_1.start() == 0:
                #         input_data[key]=temp_data[s]
                #     elif obj_1.start() > 0:
                #         input_data[key] = value[:obj_1.start()] + temp_data[s]
                if isinstance(res_name, str):
                    input_data[key] = re.sub(r"{{.*}}", res_name, str(value))
                else:
                    input_data[key] = re.sub(r"{{.*}}", res_name[0], str(value))

                # if obj_1.start() == 0:
                #     input_data[key]=res_name
                # elif obj_1.start() > 0:
                #     input_data[key] = value[:obj_1.start()] + res_name
            elif isinstance(value, str) and "{{$" not in value:
                input_data[key] = value
            elif not isinstance(value, str) and "{{$" in str(value):

                for k, v in value.items():
                    if isinstance(v, str) and "{{$" in v:
                        obj_1 = re.search(r"{{.*}}", v)
                        extract_str = obj_1.group().replace("{{$.", "").replace("}}", "")
                        if "random_number" not in extract_str:
                            if "extract.db" not in extract_str:
                                if "extract.api" not in extract_str:

                                    res_name = jmespath.search(extract_str, config_data)
                                else:
                                    section = extract_str.split("extract.api")[-1].split(".")[0]
                                    api_str = "tests" + section
                                    print("接口依赖提取：", api_str)
                                    ex_str_list = extract_str.split("extract.api")[-1].split(".")[1:]
                                    ex_str = '.'.join(ex_str_list)
                                    raw_api = jmespath.search(api_str, case_data)
                                    ext_data = extra_api_data(ex_str, raw_api)
                                    res_name = ext_data
                            else:
                                section = extract_str.split("extract.db.")[-1].split(".")[0]
                                sql_str = extract_str.split("extract.db.")[-1].split(".")[1]
                                rp_str = extract_str.split("extract.db.")[-1].split(".")[-1]
                                # print(rp_str)
                                my_db = DBC(db_path, section)
                                sql = my_db.config[section][sql_str]
                                # print("eeee",sql)
                                # # sql = "SELECT * FROM lifestyle_test.content where id = '100991'"
                                res = my_db.query(str(sql))
                                qw = "res" + rp_str
                                res_name = eval(qw)
                        else:
                            res_name = str(generate_random_number())
                        # print("222:", res_name, type(res_name))

                        if isinstance(res_name, str):
                            value[k] = re.sub(r"{{.*}}", res_name, str(v))
                        elif isinstance(res_name, int):
                            value[k] = res_name
                        else:
                            value[k] = re.sub(r"{{.*}}", res_name[0], str(v))
                input_data[key] = value
            elif not isinstance(value, str) and "{{$" not in str(value):
                input_data[key] = value
        # print(dict(input_data))
        input_data["url"] = input_data["host"] + input_data["path"]
        # print(input_data["url"])
        del input_data['host']
        del input_data['path']
        input_data_list.append(dict(input_data))
    return input_data_list


# 构造用例响应数据
def assert_response_data(case, inputs, response, expectation):
    # print("case类型：",type(case))
    # print(case["name"],case["severity"],case["description"],case["author"])
    allure.dynamic.title(case[0])
    allure.dynamic.severity(case[2])
    allure.dynamic.description(case[3])
    allure.dynamic.tag(case[1])
    allure.attach(json.dumps(inputs, indent=4, ensure_ascii=False), "接口请求", allure.attachment_type.JSON)
    allure.attach(json.dumps(response.json(), indent=4, ensure_ascii=False), "接口响应", allure.attachment_type.JSON)
    expectation_list = []
    for data in expectation:
        expectation_log = defaultdict()
        for key, value in data.items():
            if isinstance(value, list):
                exp_data = value[-1]
                jmes_str = value[0]
                if "extract.db" not in jmes_str:
                    actual_data = jmespath.search(jmes_str, response.json())
                else:
                    jmes_str = jmes_str.replace("{{$.", "").replace("}}", "")
                    section = jmes_str.split("extract.db.")[-1].split(".")[0]
                    sql_str = jmes_str.split("extract.db.")[-1].split(".")[1]
                    rp_str = jmes_str.split("extract.db.")[-1].split(".")[-1]
                    # print(rp_str)
                    my_db = DBC(db_path, section)
                    sql = my_db.config[section][sql_str]
                    # print("eeee",sql)
                    # # sql = "SELECT * FROM lifestyle_test.content where id = '100991'"
                    res = my_db.query(str(sql))
                    qw = "res" + rp_str
                    actual_data = eval(qw)
                try:
                    if key == "eq":
                        expectation_log["assert_type"] = "断言实际值等于预期值"
                        assert_equal(actual_data, exp_data)

                    elif key == "neq":
                        expectation_log["assert_type"] = "断言实际值不等于预期值"
                        assert_not_equal(actual_data, exp_data)
                    elif key == "lt":
                        expectation_log["assert_type"] = "断言实际值小于预期值"

                        assert_less_than(actual_data, exp_data)

                    elif key == "le":
                        expectation_log["assert_type"] = "断言实际值小于或等于预期值"

                        assert_less_equal_than(actual_data, exp_data)

                    elif key == "gt":
                        expectation_log["assert_type"] = "断言实际值大于预期值"

                        assert_greater_than(actual_data, exp_data)

                    elif key == "ge":
                        expectation_log["assert_type"] = "断言实际值大于或等于预期值"
                        assert_greater_equal_than(actual_data, exp_data)

                    elif key == "in":
                        expectation_log["assert_type"] = "断言实际值包含在预期列表中"

                        assert_in(actual_data, exp_data)

                    elif key == "nin":
                        expectation_log["assert_type"] = "断言实际值不包含在预期列表中"
                        assert_not_in(actual_data, exp_data)

                    elif key == "contains":
                        expectation_log["assert_type"] = "断言字符串实际值包含预期子字符串"
                        assert_contains(actual_data, exp_data)

                    elif key == "ncontains":
                        expectation_log["assert_type"] = "断言字符串实际值不包含预期子字符串"

                        assert_not_contains(actual_data, exp_data)

                    elif key == "nul":
                        expectation_log["assert_type"] = "断言实际值是None"
                        assert_null(actual_data)

                    elif key == "nnul":
                        expectation_log["assert_type"] = "断言实际值不是None"
                        assert_not_null(actual_data)

                    elif key == "el":
                        expectation_log["assert_type"] = "断言列表或字符串的长度等于预期长度"
                        assert_length_equal(actual_data, exp_data)

                    elif key == "nel":
                        expectation_log["assert_type"] = "断言列表或字符串的长度不等于预期长度"
                        assert_length_not_equal(actual_data, exp_data)

                    elif key == "ltl":
                        expectation_log["assert_type"] = "断言列表或字符串的长度小于预期长度"

                        assert_length_less_than(actual_data, exp_data)

                    elif key == "lel":
                        expectation_log["assert_type"] = "断言列表或字符串的长度小于等于预期长度"
                        assert_length_less_equal_than(actual_data, exp_data)

                    elif key == "gtl":
                        expectation_log["assert_type"] = "断言列表或字符串的长度大于预期长度"
                        assert_length_greater_than(actual_data, exp_data)

                    elif key == "gel":
                        expectation_log["assert_type"] = "断言列表或字符串的长度大于等于预期长度"
                        assert_length_greater_equal_than(actual_data, exp_data)

                    elif key == "stw":
                        expectation_log["assert_type"] = "断言字符串实际值以预期的前缀开头"
                        assert_starts_with(actual_data, exp_data)

                    elif key == "edw":
                        expectation_log["assert_type"] = "断言字符串实际值以预期的后缀结尾"
                        assert_ends_with(actual_data, exp_data)
                    elif key == "rex":
                        expectation_log["assert_type"] = "断言字符串实际值匹配预期的正则表达式"
                        assert_regex(actual_data, exp_data)

                    expectation_log["assert_field"] = jmes_str
                    expectation_log["actual_data"] = actual_data
                    expectation_log["expect_data"] = exp_data
                    expectation_list.append(expectation_log)
                except Exception as e:
                    expectation_log["assert_field"] = jmes_str
                    expectation_log["actual_data"] = actual_data
                    expectation_log["expect_data"] = exp_data
                    expectation_list.append(expectation_log)
                    allure.attach(json.dumps(expectation_list, indent=4, ensure_ascii=False), "接口断言",
                                  allure.attachment_type.JSON)
                    raise e
            else:
                print("断言格式书写的不对！")
    allure.attach(json.dumps(expectation_list, indent=4, ensure_ascii=False), "接口断言", allure.attachment_type.JSON)

# raw_data = case_data["tests"]
# input_data = make_input_data(raw_data)[0]
# print(input_data)
# expected_data = case_data["tests"][0]['expectation']["validate"]
# asser_response_data(input_data, expected_data)
