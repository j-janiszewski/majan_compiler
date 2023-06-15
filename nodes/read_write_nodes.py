from .common import Instruction, Types, ProgramMemory


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
            then_label = ProgramMemory.increment_and_read_label()
            else_label = ProgramMemory.increment_and_read_label()
            end_label = ProgramMemory.increment_and_read_label()
            if val != "":
                self.write_llvm_if(output_lines, val, then_label, else_label)
            else:
                self.write_llvm_if(output_lines, f"%{mem_id}", then_label, else_label)
            self.write_llvm_label(output_lines, then_label)
            output_lines.append(
                "call i32(i8*, ...) @printf(i8* bitcast([5 x i8]* @True   to i8 *), i32 5)"
            )
            ProgramMemory.mem_counter += 1
            self.write_llvm_goto_label(output_lines, end_label)
            self.write_llvm_label(output_lines, else_label)
            output_lines.append(
                "call i32(i8*, ...) @printf(i8* bitcast([6 x i8]* @False   to i8 *), i32 5)"
            )
            ProgramMemory.mem_counter += 1
            self.write_llvm_goto_label(output_lines, end_label)
            self.write_llvm_label(output_lines, end_label)
        if type == Types.String:
            # No need to load mem_id before, because we are printing from dispatched variable
            ProgramMemory.mem_counter += 1
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
        if type == Types.String:
            output_lines.append(
                f"%{ProgramMemory.mem_counter} = alloca [{ProgramMemory.buffer_size + 1} x i8]"
            )
            mem_str = ProgramMemory.mem_counter
            ProgramMemory.mem_counter += 1
            output_lines.append(
                f"%{ProgramMemory.mem_counter} = getelementptr inbounds [{ProgramMemory.buffer_size + 1} x i8], [{ProgramMemory.buffer_size + 1} x i8]* %{mem_str}, i64 0, i64 0"
            )
            ProgramMemory.mem_counter += 1
            output_lines.append(
                f"store i8* %{ProgramMemory.mem_counter - 1}, i8** %{ident_id}"
            )
            output_lines.append(
                f"%{ProgramMemory.mem_counter} = call i32 (i8*, ...) @scanf(i8* getelementptr inbounds ([5 x i8], [5 x i8]* @strs, i32 0, i32 0), i8* %{ProgramMemory.mem_counter - 1})"
            )
            ProgramMemory.mem_counter += 1
            ProgramMemory.variables_dict[self.left.name] = (
                type,
                ProgramMemory.buffer_size,
                ident_id,
            )
        return 0
