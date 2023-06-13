from .common import Instruction, Types, ProgramMemory

class BinOp(Instruction):
    comparison_llvm_operators = {
                      ("==","i"):"eq", ("==","f"):"oeq",
                      (">","i"):"slt", (">","f"):"ult",
                      ("<","i"):"sgt", ("<","f"):"ugt",
                      ("<=","i"):"sle", ("<=","f"):"ule",
                      (">=","i"):"sge", (">=","f"):"uge",
                      }

    math_llvm_operators ={"+": "add", "-":"sub", "*":"mul", "/":"div"}

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
            case "+" | "-" | "*"| "/": 
                return self.__handle_arithmetic_operator(
                    self.op, left_type, right_type
                )
            case "or" | "and" | "xor":
                return self.__handle_logical_operator(
                    self.op, left_type, right_type
                )
            case "==" | ">" | "<" | "<=" | ">=":
                return self.__handle_comparison_operator(self.op, left_type, right_type)
            

    def __handle_comparison_operator(self, operation_name, left_type, right_type):
        if left_type in [Types.String]:
            print(
                f"ERROR: {left_type.value} on the left side of {operation_name} is not allowed (line: {self.line_no})"
            )
            return (1, "")
        if right_type in [Types.String]:
            print(
                f"ERROR: {right_type.value} on the right side of {operation_name} is not allowed (line: {self.line_no})"
            )
            return (1, "")
        if left_type!= right_type:
            print(f"ERROR: You can only compare values of the same type (line: {self.line_no})")
            return (1, "")
        return (0, Types.Bool)
                


    def __handle_arithmetic_operator(self, operation_name, left_type, right_type):
        if left_type == right_type == Types.String:
            return (0, Types.String)
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
    
    def __write_code_arithmetic_operation(self, output_lines: list):
        left_type, left_mem_id, left_val = self.left.write_code(output_lines)
        right_type, right_mem_id, right_val = self.right.write_code(output_lines)
        if left_type == right_type == Types.String and self.op == "+":
            l = left_val + right_val + 1
            output_lines.append(
                f"%{ProgramMemory.mem_counter} = alloca [{l} x i8]"
            )
            mem_str = ProgramMemory.increment_and_read_mem()
            output_lines.append(
                f"%{ProgramMemory.mem_counter} = alloca i8*"
            )
            mem_ptrstr = ProgramMemory.increment_and_read_mem()
            output_lines.append(
                f"%{ProgramMemory.increment_and_read_mem()} = getelementptr inbounds [{l} x i8], [{l} x i8]* %{mem_str}, i64 0, i64 0"
            )
            output_lines.append(
                f"store i8* %{ProgramMemory.mem_counter - 1}, i8** %{mem_ptrstr}"
            )
            output_lines.append(
                f"%{ProgramMemory.increment_and_read_mem()} = load i8*, i8** %{mem_ptrstr}"
            )
            output_lines.append(    # Not sure if % should be before left_mem_id
                f"%{ProgramMemory.increment_and_read_mem()} = call i8* @strcpy(i8* %{ProgramMemory.mem_counter - 1}, i8* %{left_mem_id})"
            )
            output_lines.append(    # Not sure if % should be before right_mem_id
                f"%{ProgramMemory.increment_and_read_mem()} = call i8* @strcat(i8* %{ProgramMemory.mem_counter - 2}, i8* %{right_mem_id})"
            )
            return Types.String, ProgramMemory.mem_counter - 3, l-1

        if left_type != right_type:
            return_type = Types.Float
            #TODO create formatted string in oneplace isnted of writing it 4 times
            if left_type is Types.Int:
                if left_val != "":
                    output_lines.append(
                        f"%{ProgramMemory.mem_counter} = sitofp i32 {left_val} to double"
                    )
                else:
                    output_lines.append(
                        f"%{ProgramMemory.mem_counter} = sitofp i32 %{left_mem_id} to double"
                    )
                left_val = ""
                left_mem_id = ProgramMemory.increment_and_read_mem()
            else:
                if right_val != "":
                    output_lines.append(
                        f"%{ProgramMemory.mem_counter} = sitofp i32 {right_val} to double"
                    )
                else:
                    output_lines.append(
                        f"%{ProgramMemory.mem_counter} = sitofp i32 %{right_mem_id} to double"
                    )
                right_val = ""
                right_mem_id = ProgramMemory.increment_and_read_mem()
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

        operation = self.math_llvm_operators[self.op]
    
        if left_val != "" and right_val != "":
            output_lines.append(
                f"%{ProgramMemory.mem_counter} = {prefix}{operation} {result_type} {left_val}, {right_val}"
            )
        elif left_val != "":
            output_lines.append(
                f"%{ProgramMemory.mem_counter} = {prefix}{operation} {result_type} {left_val}, %{right_mem_id}"
            )
        elif right_val != "":
            output_lines.append(
                f"%{ProgramMemory.mem_counter} = {prefix}{operation} {result_type} %{left_mem_id}, {right_val}"
            )
        else:
            output_lines.append(
                f"%{ProgramMemory.increment_and_read_mem()} = {prefix}{operation} {result_type} %{left_mem_id}, %{right_mem_id}"
            )
        return return_type, ProgramMemory.mem_counter - 1, ""

    def __write_code_logical_operators(self, output_lines: list):
        if self.op in ["and","or"]:
            _, left_mem_id, left_val = self.left.write_code(output_lines)
            first_case_label = ProgramMemory.increment_and_read_label()
            second_case_label = ProgramMemory.increment_and_read_label()
            end_label = ProgramMemory.increment_and_read_label()
            label_go_to_end = ProgramMemory.increment_and_read_label()
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
                #TODO same as sitofp 
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
            ProgramMemory.mem_counter+=1
            return Types.Bool, ProgramMemory.mem_counter-1,""
        if self.op =="xor":
            _, left_mem_id, left_val = self.left.write_code(output_lines)
            _, right_mem_id, right_val = self.right.write_code(output_lines)
            #TODO same as sitofp 
            if left_val != "" and right_val != "":
                output_lines.append(
                    f"%{ProgramMemory.mem_counter} = xor i1 {left_val}, {right_val}"
                )
            elif left_val != "":
                output_lines.append(
                    f"%{ProgramMemory.mem_counter} = xor i1 {left_val}, %{right_mem_id}"
                )
            elif right_val != "":
                output_lines.append(
                    f"%{ProgramMemory.mem_counter} = xor i1 %{left_mem_id}, {right_val}"
                )
            else:
                output_lines.append(
                    f"%{ProgramMemory.mem_counter} = xor i1 %{left_mem_id}, %{right_mem_id}"
                )
            ProgramMemory.mem_counter+=1
            return Types.Bool, ProgramMemory.mem_counter-1,""

    def __write_code_comparison_operators(self, output_lines: list):
        left_type, left_mem_id, left_val = self.left.write_code(output_lines)
        _, right_mem_id, right_val = self.right.write_code(output_lines)
        if left_type == Types.Bool:
            args_type = "i1"
            prefix = "i"
        elif left_type == Types.Float:
            args_type = "double"
            prefix="f"
        elif left_type == Types.Int:
            args_type = "i32"
            prefix="i"
        operation = self.comparison_llvm_operators[(self.op, prefix)]
        #TODO same as sitofp 
        if right_val != "" and left_val!="":
            output_lines.append(f"%{ProgramMemory.mem_counter} = {prefix}cmp {operation} {args_type} {left_val} , {right_val}")
        elif right_val != "":
            output_lines.append(f"%{ProgramMemory.mem_counter} = {prefix}cmp {operation} {args_type} %{left_mem_id} , {right_val}")
        elif left_val != "":
            output_lines.append(f"%{ProgramMemory.mem_counter} = {prefix}cmp {operation} {args_type} {left_val} , %{right_mem_id}")
        else:
            output_lines.append(f"%{ProgramMemory.mem_counter} = {prefix}cmp {operation} {args_type} %{left_mem_id} , %{right_mem_id}")
        ProgramMemory.mem_counter+=1
        return Types.Bool, ProgramMemory.mem_counter-1, ""
            


    def write_code(self, output_lines: list):
        if self.op in ["+", "-", "*", "/"]:
            return self.__write_code_arithmetic_operation(output_lines)
        if self.op in ["and","or", "xor"]:
            return self.__write_code_logical_operators(output_lines)
        if self.op in ["==", ">", ">=", "<", "<="]:
            return self.__write_code_comparison_operators(output_lines)
        


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
    

class Length(Instruction):
    def __init__(self, line_no, value) -> None:
        super().__init__(line_no, value)
        self.type = "length"

    def check_semantics(self, variables_dict):
        if not self.left.name in variables_dict:
            print(f"ERROR: Undeclared variable (line: {self.line_no}) ")
            return (1, "")
        id_type = variables_dict[self.left.name]
        if id_type != Types.String:
            print(
                f"ERROR: Function length accepts only string type variables (line: {self.line_no}) "
            )
            return (1, "")
        return (0, Types.Int)
    
    def __str__(self, indent_level=0):
        return super().__str__(indent_level, f"({self.type})")
    
    def write_code(self, output_lines):
        _, var_mem_id, _ = self.left.write_code(output_lines)
        output_lines.append(
            f"%{ProgramMemory.increment_and_read_mem()} = call i64 @strlen(i8* %{var_mem_id})"
        )
        output_lines.append(
            f"%{ProgramMemory.increment_and_read_mem()} = trunc i64 %{ProgramMemory.mem_counter - 1} to i32"
        )

        return Types.Int, ProgramMemory.mem_counter - 1, ""