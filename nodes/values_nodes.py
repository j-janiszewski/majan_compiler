from .common import Instruction, Types, ProgramMemory, Node, WriteMode


class Init(Node):
    def __init__(self, line_no, variable_type, left=None) -> None:
        super().__init__(line_no, left)
        self.variable_type = variable_type
        self.type = "init node"

    def check_semantics(self, variables_dict):
        variable_type = self.variable_type
        left_node = self.left
        while left_node:
            if left_node.name in variables_dict:
                print(
                    f"ERROR: Variable already defined, (line: {left_node.line_no})"
                )
                return 1, ""
            variables_dict[left_node.name] = variable_type
            left_node = left_node.left
        return 0, ""

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
        mode = ""
        if self.left.name in ProgramMemory.local_var_dict:
            var_type, var_value, var_mem_id = ProgramMemory.local_var_dict[self.left.name]
            mode = WriteMode.Local
        else:
            var_type, var_value, var_mem_id = ProgramMemory.variables_dict[self.left.name]
            mode = WriteMode.Global
        right_type, right_mem_id, right_value = self.right.write_code(output_lines)
        if var_type is Types.Int:
            if right_value != "":
                if mode is WriteMode.Local:
                    output_lines.append(
                        f"store i32 {right_value}, i32* %{var_mem_id}, align 4"
                    )
                elif mode is WriteMode.Global:
                    output_lines.append(
                        f"store i32 {right_value}, i32* @g{var_mem_id}, align 4"
                    )
            else:
                if mode is WriteMode.Local:
                    output_lines.append(
                        f"store i32 %{right_mem_id}, i32* %{var_mem_id}, align 4"
                    )
                elif mode is WriteMode.Global:
                    output_lines.append(
                        f"store i32 %{right_mem_id}, i32* @g{var_mem_id}, align 4"
                    )
        if var_type is Types.Float:
            if right_type is Types.Int:
                if right_value != "":
                    output_lines.append(
                        f"%{ProgramMemory.mem_counter} = sitofp i32 {right_value} to double"
                    )
                    right_value = ""
                else:
                    output_lines.append(
                        f"%{ProgramMemory.mem_counter} = sitofp i32 %{right_mem_id} to double"
                    )
                right_mem_id = ProgramMemory.mem_counter
                ProgramMemory.mem_counter += 1
            if right_value != "":
                if mode is WriteMode.Local:
                    output_lines.append(
                        f"store double {right_value}, double* %{var_mem_id}, align 8"
                    )
                elif mode is WriteMode.Global:
                    output_lines.append(
                        f"store double {right_value}, double* @g{var_mem_id}, align 8"
                    )
            else:
                if mode is WriteMode.Local:
                    output_lines.append(
                        f"store double %{right_mem_id}, double* %{var_mem_id}, align 8"
                    )
                elif mode is WriteMode.Global:
                    output_lines.append(
                        f"store double %{right_mem_id}, double* @g{var_mem_id}, align 8"
                    )
        if var_type is Types.Bool:
            if right_value != "":
                output_lines.append(f"store i1 {right_value}, i1* %{var_mem_id}")
            else:
                output_lines.append(f"store i1 %{right_mem_id}, i1* %{var_mem_id}")
        if var_type is Types.String:
            if right_value != "":
                if mode is WriteMode.Local:
                    output_lines.append(
                        f"store i8* %{ProgramMemory.mem_counter - 1}, i8** %{var_mem_id}"
                    )
                    ProgramMemory.local_var_dict[self.left.name] = (
                        var_type,
                        right_value,
                        var_mem_id,
                    )
                elif mode is WriteMode.Global:
                    output_lines.append(
                        f"store i8* %{ProgramMemory.mem_counter - 1}, i8** @g{var_mem_id}"
                    )
                    ProgramMemory.variables_dict[self.left.name] = (
                        var_type,
                        right_value,
                        var_mem_id,
                    )
        return var_type, var_mem_id, ""


class Variable(Node):
    def __init__(self, line_no, name, variable_type=None, left=None) -> None:
        super().__init__(line_no, left)
        self.type = "variable"
        self.name = name
        self.variable_type = variable_type

    def check_semantics(self, variables_dict):
        if not self.name in variables_dict:
            print(f"ERROR: Undeclared variable '{self.name}' (line: {self.line_no}) ")
            return (1, "")
        return (0, variables_dict[self.name])

    def __str__(self, indent_level=0):
        return super().__str__(
            indent_level, f"(name={self.name}, type={self.variable_type})"
        )

    def write_init_code(self, output_lines):
        if self.variable_type is Types.Int:
            if(ProgramMemory.global_var):
                ProgramMemory.header_lines.append(f"@g{ProgramMemory.global_counter} = global i32 0")
                ProgramMemory.global_counter += 1
            else:
                output_lines.append(f"%{ProgramMemory.mem_counter} = alloca i32, align 4")
                ProgramMemory.mem_counter += 1
        elif self.variable_type is Types.Float:
            if(ProgramMemory.global_var):
                ProgramMemory.header_lines.append(f"@g{ProgramMemory.global_counter} = global double 0")
                ProgramMemory.global_counter += 1
            else:
                output_lines.append(f"%{ProgramMemory.mem_counter} = alloca double, align 8")
                ProgramMemory.mem_counter += 1
        elif self.variable_type is Types.Bool:
            output_lines.append(
                f"%{ProgramMemory.increment_and_read_mem()} = alloca i1"
            )
        elif self.variable_type is Types.String:
            if(ProgramMemory.global_var):
                ProgramMemory.header_lines.append(
                    f"@g{ProgramMemory.global_counter} = global i8* null"
                )
                ProgramMemory.global_counter += 1
            else:
                output_lines.append(
                    f"%{ProgramMemory.increment_and_read_mem()} = alloca i8*"
                )
        return

    def write_code(self, output_lines):
        mode = ""
        if self.name in ProgramMemory.local_var_dict:
            var_type, var_value, var_mem_id = ProgramMemory.local_var_dict[self.name]
            mode = WriteMode.Local
        elif self.name in ProgramMemory.variables_dict:
            var_type, var_value, var_mem_id = ProgramMemory.variables_dict[self.name]
            mode = WriteMode.Global
        elif self.name in ProgramMemory.function_dict:
            var_type, _, _ = ProgramMemory.function_dict[self.name]
            mode = WriteMode.FunCall
        else:
            print(
                    f"ERROR: Unknown {self.name}: local > global > function"
                )
            return "", "", -1
        if var_type is Types.Int:
            if mode is WriteMode.Local:
                output_lines.append(
                    f"%{ProgramMemory.mem_counter} = load i32, i32* %{var_mem_id}, align 4"
                )
            elif mode is WriteMode.Global:
                output_lines.append(
                    f"%{ProgramMemory.mem_counter} = load i32, i32* @g{var_mem_id}, align 4"
                )
            elif mode is WriteMode.FunCall:
                output_lines.append(
                    f"%{ProgramMemory.mem_counter} = call i32 @{self.name}()"
                )
            ProgramMemory.mem_counter += 1
        elif var_type is Types.Float:
            if mode is WriteMode.Local:
                output_lines.append(
                    f"%{ProgramMemory.mem_counter} = load double, double* %{var_mem_id}, align 8"
                )
            elif mode is WriteMode.Global:
                output_lines.append(
                    f"%{ProgramMemory.mem_counter} = load double, double* @g{var_mem_id}, align 8"
                )
            elif mode is WriteMode.FunCall:
                output_lines.append(
                    f"%{ProgramMemory.mem_counter} = call double @{self.name}"
                )
            ProgramMemory.mem_counter += 1
        elif var_type is Types.Bool:
            output_lines.append(
                f"%{ProgramMemory.increment_and_read_mem()} = load i1, i1* %{var_mem_id}"
            )

        elif var_type is Types.String:
            if mode is WriteMode.Local:
                output_lines.append(
                    f"%{ProgramMemory.increment_and_read_mem()} = load i8*, i8** %{var_mem_id}"
                )
            elif mode is WriteMode.Global:
                output_lines.append(
                    f"%{ProgramMemory.increment_and_read_mem()} = load i8*, i8** @g{var_mem_id}"
                )

            return var_type, ProgramMemory.mem_counter - 1, var_value
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


class StringValue(Value):
    def __init__(self, line_no, value):
        super().__init__(line_no, value, Types.String)
        self.alias = f"str{ProgramMemory.str_alias}"
        ProgramMemory.str_alias += 1

    def write_code(self, output_lines):
        l = len(self.value) + 1
        n = f"{self.alias}"
        ProgramMemory.header_lines.append(
            f'@{n} = private constant [{l} x i8] c"{self.value}\\00"'
        )
        output_lines.append(f"%{n} = alloca [{l+1} x i8]")
        output_lines.append(
            f"%{ProgramMemory.mem_counter} = bitcast [{l} x i8]* %{n} to i8*"
        )
        output_lines.append(
            f"call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 1 %{ProgramMemory.increment_and_read_mem()}, i8* align 1 getelementptr inbounds ([{l} x i8], [{l} x i8]* @{n}, i32 0, i32 0), i64 {l}, i1 false)"
        )
        output_lines.append(f"%ptr{n} = alloca i8*")
        output_lines.append(
            f"%{ProgramMemory.increment_and_read_mem()} = getelementptr inbounds [{l} x i8], [{l} x i8]* %{n}, i64 0, i64 0"
        )
        output_lines.append(f"store i8* %{ProgramMemory.mem_counter - 1}, i8** %ptr{n}")
        return self.value_type, f"%ptr{n}", l - 1
