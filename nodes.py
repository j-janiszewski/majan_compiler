from enum import Enum


class ProgramMemory(object):
    string_count = 0
    mem_counter = 1
    labels_count = 1
    variables_dict = dict()
    header_lines = []
    str_alias = 1


class Types(Enum):
    Int = "int"
    Float = "float"
    Bool = "bool"
    String = "string"


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


class Instruction(Node):
    pass


class BinOp(Instruction):
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
            case "or":
                return self.__handle_logical_operator(
                    "Logical OR", left_type, right_type
                )
            case "and":
                return self.__handle_logical_operator(
                    "Logical AND", left_type, right_type
                )
            case "xor":
                return self.__handle_logical_operator(
                    "Logical XOR", left_type, right_type
                )

    def __handle_arithmetic_operator(self, operation_name, left_type, right_type):
        if left_type in [Types.Bool, Types.String]:
            print(
                f"ERROR: {left_type.value} on the left side of {operation_name} is not allowed (line: {self.line_no})"
            )
            return (1, "")
        if right_type in [Types.Bool, Types.String]:
            print(
                f"ERROR: {right_type.value} on the right side of {operation_name} is not allowed (line: {self.line_no})"
            )
            return (1, "")
        if left_type == right_type == Types.Int:
            return (0, Types.Int)
        return (0, Types.Float)

    def __handle_logical_operator(self, operation_name, left_type, right_type):
        if left_type in [Types.Float, Types.Int, Types.String]:
            print(
                f"ERROR: {left_type.value} on the left side of {operation_name} is not allowed (line: {self.line_no})"
            )
            return (1, "")
        if right_type in [Types.Float, Types.Int, Types.String]:
            print(
                f"ERROR: {right_type.value} on the right side of {operation_name} is not allowed (line: {self.line_no})"
            )
            return (1, "")
        return (0, Types.Bool)

    def __str__(self, indent_level=0):
        return super().__str__(indent_level, f"({self.op})")

    def write_code(self, output_lines: list):
        if self.op in ["+", "-", "*", "/"]:
            left_type, left_mem_id, left_val = self.left.write_code(output_lines)
            right_type, right_mem_id, right_val = self.right.write_code(output_lines)

            if left_type != right_type:
                return_type = Types.Float
                if left_type is Types.Int:
                    if left_val != "":
                        output_lines.append(
                            f"  %{ProgramMemory.mem_counter} = sitofp i32 {left_val} to double"
                        )
                    else:
                        output_lines.append(
                            f"  %{ProgramMemory.mem_counter} = sitofp i32 %{left_mem_id} to double"
                        )
                    left_val = ""
                    left_mem_id = ProgramMemory.mem_counter
                    ProgramMemory.mem_counter += 1
                else:
                    if right_val != "":
                        output_lines.append(
                            f"  %{ProgramMemory.mem_counter} = sitofp i32 {right_val} to double"
                        )
                    else:
                        output_lines.append(
                            f"  %{ProgramMemory.mem_counter} = sitofp i32 %{right_mem_id} to double"
                        )
                    right_val = ""
                    right_mem_id = ProgramMemory.mem_counter
                    ProgramMemory.mem_counter += 1
            else:
                return_type = left_type

            if left_type is Types.Int and right_type is Types.Int:
                result_type = "i32"
                prefix = ""
            else:
                result_type = "double"
                prefix = "f"
            if result_type == "i32" and self.op == "/":
                prefix = "u"

            operation = ""
            if self.op == "+":
                operation = "add "
            elif self.op == "-":
                operation = "sub "
            elif self.op == "*":
                operation = "mul "
            elif self.op == "/":
                operation = "div "

            if left_val != "" and right_val != "":
                output_lines.append(
                    f"  %{ProgramMemory.mem_counter} = {prefix}{operation} {result_type} {left_val}, {right_val}"
                )
            elif left_val != "":
                output_lines.append(
                    f"  %{ProgramMemory.mem_counter} = {prefix}{operation} {result_type} {left_val}, %{right_mem_id}"
                )
            elif right_val != "":
                output_lines.append(
                    f"  %{ProgramMemory.mem_counter} = {prefix}{operation} {result_type} %{left_mem_id}, {right_val}"
                )
            else:
                output_lines.append(
                    f"  %{ProgramMemory.mem_counter} = {prefix}{operation} {result_type} %{left_mem_id}, %{right_mem_id}"
                )

            ProgramMemory.mem_counter += 1
            return return_type, ProgramMemory.mem_counter - 1, ""
        if self.op in ["and", "xor", "or"]:
            _, left_mem_id, left_val = self.left.write_code(output_lines)
            first_case_label = ProgramMemory.labels_count
            second_case_label = ProgramMemory.labels_count+1
            end_label = ProgramMemory.labels_count+2
            label_go_to_end = ProgramMemory.labels_count+3
            ProgramMemory.labels_count+=4
            output_lines.append(f"br label %l{first_case_label}")
            output_lines.append(f"l{first_case_label}:")
            if self.op =="and":
                if left_val!="":
                    output_lines.append(f"br i1 {left_val}, label %l{second_case_label}, label %l{end_label}")
                else:
                    output_lines.append(f"br i1 %{left_mem_id}, label %l{second_case_label}, label %l{end_label}")
                output_lines.append(f"l{second_case_label}:")
                _, right_mem_id, right_val = self.right.write_code(output_lines)
                output_lines.append(f"br label %l{label_go_to_end}")
                output_lines.append(f"l{label_go_to_end}:")
                output_lines.append(f"br label %l{end_label}")
                output_lines.append(f"l{end_label}:")
                if right_val!="":
                    output_lines.append(f"%{ProgramMemory.mem_counter} = phi i1[0, %l{first_case_label}],[{right_val},%l{label_go_to_end}]")
                else:
                    output_lines.append(f"%{ProgramMemory.mem_counter} = phi i1[0, %l{first_case_label}],[%{right_mem_id},%l{label_go_to_end}]")
            if self.op =="or":
                if left_val!="":
                    output_lines.append(f"br i1 {left_val}, label %l{end_label}, label %l{second_case_label}")
                else:
                    output_lines.append(f"br i1 %{left_mem_id}, label %l{end_label}, label %l{second_case_label}")
                output_lines.append(f"l{second_case_label}:")
                _, right_mem_id, right_val = self.right.write_code(output_lines)
                output_lines.append(f"br label %l{label_go_to_end}")
                output_lines.append(f"l{label_go_to_end}:")
                output_lines.append(f"br label %l{end_label}")
                output_lines.append(f"l{end_label}:")
                if right_val!="":
                    output_lines.append(f"%{ProgramMemory.mem_counter} = phi i1[1, %l{first_case_label}],[{right_val},%l{label_go_to_end}]")
                else:
                    output_lines.append(f"%{ProgramMemory.mem_counter} = phi i1[1, %l{first_case_label}],[%{right_mem_id},%l{label_go_to_end}]")
            if self.op =="xor":
                pass # TODO implement it
            ProgramMemory.mem_counter+=1
            return Types.Bool, ProgramMemory.mem_counter-1,""
        


class UnOp(Instruction):
    def __init__(self, line_no, left, op) -> None:
        super().__init__(line_no, left)
        self.type = "unop"
        self.op = op

    def __str__(self, indent_level=0):
        return super().__str__(indent_level, f"({self.op})")

    def check_semantics(self, variables_dict):
        left_semantic_check, left_type = self.left.check_semantics(variables_dict)
        if left_semantic_check != 0:
            return (1, "")
        if left_type != Types.Bool:
            print(
                "ERROR: Negation is only allowed for bool type (line: {self.line_no})"
            )
            return (1, "")
        else:
            return (0, Types.Bool)
        
    def write_code(self, output_lines: list):
        _, mem_id, val = self.left.write_code(output_lines)
        if val !="":
            output_lines.append(f"%{ProgramMemory.mem_counter} = xor i1 {val}, 1")
        else:
            output_lines.append(f"%{ProgramMemory.mem_counter} = xor i1 %{mem_id}, 1")
        ProgramMemory.mem_counter+=1
        return Types.Bool, ProgramMemory.mem_counter-1, ""
        


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


class Assign(Instruction):
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
    
    def write_code(self, output_lines):
        var_type, var_value, var_mem_id = ProgramMemory.variables_dict[self.left.name]
        right_type, right_mem_id, right_value = self.right.write_code(output_lines)    
        if var_type is Types.Int:
            if right_value != "":
                output_lines.append(
                    f"  store i32 {right_value}, i32* %{var_mem_id}, align 4"
                )
            else:
                output_lines.append(
                    f"  store i32 %{right_mem_id}, i32* %{var_mem_id}, align 4"
                )
        if var_type is Types.Float:
            if right_type is Types.Int:
                if right_value != "":
                    output_lines.append(
                        f"  %{ProgramMemory.mem_counter} = sitofp i32 {right_value} to double"
                    )
                    right_value = ""
                else:
                    output_lines.append(
                        f"  %{ProgramMemory.mem_counter} = sitofp i32 %{right_mem_id} to double"
                    )
                right_mem_id = ProgramMemory.mem_counter
                ProgramMemory.mem_counter += 1
            if right_value != "":
                output_lines.append(
                    f"  store double {right_value}, double* %{var_mem_id}, align 8"
                )
            else:
                output_lines.append(
                    f"  store double %{right_mem_id}, double* %{var_mem_id}, align 8"
                )
        if var_type is Types.Bool:
            if right_value != "":
                output_lines.append(
                    f"  store i1 {right_value}, i1* %{var_mem_id}"
                )
            else:
                output_lines.append(
                    f"  store i1 %{right_mem_id}, i1* %{var_mem_id}"
                )
        if var_type is Types.String:
            if right_value != "":
                output_lines.append(    # TODO not sure if we can use mem_counter here or should dereference right_mem_id
                    f"  store i8* %{ProgramMemory.mem_counter - 1}, i8** %{var_mem_id}"
                )
            else:
                print("ASSING string var ID - TODO")


        return var_type, var_mem_id, ""

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

    def write_init_code(self, output_lines):
        if self.variable_type is Types.Int:
            output_lines.append(
                f"  %{ProgramMemory.mem_counter} = alloca i32, align 4"
            )
            ProgramMemory.mem_counter += 1
        elif self.variable_type is Types.Float:
            output_lines.append(
                f"  %{ProgramMemory.mem_counter} = alloca double, align 8"
            )
            ProgramMemory.mem_counter += 1
        elif self.variable_type is Types.Bool:
            output_lines.append(
                f"  %{ProgramMemory.mem_counter} = alloca i1"
            )
            ProgramMemory.mem_counter += 1
        elif self.variable_type is Types.String:
            output_lines.append(
                f"  %{ProgramMemory.mem_counter} = alloca i8*"
            )
            ProgramMemory.mem_counter += 1
        return

    def write_code(self, output_lines):
        var_type, var_value, var_mem_id = ProgramMemory.variables_dict[self.name]
        if var_type is Types.Int:
            output_lines.append(
                f"%{ProgramMemory.mem_counter} = load i32, i32* %{var_mem_id}, align 4"
            )
            ProgramMemory.mem_counter += 1
        elif var_type is Types.Float:
            output_lines.append(
                f"%{ProgramMemory.mem_counter} = load double, double* %{var_mem_id}, align 8"
            )
            ProgramMemory.mem_counter += 1
        elif var_type is Types.Bool:
            output_lines.append(
                f"%{ProgramMemory.mem_counter} = load i1, i1* %{var_mem_id}"
            )
            ProgramMemory.mem_counter += 1
        elif var_type is Types.String:
            output_lines.append(
                f"%{ProgramMemory.mem_counter} = load i8*, i8** %{var_mem_id}"  # TODO check if there should be loaded str or pointer
            )
            ProgramMemory.mem_counter += 1
        return var_type, ProgramMemory.mem_counter - 1, ""


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

    def write_code(self, output_lines):
        return self.value_type, -1, self.value


class IntValue(Value):
    def __init__(self, line_no, value):
        super().__init__(line_no, value, Types.Int)


class FloatValue(Value):
    def __init__(self, line_no, value):
        super().__init__(line_no, value, Types.Float)


class BoolValue(Value):
    def __init__(self, line_no, value):
        super().__init__(line_no, value, Types.Bool)


class Write(Instruction):
    def __init__(self, line_no, value) -> None:
        super().__init__(line_no, value)
        self.type = "write"

    def check_semantics(self, variables_dict):
        left_semantic_check, id_type = self.left.check_semantics(variables_dict)
        if left_semantic_check != 0:
            return (1, "")
        return (0, id_type)

    def write_code(self, output_lines: list):
        type, mem_id, val = self.left.write_code(output_lines)
        if type == Types.Int:
            if val != "":
                output_lines.append(
                    f"call i32(i8*, ...) @printf(i8* bitcast([3 x i8]* @int to i8 *), i32 {val})"
                )
            else:
                output_lines.append(
                    f"call i32(i8*, ...) @printf(i8* bitcast([3 x i8]* @int to i8 *), i32 %{mem_id})"
                )
            ProgramMemory.mem_counter += 1
        if type == Types.Float:
            if val != "":
                output_lines.append(
                    f"call i32(i8*, ...) @printf(i8* bitcast([4 x i8]* @double to i8 *), double {val})"
                )
            else:
                output_lines.append(
                    f"call i32(i8*, ...) @printf(i8* bitcast([4 x i8]* @double to i8 *), double %{mem_id})"
                )
            ProgramMemory.mem_counter += 1
        if type == Types.Bool:
            then_label = ProgramMemory.labels_count
            else_label = ProgramMemory.labels_count + 1
            end_label = ProgramMemory.labels_count + 2
            ProgramMemory.labels_count += 3
            if val != "":
                output_lines.append(
                    f"br i1 {val}, label %l{then_label}, label %l{else_label}"
                )
            else:
                output_lines.append(
                    f"br i1 %{mem_id}, label %l{then_label}, label %l{else_label}"
                )
            output_lines.append(f"l{then_label}:")
            output_lines.append(
                "call i32(i8*, ...) @printf(i8* bitcast([5 x i8]* @True   to i8 *), i32 5)"
            )
            ProgramMemory.mem_counter += 1
            output_lines.append(f"br label %l{end_label}")
            output_lines.append(f"l{else_label}:")
            output_lines.append(
                "call i32(i8*, ...) @printf(i8* bitcast([6 x i8]* @False   to i8 *), i32 5)"
            )
            ProgramMemory.mem_counter += 1
            output_lines.append(f"br label %l{end_label}")
            output_lines.append(f"l{end_label}:")
        if type == Types.String:
            # No need to load mem_id before, because we are printig from dispatched variable
            output_lines.append(
                    f"%{ProgramMemory.mem_counter} = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strps, i32 0, i32 0), i8* %{mem_id})"
                )
        return 0


class Read(Instruction):
    def __init__(self, line_no, value) -> None:
        super().__init__(line_no, value)
        self.type = "read"

    def check_semantics(self, variables_dict):
        if not self.left.name in variables_dict:
            print(f"ERROR: Undeclared variable (line: {self.line_no}) ")
            return (1, "")
        id_type = variables_dict[self.left.name]
        if id_type == Types.Bool:
            print(
                f"ERROR: Reading to bool variable is not allowed (line: {self.line_no}) "
            )
            return (1, "")
        # TODO: decide if reading to string variable is allowed
        return (0, id_type)

    def write_code(self, output_lines: list):
        type, _, ident_id = ProgramMemory.variables_dict[self.left.name]
        if type == Types.Int:
            output_lines.append(
                f"call i32 (i8*, ...) @scanf(i8* bitcast ([3 x i8]* @int to i8*), i32* %{ident_id})"
            )
            ProgramMemory.mem_counter += 1
        if type == Types.Float:
            output_lines.append(
                f"call i32 (i8*, ...) @scanf(i8* bitcast ([4 x i8]* @double to i8*), double* %{ident_id})"
            )
            ProgramMemory.mem_counter += 1
        return 0


class StringValue(Value):
    def __init__(self, line_no, value):
        super().__init__(line_no, value, Types.String)
        self.alias = f"str{ProgramMemory.str_alias}"
        ProgramMemory.str_alias += 1

    def write_code(self, output_lines):
        l = len(self.value) + 1
        n = f"{self.alias}"
        ProgramMemory.header_lines.append(
            f'@{n} = private constant [{l} x i8] c"{self.value}\00"'
        )   
        output_lines.append(
            f"  %{n} = alloca [{l+1} x i8]"
        )
        output_lines.append(
            f"  %{ProgramMemory.mem_counter} = bitcast [{l} x i8]* %{n} to i8*"
        )
        output_lines.append(
            f"  call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 1 %{ProgramMemory.mem_counter}, i8* align 1 getelementptr inbounds ([{l} x i8], [{l} x i8]* @{n}, i32 0, i32 0), i64 {l}, i1 false)"
        )
        ProgramMemory.mem_counter += 1
        output_lines.append(
            f"  %ptr{n} = alloca i8*"
        )
        output_lines.append(
            f"  %{ProgramMemory.mem_counter} = getelementptr inbounds [{l} x i8], [{l} x i8]* %{n}, i64 0, i64 0"
        )
        ProgramMemory.mem_counter += 1
        output_lines.append(
            f"  store i8* %{ProgramMemory.mem_counter - 1}, i8** %ptr{n}"
        )
        return self.value_type, f"%ptr{n}", l-1


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
                        print(
                            f"ERROR: Variable already defined, (line: {left_node.line_no})"
                        )
                        return 1
                    variables_dict[left_node.name] = variable_type
                    left_node = left_node.left
            elif isinstance(node, Instruction):
                semantic_check, _ = node.check_semantics(variables_dict)
                if semantic_check != 0:
                    return 1

    def create_llvm_output(self, filename):
        output_lines = []
        # TODO Check if everything below is needed
        ProgramMemory.header_lines.append(f'@int = constant [ 3 x i8] c"%d\\00"')
        ProgramMemory.header_lines.append(f'@double = constant [ 4 x i8] c"%lf\\00"')
        ProgramMemory.header_lines.append(f'@True = constant [5 x i8 ] c"True\\00"')
        ProgramMemory.header_lines.append(f'@False = constant [6 x i8 ] c"False\\00"')
        ProgramMemory.header_lines.append(f'@strps = constant [4 x i8] c\"%s\\0A\\00\"')
        ProgramMemory.header_lines.append(f"")
        ProgramMemory.header_lines.append(f"declare i32 @printf(i8*, ...)")
        ProgramMemory.header_lines.append(f"declare i32 @scanf(i8*, ...)")
        ProgramMemory.header_lines.append(f"declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg)")
        ProgramMemory.header_lines.append(f"")
        output_lines.append(
            f"define dso_local i32 @main() #0 {{"
        )  # TODO do we really need dso_local param?
        if self.root == None:
            output_lines.append(f"  ret i32 0")
            output_lines.append(f"}}")
            join_and_write_to_file_ll(filename, output_lines)
            return
        for node in self.root.instructions:
            if isinstance(node, Init):
                var_type = node.variable_type
                next = node.left
                while next:
                    ProgramMemory.variables_dict[next.name] = (
                        var_type,
                        0,
                        ProgramMemory.mem_counter,
                    )
                    next.write_init_code(output_lines)
                    next = next.left
            elif isinstance(node, Instruction):
                node.write_code(output_lines)
            elif isinstance(node, Instructions):
                print("Instructions instance")  # TODO to implement

        output_lines.append(f"ret i32 0")
        output_lines.append(f"}}")
        join_and_write_to_file_ll(filename, output_lines)

        print(f"Program memory: {ProgramMemory.variables_dict}")
        return


def join_and_write_to_file_ll(filename, main_lines):
    ProgramMemory.header_lines.append(f"")
    header = "\n".join(ProgramMemory.header_lines)
    main = "\n".join(main_lines)
    data = header + "\n" + main
    with open(filename + ".ll", "w") as file:
        file.write(data)
