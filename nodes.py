from enum import Enum


class PromgramMemory(object):
    string_count = 0
    mem_counter = 1
    labels_count = 1
    variables_dict = dict()


class Types(Enum):
    Int = "int"
    Float = "float"
    Bool = "bool"


class Node:
    def __init__(self, line_no, left=None, right=None) -> None:
        self.left = left
        self.right = right
        self.line_no = line_no

    def __str__(self, indent_level=0, additional_info=None):
        indentation = " " * 4 * indent_level
        node_as_text = f"{indentation}{self.type} node"
        if additional_info:
            node_as_text += additional_info
        if self.left:
            left_str = self.left.__str__(indent_level + 1)
            node_as_text += f"\n{indentation}Left node:\n{left_str}"
        if self.right:
            right_str = self.right.__str__(indent_level + 1)
            node_as_text += f"\n{indentation}Right node:\n{right_str}"
        return node_as_text


class Expression(Node):
    pass


class BinOp(Expression):
    def __init__(self, line_no, left, op, right):
        super().__init__(line_no, left, right)
        self.type = "binop"
        self.op = op

    def check_semantics(self, variables_dict):
        left_semantic_check, left_type = self.left.check_semantics(variables_dict)
        if left_semantic_check != 0:
            return (1, "")
        right_semantic_check, right_type = self.right.check_semantics(variables_dict)
        if right_semantic_check != 0:
            return (1, "")
        match self.op:
            case "+":
                return self.__handle_arithmetic_operator(
                    "Adding", left_type, right_type
                )
            case "-":
                return self.__handle_arithmetic_operator(
                    "Substracting", left_type, right_type
                )
            case "*":
                return self.__handle_arithmetic_operator(
                    "Multiplying", left_type, right_type
                )
            case "/":
                return self.__handle_arithmetic_operator(
                    "Dividing", left_type, right_type
                )

    def __handle_arithmetic_operator(self, operation_name, left_type, right_type):
        if left_type == Types.Bool or right_type == Types.Bool:
            print(
                f"ERROR: {operation_name} bool type is not allowed (line: {self.line_no}) "
            )
            return (1, "")
        if left_type == right_type == Types.Int:
            return (0, Types.Int)
        return (0, Types.Float)

    def __str__(self, indent_level=0):
        return super().__str__(indent_level, f"({self.op})")


class Instructions(Node):
    def __init__(self, line_no, instructions_node=None) -> None:
        super().__init__(line_no)
        if instructions_node:
            if isinstance(instructions_node, Instructions):
                self.instructions = instructions_node.instructions
            else:
                self.instructions = [instructions_node]
        else:
            self.instructions = list()

    def __str__(self, indent_level=0):
        indentation = " " * 4 * indent_level
        node_as_text = f"{indentation} Instructions node:\n"
        for i, inst in enumerate(self.instructions):
            node_as_text += f" {indentation}{i}: {inst.__str__()} \n"
        return node_as_text


class Init(Node):
    def __init__(self, line_no, variable_type) -> None:
        super().__init__(line_no)
        self.variable_type = variable_type
        self.type = "init node"

    def __str__(self, indent_level=0):
        return super().__str__(indent_level, f"(type: {self.variable_type})")


class Assign(Expression):
    def __init__(self, line_no, left, right) -> None:
        super().__init__(line_no, left, right)
        self.type = "assign node"

    def check_semantics(self, variables_dict):
        left_semantic_check, id_type = self.left.check_semantics(variables_dict)
        if left_semantic_check != 0:
            return (1, "")
        right_semantic_check, exp_type = self.right.check_semantics(variables_dict)
        if right_semantic_check != 0:
            return (1, "")
        if id_type != exp_type:
            if id_type == Types.Float and exp_type == Types.Int:
                return (0, Types.Float)
            else:
                print(
                    f"ERROR: Assignment to variable of type {id_type.value} exp of type {exp_type.value} (line: {self.line_no}) "
                )
                return (1, "")
        return (0, id_type)

    def __str__(self, indent_level=0):
        return super().__str__(indent_level)


class Variable(Node):
    def __init__(self, line_no, name, variable_type=None) -> None:
        super().__init__(line_no)
        self.type = "variable"
        self.name = name
        self.variable_type = variable_type

    def check_semantics(self, variables_dict):
        if not self.name in variables_dict:
            print(f"ERROR: Undeclared variable (line: {self.line_no}) ")
            return (1, "")
        return (0, variables_dict[self.name])

    def __str__(self, indent_level=0):
        return super().__str__(
            indent_level, f"(name={self.name}, type={self.variable_type})"
        )


class Value(Node):
    def __init__(self, line_no, value, value_type) -> None:
        super().__init__(line_no)
        self.type = "value"
        self.value = value
        self.value_type = value_type

    def check_semantics(self, variables_dict):
        return (0, self.value_type)

    def __str__(self, indent_level=0) -> str:
        return super().__str__(
            indent_level, f"(value: {self.value}, value_type: {self.value_type})"
        )


class IntValue(Value):
    def __init__(self, line_no, value):
        super().__init__(line_no, value, Types.Int)


class FloatValue(Value):
    def __init__(self, line_no, value):
        super().__init__(line_no, value, Types.Float)


class BoolValue(Value):
    def __init__(self, line_no, value):
        super().__init__(line_no, value, Types.Bool)


class AST:
    def __init__(self, root: Instructions) -> None:
        self.root = root

    def check_semantic_errors(self):
        variables_dict = dict()
        if not self.root:
            return 0
        for node in self.root.instructions:
            if isinstance(node, Init):
                variable_type = node.variable_type
                left_node = node.left
                while left_node:
                    if left_node.name in variables_dict:
                        # TODO LINE NUMBER
                        print(
                            f"ERROR: Variable already defined, (line: {left_node.line_no})"
                        )
                        return 1
                    variables_dict[left_node.name] = variable_type
                    left_node = left_node.left
            elif isinstance(node, Expression):
                semantic_check, _ = node.check_semantics(variables_dict)
                if semantic_check != 0:
                    return 1
                
    def create_llvm_output(self, filename):
        variablesDict = dict()
        output_lines = []
        output_lines.append(f"@int = constant [ 3 x i8] c\"%d\\00\"")
        output_lines.append(f"@double = constant [ 4 x i8] c\"%lf\\00\"")
        output_lines.append(f"@True = constant [5 x i8 ] c\"True\\00\"")
        output_lines.append(f"@False = constant [6 x i8 ] c\"False\\00\"")
        output_lines.append(f"")
        output_lines.append(f"declare i32 @printf(i8*, ...)")
        output_lines.append(f"declare i32 @scanf(i8*, ...)")
        output_lines.append(f"")
        #output_lines += f"" #header text
        output_lines.append(f"define dso_local i32 @main() #0 {{")   #do we really need dso_local param?
        if self.root == None:
            output_lines.append(f"ret i32 0")
            output_lines.append(f"}}")
            join_and_write_to_file_ll(filename, output_lines)
            return
        print("ERROR WRITE")
        return




def join_and_write_to_file_ll(filename, data_lines):
    data = '\n'.join(data_lines)
    with open(filename+".ll", "w") as file:
        file.write(data)
