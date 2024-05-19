# -*- coding: utf-8 -*-
"""
@Time ： 2024/4/15 17:50
@Auth ： jun.guo
@File ：test_oapi_dingtalk_api.py
@IDE ：PyCharm
"""
import time
import pytest
import requests
from commons.engine import assert_response_data


class TestOapiDingTalk:
    @pytest.mark.datafile('data/test/oapi_dingtalk/oapi_dingtalk_api.yaml')
    def test_oapi_dingtalk_api(self, case, inputs, expectation):
        # print("正在执行用例", case)
        # print("入参数据：",inputs)
        # print("断言数据",expectation)
        response = requests.request(**inputs)
        # print("响应数据：",response)
        assert_response_data(case,inputs,response, expectation)
