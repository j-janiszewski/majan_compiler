from enum import Enum


class Types(Enum):
    Int = "int"
    Float = "float"
    Bool = "bool"


class Node:
    def __init__(self, left=None, right=None) -> None:
        self.left = left
        self.right = right

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
    def __init__(self, left, op, right):
        super().__init__(left, right)
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
            # TODO: dodać zapamietywanie linijki i ja wyswietlac tutaj
            print(f"{operation_name} bool type is not allowed, error in line: ")
            return (1, "")
        if left_type == right_type == Types.Int:
            return (0, Types.Int)
        return (0, Types.Float)

    def __str__(self, indent_level=0):
        return super().__str__(indent_level, f"({self.op})")


class Instructions(Node):
    def __init__(self, instructions_node=None) -> None:
        super().__init__()
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
    def __init__(self, variable_type) -> None:
        super().__init__()
        self.variable_type = variable_type
        self.type = "init node"

    def __str__(self, indent_level=0):
        return super().__str__(indent_level, f"(type: {self.variable_type})")


class Assign(Expression):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)
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
                # TODO ADD LINE NUMBERS
                print(
                    f"ERROR: Assignment to variable of type {id_type.value} exp of type {exp_type.value} at line: "
                )
                return (1, "")
        return (0, id_type)

    def __str__(self, indent_level=0):
        return super().__str__(indent_level)


class Variable(Node):
    def __init__(self, name, variable_type=None) -> None:
        super().__init__()
        self.type = "variable"
        self.name = name
        self.variable_type = variable_type

    def check_semantics(self, variables_dict):
        if not self.name in variables_dict:
            # TODO add LINE NUMBER
            print("Undeclared variable at line: ")
            return (1, "")
        return (0, variables_dict[self.name])

    def __str__(self, indent_level=0):
        return super().__str__(
            indent_level, f"(name={self.name}, type={self.variable_type})"
        )


class Value(Node):
    def __init__(self, value, value_type) -> None:
        super().__init__()
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
    def __init__(self, value):
        super().__init__(value, Types.Int)


class FloatValue(Value):
    def __init__(self, value):
        super().__init__(value, Types.Float)


class BoolValue(Value):
    def __init__(self, value):
        super().__init__(value, Types.Bool)


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
                        print("Variable already defined, error at line:")
                        return 1
                    variables_dict[left_node.name] = variable_type
                    left_node = left_node.left
            elif isinstance(node, Expression):
                semantic_check, _ = node.check_semantics(variables_dict)
                if semantic_check != 0:
                    return 1
