# -*- coding: utf-8 -*-

from .types import Environment, DiyLangError, Closure, String
from .ast import is_boolean, is_atom, is_symbol, is_list, is_closure, \
    is_integer, is_string
from .parser import unparse

"""
This is the Evaluator module. The `evaluate` function below is the heart
of your language, and the focus for most of parts 2 through 6.

A score of useful functions is provided for you, as per the above imports,
making your work a bit easier. (We're supposed to get through this thing
in a day, after all.)
"""

def evaluate(ast, env):
    """Evaluate an Abstract Syntax Tree in the specified environment."""
    if is_boolean(ast):
        return ast
    if is_integer(ast):
        return ast
    if is_symbol(ast):
        return env.lookup(ast)
    if is_list(ast):
        if ast[0] == "quote":
            return ast[1]
        if ast[0] == "atom":
            result = evaluate(ast[1], env)
            return is_atom(result)
        if ast[0] == "eq":
            left = evaluate(ast[1], env)
            right = evaluate(ast[2], env)
            if not is_atom(left) or not is_atom(right):
                return False
            return left == right
        if ast[0] in ["+", "-", "/", "*", "mod", ">"]:
            left = evaluate(ast[1], env)
            right = evaluate(ast[2], env)
            if not is_integer(left) or not is_integer(right):
                raise DiyLangError(f"{left} or {right} is not a number")
            if ast[0] == "+":
                return left + right
            if ast[0] == "-":
                return left - right
            if ast[0] == "/":
                return left // right
            if ast[0] == "*":
                return left * right
            if ast[0] == "mod":
                return left % right
            if ast[0] == ">":
                return left > right
        if ast[0] == "if":
            predicate = evaluate(ast[1], env)     
            if predicate:
                return evaluate(ast[2], env)
            else:
                return evaluate(ast[3], env)
        if ast[0] == "define":
            if len(ast[1:]) != 2:
                raise DiyLangError("Wrong number of arguments")
            left = ast[1]
            if not is_symbol(left):
                raise DiyLangError(f"{left} is not a symbol")
            right = evaluate(ast[2], env)
            env.set(left, right)
            
            