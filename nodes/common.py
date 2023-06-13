from enum import Enum


class ProgramMemory(object):
    string_count = 0
    mem_counter = 1
    labels_count = 1
    variables_dict = dict()
    header_lines = []
    str_alias = 1
    buffer_size = 16

    @classmethod
    def increment_and_read_mem(cls):
        cls.mem_counter+=1
        return cls.mem_counter-1
    
    @classmethod
    def increment_and_read_label(cls):
        cls.labels_count+=1
        return cls.labels_count-1
        


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
    def write_llvm_if(self, val, first_case_label,second_case_label):
        return f"br i1 {val}, label %l{first_case_label}, label %l{second_case_label}"
    
    def write_llvm_goto_label(self, label):
        return f"br label %l{label}"
    
    def write_llvm_label(self, label):
        return f"l{label}:"


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
            node_as_text += f" {indentation}{i}: {inst.__str__(indent_level)} \n"
        return node_as_text
    
    def check_semantics(self, variables_dict):
        for node in self.instructions:
            semantic_check, _ = node.check_semantics(variables_dict)
            if semantic_check != 0:
                return 1, ""
        return 0, ""
    
    def write_code(self, output_lines: list):
        for node in self.instructions:
            node.write_code(output_lines)
        return 0
    
    


class AST:
    def __init__(self, root: Instructions) -> None:
        self.root = root

    def check_semantic_errors(self):
        variables_dict = dict()
        if not self.root:
            return 0
        for node in self.root.instructions:
            if node.type == "init node":
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
        return 0

    def create_llvm_output(self, filename):
        output_lines = []
        # TODO Check if everything below is needed
        ProgramMemory.header_lines.append(f'@int = constant [ 3 x i8] c"%d\\00"')
        ProgramMemory.header_lines.append(f'@double = constant [ 4 x i8] c"%lf\\00"')
        ProgramMemory.header_lines.append(f'@True = constant [5 x i8 ] c"True\\00"')
        ProgramMemory.header_lines.append(f'@False = constant [6 x i8 ] c"False\\00"')
        ProgramMemory.header_lines.append(f'@strps = constant [4 x i8] c\"%s\\0A\\00\"')
        ProgramMemory.header_lines.append(f'@strs = constant [5 x i8] c\"%10s\\00\"')
        ProgramMemory.header_lines.append(f"")
        ProgramMemory.header_lines.append(f"declare i32 @printf(i8*, ...)")
        ProgramMemory.header_lines.append(f"declare i32 @scanf(i8*, ...)")
        ProgramMemory.header_lines.append(f"declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg)")
        ProgramMemory.header_lines.append(f"declare i64 @strlen(i8*)")
        ProgramMemory.header_lines.append(f"declare i8* @strcpy(i8*, i8*)")
        ProgramMemory.header_lines.append(f"declare i8* @strcat(i8*, i8*)")
        ProgramMemory.header_lines.append(f"declare i32 @__isoc99_scanf(i8*, ...)")
        ProgramMemory.header_lines.append(f"")
        output_lines.append(
            f"define dso_local i32 @main() #0 {{"
        )  # TODO do we really need dso_local param?
        if self.root == None:
            output_lines.append(f"ret i32 0")
            output_lines.append(f"}}")
            join_and_write_to_file_ll(filename, output_lines)
            return
        for node in self.root.instructions:
            if node.type == "init node":
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

        output_lines.append(f"ret i32 0")
        output_lines.append(f"}}")
        join_and_write_to_file_ll(filename, output_lines)
        return


def join_and_write_to_file_ll(filename, main_lines):
    ProgramMemory.header_lines.append(f"")
    header = "\n".join(ProgramMemory.header_lines)
    main = "\n".join(main_lines)
    data = header + "\n" + main
    with open(filename + ".ll", "w") as file:
        file.write(data)