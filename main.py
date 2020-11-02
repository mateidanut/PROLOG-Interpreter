#! /usr/bin/python3
import re
from pprint import pprint
from MateiGabrielDanut22_utils import *
from itertools import compress
from sys import argv

kb = []
kb_uniq = False
interogs = []

def printTree(token, indent=0):
    if type(token) is str:
        print('  ' * indent + token)
        return

    elif type(token) is list:
        for x in token:
            printTree(x, indent)

    else:
        print('  ' * indent + token[0])
        for x in token[1:]:
            printTree(x, indent + 1)


def getLine(text : str):
    token, rest = getAffirm(text)
    if token:
        return token

    token, rest = getInter(text)

    if token:
        return token

    token, rest = getComm(text)

    if token:
        return token

    return None


def getAffirm(text : str):
    global kb
    token, rest = getAtom(text)
    if token:
        if rest and rest[0] == ':':
            token2, rest = getCond(rest[1:].strip())
            # add to kb
            add_statement(kb, token, *token2)
            return token, rest.strip()
        else:
            # add to kb
            add_statement(kb, token)
            return token, rest.strip()

    return None, text


def getAtom(text : str):
    token, rest = getName(text)

    if token:
        if rest[0:2] == '()':
            return make_atom(token), rest[2:].strip()
        elif rest[0] == '(':
            token2, rest = getTerms(rest[1:].strip())
            if token and rest[0] == ')':
                return make_atom(token, *token2), rest[1:].strip()
    return None, text


def getName(text : str):
    match = re.match('[A-Za-z0-9_]+', text)
    if match:
        token = match.group(0)
        rest = text[len(token):]

        return token, rest.strip()

    return None, text


def getTerms(text : str):
    token, rest = getTerm(text)

    tokens = [token]
    while rest and rest[0] == ',':
        token, rest = getTerm(rest[1:].strip())
        tokens.append(token)

    return tokens, rest.strip()


def getTerm(text : str):
    token, rest = getFunc(text)
    if token:
        return token, rest.strip()

    token, rest = getVar(text)
    if token:
        return token, rest.strip()

    token, rest = getConst(text)
    if token:
        return token, rest.strip()

    return None, text


def getConst(text : str):
    token, rest = getNumber(text)
    if token:
        return make_const(token), rest.strip()

    match = re.match('[A-Za-z][A-Za-z0-9_]*', text)
    if match:
        token = match.group(0)
        rest = text[len(token):]

        return make_const(token), rest.strip()

    return None, text


def getVar(text : str):
    if text and text[0] == '?':
        token, rest = getName(text[1:].strip())
        if token:
            return make_var(token), rest.strip()

    return None, text


def keep_relevant_substs(subst, interog):
    to_keep = list(map(is_variable, get_args(interog)))
    interog_values = list(map(lambda x: x['val'], list(subst.values())[:len(to_keep)][::-1]))
    interog_values_to_keep = list(compress(interog_values, to_keep))
    keys_to_keep = list(map(lambda x: x['name'], list(filter(is_variable, get_args(interog)))))
    return list(zip(keys_to_keep, interog_values_to_keep))


def getInter(text : str):
    global kb, kb_uniq, interogs
    if text and text[0] == '?':
        token, rest = getAtom(text[1:].strip())
        if token:
            if not kb_uniq:
                kb = make_unique_var_names(kb)
                kb_uniq = True

            substs = backward_chaining([token], None)
            result = list(map(lambda x: keep_relevant_substs(x, token), substs))
            print()
            interogs.append((token, result))
            
            return text, rest.strip()

    return None, text


def getComm(text : str):
    match = re.match('(#|%|:).*', text)
    if match:
        token = match.group(0)
        rest = text[len(token):]
        #print('COMMENT')
        return text, rest.strip() 

    return None, text


def getCond(text : str):
    token, rest = getAtom(text)
    tokens = [token]
    while rest and rest[0] == ',':
        token, rest = getAtom(rest[1:].strip())
        tokens.append(token)

    return tokens, rest.strip()


def getNumber(text : str):
    match = re.match('0|[1-9][0-9]*', text)
    if match:
        token = match.group(0)
        rest = text[len(token):]

        return token, rest.strip()

    return None, text


def getFunc(text : str):
    token, rest = getName(text)

    if token:
        if rest[0:2] == '()':
            return make_function_call(token), rest[2:].strip()
        elif rest[0] == '(':
            token2, rest = getTerms(rest[1:].strip())
            if token and rest[0] == ')':
                return make_function_call(token, *token2), rest[1:].strip()
    return None, text


def compose(a, b):
    c = {}
    for k1, v1 in a.items():
        if list(v1.values())[0] in b.keys():
            c[k1] = b[list(v1.values())[0]]
        else:
            c[k1] = v1

    for k2, v2 in b.items():
        if k2 not in map(lambda x: list(x.values())[0], a.values()):
            c[k2] = v2
    return c


def backward_chaining(goals, subst=None, depth=0):
    global kb

    if subst is None:
        subst = {}

    if len(goals) == 0:
        return [subst]

    answers = []
    qp = substitute(goals[0], subst)
    print('  ' * depth + 'Scopuri de demonstrat:', print_formula(qp, True))

    for sent in kb:
        q = None
        q = get_conclusion(sent) if is_rule(sent) else sent
        new_subst = unify(q, qp)
        if new_subst is not False:
            if is_rule(sent):
                print('  ' * depth + 'Incercam', print_formula(sent, True))
                new_goals = deepcopy(get_premises(sent)) + deepcopy(goals[1:])
            else:
                print('  ' * depth + print_formula(sent, True), 'este un fapt')
                new_goals = deepcopy(goals[1:])

            answers = answers + backward_chaining(new_goals, compose(subst, new_subst), depth + 1)

    return answers

if __name__ == '__main__':
    if len(argv) < 2:
        print('Usage: {} <input_file_path>'.format(argv[0]))
        exit(1)

    with open(argv[1], 'r') as f:
        print()
        lines = [line.strip() for line in f.readlines()]
        lines = (list(filter(lambda x: x, lines)))
        lines = (list(map(getLine, lines)))

        rules = list(filter(is_rule, kb))
        facts = list(filter(lambda x: not is_rule(x), kb))

        print()
        print_KB(kb)
        print()

        print('RULES')
        list(map(print_formula, rules))
        print()
        print('FACTS')
        list(map(print_formula, facts))
        print()
        print('INTEROGATIONS')
        for form, results in interogs:
            print_formula(form)
            if len(results) == 0:
                print(': False')
            elif len(results[0]) == 0:
                print(': True')
            else:
                for result in results:
                    print(':', result)

                #print(result)


        #list(map(print_formula, (list(map(lambda x: x[0], interogs)))))
        print()
