# -*- coding:utf-8 -*-
from checker.Checker import BoundedInterval


class LTLChecker(object):
    '''
    A LTL formula checker that supports bounded until, next LTL formula
    '''
    AND_TOKEN = '&'
    OR_TOKEN = '|'
    NOT_TOKEN = '!'
    UNTIL_TOKEN = 'U'
    NEXT_TOKEN = 'X'
    TRUE_TOKEN = 'true'

    def check(self, path, formula):
        '''
        check whether a path satisfy the given formula
        :param path: list of AnotherStep instance
        :param formula: a parsed LTL formula
        :return: boolean
        '''
        return path[0] in self._check(path, formula, 0)

    def _check(self, path, formula, index):
        '''
        recursively check method
        :param path: list of AnotherStep instance
        :param formula: a parsed ltl formula
        :param index: the index pointing to the current checked ltl token
        :return: steps(set) that satisfy the formula
        '''
        if len(path) == 0 or not formula:
            return set([])
        if index >= len(formula):
            return set([])
        token = formula[index]
        if token == self.AND_TOKEN:
            return self._check(path, formula, 2*index+1).intersection(self._check(path, formula, 2*index+2))
        elif token == self.OR_TOKEN:
            return self._check(path, formula, 2*index+1).union(self._check(path, formula, 2*index+2))
        elif token == self.NOT_TOKEN:
            return set(path).difference(self._check(path, formula, 2*index+1))
        elif token.startswith(self.UNTIL_TOKEN):
            interval = BoundedInterval.parse_literal(token[1:])
            return self._check_until(path, self._check(path, formula, 2*index+1), self._check(path, formula, 2*index+2), interval)
        elif token == self.NEXT_TOKEN:
            ans = set([])
            next_steps = self._check(path, formula, 2*index+1)
            for step in next_steps:
                if path.index(step) <= 0:
                    continue
                ans.add(path[path.index(step)-1])
            return ans
        else:
            # token is some ap
            if token == self.TRUE_TOKEN:
                return set(path)
            return set([step for step in path if token in step.get_ap_set()])

    def _check_until(self, path, steps1, steps2, interval):
        '''
        check formula like y1 U[d1,d2] y2
        :param path: list of AnotherStep instance
        :param steps1: steps satisfying y1
        :param steps2: steps satisfying y2
        :param interval: BoundedInterval instance
        :return: steps that satisfying y1 U[d1,d2] y2
        '''
        ans = set([])
        flag = False # whether a y2-step is found
        for step in path[::-1]:
            if flag:
                if step in steps1:
                    ans.add(step)
                else:
                    flag = False
            else:
                if step in steps2 and interval.contains(step.get_passed_time()):
                    flag = True
                    ans.add(step)
        return ans



