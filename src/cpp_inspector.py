#!/usr/bin/env python3

import os
import re
import subprocess
import sys


def walk_tree(node):
    # print("yield", node.kind, node.displayname)
    for child in node.get_children():
        yield from walk_tree(child)
    yield node


class StyleError(object):

    def __init__(self, line_num, kind, contents, url):
        self.kind = kind
        self.line_num = line_num
        self.url = url
        self.contents = contents

    def to_string(self):
        return ("line %d: " % self.line_num + self.contents +
                " https://google.github.io/styleguide/cppguide.html#%s" % self.url)


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
                err = StyleError(elem.line_num, elem.kind,
                                 "Data member should be private",
                                 "Access_Control")
                self.errors.append(err)

    def check_naming(self, elem):
        if elem.displayname[0].upper() != elem.displayname[0]:
            err = StyleError(elem.line_num, elem.kind,
                             "Class name should be camel case",
                             "Type_Names")
            self.errors.append(err)
        if '_' in elem.displayname:
            err = StyleError(elem.line_num, elem.kind,
                             "Class name should be camel case",
                             "Type_Names")
            self.errors.append(err)


class FunctionRule(RuleBase):

    def __init__(self):
        super().__init__()
        # self.check_methods.append(self.check_const)
        self.check_methods.append(self.check_naming)
        self.check_methods.append(self.check_arguments)
        self.check_methods.append(self.check_arguments_order)

    def iter_for_all_element(self, ast):
        for elem in walk_tree(ast):
            if elem.kind == 'FunctionDecl':
                yield elem

    def check_naming(self, elem):
        if elem.displayname[0].upper() != elem.displayname[0]:
            err = StyleError(elem.line_num, elem.kind,
                             "Function name should be camel case",
                             "Function_Names")
            self.errors.append(err)
        if '_' in elem.displayname:
            err = StyleError(elem.line_num, elem.kind,
                             "Function name should be camel case",
                             "Function_Names")
            self.errors.append(err)

    # TODO: not implemented
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

    # TODO: move to ParmVarDeclRule
    def check_arguments(self, elem):
        for node in elem.get_children():
            if node.kind == 'ParmVarDecl':
                if '&' in node.type and 'const' not in node.type:
                    err = StyleError(elem.line_num, elem.kind,
                                     "Reference arguments should be called with 'const'",
                                     "Variable_Names")
                    self.errors.append(err)

    def check_arguments_order(self, elem):
        pointer_found = False
        for node in elem.get_children():
            if node.kind == 'ParmVarDecl':
                if pointer_found and not node.is_pointer:
                    err = StyleError(elem.line_num, elem.kind,
                                     "Output arguments should be should appear after input parameters",
                                     "Output_Parameters")
                    self.errors.append(err)
                if '*' in node.type:
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
        if elem.displayname.lower() != elem.displayname:
            self.errors.append(elem)
        if not elem.displayname.endswith('_'):
            err = StyleError(elem.line_num, elem.kind,
                             "Data member name should end with '_'",
                             "Variable_Names")
            self.errors.append(err)


class GlobalVariableRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_naming)
        self.check_methods.append(self.check_type)

    def iter_for_all_element(self, ast):
        for elem in ast.get_children():
            if elem.kind == 'VarDecl' and elem.scope == 'global':
                yield elem

    def check_naming(self, elem):
        if 'const' in elem.type and elem.children[0].kind in ('IntegerLiteral', 'FloatingLiteral'):
            if len(elem.displayname) == 1 or elem.displayname.upper()[1].isupper() or \
                    elem.displayname.upper()[0] != "k":
                err = StyleError(elem.line_num, elem.kind,
                                 "Static const variable name should be camel case",
                                 "Variable_Names")
                self.errors.append(err)
        else:
            if elem.displayname.lower() != elem.displayname.lower():
                err = StyleError(elem.line_num, elem.kind,
                                 "Local variable name should be all lowercase",
                                 "Variable_Names")
                self.errors.append(err)
        if elem.displayname.endswith('_'):
            err = StyleError(elem.line_num, elem.kind,
                             "Local variable name should not end with '_'",
                             "Variable_Names")
            self.errors.append(err)

    # TODO: this is no strict check. struct should be allowed.
    def check_type(self, elem):
        if elem.type not in ('int', 'size_t', 'bool', 'char', 'float', 'double'):
            err = StyleError(elem.line_num, elem.kind,
            "Objects with static storage duration are forbidden",
            "Static_and_Global_Variables")
            self.errors.append(err)


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
            if len(elem.displayname) == 1 or elem.displayname[1].islower() or \
                    elem.displayname[0] != "k" or '_' in elem.displayname:
                err = StyleError(elem.line_num, elem.kind,
                                 "Static const variable name should be like `kConstValue`",
                                 "Variable_Names")
                self.errors.append(err)
        else:
            if elem.displayname.lower() != elem.displayname:
                err = StyleError(elem.line_num, elem.kind,
                                 "Local variable name should be all lowercase",
                                 "Variable_Names")
                self.errors.append(err)
        if elem.displayname.endswith('_'):
            err = StyleError(elem.line_num, elem.kind,
                             "Local variable name should not end with '_'",
                             "Variable_Names")
            self.errors.append(err)


class UnaryOperatorRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_prefix)

    def iter_for_all_element(self, ast):
        for elem in walk_tree(ast):
            if elem.kind == 'UnaryOperator':
                yield elem

    def check_prefix(self, elem):
        if elem.displayname == "postfix '++'" or elem.displayname == "postfix '--'":
            if elem.type not in ("'int'", "'size_t'"):
                err = StyleError(elem.line_num, elem.kind,
                                 "Use prefix form (++i) of the increment and decrement operators with iterators and other template objects.",
                                 "Preincrement_and_Predecrement")
                self.errors.append(err)


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
            err = StyleError(elem.line_num, elem.kind,
                             "Prefer sizeof(varname) to sizeof(type)",
                             "sizeof")
            self.errors.append(err)

class CStyleCastExprRule(RuleBase):

    def __init__(self):
        super().__init__()
        self.check_methods.append(self.check_cstylecast)

    def iter_for_all_element(self, ast):
        for elem in walk_tree(ast):
            if elem.kind == 'CStyleCastExpr':
                yield elem

    def check_cstylecast(self, elem):
        err = StyleError(elem.line_num, elem.kind,
                         "Use C++ style cast 'static_cast<int>' instead of C style cast '(int)' )",
                         "Casting")
        self.errors.append(err)


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
        elif self.kind == 'VarDecl':
            if 'global_var' in line:
                self.scope = 'global'
            else:
                self.scope = 'local'
            self.type = re.search(r"'[a-zA-Z\ \*\&]+'", line).group().replace("'", "")
            words = line[:line.find("'")].split(' ')
            self.displayname = words[-2]
        elif self.kind == 'CXXRecordDecl':
            self.displayname = words[-2]
        elif self.kind == 'AccessSpecDecl':
            self.displayname = words[-1].replace("'", "")
        elif self.kind == 'FunctionDecl':
            words = line[:line.find("'")].split(' ')
            self.displayname = words[-2]
            if self.displayname in ('new', 'delete', 'new[]', 'delete[]'):
                self.kind = 'NotInspetTarget'
        elif self.kind == 'ParmVarDecl':
            self.type = re.search(r"'[a-zA-Z\ \*\&]+'", line).group()
            words = line[:line.find("'")].split(' ')
            self.displayname = words[-2]
        else:
            self.displayname = ' '.join(words[1:])

        if 'line:' in line:
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


def inspect(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError("File %s is not found" % filename)
    command = ("clang", "-Xclang", "-ast-dump", "-fno-diagnostics-color", filename)
    try:
        dump_result = subprocess.check_output(command)
    except subprocess.CalledProcessError as e:
        dump_result = e.output
    tree = make_tree(dump_result.decode())

    rule_classes = (FieldRule, FunctionRule,
                    CStyleCastExprRule, UnaryExprOrTypeTraitExprRule,
                    UnaryOperatorRule, LocalVarialeRule, GlobalVariableRule,
                    ClassRule)

    errors = []
    for rule_class in rule_classes:
        rule = rule_class()
        rule.check_all_rules(tree)
        for error in rule.errors:
            errors.append(error)
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./cpp_inspector.py your_code.cpp")
        exit(1)
    [print(error.to_string()) for error in inspect(sys.argv[1])]
