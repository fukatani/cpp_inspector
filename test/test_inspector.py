import os
import unittest

from src import cpp_inspector

class TestRule(unittest.TestCase):
    def test_valuable_rule(self):
        errs = cpp_inspector.inspect(os.path.abspath('./variable_rules.cc'))
        self.assertEqual(errs[0].line_num, 4)
        self.assertEqual(errs[1].line_num, 5)
        self.assertEqual(errs[2].line_num, 6)
        self.assertEqual(errs[3].line_num, 8)
        self.assertEqual(errs[4].line_num, 9)
        self.assertEqual(errs[5].line_num, 10)

    def test_other_rule(self):
        errs = cpp_inspector.inspect(os.path.abspath('./other_rules.cc'))
        self.assertEqual(errs[0].line_num, 5)
        self.assertEqual(errs[1].line_num, 6)
        self.assertEqual(errs[2].line_num, 9)

    def test_field(self):
        errs = cpp_inspector.inspect(os.path.abspath('./field_rules.cc'))
        self.assertEqual(errs[0].line_num, 6)
        self.assertEqual(errs[1].line_num, 7)
        self.assertEqual(errs[2].line_num, 3)


if __name__ == '__main__':
    unittest.main()