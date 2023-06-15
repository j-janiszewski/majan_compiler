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
    data2 = """
    int myGlob;
    myGlob = 3;
    function int test(){
    int a, b;
    a = 5;
    b = 1;
    if(a > b)
    {
        write(a + b);
    }
    write(a);
    }
    float myGlobFloat;
    myGlobFloat = 1.5;
    test();
    write(myGlob + myGlobFloat);
    """

    data = """
    function float test(){
        int a;
        a = 5;
    }

    function int test2(){
        int a;
        a = 3;
    }
    """

    data1 = """
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
