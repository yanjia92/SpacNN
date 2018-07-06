import ply.yacc as yacc
from LTLLexer import LTLLexer
from collections import namedtuple
import os
import copy
from util.BinaryTreeUtils import BT_level_traverse
TreeNode = namedtuple("TreeNode", ["object", "left", "right"])


class LTLParser(object):
    def __init__(self):
        self.lexer = LTLLexer()
        self.tokens = self.lexer.tokens
        self.parser = None
        self.parsed_results = list()

    def p_statement(self, p):
        '''statement : path_statement
                     | state_statement'''
        pass

    def p_path_statement(self, p):
        '''path_statement : state_statement UNTIL state_statement'''
        left = p[1]
        right = p[3]
        p[0] = TreeNode("U", left, right)
        self.parsed_results.append(BT_level_traverse(p[0]))

    def p_path_statement1(self, p):
        '''path_statement : NEXT state_statement'''
        p[0] = TreeNode("X", p[2], None)

    def p_path_statement2(self, p):
        '''path_statement : state_statement UNTIL LT NUM state_statement
                          | state_statement UNTIL LE NUM state_statement'''
        left = p[1]
        right = p[5]
        num = p[4]
        p[0] = TreeNode("U[0, {}]".format(num), left, right)
        self.parsed_results.append(BT_level_traverse(p[0]))

    def p_state_statement(self, p):
        '''state_statement : ap'''
        p[0] = p[1]

    def p_state_statement3(selfs, p):
        '''state_statement : state_statement AND ap'''
        left = p[1]
        right = p[3]
        p[0] = TreeNode("&", left, right)

    def p_state_statement4(self, p):
        '''state_statement : state_statement OR ap'''
        left = p[1]
        right = p[3]
        p[0] = TreeNode("|", left, right)

    def p_state_statement5(self, p):
        '''state_statement : NOT state_statement'''
        p[0] = TreeNode("!", p[2], None)

    def p_state_statement6(self, p):
        '''state_statement : path_statement'''
        print "state_statement can not be path_statement for now"

    def p_ap(self, p):
        '''ap : NAME
              | TRUE
              | FALSE'''
        p[0] = TreeNode(p[1], None, None)

    def build_parser(self):
        self.parser = yacc.yacc(module=self)
        return self

    def parse_file(self, path):
        if not os.path.exists(path):
            print "ltl file not exists."
            exit(1)
        with open(path, "r") as f:
            for line in f:
                self.parser.parse(line, lexer=self.lexer.lexer)
        return self._get_parsed_result()

    def parse_line(self, ltl_str):
        self.parser.parse(ltl_str, lexer=self.lexer.lexer)
        return self._get_parsed_result(index=0)

    def _get_parsed_result(self, index=None):
        if index is not None:
            result = self.parsed_results.pop(index)
            self._clear_results()
            return result
        results = copy.copy(self.parsed_results)
        self._clear_results()
        return results

    def _clear_results(self):
        while len(self.parsed_results) > 0:
            self.parsed_results.pop(0)


def main():
    parser = LTLParser().build_parser()
    print parser.parse_file("../../prism_model/LTLTest.props")


if __name__ == "__main__":
    main()