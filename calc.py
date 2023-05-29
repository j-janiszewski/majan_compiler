import ply.lex as lex
import ply.yacc as yacc
from nodes import IntValue, BinOp, Variable, Instructions

tokens = (
    "INT_VALUE",
    "PLUS",
    "MINUS",
    "TIMES",
    "COMMA",
    "ID",
    "IF",
    "ELSE",
    "WHILE",
    "INT",
    "FLOAT",
    "BOOL",
)


t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_COMMA = r","

reserved = {
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "int": "INT",
    "float": "FLOAT",
    "bool": "BOOL",
}


def t_ID(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    t.type = reserved.get(t.value, "ID")  # Check for reserved words
    return t


def t_INT_VALUE(t):
    r"([+-]?[1-9]\d*|0)"
    t.value = int(t.value)
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


t_ignore_COMMENT = r"\#.*"
# check if it works properly
t_ignore = " \t"


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Parser part

start = "program"


def p_program(p):
    "program : expression_list"
    p[0] = p[1]


def p_expression_binop(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression"""

    p[0] = BinOp(p[1], p[2], p[3])


def p_expression_single_one(p):
    "expression_list : expression"
    p[0] = p[1]


def p_expression_list(p):
    "expression_list : expression expression_list"
    node = Instructions(p[2])
    node.instructions.insert(0, p[1])
    p[0] = node


def p_expression_int_value(p):
    "expression : INT_VALUE"
    p[0] = IntValue(p[1])


def p_expression_int_vars_init(p):
    "expression : INT int_ids"
    p[0] = p[2]


def p_int_id_single(p):
    "int_ids : ID"
    p[0] = Variable(p[1], "int")


def p_int_ids(p):
    """int_ids : int_ids COMMA ID"""
    node = Variable(p[3], "int")
    node.left = p[1]
    p[0] = node


def p_expression_float_vars_init(p):
    "expression : FLOAT float_ids"
    p[0] = p[2]


def p_float_id_single(p):
    "float_ids : ID"
    p[0] = Variable(p[1], "float")


def p_float_ids(p):
    """float_ids : float_ids COMMA ID"""
    node = Variable(p[3], "float")
    node.left = p[1]
    p[0] = node


def p_expression_bool_vars_init(p):
    "expression : BOOL bool_ids"
    p[0] = p[2]


def p_bool_id_single(p):
    "bool_ids : ID"
    p[0] = Variable(p[1], "bool")


def p_bool_ids(p):
    """bool_ids : bool_ids COMMA ID"""
    node = Variable(p[3], "bool")
    node.left = p[1]
    p[0] = node


def p_error(p):
    print(f"Syntax error in input in line: {p.lineno}!")
    print(p)


# Build the lexer
lexer = lex.lex()

# testing
data = """
3 + 4 * 10 \n int num, num2, num4 \n float tuto, tiki, tson
"""


parser = yacc.yacc()


result = parser.parse(data)

print(result)
