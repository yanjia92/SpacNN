# -*- coding: utf-8 -*-
from compiler.PRISMParser import ModelConstructor as Constructor
from math import log, pow, e, fabs
from util.MathUtils import pcf
import logging

logger = logging.getLogger("testParseExpr.py logging")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


# 验证PRISMParser.py对expr对象的解析功能
def test():
    # get model object
    constructor = Constructor()
    model_file_path = "../../prism_model/smalltest.prism"
    constructor._parseModelFile(model_file_path)
    model = constructor.model
    # set day's value
    days = range(1, 365*5)
    # 运用parsed function计算出的结果
    parsed_prbs = []
    # 运用模型中的数据计算出的真实的结果
    prbs = []  # [(sb_fail_prb, s3r_fail_prb)]
    for day_val in days:
        # compute the failure probability of modules
        # get the fail prob function and compute
        var_day = model.getLocalVar("day")
        var_day.set_value(day_val)
        prbs.append(fail_prob_of_model(model, constructor.parser.vfmap))

        # get the parsed function and use it to compute the failure probability
        f_sb = constructor.parser.vfmap["sb_fail_prob"]
        f_s3r = constructor.parser.vfmap["s3r_fail_prob"]
        parsed_prbs.append((f_sb(), f_s3r()))
    # compare
    assert len(prbs) == len(parsed_prbs)
    for tuple1, tuple2 in zip(prbs, parsed_prbs):
        f1, f2 = tuple1
        f3, f4 = tuple2
        precision = 1e-8
        # logger.info("f1={}, f3={}".format(f1, f3))
        # logger.info("f2={}, f4={}".format(f2, f4))
        assert fabs(f1 - f3) < precision, "day={}, f1={}, f3={}".format(day_val, f1, f3)
        assert fabs(f2 - f4) < precision, "day={}, f2={}, f4={}".format(day_val, f2, f4)


# compute the failure probability of the model given the day value and SCREEN_THICKNESS
# result: (sb_fail_prob, s3r_fail_prob)
def fail_prob_of_model(model, vfmap):
    vs = model.localVars
    cs = model.constants
    sb_stdx = stdx_sb(vs, cs, vfmap)
    s3r_stdx = std_x_s3r(vs, cs, vfmap)
    return map(lambda x: 1-pcf(x), (sb_stdx, s3r_stdx))


# 根据day_val计算sb模块的std_x
def stdx_sb(vs, cs, vfmap):
    x = vs["day"].get_value()
    NIEL_YEAR = vfmap["NIEL_YEAR"]()
    dose = x / 365.0 * NIEL_YEAR
    cdf_x = (1 - cs["SB_P_THRESHOLD"].get_value()) / (log(1 + dose * cs["SB_B"].get_value()))
    std_x = (cdf_x - cs["SB_A_MU"].get_value()) / cs["SB_A_SIGMA"].get_value()
    return std_x


def std_x_s3r(vs, cs, vfmap):
    x = vs["day"].get_value()
    IEL_YEAR = vfmap["IEL_YEAR"]()
    dose = x / 365.0 * IEL_YEAR
    cdf_x = cs["S3R_DELTAV_THRESHOLD"].get_value() / (cs["S3R_B"] * pow(e, cs["S3R_B"] * dose))
    std_x = (cdf_x - cs["S3R_A_MU"].get_value()) / cs["S3R_A_SIGMA"].get_value()
    return std_x

if __name__ == "__main__":
    test()