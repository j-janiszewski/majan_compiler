
# MAJAN language compiler

Project for the course "Formal languages and compilers" at Warsaw University of Technology 2023. The project was to create a new programming language describing the allowed instructions and syntax rules and then implement a compiler that compiles source code in that language into LLVM code. Description of the **MAJAN** language can be found in *intruction.pdf*. 

## How to use it


In order to compile your source file to LLVM code following command should be executed:
```
python compile . py <path_to_your_source_file >
```
In the same directory where compile.py is located file named output.ll sould appear.
