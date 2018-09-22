# -*- coding:utf-8 -*-
from ModelTestBase import ModelTestBase


class PRISMParserTest(ModelTestBase):

    '''
    单元测试模型
    ctmc
    const int param1 = 11;
    const double param2 = 11.0;
    const int param3 = 2 * param1;

    module XXX
        // variable definitions
        var1 : [0, param1] param1;
        var2 : [0, 10] init 5;
        var3 : [param1, 2 * param1] init param1;

        // command definitions
        [comm1] var1 == param1 -> param1 : (var1'=var1 - 1);
        [comm2] var1 != param1 -> true;
        [comm3] var1 == param1 -> param1 : (var1'=var1 - 1);
    endmodule

    module YYY
        var4: [0, 2] init 2;
        [comm1] var4 == 2 -> 1.5 -> (var4'=1);
    endmodule

    formula some_formula = (var2==5?6:4) + (var4==2?3:1);
    '''

    def _get_model_name(self):
        return "ParserTestModel"

    def testVarAndConst(self):
        '''
        验证常数，变量的解析正确，即参数的值解析正确，变量的初始值，范围和类型解析正确
        :return:
        '''
        m = self._model
        param1 = m.get_constant('param1')
        param2 = m.get_constant("param2")
        param3 = m.get_constant("param3")
        var1 = m.get_variable("var1")
        var2 = m.get_variable("var2")
        var3 = m.get_variable("var3")
        self.assertIsNotNone(var1)
        self.assertIsNotNone(var2)
        self.assertIsNotNone(var3)
        self.assertAlmostEqual(param2.get_value(), 11.0, 1e-10)
        self.assertEqual(param1.get_value(), 11)
        self.assertEqual(param3.get_value(), 2 * 11)
        self.assertEqual(var1.get_min(), 0)
        self.assertEqual(var1.get_max(), param1.get_value())
        self.assertEqual(var1.get_init(), param1.get_value())
        self.assertEqual(var2.get_min(), 0)
        self.assertEqual(var2.get_max(), 10)
        self.assertEqual(var2.get_init(), 5)
        self.assertEqual(var3.get_min(), param1.get_value())
        self.assertEqual(var3.get_max(), param1.get_value() * 2)
        self.assertEqual(var3.get_init(), param1.get_value())

    def testCommands(self):
        '''
        验证command解析正确，guard结果正确，概率/rate解析正确
        :return:
        '''
        model = self._model
        commands = model.get_commands()
        comm1 = commands.get("comm1")[0]
        comm2 = commands.get("comm2")[0]
        comm3 = commands.get("comm3")[0]

        self.assertTrue(comm1.evaluate())
        self.assertFalse(comm2.evaluate())
        self.assertTrue(comm3.evaluate())

        self.assertTrue(callable(comm3.get_prob()))
        self.assertEqual(comm3.get_prob()(), 11)

        comm1.execute()
        var1 = model.get_variable('var1')
        self.assertEqual(var1.get_value(), 10)

    def testSyncCommands(self):
        model = self._model
        comm1 = model.get_commands()['comm1']
        self.assertEqual(len(comm1), 1)
        comm1 = comm1[0]
        self.assertTrue(comm1.evaluate())
        self.assertAlmostEqual(comm1.get_prob()(), 1.5*11, delta=1e-5)
        comm1.execute()
        var1 = model.get_variable('var1')
        var4 = model.get_variable('var4')
        self.assertEqual(var1.get_value(), 10)
        self.assertEqual(var4.get_value(), 1)

    def testConditionExpression(self):
        formula = self._constructor.get_formula("some_formula")
        if callable(formula):
            self.assertEqual(formula(), 9)
