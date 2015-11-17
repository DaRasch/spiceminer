# -*- coding: utf-8 -*-

# The integration of c-code seems to cause failures so we need to mock up the
# wrapper module for the time beeing.
# Normally autodoc should be able to help us here, but it seems uncooperative.
import os
import re
import ast
import shutil

def _rebuild_imports(tree, indent=0):
    indent_string = ' ' * indent
    def rebuild_as(imp):
        for name in imp.names:
            if name.asname is not None:
                yield '{n.name} as {n.asname}'.format(n=name)
            else:
                yield '{n.name}'.format(n=name)
    for imp in tree.body:
        if isinstance(imp, ast.Import):
            names = ', '.join(rebuild_as(imp))
            yield '{}import {}\n'.format(indent_string, names)
        elif isinstance(imp, ast.ImportFrom):
            names = ', '.join(rebuild_as(imp))
            yield '{}from {}{} import {}\n'.format(indent_string, '.' * imp.level, imp.module or '', names)

def _rebuild_functions(tree, indent=0):
    indent_string = ' ' * indent
    for func in tree.body:
        if isinstance(func, ast.FunctionDef):
            for item in func.decorator_list:
                yield '{}@{}\n'.format(indent_string, item.id)
            try:
                args = ', '.join([item.id for item in func.args.args])
            except AttributeError:
                # In python3 it's arg.arg and not Name.id
                args = ', '.join([item.arg for item in func.args.args])
            yield '{}def {}({}):\n'.format(indent_string, func.name, args)
            yield '{}pass\n'.format(' ' * (indent + 1))

def _rebuild_classes(tree, indent=0):
    indent_string = ' ' * indent
    for cls in tree.body:
        if isinstance(cls, ast.ClassDef):
            for item in cls.decorator_list:
                yield '{}@{}\n'.format(indent_string, item.id)
            bases = ', '.join([b.id for b in cls.bases] or ['object'])
            yield 'class {}({}):\n'.format(cls.name, bases)
            yield '{}pass\n'.format(' ' * (indent + 1))
            for imp in _rebuild_imports(cls, indent + 1):
                yield imp
            for cls_ in _rebuild_classes(cls, indent + 1):
                yield cls_
            for func in _rebuild_functions(cls, indent + 1):
                yield func


def mockup(origin, target, *mockfiles):
    mockdir = os.path.join(target, os.path.basename(origin))
    shutil.rmtree(mockdir, ignore_errors=True)
    shutil.copytree(origin, mockdir, ignore=shutil.ignore_patterns('*.pyc', '*.so', '__*__'))
    for fname in mockfiles:
        with open(os.path.join(mockdir, fname), 'rt') as f:
            tree = ast.parse(f.read())
        with open(os.path.join(mockdir, fname), 'wt') as f:
            f.writelines(_rebuild_imports(tree))
            f.writelines(_rebuild_classes(tree))
            f.writelines(_rebuild_functions(tree))
    return mockdir

def find_version(filepath):
    with open(filepath) as f:
        return re.search("__version__ = '([^']+)'", f.read()).group(1)
