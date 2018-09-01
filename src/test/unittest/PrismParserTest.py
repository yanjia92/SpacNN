# -*- coding:utf-8 -*-
from ModelTestBase import ModelTestBase


class PRISMParserTest(ModelTestBase):

    '''
    单元测试模型
    const int param1 = 11;
    const double param2 = 11.0;

    module XXX
        // variable definitions
        var1 : [0, param1] param1;
        var2 : [0, 10] init 5;
        var3 : [param1, 2 * param1] init param1;

        // command definitions
        [comm1] var1 == param1 -> true;
        [comm2] var1 != param1 -> true;
        [comm3] var1 == param1 -> param1 -> (var1'=var-1);
    endmodule
    '''
    def setUp(self):
        ModelTestBase.setUp(self)

    def _get_model_name(self):
        return "ParserTestModel"

    def testVarAndConst(self):
        model = self._model
        variables = model.localVars
        constants = model.constants
        self.assertIsNotNone(variables)
        self.assertIsNotNone(constants)
        param1 = constants.get("param1")
        param2 = constants.get("param2")
        var1 = variables.get("var1")
        var2 = variables.get("var2")
        var3 = variables.get("var3")
        self.assertIsNotNone(var1)
        self.assertIsNotNone(var2)
        self.assertIsNotNone(var3)
        self.assertAlmostEqual(param2, 11.0, 1e-10)
        self.assertEqual(param1, 11)
        self.assertEqual(var1.range[0], 0)
        self.assertEqual(var1.range[-1], param1)
        self.assertEqual(var1.init_val, param1)
        self.assertEqual(var2.range[0], 0)
        self.assertEqual(var2.range[-1], 10)
        self.assertEqual(var2.init_val, 5)
        self.assertEqual(var3.range[0], param1)
        self.assertEqual(var3.range[-1], param1 * 2)
        self.assertEqual(var3.init_val, param1)

    def testCommands(self):
        model = self._model
        vs = model.localVars
        cs = model.constants
        commands = {}
        for _, mod in model.modules.items():
            commands.update(mod.commands)
        comm1 = commands.get("comm1")[0]
        comm2 = commands.get("comm2")[0]
        comm3 = commands.get("comm3")[0]

        self.assertTrue(comm1.guards[0](vs, cs))
        self.assertFalse(comm2.guards[0](vs, cs))
        self.assertTrue(comm3.guards[0](vs, cs))

        self.assertTrue(callable(comm3.prob))
        self.assertEqual(comm3.prob(), 11)




