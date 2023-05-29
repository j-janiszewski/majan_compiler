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


class BinOp(Node):
    def __init__(self, left, op, right):
        super().__init__(left, right)
        self.type = "binop"
        self.op = op

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


class Variable(Node):
    def __init__(self, name, variable_type) -> None:
        super().__init__()
        self.type = "variable"
        self.name = name
        self.variable_type = variable_type

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

    def __str__(self, indent_level=0) -> str:
        return super().__str__(
            indent_level, f"(value: {self.value}, value_type: {self.value_type})"
        )


class IntValue(Value):
    def __init__(self, value):
        super().__init__(value, "int")


class FloatValue(Value):
    def __init__(self, value):
        super().__init__(value, "float")


class BoolValue(Value):
    def __init__(self, value):
        super().__init__(value, "bool")
