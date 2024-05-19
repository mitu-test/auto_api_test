# -*- coding: utf-8 -*-
"""
@Time ： 2024/3/17 18:14
@Auth ： jun.guo
@File ：api_demo.py
@IDE ：PyCharm
"""
import pytest
import requests
import allure
from commons.engine import assert_response_data


class TestContent:
    @pytest.mark.datafile('data/test/csd_content/data_api_demo.yaml')
    def test_pugc_list(self, case, inputs, expectation):
        # print("正在执行用例", case)
        # print("入参数据：",inputs)
        # print("断言数据",expectation)
        response = requests.request(**inputs)
        # print("响应数据：",response)
        assert_response_data(case,inputs,response, expectation)
