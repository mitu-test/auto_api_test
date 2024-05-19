# -*- coding: utf-8 -*-
"""
@Time ： 2024/3/13 11:47
@Auth ： jun.guo
@File ：asst.py
@IDE ：PyCharm
"""
import jmespath


def assert_equal(actual, expected):
    """断言实际值等于预期值"""
    assert actual == expected, f"Expected {expected}, but got {actual}"


def assert_not_equal(actual, expected):
    """断言实际值不等于预期值"""
    assert actual != expected, f"Expected not {expected}, but got {actual}"


def assert_greater_than(actual, expected):
    """断言实际值大于预期值"""
    assert actual > expected, f"Expected {actual} to be greater than {expected}, but it's not"


def assert_less_than(actual, expected_value):
    """断言实际值小于预期值"""
    assert actual < expected_value, f"Expected {actual} to be less than {expected_value}, but it's not"


def assert_greater_equal_than(actual, expected_value):
    """断言实际值大于或等于预期值"""
    assert actual >= expected_value, f"Expected {actual} to be greater than or equal to {expected_value}, but it's not"


def assert_less_equal_than(actual, expected_value):
    """断言实际值小于或等于预期值"""
    assert actual <= expected_value, f"Expected {actual} to be less than or equal to {expected_value}, but it's not"


def assert_in(actual, expected_list):
    """断言实际值包含在预期列表中"""
    assert actual in expected_list, f"Expected {actual} to be in {expected_list}, but it's not"


def assert_not_in(actual, unexpected_list):
    """断言实际值不包含在预期列表中"""
    assert actual not in unexpected_list, f"Expected {actual} not to be in {unexpected_list}, but it is"


def assert_contains(actual_str, expected_str):
    """断言字符串实际值包含预期子字符串"""
    assert expected_str in actual_str, f"Expected '{actual_str}' to contain '{expected_str}', but it does not"


def assert_not_contains(actual_str, unexpected_str):
    """断言字符串实际值不包含预期子字符串"""
    assert unexpected_str not in actual_str, f"Expected '{actual_str}' not to contain '{unexpected_str}', but it does"


def assert_type(actual, expected_type):
    """断言实际值的类型等于预期类型"""
    assert type(actual) == expected_type, f"Expected type {expected_type}, but got {type(actual)}"


def assert_not_type(actual, expected_type):
    """断言实际值的类型不等于预期类型"""
    assert type(actual) != expected_type, f"Expected type {expected_type}, but got {type(actual)}"


def assert_length_equal(actual_list, expected_length):
    """断言列表或字符串的长度等于预期长度"""
    assert len(actual_list) == expected_length, f"Expected length {expected_length}, but got {len(actual_list)}"


def assert_length_not_equal(actual_list, expected_length):
    """断言列表或字符串的长度不等于预期长度"""
    assert len(actual_list) != expected_length, f"Expected length {expected_length}, but got {len(actual_list)}"


def assert_length_greater_than(actual_list, expected_length):
    """断言列表或字符串的长度大于预期长度"""
    assert len(actual_list) > expected_length, f"Expected length {expected_length}, but got {len(actual_list)}"


def assert_length_greater_equal_than(actual_list, expected_length):
    """断言列表或字符串的长度大于等于预期长度"""
    assert len(actual_list) >= expected_length, f"Expected length {expected_length}, but got {len(actual_list)}"


def assert_length_less_than(actual_list, expected_length):
    """断言列表或字符串的长度小于预期长度"""
    assert len(actual_list) < expected_length, f"Expected length {expected_length}, but got {len(actual_list)}"


def assert_length_less_equal_than(actual_list, expected_length):
    """断言列表或字符串的长度小于等于预期长度"""
    assert len(actual_list) <= expected_length, f"Expected length {expected_length}, but got {len(actual_list)}"


def assert_null(actual):
    """断言实际值是None"""
    assert actual is None, f"Expected None, but got {actual}"


def assert_not_null(actual):
    """断言实际值不是None"""
    assert actual is not None, f"Expected not None, but got {actual}"


def assert_starts_with(actual_str, expected_prefix):
    """断言字符串实际值以预期的前缀开头"""
    assert actual_str.startswith(expected_prefix), f"Expected '{actual_str}' to start with '{expected_prefix}'"


def assert_ends_with(actual_str, expected_suffix):
    """断言字符串实际值以预期的后缀结尾"""
    assert actual_str.endswith(expected_suffix), f"Expected '{actual_str}' to end with '{expected_suffix}'"


def assert_regex(actual_str, pattern):
    """断言字符串实际值匹配预期的正则表达式"""
    import re
    assert re.match(pattern, actual_str) is not None, f"Expected string '{actual_str}' to match pattern '{pattern}'"


def assert_jsonpath(response_json, jsonpath_expression, expected_value):
    """使用jmespath断言JSONPath表达式的结果"""
    actual_value = jmespath.search(jsonpath_expression, response_json)
    assert_equal(actual_value, expected_value,
                 f"JSONPath expression {jsonpath_expression} expected to be {expected_value}, but got {actual_value}")
