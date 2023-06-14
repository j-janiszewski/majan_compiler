from .common import Instruction, Types, ProgramMemory


class If(Instruction):
    def __init__(self, line_no, condition ) -> None:
        super().__init__(line_no)
        self.condition = condition
        self.type = "if node"

    def __str__(self, indent_level=0):
        indentation = " " * 4 * indent_level
        node_as_text = f"{indentation}{self.type} node"
        node_as_text += "\nCondition:"
        node_as_text+= f"\n{self.condition.__str__(indent_level+1)}"
        node_as_text+="\nIf branch:"
        node_as_text+=f"\n{self.left.__str__(indent_level+1)}"
        if self.right:
            node_as_text+="\nElse branch:"
            node_as_text+=f"\n{self.right.__str__(indent_level+1)}"
        return node_as_text


    def check_semantics(self, variables_dict):
        cond_semantic_check, cond_type = self.condition.check_semantics(variables_dict)
        if cond_type != Types.Bool:
            print(f"ERROR: {cond_type} passed as a condition for if (line: {self.line_no})")
            return (1, "")
        if cond_semantic_check!= 0:
            return (1, "")
        left_semantic_check, _= self.left.check_semantics(variables_dict)
        if left_semantic_check != 0:
            return (1, "")
        if self.right:
            right_semantic_check, _= self.right.check_semantics(variables_dict)
            if right_semantic_check != 0:
                return (1, "")
        return 0, ""
    
    def write_code(self, output_lines: list):
        cond_type, cond_mem_id, cond_val = self.condition.write_code(output_lines)
        then_label = ProgramMemory.labels_count
        if self.right:
            else_label = ProgramMemory.labels_count+1
            end_label = ProgramMemory.labels_count+2
            ProgramMemory.labels_count+=3
            if cond_val!="":
                output_lines.append(f"br i1 {cond_val}, label %l{then_label}, label %l{else_label}")
            else:
                output_lines.append(f"br i1 %{cond_mem_id}, label %l{then_label}, label %l{else_label}")
            output_lines.append(f"l{then_label}:")
            self.left.write_code(output_lines)
            output_lines.append(f"br label %l{end_label}")
            output_lines.append(f"l{else_label}:")
            self.right.write_code(output_lines)
        else:
            end_label = ProgramMemory.labels_count+1
            ProgramMemory.labels_count+=2
            if cond_val!="":
                output_lines.append(f"br i1 {cond_val}, label %l{then_label}, label %l{end_label}")
            else:
                output_lines.append(f"br i1 %{cond_mem_id}, label %l{then_label}, label %l{end_label}")
            output_lines.append(f"l{then_label}:")
            self.left.write_code(output_lines)

        output_lines.append(f"br label %l{end_label}")
        output_lines.append(f"l{end_label}:")
        return 0


class Function(Instruction):
    def __init__(self, line_no, name, return_type) -> None:
        super().__init__(line_no)
        self.name = name
        self.return_type = return_type
        self.type = "function node"

    def write_code(self, output_lines: list):
        ProgramMemory.global_var = False



        output_lines.extend(ProgramMemory.buffer) # TODO check how works
        ProgramMemory.global_var = True
        ProgramMemory.temp_mem_id = 1
        ProgramMemory.buffer = []
        return 0
    
