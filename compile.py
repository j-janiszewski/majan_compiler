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
    data1 = """
    int a, b;
    """

    data = """
    function int nope(int a){
        return a;
    }

    function float test(int a, float b){
        float c;
        c = a + b;
        write(c);
        return c;
    }

    int aa;
    aa = 1;
    float bb;
    bb = 2.0;
    float cc;
    cc = test(aa, bb);
    write(cc);
    """

    data2 = """
    string b;

    function int test(){
        string a;
        a = "test";
        write(a);
        a = a + b;
        write(a);
    }

    int a;
    b = "pies";
    a = 3;
    a = a + 1;
    test();
    write(a);
    write(a);
    """

result = parser.parse(data)

print(result)

ast = AST(result)

ast.check_semantic_errors()

ast.create_llvm_output("output")
