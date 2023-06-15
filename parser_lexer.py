import ply.lex as lex
import ply.yacc as yacc
from nodes import (
    IntValue,
    FloatValue,
    BinOp,
    Variable,
    Instructions,
    Types,
    Init,
    BoolValue,
    Assign,
    Write,
    Read,
    StringValue,
    UnOp,
    Length,
    If,
    While,
    Function,
)

tokens = (
    "FLOAT_VALUE",
    "INT_VALUE",
    "BOOL_VALUE",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "COMMA",
    "ASSIGNMENT",
    "SEMICOLON",
    "ID",
    "IF",
    "ELSE",
    "WHILE",
    "INT",
    "FLOAT",
    "BOOL",
    "LPAREN",
    "RPAREN",
    "LCURLY",
    "RCURLY",
    "WRITE",
    "READ",
    "STRING",
    "STRING_VALUE",
    "NEG",
    "AND",
    "OR",
    "XOR",
    "LENGTH",
    "COMPARISON",
    "FUNCTION",
)


t_COMPARISON = r"(>=)|(<=)|(==)|(>)|(<)"
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_COMMA = r","
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_SEMICOLON = r";"
t_ASSIGNMENT = r"="
t_NEG = r"!"
t_LCURLY = r"{"
t_RCURLY = r"}"


reserved = {
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "int": "INT",
    "float": "FLOAT",
    "bool": "BOOL",
    "true": "BOOL_VALUE",
    "false": "BOOL_VALUE",
    "write": "WRITE",
    "read": "READ",
    "string": "STRING",
    "and": "AND",
    "or": "OR",
    "xor": "XOR",
    "length": "LENGTH",
    "function": "FUNCTION",
}

precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
)

# fmt: off
def t_STRING_VALUE(t):
    r"\"([^\"]*)\""
    t.value = t.value.strip('"')
    return t
# fmt: on


def t_ID(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    t.type = reserved.get(t.value, "ID")  # Check for reserved words
    if t.type == "BOOL_VALUE":
        if t.value == "true":
            t.value = 1
        else:
            t.value = 0
    return t


def t_FLOAT_VALUE(t):
    r"[-+]?[0-9]+\.[0-9]*"
    t.value = float(t.value)
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
    "program : lines"
    p[0] = p[1]


def p_lines_single_one(p):
    "lines : instruction"
    node = Instructions(p.lineno(1))
    node.instructions.insert(0, p[1])
    p[0] = node


def p_lines_list(p):
    "lines : instruction lines"
    node = Instructions(p.lineno(1), p[2])
    node.instructions.insert(0, p[1])
    p[0] = node


def p_instruction(p):
    """instruction : expression SEMICOLON
    | init SEMICOLON
    | write SEMICOLON
    | read SEMICOLON"""
    p[0] = p[1]

def p_instruction_if(p):
    """instruction : IF LPAREN expression RPAREN LCURLY lines RCURLY """
    p[0] = If(p.lineno(1), p[3], p[6])

def p_instruction_if_else(p):
    """instruction : IF LPAREN expression RPAREN LCURLY lines RCURLY ELSE LCURLY lines RCURLY """
    p[0] = If(p.lineno(1), p[3], p[6], p[10])

def p_instruction_while(p):
    """instruction : WHILE LPAREN expression RPAREN LCURLY lines RCURLY """
    p[0] = While(p.lineno(1),p[3],p[6])

def p_instruction_assignment_exp(p):
    """instruction : ID ASSIGNMENT expression SEMICOLON"""
    p[0] = Assign(p.lineno(1), Variable(p.lineno(2), p[1]), p[3])


def p_instruction_assignment_string(p):
    """instruction : ID ASSIGNMENT STRING_VALUE SEMICOLON"""
    p[0] = Assign(
        p.lineno(1), Variable(p.lineno(2), p[1]), StringValue(p.lineno(3), p[3])
    )

def p_instruction_function(p):
    """instruction : FUNCTION INT ID LPAREN RPAREN LCURLY lines RCURLY
    | FUNCTION FLOAT ID LPAREN RPAREN LCURLY lines RCURLY"""
    node = Function(p.lineno(1), p[3], p[2])
    node.right = p[7]   # TODO right note for function code, left node for parameters?
    p[0] = node


def p_instruction_function_params(p):
    """instruction : FUNCTION INT ID LPAREN params RPAREN LCURLY lines RCURLY
    | FUNCTION FLOAT ID LPAREN params RPAREN LCURLY lines RCURLY"""
    node = Function(p.lineno(1), p[3], p[2])
    node.left = p[5]
    node.right = p[8]   # TODO right note for function code, left node for parameters?
    p[0] = node


def p_function_params_int(p):
    """params : INT ID COMMA params"""
    p[0] = Variable(p.lineno(2), p[2], Types.Int, p[4])


def p_function_params_float(p):
    """params : FLOAT ID COMMA params"""
    p[0] = Variable(p.lineno(2), p[2], Types.Float, p[4])


def p_function_params_one_int(p):
    """params : INT ID"""
    p[0] = Variable(p.lineno(2), p[2], Types.Int)


def p_function_params_one_float(p):
    """params : FLOAT ID"""
    p[0] = Variable(p.lineno(2), p[2], Types.Float)


def p_expression_binop(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression
    | expression DIVIDE expression
    | expression AND expression
    | expression OR expression
    | expression XOR expression
    | expression COMPARISON expression"""

    p[0] = BinOp(p.lineno(2), p[1], p[2], p[3])


def p_expression_unop(p):
    "expression : NEG expression"
    p[0] = UnOp(p.lineno(1), p[2], p[1])


def p_expression_groupop(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]


def p_expression_variable(p):
    "expression : ID"
    p[0] = Variable(p.lineno(1), p[1])


def p_expression_int_value(p):
    "expression : INT_VALUE"
    p[0] = IntValue(p.lineno(1), p[1])


def p_expression_float_value(p):
    "expression : FLOAT_VALUE"
    p[0] = FloatValue(p.lineno(1), p[1])


def p_expression_bool_value(p):
    "expression : BOOL_VALUE"
    p[0] = BoolValue(p.lineno(1), p[1])


def p_expression_function_call(p):
    "expression : ID LPAREN RPAREN"
    node = Variable(p.lineno(1), p[1])  # treating function call as variable (without assign to)
    node.type = "function call"
    p[0] = node


def p_expression_function_call_params(p):
    "expression : ID LPAREN call_params RPAREN"
    node = Variable(p.lineno(1), p[1])  # treating function call as variable (without assign to)
    node.type = "function call"
    node.left = p[3]
    p[0] = node


def p_function_call_params(p):
    """call_params : ID COMMA call_params"""
    node = Variable(p.lineno(1), p[1])
    node.left = p[3]
    p[0] = node


def p_function_call_one_param(p):
    """call_params : ID"""
    p[0] = Variable(p.lineno(1), p[1])


def p_expression_int_vars_init(p):
    "init : INT int_ids"
    p[0] = Init(p.lineno(1), Types.Int , p[2])


def p_int_id_single(p):
    "int_ids : ID"
    p[0] = Variable(p.lineno(1), p[1], Types.Int)


def p_int_ids(p):
    """int_ids : int_ids COMMA ID"""
    p[0] = Variable(p.lineno(3), p[3], Types.Int, p[1])


def p_expression_float_vars_init(p):
    "init : FLOAT float_ids"
    p[0] = Init(p.lineno(1), Types.Float , p[2])


def p_float_id_single(p):
    "float_ids : ID"
    p[0] = Variable(p.lineno(1), p[1], Types.Float)


def p_float_ids(p):
    """float_ids : float_ids COMMA ID"""
    p[0] = Variable(p.lineno(3), p[3], Types.Float, p[1])


def p_expression_bool_vars_init(p):
    "init : BOOL bool_ids"
    p[0] = Init(p.lineno(1), Types.Bool , p[2])


def p_bool_id_single(p):
    "bool_ids : ID"
    p[0] = Variable(p.lineno(1), p[1], Types.Bool)


def p_bool_ids(p):
    """bool_ids : bool_ids COMMA ID"""
    p[0] = Variable(p.lineno(3), p[3], Types.Bool, p[1])


def p_expression_write(p):
    "write : WRITE LPAREN expression RPAREN"
    p[0] = Write(p.lineno(3), p[3])


def p_expression_read(p):
    "read : READ LPAREN ID RPAREN"
    p[0] = Read(p.lineno(3), Variable(p.lineno(3), p[3]))


def p_expression_length(p):
    "expression : LENGTH LPAREN ID RPAREN"
    p[0] = Length(p.lineno(3), Variable(p.lineno(3), p[3]))


def p_expression_string_vars_init(p):
    "init : STRING string_ids"
    p[0] = Init(p.lineno(1), Types.String , p[2])


def p_string_id_single(p):
    "string_ids : ID"
    p[0] = Variable(p.lineno(1), p[1], Types.String)


def p_string_ids(p):
    """string_ids : string_ids COMMA ID"""
    p[0] = Variable(p.lineno(3), p[3], Types.String, p[1])


def p_error(p):
    print(f"Syntax error in input in line: {p.lineno}!")
    print(p)


# Build the lexer
lexer = lex.lex()

parser = yacc.yacc()
