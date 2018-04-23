# -*- coding:utf-8 -*-
from module.Module import Constant


class SPSConfig():
    def __init__(self):
        self.params = {}
        self.params['SB_K'] = Constant('SB_K', 0.0039)
        self.params['SB_B'] = Constant('SB_B', 1.8)
        self.params['SB_P_THRESHOLD'] = Constant('SB_P_THRESHOLD', 0.78 * 1.05)
        self.params['SB_A_MU'] = Constant('SB_A_MU', 0.1754)
        self.params['SB_A_SIGMA'] = Constant('SB_A_SIGMA', 0.02319029 * 21)
        self.params['S3R_K'] = Constant('S3R_K', 200.5 / 3.0)  # s3r, bdr, bcr三个模块均摊电离能损
        self.params['S3R_DELTAV_THRESHOLD'] = Constant('S3R_DELTAV_THRESHOLD', 880 * (10.0/880))
        self.params['S3R_A_MU'] = Constant('S3R_A_MU', 570.8 * 18 - 570.8 * 5)
        self.params['S3R_A_SIGMA'] = Constant('S3R_A_SIGMA', 6.7471 * 220)
        self.params['S3R_B'] = Constant('S3R_B', 0.0131*0.57 * 0.1)
        self.params['SCREEN_THICKNESS'] = Constant('SCREEN_THICKNESS', 1)
        self.params['DURATION_IN_DAY'] = Constant('DURATION_IN_DAY', 365*2)

    def getParam(self, name):
        if name in self.params.keys():
            return self.params[name]
        else:
            raise Exception('no parameter found: {0}'.format(name))

    def setParam(self, name, value):
        self.params[name].value = value

    def export2prism(self, prismfileaddr):
        """
        SPSConfig.py文件中保存着SPS系统的唯一一份参数值的映射
        所以,修改了这个函数中的参数值,需要将修改的值同步到PRISM的model文件
        prismfileaddr: PRISMmodel文件的绝对路径
        """
        i= prismfileaddr.rfind(r"/")
        newfileaddr = prismfileaddr[:i] + "/NewModel.prism"
        f_new = open(newfileaddr, "w")
        with open(prismfileaddr) as f:
            for line in f:
                written = False
                temp = line.lower()
                # 去掉注释
                i = temp.find(r"//")
                temp = temp[:i]
                comment = temp[i:]
                if i == -1:
                    comment = ""
                for k, v in self.params.items():
                    if temp.find(k.lower()) != -1 and temp.find("const") != -1:
                        i = line.find('=')
                        if i == -1:
                            break
                        line = line[:i+1] + " " + str(v.getValue()) + ";" + comment + "\n"
                        f_new.write(line)
                        written = True
                        break
                if not written:
                    f_new.write(line)
        f_new.close()


def export_2_smalltest():
    config = SPSConfig()
    config.export2prism("../../prism_model/smalltest.prism")


if __name__ == "__main__":
    export_2_smalltest()