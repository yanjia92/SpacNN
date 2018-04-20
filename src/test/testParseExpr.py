# -*- coding: utf-8 -*-
from compiler.PRISMParser import ModelConstructor as Constructor
from math import log, pow, e, fabs
from util.MathUtils import pcf


# 验证PRISMParser.py对expr对象的解析功能
def test():
    # get model object
    constructor = Constructor()
    model_file_path = "../../prism_model/smalltest.prism"
    constructor.parseModelFile(model_file_path)
    model = constructor.model
    # set day's value
    days = range(10)
    # 运用parsed function计算出的结果
    parsed_prbs = []
    # 运用模型中的数据计算出的真实的结果
    prbs = []  # [(sb_fail_prb, s3r_fail_prb)]
    for day_val in days:
        # compute the failure probability of modules
        # get the fail prob function and compute
        var_day = model.getLocalVars("day")
        var_day.setValue(day_val)
        prbs.append(fail_prob_of_model(model))

        # get the parsed funciton and use it to compute the failure probability
        f_sb = constructor.parser.vfmap["sb_fail_prob"]
        f_s3r = constructor.parser.vfmap["s3r_fail_prob"]
        parsed_prbs.append((f_sb(), f_s3r()))
    # compare
    assert len(prbs) == len(parsed_prbs)
    for tuple1, tuple2 in zip(prbs, parsed_prbs):
        f1, f2 = tuple1
        f3, f4 = tuple2
        precision = 1e-4
        assert fabs(f1 - f3) < precision
        assert fabs(f2 - f4) < precision


# compute the failure probability of the model given the day value and SCREEN_THICKNESS
# result: (sb_fail_prob, s3r_fail_prob)
def fail_prob_of_model(model):
    vs = model.localVars
    cs = model.constants
    sb_stdx = stdx_sb(vs, cs)
    s3r_stdx = std_x_s3r(vs, cs)
    return map(pcf, (sb_stdx, s3r_stdx))


# 根据day_val计算sb模块的std_x
def stdx_sb(vs, cs):
    x = vs["day"].getValue()
    dose = x / 365.0 * cs["NIEL_YEAR"]
    cdf_x = (1 - cs["SB_P_THRESHOLD"]) / (log(1 + dose * cs["SB_B"]))
    std_x = (cdf_x - cs["SB_MU"]) / cs["SB_SIGMA"]
    return std_x


def std_x_s3r(vs, cs):
    x = vs["day"].getValue()
    dose = x / 365.0 * cs["IEL_YEAR"]
    cdf_x = cs["S3R_DELTAV_THRESHOLD"] / (cs["S3R_B"] * pow(e, cs["S3R_B"] * dose))
    std_x = (cdf_x - cs["S3R_A_MU"]) / cs["S3R_A_SIGMA"]
    return std_x

if __name__ == "__main__":
    test()