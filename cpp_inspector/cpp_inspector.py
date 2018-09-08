#!/usr/bin/env python3

import sys

import clang.cindex
from clang.cindex import Index
from clang.cindex import Config


def print_node_tree(node):
    print("%s : %s" % (node.kind.name, node.displayname))
    for child in node.get_children():
        print_node_tree(child)


class RuleBase(object):

    def __init__(self):
        self.errors = []
        self.check_methods = []

    def check_all_rules(self, ast):
        for check_method in self.check_methods:
            check_method(ast)

    def iter_for_all_element(self, ast):
        raise NotImplementedError()

    def check_one_element(self, elem):
        raise NotImplementedError()


class ClassRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_data_member_accesibility)
        self.check_methods.append(self.check_naming)

    def iter_for_all_element(self, ast):
        for elem in ast:
            if 'CXXRecordDecl' in elem:
                yield elem

    def check_data_member_accesibility(self, elem):
        'AccessSpecDecl' == 'public'
        "FieldDecl"

    def check_naming(self, elem):
        if elem.name[0].upper() == elem.name[0]:
            self.errors.append(elem)
        if '_' in elem:
            self.errors.append(elem)


class FunctionRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_const)
        self.check_methods.append(self.check_naming)
        self.check_methods.append(self.check_arguments)
        self.check_methods.append(self.check_arguments_order)

    def iter_for_all_element(self, ast):
        for elem in ast:
            if 'FunctionDecl' in elem:
                yield elem

    def check_naming(self, elem):
        if elem.name[0].upper() == elem.name[0]:
            self.errors.append(elem)
        if '_' in elem:
            self.errors.append(elem)

    def check_const(self, elem):
        var_list = []
        for elem2 in elem:
            if elem == 'VarDecl' and elem != 'const':
                var_list.append(elem2)
        reassignment_list = []
        for elem2 in elem:
            if elem == 'DeclRefExpr':
                reassignment_list.append(elem2)
        for elem2 in elem:
            if elem2 == 'CallExpr':
                if elem2.arg == 'RefExpr':
                    reassignment_list.append(elem2)

        for var in var_list:
            if var not in reassignment_list:
                self.errors.append(var)

    def check_arguments(self, elem):
        for parm in elem:
            if 'ParmVarDecl' in parm:
                if parm.startswith('const') and parm[-1] != '&' and \
                        'int' not in parm:
                    self.errors.append(parm)
                if parm[-1] == '&' and not parm.startswith('const'):
                    self.errors.append(parm)

    def check_arguments_order(self, elem):
        pointer_found = False
        for parm in elem:
            if 'ParmVarDecl' in parm:
                if pointer_found and not parm.is_pointer:
                    self.errors.append(parm)
                if parm.is_pointer:
                    pointer_found = True


class FieldRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_naming)

    def iter_for_all_element(self, ast):
        for elem in ast:
            if 'FieldDecl' in elem:
                yield elem

    def check_naming(self, elem):
        if elem.lower() != elem.lower():
            self.errors.append(elem)
        if not elem.endswith('_'):
            self.errors.append(elem)


class GlovalVariableRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_naming)
        self.check_methods.append(self.check_type)

    def iter_for_all_element(self, ast):
        for elem in ast.childs:
            yield elem

    def check_naming(self, elem):
        if elem.name[0].upper() == elem.name[0]:
            self.errors.append(elem)
        if '_' in elem:
            self.errors.append(elem)

    def check_type(self, elem):
        if elem.type not in ('int', 'size_t', 'bool', 'char', 'float', 'double'):
            self.errors.append(elem)


class LocalVarialeRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_naming)

    def iter_for_all_element(self, ast):
        for elem in ast:
            if 'VarDecl' in elem:
                yield elem

    def check_naming(self, elem):
        if 'const' and 'constexpr':
            if elem.name[0].upper() == elem.name[0]:
                self.errors.append(elem)
        else:
            if elem.lower() != elem.lower():
                self.errors.append(elem)

        if not elem.endswith('_'):
            self.errors.append(elem)


class UnaryOperatorRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_prefix)

    def iter_for_all_element(self, ast):
        for elem in ast:
            if 'UnaryOperator' in elem:
                yield elem

    def check_prefix(self, elem):
        if "prefix '++'":
            if elem.lvalue == 'int' or elem.lvalue == 'size_t':
                self.elem.append(elem)


class UnaryExprOrTypeTraitExprRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_cast_target)

    def iter_for_all_element(self, ast):
        for elem in ast:
            if 'UnaryExprOrTypeTraitExpr' in elem:
                yield elem

    def check_cast_target(self, elem):
        if elem.sizeof == 'int':
            self.elem.append(elem)


class CStyleCastExprRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_cstylecast)

    def iter_for_all_element(self, ast):
        for elem in ast:
            if 'CStyleCastExpr' in elem:
                yield elem

    def check_cstylecast(self, elem):
        self.append(elem)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./cpp_inspector.py your_code.cpp")
    index = Index.create()
    tu = index.parse(sys.argv[1])
    print_node_tree(tu.cursor)
    rule_classes = (ClassRule, FunctionRule, FieldRule, GlovalVariableRule,
             LocalVarialeRule, UnaryOperatorRule, UnaryExprOrTypeTraitExprRule,
             CStyleCastExprRule)
    for rule_class in rule_classes:
        rule = rule_class()
        rule.check_all_rules(tu.cursor)
        print(rule.errors)
