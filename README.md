# PROLOG Interpreter

This is a PROLOG interpreter written in Python. It can parse and evaluate a subset of the PROLOG programming language.

## Usage

To use the interpreter, simply run the following command:

```python
python3 interpreter.py <input_file>
```

Where <input_file> is a text file containing PROLOG statements.

## Features

The interpreter supports the following features:

* Facts and rules with arbitrary arity
* Queries (i.e. asking the interpreter to prove a statement)
* Variables
* Unification and backtracking
* Conjunctions and disjunctions

## Examples

Here are some examples of valid input files:

Example 1:

```prolog
parent(john, mary).
parent(john, mark).
parent(jane, mary).
parent(jane, mark).

ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
```

This input file defines four facts and two rules. The ancestor rule defines a recursive relationship between a person and their ancestors.

Example 2:

```prolog
likes(john, mary).
likes(john, pizza).
likes(jane, pizza).

friend(X, Y) :- likes(X, Z), likes(Y, Z).
```

This input file defines three facts and one rule. The friend rule defines a relationship between two people who like the same thing.

## Limitations

The interpreter has the following limitations:

* It only supports a subset of the PROLOG programming language
* It is not optimized for performance
* It may not handle certain edge cases correctly
