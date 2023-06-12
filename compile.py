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
    int a, b, c;
    float d;
    d=76.5;
    a=6;
    b=7;
    write(a <=(b + 5));
   
    
    """
result = parser.parse(data)

print(result)

ast = AST(result)
#print(ast)
ast.check_semantic_errors()

ast.create_llvm_output("output")
