from .common import Instruction, Types, ProgramMemory
from .values_nodes import IntValue, FloatValue, Variable


class While(Instruction):
    def __init__(self, line_no, condition, left) -> None:
        super().__init__(line_no, left)
        self.condition = condition
        self.type = "while node"

    def __str__(self, indent_level=0):
        indentation = " " * 4 * indent_level
        node_as_text = f"{indentation}{self.type} node"
        node_as_text += f"\n{indentation}Condition:"
        node_as_text += f"\n{self.condition.__str__(indent_level+1)}"
        node_as_text += f"\n{indentation}Loop body:"
        node_as_text += f"\n{self.left.__str__(indent_level+1)}"
        return node_as_text

    def check_semantics(self, variables_dict):
        cond_semantic_check, cond_type = self.condition.check_semantics(variables_dict)
        if cond_type != Types.Bool:
            print(
                f"ERROR: {cond_type} passed as a condition for if (line: {self.line_no})"
            )
            return (1, "")
        if cond_semantic_check != 0:
            return (1, "")
        left_semantic_check, _ = self.left.check_semantics(variables_dict)
        if left_semantic_check != 0:
            return (1, "")
        return 0, ""

    def write_code(self, output_lines: list):
        cond_label = ProgramMemory.increment_and_read_label()
        loop_label = ProgramMemory.increment_and_read_label()
        end_label = ProgramMemory.increment_and_read_label()
        self.write_llvm_goto_label(output_lines, cond_label)
        self.write_llvm_label(output_lines, cond_label)
        _, cond_mem_id, cond_val = self.condition.write_code(output_lines)
        if cond_val != "":
            self.write_llvm_if(output_lines, cond_val, loop_label, end_label)
        else:
            self.write_llvm_if(output_lines, f"%{cond_mem_id}", loop_label, end_label)
        self.write_llvm_label(output_lines, loop_label)
        self.left.write_code(output_lines)
        self.write_llvm_goto_label(output_lines, cond_label)
        self.write_llvm_label(output_lines, end_label)
        return 0


class If(Instruction):
    def __init__(self, line_no, condition, left, right=None) -> None:
        super().__init__(line_no, left, right)
        self.condition = condition
        self.type = "if node"

    def __str__(self, indent_level=0):
        indentation = " " * 4 * indent_level
        node_as_text = f"{indentation}{self.type} node"
        node_as_text += f"\n{indentation}Condition:"
        node_as_text += f"\n{self.condition.__str__(indent_level+1)}"
        node_as_text += f"\n{indentation}If branch:"
        node_as_text += f"\n{self.left.__str__(indent_level+1)}"
        if self.right:
            node_as_text += f"\n{indentation}Else branch:"
            node_as_text += f"\n{self.right.__str__(indent_level+1)}"
        return node_as_text

    def check_semantics(self, variables_dict):
        cond_semantic_check, cond_type = self.condition.check_semantics(variables_dict)
        if cond_type != Types.Bool:
            print(
                f"ERROR: {cond_type} passed as a condition for if (line: {self.line_no})"
            )
            return (1, "")
        if cond_semantic_check != 0:
            return (1, "")
        left_semantic_check, _ = self.left.check_semantics(variables_dict)
        if left_semantic_check != 0:
            return (1, "")
        if self.right:
            right_semantic_check, _ = self.right.check_semantics(variables_dict)
            if right_semantic_check != 0:
                return (1, "")
        return 0, ""

    def write_code(self, output_lines: list):
        _, cond_mem_id, cond_val = self.condition.write_code(output_lines)
        then_label = ProgramMemory.increment_and_read_label()
        if self.right:
            else_label = ProgramMemory.increment_and_read_label()
            end_label = ProgramMemory.increment_and_read_label()
            if cond_val != "":
                self.write_llvm_if(output_lines, cond_val, then_label, else_label)
            else:
                self.write_llvm_if(
                    output_lines, f"%{cond_mem_id}", then_label, else_label
                )
            self.write_llvm_label(output_lines, then_label)
            self.left.write_code(output_lines)
            self.write_llvm_goto_label(output_lines, end_label)
            self.write_llvm_label(output_lines, else_label)
            self.right.write_code(output_lines)
        else:
            end_label = ProgramMemory.increment_and_read_label()
            if cond_val != "":
                self.write_llvm_if(output_lines, cond_val, then_label, end_label)
            else:
                self.write_llvm_if(
                    output_lines, f"%{cond_mem_id}", then_label, end_label
                )
            self.write_llvm_label(output_lines, then_label)
            self.left.write_code(output_lines)
        self.write_llvm_goto_label(output_lines, end_label)
        self.write_llvm_label(output_lines, end_label)
        return 0


class Function(Instruction):
    def __init__(self, line_no, name, return_type, return_node) -> None:
        super().__init__(line_no)
        self.name = name
        self.return_type = return_type
        self.type = "function node"
        self.return_node = return_node

    def check_semantics(self, variables_dict):  # TODO
        if self.return_type not in [Types.Int, Types.Float]:
            return (1, "")
        right_semantic_check, _= self.right.check_semantics(variables_dict)
        if right_semantic_check != 0:
            return (1, "")
        return (0, "")

    def write_code(self, output_lines: list):
        ProgramMemory.global_var = False
        ProgramMemory.main_mem_count = ProgramMemory.mem_counter
        ProgramMemory.mem_counter = 1
        ProgramMemory.local_var_dict.clear()

        ret_type = "i32"    # default case, returns int
        if self.return_type == "float":
            ret_type = "double"

        params = self.get_params()

        ProgramMemory.buffer.append(f"define {ret_type} @{self.name}({params}) nounwind {{")

        next = self.left
        while next:
            ProgramMemory.local_var_dict[next.name] = (
                next.variable_type,
                0,
                ProgramMemory.mem_counter,
            )
            next.write_param_code(ProgramMemory.buffer, next.name)
            next = next.left

        if self.right:
            self.right.write_code(ProgramMemory.buffer)
        self.write_return_code(ProgramMemory.buffer, ret_type)

        ProgramMemory.buffer.append(f"}}\n")
        ProgramMemory.function_lines.extend(ProgramMemory.buffer)

        ProgramMemory.global_var = True
        ProgramMemory.mem_counter = ProgramMemory.main_mem_count
        ProgramMemory.main_mem_count = 1
        ProgramMemory.buffer = []
        ProgramMemory.local_var_dict.clear()
        return 0
    
    def get_params(self):
        params = []
        next = self.left
        while next:
            if next.variable_type is Types.Int:
                params.append(f"i32 %{next.name}")
            elif next.variable_type is Types.Float:
                params.append(f"double %{next.name}")
            next = next.left
        return ", ".join(params)
    
    def write_return_code(self, output_lines, return_type):
        if isinstance(self.return_node, IntValue):
            output_lines.append(f"ret {return_type} {self.return_node.value}")
        elif isinstance(self.return_node, FloatValue):
            output_lines.append(f"ret {return_type} {self.return_node.value}")
        elif isinstance(self.return_node, Variable):
            if self.return_node.name in ProgramMemory.local_var_dict:
                var_type, _, var_mem_id = ProgramMemory.local_var_dict[self.return_node.name]
                if var_type is Types.Int:                   
                    output_lines.append(f"%{ProgramMemory.mem_counter} = load i32, i32* %{var_mem_id}, align 4")
                elif var_type is Types.Float:
                    output_lines.append(f"%{ProgramMemory.mem_counter} = load double, double* %{var_mem_id}, align 8")
                output_lines.append(f"ret {return_type} %{ProgramMemory.increment_and_read_mem()}")
            elif self.return_node.name in ProgramMemory.variables_dict:
                var_type, _, var_mem_id = ProgramMemory.variables_dict[self.return_node.name]
                if var_type is Types.Int:                   
                    output_lines.append(f"%{ProgramMemory.mem_counter} = load i32, i32* @g{var_mem_id}, align 4")
                elif var_type is Types.Float:
                    output_lines.append(f"%{ProgramMemory.mem_counter} = load double, double* @g{var_mem_id}, align 8")
                output_lines.append(f"ret {return_type} %{ProgramMemory.increment_and_read_mem()}")
            else:
                print(f"ERROR: Function {self.name} has invalid return - variable not found: local > global")
        else:
            print(f"ERROR: Function {self.name} has invalid return.")

    
