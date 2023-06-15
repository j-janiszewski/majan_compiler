""" Example of usage:
python compile.py <program-to-compile>
"""
from nodes import AST
from parser_lexer import parser
import sys

if len(sys.argv) > 1:
    with open(sys.argv[1], "r") as f:
        data = f.read()
else:
    data = """
    int a, b, c;
    float d;
    string s;
    read(s);
    bool num;
    d=76.5;
    read(a);
    b=7;
 
   
   while (!(a==10)){
   write(a);
   true xor false;
   a = a + 1;
   }
    
    """
result = parser.parse(data)

print(result)

ast = AST(result)

ast.check_semantic_errors()

ast.create_llvm_output("output")
