""" Example of usage:
python compile.py <program-to-compile>
"""
from nodes import AST
from parser_lexer import parser
import sys

if len(sys.argv) >1:
    with open(sys.argv[1],"r") as f:
        data = f.read()
else:
    data = """
    string a, b, c;
    read(a);
    b = "ispies";
    c = a + b;
    """

result = parser.parse(data)

print(result)

ast = AST(result)

ast.check_semantic_errors()

ast.create_llvm_output("output")
