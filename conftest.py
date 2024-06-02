import os
import platform
import shutil
import re
import time
import random
import requests
import jmespath
from collections import defaultdict
from commons.db import DBC
from commons.files import file_handler
import subprocess


def pytest_collection_modifyitems(items):
    # 解决运行结果乱码问题
    for item in items:
        item.name = item.name.encode('UTF-8').decode('unicode-escape')
        item._nodeid = item.nodeid.encode('UTF-8').decode('unicode-escape')


# 生成随机数
def generate_random_number():
    return random.randint(1, 10000)  # 假设我们需要一个1到10000之间的随机数


# 提取关联接口响应数据
def extra_api_data(extract_str, config_data, case_data, db_path):
    request_params = make_input_data(config_data, case_data, db_path)[0]
    # 使用请求参数字典发送请求
    response = requests.request(**request_params).json()
    # print("上游接口响应",response)
    return jmespath.search(extract_str, response)


# 构造用例入参数据
def make_input_data(config_data, case_data, db_path):
    # extract_str = 'users[?id == `1`].tokens."10001"'
    # print(case_data["tests"][0]["input"]["params"])
    # print("配置数据：",config_data)
    # print("测试数据：", type(case_data["tests"][-1]["input"]['json']))
    # print("数据库路径：",db_path)
    input_data_list = []
    input_data = defaultdict()
    # print("wwwwww",case_data)
    if "tests" in case_data:
        rw_data = case_data["tests"]
    else:
        rw_data = case_data
    for case in rw_data:
        for key, value in case["input"].items():
            # print("测试case", key, value)
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
                    # print("key:", k)
                    # print("value", v)
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
                                    # print("接口提取：", api_str)
                                    ex_str_list = extract_str.split("extract.api")[-1].split(".")[1:]
                                    ex_str = '.'.join(ex_str_list)
                                    raw_api = jmespath.search(api_str, case_data)
                                    # print("api提取", raw_api)
                                    ext_data = extra_api_data(ex_str, config_data, raw_api, db_path)
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
                            # print("类型", type(res_name), res_name)
                            value[k] = re.sub(r"{{.*}}", res_name[0], str(v))
                    elif not isinstance(v, str) and "{{$" in str(v):
                        for i, j in v.items():
                            # print("iiii:", i)
                            # print("jjj", j)
                            if isinstance(j, str) and "{{$" in j:
                                obj_1 = re.search(r"{{.*}}", j)
                                extract_str = obj_1.group().replace("{{$.", "").replace("}}", "")
                                if "random_number" not in extract_str:
                                    if "extract.db" not in extract_str:
                                        if "extract.api" not in extract_str:
                                            res_name = jmespath.search(extract_str, config_data)
                                        else:
                                            section = extract_str.split("extract.api")[-1].split(".")[0]
                                            api_str = "tests" + section
                                            # print("接口提取：", api_str)
                                            ex_str_list = extract_str.split("extract.api")[-1].split(".")[1:]
                                            ex_str = '.'.join(ex_str_list)
                                            raw_api = jmespath.search(api_str, case_data)
                                            # print("api提取", raw_api)
                                            ext_data = extra_api_data(ex_str, config_data, raw_api, db_path)
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
                                    v[i] = re.sub(r"{{.*}}", res_name, str(j))
                                elif isinstance(res_name, int):
                                    v[i] = res_name
                                else:
                                    # print("类型", type(res_name), res_name)
                                    v[i] = re.sub(r"{{.*}}", res_name[0], str(j))

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


def pytest_addoption(parser):
    """
    在session开始之前，添加命令行参数，参数会保存在config对象的option属性中。
    """
    parser.addoption("--env",
                     action="store",
                     dest="env",
                     default="test",
                     help="env: test or stg")

    parser.addoption("--config",
                     action="store",
                     dest="conf",
                     default="demo_config.yaml",
                     help="configuration of testing project")


def pytest_configure(config):
    # print("项目根路径", config.rootdir)
    env = config.getoption("--env")
    conf = config.getoption("--config")
    rootpath = config.rootdir
    # print("根路径：",rootpath)
    config_path = os.path.join(rootpath, "config", env, conf)
    # print("配置文件路径：",config_path)
    os.environ['ENV'] = str(env)
    os.environ['ROOTPATH'] = str(rootpath)
    os.environ['CONF_PATH'] = str(config_path)
    # print(os.environ.get("ROOTPATH"))


def pytest_generate_tests(metafunc):
    env = os.environ.get("ENV")
    rootpath = os.environ.get("ROOTPATH")
    config_path = os.environ.get("CONF_PATH")
    db_path = str(os.path.join(rootpath, "config", env, "db.ini"))
    # print("数据库配置路径：", db_path)
    markers = metafunc.definition.own_markers
    for marker in markers:
        if marker.name == 'datafile':
            data_env_path = marker.args[0].split("/")[1]
            if data_env_path == env:
                test_data_path = os.path.join(metafunc.config.rootdir, marker.args[0])
            else:
                test_data_path = os.path.join(metafunc.config.rootdir, marker.args[0].replace(data_env_path, env))
            # print("测试数据路径：", test_data_path)
            config_data = file_handler.read_file(config_path)
            test_data = file_handler.read_file(test_data_path)
            inputs = make_input_data(config_data, test_data, db_path)
            # print("type:",type(inputs))
            expectation = []
            name = []
            author = []
            severity = []
            description = []
            for data in test_data["tests"]:
                name.append(data["case"])
                author.append(data["report"]["author"])
                severity.append(data["report"]["severity"])
                description.append(data["report"]["description"])
                expectation.append(data["expectation"]["validate"])
            # print("用例名称", case)
            # print("入参数据", make_input_data(config_data, test_data, db_path))
            # print("验证数据", expectation)
            # print("name_list",name)
            # print("聚合数据：",list(zip(name,author,severity,description)))
            cases_list = list(zip(name, author, severity, description))

            if "case" in metafunc.fixturenames and "inputs" in metafunc.fixturenames and "expectation" in metafunc.fixturenames:
                metafunc.parametrize("case,inputs,expectation", tuple(zip(cases_list, inputs, expectation)), ids=name,
                                     scope="function")


# @pytest.fixture(autouse=True)
# def custom_allure_report(author):
#     allure.dynamdynamicic.tag(author)

def pytest_sessionfinish(session, exitstatus):
    root_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    platform_name = platform.system()
    allure_results_path = root_path + r"/reports/allure_results"
    allure_reports_path = root_path + r"/reports/allure_reports"
    from_allure_enviornment_path = root_path + r"/environment.properties"
    to_allure_enviornment_path = allure_results_path + r"/environment.properties"
    # 尝试执行 'allure --version' 命令来检查 Allure 是否安装并可用
    if platform_name == "Darwin":
        try:
            result = subprocess.run(['allure', '--version'], check=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL)
            if result:
                # 默认生成报告路径:../reports/allure_reports
                os.system(f"cp {from_allure_enviornment_path} {to_allure_enviornment_path}")
                os.system(f"allure generate {allure_results_path} -o {allure_reports_path} --clean")
                # 直接打开allure报告
                os.system(f"allure serve {allure_results_path}")
        except subprocess.CalledProcessError as e:
            # 如果命令执行失败，打印错误信息
            print(f"allure 命令不可用或未正确安装。错误信息: {e}")
        except FileNotFoundError:
            # 如果命令未找到，说明 allure 未安装
            print("allure 命令未找到，可能未安装 allure cli。")

    elif platform_name == "Windows":
        try:
            # 判断allure在环境路径中，通常意味着可以直接执行
            if [i for i in os.getenv('path').split(';') if os.path.exists(i) and 'allure' in os.listdir(i)]:
                # 默认生成报告路径为:../reports/allure_reports
                shutil.copy(from_allure_enviornment_path, to_allure_enviornment_path)
                os.system(f"allure generate ../../reports/allure_results -o ../../reports/allure_reports -clean")
                # 直接打开allure报告
                # os.system(f"allure serve ../../reports/allure_results")
            else:
                print('allure不在环境变量中，无法直接生成htmL报告!')
        except Exception as e:
            print(e)
    else:
        print("当前在linux环境下，不需要直接打开allure报告！")


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """收集测试报告summary,并存入文件，给Jenkins调用"""

    passed_num = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    failed_num = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    error_num = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    skipped_num = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    total_num = passed_num + failed_num + error_num + skipped_num
    test_result = '测试通过' if total_num == passed_num + skipped_num else '测试失败'
    duration = round((time.time() - terminalreporter._sessionstarttime), 2)

    with open('./reports/status.txt', 'w', encoding='utf-8') as f:
        f.write(f'TEST_TOTAL={total_num}\n')
        f.write(f'TEST_PASSED={passed_num}\n')
        f.write(f'TEST_FAILED={failed_num}\n')
        f.write(f'TEST_ERROR={error_num}\n')
        f.write(f'TEST_SKIPPED={skipped_num}\n')
        f.write(f'TEST_DURATION={duration}\n')
        f.write(f'TEST_RESULT={test_result}\n')
