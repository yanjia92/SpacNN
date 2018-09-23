# -*- coding:utf-8 -*-
from util.CsvFileHelper import parse_csv_rows
from PathHelper import *


variances_path = get_results_dir() + get_sep() + "variances.txt"
anti_variance_path = get_results_dir() + get_sep() + "anti_variances.txt"

variances = parse_csv_rows(variances_path, has_headers=False)
anti_variances = parse_csv_rows(anti_variance_path, has_headers=False)


def _compute_percentage(nums, threshold):
    '''
    计算nums中小于threshold的数所占的比例
    :param nums: list of number
    :param threshold: number
    :return:
    '''
    filtered = filter(lambda elem: elem <= threshold, nums)
    return float(len(filtered)) / len(nums)


def _compute_z_value(nums, percentage):
    '''
    给出比例，计算nums中该比例对应的数
    :param nums: list of number
    :param percentage: [0,1)
    :return: number
    '''
    sorted_nums = sorted(nums)
    size = len(sorted_nums)
    return sorted_nums[int(size*percentage)]


print _compute_percentage(variances, 0.01)
print _compute_percentage(anti_variances, 0.01)
print _compute_z_value(variances, 0.8)
print _compute_z_value(anti_variances, 0.8)