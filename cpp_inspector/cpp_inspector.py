#!/usr/bin/env python3

import re
import subprocess
import sys


def walk_tree(node):
    # print("yield", node.kind, node.displayname)
    for child in node.get_children():
        yield from walk_tree(child)
    yield node


class RuleBase(object):

    def __init__(self):
        self.errors = []
        self.check_methods = []

    def check_all_rules(self, ast):
        for check_method in self.check_methods:
            for elem in self.iter_for_all_element(ast):
                check_method(elem)

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
        for elem in ast.get_children():
            if elem.kind == 'CXXRecordDecl':
                yield elem

    def check_data_member_accesibility(self, elem):
        current_accesibility = 'public'
        for elem in elem.get_children():
            if elem.kind == 'AccessSpecDecl':
                current_accesibility = elem.displayname
            if elem.kind == "FieldDecl" and current_accesibility == 'public':
                self.errors.append(elem)

    def check_naming(self, elem):
        if elem.displayname[0].upper() != elem.displayname[0]:
            self.errors.append(elem)
        if '_' in elem.displayname:
            self.errors.append(elem)


class FunctionRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_const)
        self.check_methods.append(self.check_naming)
        self.check_methods.append(self.check_arguments)
        self.check_methods.append(self.check_arguments_order)

    def iter_for_all_element(self, ast):
        for elem in walk_tree(ast):
            if elem.kind == 'FunctionDecl':
                yield elem

    def check_naming(self, elem):
        if elem.name[0].upper() == elem.name[0]:
            self.errors.append(elem)
        if '_' in elem:
            self.errors.append(elem)

    def check_const(self, elem):
        var_list = []
        for elem2 in elem.get_children():
            if elem == 'VarDecl' and elem != 'const':
                var_list.append(elem2)
        reassignment_list = []
        for elem2 in elem.get_children():
            if elem == 'DeclRefExpr':
                reassignment_list.append(elem2)
        for elem2 in elem.get_children():
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
        for elem in walk_tree(ast):
            if elem.kind == 'FieldDecl':
                yield elem

    def check_naming(self, elem):
        if elem.displayname.lower() != elem.displayname.lower():
            self.errors.append(elem)
        if not elem.displayname.endswith('_'):
            self.errors.append(elem)


class GlovalVariableRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_naming)
        self.check_methods.append(self.check_type)

    def iter_for_all_element(self, ast):
        for elem in ast.get_children():
            if elem.kind == 'VarDecl' and elem.scope == 'gloval':
                yield elem

    def check_naming(self, elem):
        if 'const' in elem.type and elem.children[0].kind in ('IntegerLiteral', 'FloatingLiteral'):
            if elem.kind.upper() == elem.kind:
                self.errors.append(elem)
        else:
            if elem.kind.lower() != elem.kind.lower():
                self.errors.append(elem)
        if elem.kind.endswith('_'):
            self.errors.append(elem)

    def check_type(self, elem):
        if elem.type not in ('int', 'size_t', 'bool', 'char', 'float', 'double'):
            self.errors.append(elem)


class LocalVarialeRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_naming)

    def iter_for_all_element(self, ast):
        for elem in walk_tree(ast):
            if elem.kind == 'VarDecl' and elem.scope == 'local':
                yield elem

    def check_naming(self, elem):
        if 'const' in elem.type and elem.children[0].kind in ('IntegerLiteral', 'FloatingLiteral'):
            if elem.kind.upper() == elem.kind:
                self.errors.append(elem)
        else:
            if elem.kind.lower() != elem.kind.lower():
                self.errors.append(elem)
        if elem.kind.endswith('_'):
            self.errors.append(elem)


class UnaryOperatorRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_prefix)

    def iter_for_all_element(self, ast):
        for elem in walk_tree(ast):
            if elem.kind == 'UnaryOperator':
                yield elem

    def check_prefix(self, elem):
        if elem.displayname == "postfix '++'":
            if elem.type not in ("'int'", "'size_T'"):
                self.errors.append(elem)


class UnaryExprOrTypeTraitExprRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_cast_target)

    def iter_for_all_element(self, ast):
        for elem in walk_tree(ast):
            if elem.kind == 'UnaryExprOrTypeTraitExpr':
                yield elem

    def check_cast_target(self, elem):
        target = list(elem.get_children())
        if not target:
            self.errors.append(elem)


class CStyleCastExprRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_cstylecast)

    def iter_for_all_element(self, ast):
        for elem in walk_tree(ast):
            if elem.kind == 'CStyleCastExpr':
                yield elem

    def check_cstylecast(self, elem):
        self.errors.append(elem)


class Node(object):
    def __init__(self, line, parent):
        self.parent = parent
        words = line.split()
        self.scope = None
        self.kind = words[0]
        self.line_num = None
        if self.kind == 'FieldDecl':
            self.displayname = words[-2]
            self.type = words[-1]
        elif self.kind == 'UnaryOperator':
            self.displayname = ' '.join(words[-2:])
            self.type = words[-3]
            print(self.displayname, self.type)
        elif self.kind == 'VarDecl':
            if 'global_var' in line:
                self.scope = 'global'
            else:
                self.scope = 'local'
            self.type = re.search(r"'[a-zA-Z\ \*\&]+'", line).group()
            self.displayname = ' '.join(words[1:])
        elif self.kind == 'CXXRecordDecl':
            self.displayname = words[-2]
        elif self.kind == 'AccessSpecDecl':
            self.displayname = words[-1].replace("'", "")
        else:
            self.displayname = ' '.join(words[1:])
        # TODO
        if 'line:' in line:
            # r"('line:[0-9]*)'"
            match = re.search(r"line:[0-9]+", line)
            self.line_num = int(line[match.span()[0] + 5: match.span()[1]])
        self.children = []
        if self.line_num is None and self.parent is not None:
            self.line_num = self.parent.line_num

    def get_children(self):
        return self.children

    def add_children(self, node):
        self.children.append(node)


def make_tree(output):
    output = output.split("\n")
    for i, line in enumerate(output):
        if line.startswith("TranslationUnitDecl"):
            line_num = i
            break

    new_tree_ref_dict = {}
    root = Node(line, None)
    new_tree_ref_dict[0] = root
    for line in output[line_num + 1:]:
        # print(line)
        match = re.search(r'[A-Z]+', line)

        if match:
            # print(match.start())
            cur_nest = match.start() // 2
            assert cur_nest > 0
            parent = new_tree_ref_dict[cur_nest - 1]
            cur_node = Node(line[match.start():], parent)
            parent.add_children(cur_node)
            new_tree_ref_dict[cur_nest] = cur_node
    return root


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./cpp_inspector.py your_code.cpp")
    print(sys.argv[1])

    command = ("clang", "-Xclang", "-ast-dump", "-fno-diagnostics-color", sys.argv[1])
    try:
        dump_result = subprocess.check_output(command)
    except subprocess.CalledProcessError as e:
        dump_result = e.output
    tree = make_tree(dump_result.decode())

    rule_classes = (FieldRule,
                    CStyleCastExprRule, UnaryExprOrTypeTraitExprRule,
                    UnaryOperatorRule, LocalVarialeRule, GlovalVariableRule,
                    ClassRule)
    for rule_class in rule_classes:
        rule = rule_class()
        rule.check_all_rules(tree)
        print("errors:")
        for error in rule.errors:
            print(error.line_num, error.kind, error.displayname)
