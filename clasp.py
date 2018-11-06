#!/usr/bin/env python3
from collections import namedtuple, ChainMap
from functools import reduce
import cmd
import sys

Node = namedtuple('Node', ['parent', 'childs'])

pyeval = eval


class SyntaxException(Exception):
    def __init__(self, msg, line=None, char=None):
        if line is not None:
            msg = "%s at position %s:%s" % (msg, line, char)
        super(Exception, self).__init__(msg)


def make_token(word):
    try:
        return int(word)
    except ValueError:
        try:
            return float(word)
        except ValueError:
            return word


def tokenize(code):
    word = None
    line, char = 1, 1
    reading_string = False
    string = None
    it = iter(code)
    while True:
        try:
            c = next(it)
        except StopIteration:
            return

        if c == ';':
            while c != '\n':
                c = next(it)
            continue
        if c == '"':
            if not reading_string:
                reading_string, string = True, '"'
            else:
                string += '"'
                yield make_token(string), (line, char)
                reading_string, string = False, None
        elif reading_string:
            string += c
        elif c == ' ' or c == '(' or c == ')':
            if word is not None:
                yield make_token(word), (line, char)
                word = None
            if c != ' ':
                yield c, (line, char)
        elif c == '\n':
            line += 1
            char = 1
        else:
            word = c if word is None else word + c
        char += 1


def parse(code):
    current = Node(parent=None, childs=[])
    open_par = 0
    for token, (line, char) in tokenize(code):
        if token == '(':
            open_par += 1
            new_leaf = Node(parent=current, childs=[])
            current.childs.append(new_leaf)
            current = new_leaf
        elif token == ')':
            open_par -= 1
            if current.parent is None:
                raise SyntaxException("Unexpected )", line, char)
            current = current.parent
        else:
            current.childs.append(token)
    if open_par != 0:
        raise SyntaxException("Unclosed parenthesis.", line, char)
    return current


def tree_to_list(root):
    list = []
    for child in root.childs:
        if isinstance(child, Node):
            list.append(tree_to_list(child))
        else:
            list.append(child)
    return list


def raise_function(msg):
    raise Exception(msg)


default_env = {
    '+': lambda a, b: a + b,
    '*': lambda a, b: a * b,
    '>': lambda a, b: a > b,
    '<': lambda a, b: a < b,
    '>=': lambda a, b: a >= b,
    '<=': lambda a, b: a <= b,
    'not': lambda x: not x,
    'and': lambda a, b: a and b,
    'or': lambda a, b: a or b,
    'begin': lambda *x: x[-1],
    'print': lambda *x: print(*x),
    'len': len,
    'at': lambda l, i: l[i],
    'list': lambda *l: list(l),
    'list?': lambda l: isinstance(l, list),
    'head': lambda l: l[0],
    'tail': lambda l: l[1:],
    'cons': lambda x, l: [x] + l,
    'reduce': lambda l, f: reduce(f, l),
    'eq?': lambda a, b: a == b,
    'procedure?': lambda x: callable(x),
    'raise': raise_function,
    'py': lambda exp: pyeval(exp[1:-1]),
    'load': lambda file: run_file(file)
}


def pairwise(l):
    it = iter(l)
    while True:
        yield next(it), next(it)


def eval(exp, env):
    if isinstance(exp, int) or isinstance(exp, float):
        return exp
    elif isinstance(exp, str):
        if exp[0] == '"' and exp[-1] == '"':
            return exp[1:-1]
        elif exp == "True":
            return True
        elif exp == "False":
            return False
        else:
            # it's a variable
            return env[exp]

    op, args = exp[0], exp[1:]
    # print("op:%s args:%s" % (op, args))

    if op == 'def':
        name, defexp = args
        if name in env:
            raise SyntaxException("%s already defined" % name)
        env[name] = eval(defexp, env)
        return None
    elif op == 'let':
        pairs, body = args
        let_env = {}
        for name, name_exp in pairwise(pairs):
            if name in env:
                raise SyntaxException("%s already defined" % name)
            let_env[name] = eval(name_exp, ChainMap(let_env, env))
        return eval(body, ChainMap(let_env, env))
    elif op == 'set!':
        name, set_exp = args
        if name not in env:
            raise SyntaxException("%s not defined before set!." % name)
        env[name] = eval(set_exp, env)
        return None
    elif op == 'if':
        if len(args) == 2:
            test, conseq = args
            if eval(test, env):
                return eval(conseq, env)
        elif len(args) == 3:
            test, conseq, alt = args
            expr = conseq if eval(test, env) else alt
            return eval(expr, env)
    elif op == 'lambda' or op == '=>':
        params, body = args

        def local_lambda(*lambda_args):
            # ChainMap(x, overwritten_by_x)
            lambda_env = ChainMap(dict(zip(params, lambda_args)), env)
            return eval(body, lambda_env)

        return local_lambda
    elif op == 'while':
        cond, expr = args
        while eval(cond, env):
            eval(expr, env)
        return
    elif op == 'str':
        return ''.join([eval(arg, env) for arg in args])
    else:
        if op not in env:
            raise SyntaxException("Function %s not defined." % op)
        args = [eval(arg, env) for arg in args]

        if callable(env[op]):
            return env[op](*args)


def eval_tree(tree):
    ret = None
    for p in tree_to_list(tree):
        ret = eval(p, default_env)
    return ret


def run(code):
    tree = parse(code)
    return eval_tree(tree)


def run_file(file_path):
    f = open(file_path, "r")
    code = f.read()
    run(code)
    print("File %s executed." % file_path)


def repl():
    class Repl(cmd.Cmd):
        intro = 'Welcome to Clasp REPL\n'
        prompt = '> '
        file = None

        def onecmd(self, line):
            try:
                print(run(line))
            except Exception as e:
                print(e)

    Repl().cmdloop()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Clasp interpreter. Usage:")
        print("$ ./clasp.py repl")
        print("$ ./clasp.py file.clasp")
        sys.exit(0)
    if sys.argv[1] == 'repl':
        repl()
    else:
        run_file(sys.argv[1])
