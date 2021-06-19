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
    print(ast)
    if is_boolean(ast):
        return ast
    if is_integer(ast):
        return ast
    if is_string(ast):
        return ast
    if is_symbol(ast):
        return env.lookup(ast)
    if is_list(ast):
        if len(ast) == 0:
            raise DiyLangError("Empty list")
        if ast[0] == "quote":
            if len(ast[1:]) != 1:
                raise DiyLangError(f"Wrong number of arguments in {ast[0]}")
            return ast[1]
        if ast[0] == "atom":
            if len(ast[1:]) != 1:
                raise DiyLangError(f"Wrong number of arguments in {ast[0]}")
            result = evaluate(ast[1], env)
            return is_atom(result)
        if ast[0] == "eq":
            if len(ast[1:]) != 2:
                raise DiyLangError(f"Wrong number of arguments in {ast[0]}")
            left = evaluate(ast[1], env)
            right = evaluate(ast[2], env)
            if not is_atom(left) or not is_atom(right):
                return False
            return left == right
        if ast[0] in ["+", "-", "/", "*", "mod", ">"]:
            if len(ast[1:]) != 2:
                raise DiyLangError(f"Wrong number of arguments in {ast[0]}")
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
            if len(ast[1:]) != 3:
                raise DiyLangError(f"Wrong number of arguments in {ast[0]}")
            predicate = evaluate(ast[1], env)     
            if predicate:
                return evaluate(ast[2], env)
            else:
                return evaluate(ast[3], env)
        if ast[0] == "define":
            if len(ast[1:]) != 2:
                raise DiyLangError(f"Wrong number of arguments in {ast[0]}")
            left = ast[1]
            if not is_symbol(left):
                raise DiyLangError(f"{left} is not a symbol")
            right = evaluate(ast[2], env)
            env.set(left, right)
            return
        if ast[0] == "cons":
            head = evaluate(ast[1], env)
            tail = evaluate(ast[2], env)
            if is_list(tail):
                return [head] + tail
            if is_string(tail):
                return String(head.val + tail.val)
            raise DiyLangError("Can't use cons on a non list/string")
        if ast[0] == "head":
            list_ = evaluate(ast[1], env)
            if is_list(list_):
                if len(list_) == 0:
                    raise DiyLangError("Can't use head on empty list")
                return list_[0]
            if is_string(list_):
                if len(list_.val) == 0:
                    raise DiyLangError("Can't use head on empty string")
                return String(list_.val[0])
            raise DiyLangError("Can't use head on a non list/string")
        if ast[0] == "tail":
            list_ = evaluate(ast[1], env)
            if is_list(list_):
                if len(list_) == 0:
                    raise DiyLangError("Can't use tail on empty list")
                return list_[1:]
            if is_string(list_):
                if len(list_.val) == 0:
                    raise DiyLangError("Can't use tail on empty string")
                return  String(list_.val[1:])
            raise DiyLangError("Can't use tail on a non list/string")
        if ast[0] == "empty":
            list_ = evaluate(ast[1], env)
            if is_list(list_):
                return len(list_) == 0
            if is_string(list_):
                return len(list_.val) == 0
            raise DiyLangError("Can't use empty on a non list/string")
        if ast[0] == "cond":
            cases = ast[1]
            for (condition, value) in cases:
                if evaluate(condition, env):
                    return evaluate(value, env)
            return False
        if ast[0] == "let":
            new_env = env
            for (key, value) in ast[1]:
                evaluated_value = evaluate(value, new_env)
                new_env = new_env.extend({
                    key: evaluated_value
                })
            return evaluate(ast[2], new_env)
        if ast[0] == "defn":
            return evaluate(["define", ast[1], ["lambda", ast[2], ast[3]]], env)
        if ast[0] == "lambda":
            if len(ast[1:]) != 2:
                raise DiyLangError(f"Wrong number of arguments in {ast[0]}")
            params = ast[1]
            if not is_list(params):
                raise DiyLangError(f"{params} is not a list")
            for param in params:
                if not is_symbol(param):
                    raise DiyLangError(f"{param} is not a symbol")
            body = ast[2]
            return Closure(env, params, body)
        if is_closure(ast[0]):
            closure = ast[0]
            args = ast[1:]
            return evaluate_closure(closure, args, env)
        if is_list(ast[0]):
            closure = evaluate(ast[0], env)
            args = ast[1:]
            return evaluate_closure(closure, args, env)
        function_name = ast[0]
        if not is_symbol(function_name):
            raise DiyLangError(f"{function_name} is not a function")
        closure = env.lookup(function_name)
        if not is_closure(closure):
            raise DiyLangError(f"{closure} is not a function")
        args = ast[1:]
        return evaluate_closure(closure, args, env)

def evaluate_closure(closure, args, env):
    num_params = len(closure.params)
    num_args = len(args)
    if num_args != num_params:
        raise DiyLangError(f"wrong number of arguments, expected {num_params} got {num_args}")
    evaluated_args = [evaluate(arg, env) for arg in args]
    new_vars = dict(zip(closure.params, evaluated_args))
    new_env = closure.env.extend(new_vars)
    return evaluate(closure.body, new_env)