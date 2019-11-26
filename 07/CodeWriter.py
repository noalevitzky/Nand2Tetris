CONST = "constant"
PUSH_CMD = "C_PUSH"
TMP = "temp"
class CodeWriter:

    #todo Check what's the ram address for the static segment
    __register_seg_dict__ = {"argument":2, "local":1, "this":3, "that":4, "temp":5}



    def __init__(self, out_file):
        """
        A constructor for this class
        :param out_file: The output file that's being written
        """
        self.out_file = open(out_file, "w+")
        self.stack = []
        self.boolean_counter = 0


    def set_file_name(self, file_name):
        """
        Informs the class that the translation of a new VM file has started.
        :param file_name:
        :return:
        """
        #???
        pass

    def write_arithmetic(self, command):
        """
        Writes a given command to the output file
        :param command: The fully processed ASM command
        """
        if command == "add":
            self.write_add()
        elif command == "sub":
            self.write_sub()
        elif command == "neg":
            self.write_negate()
        elif command == "eq":
            self.write_eq()
            self.set_false()
            self.set_true()
            self.set_func()
            self.boolean_counter += 1
        elif command == "gt":
            self.write_gt()
            self.set_false()
            self.set_true()
            self.set_func()
            self.boolean_counter += 1
        elif command == "lt":
            self.write_lt()
            self.set_false()
            self.set_true()
            self.set_func()
            self.boolean_counter += 1
        elif command == "and":
            self.write_and()
        elif command == "or":
            self.write_or()
        elif command == "not":
            self.write_not()

    def write_negate(self):
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=-M" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")

    def write_add(self):
        self.pop_stack_to_d()
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=M+D" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")

    def set_false(self):
        self.out_file.write("(FALSE" + str(self.boolean_counter) + ")" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=0" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")
        self.out_file.write("@FUNC" + str(self.boolean_counter) + "\n")
        self.out_file.write("0;JMP" + "\n\n")

    def set_func(self):
        self.out_file.write("(FUNC" + str(self.boolean_counter) + ")" + "\n")

    def set_true(self):
        self.out_file.write("(TRUE" + str(self.boolean_counter) + ")" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=-1" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")
        self.out_file.write("@FUNC" + str(self.boolean_counter) + "\n")
        self.out_file.write("0;JMP" + "\n\n")

    def write_eq(self):
        self.set_boolean()
        self.out_file.write("@TRUE" + str(self.boolean_counter) + "\n")
        self.out_file.write("D;JEQ" + "\n")
        self.out_file.write("@FALSE" + str(self.boolean_counter) + "\n")
        self.out_file.write("D;JNE" + "\n")

    def write_lt(self):
        self.set_boolean()
        self.out_file.write("@TRUE" + str(self.boolean_counter) + "\n")
        self.out_file.write("D;JLT" + "\n")
        self.out_file.write("@FALSE" + str(self.boolean_counter) + "\n")
        self.out_file.write("D;JGE" + "\n")

    def write_gt(self):
        self.set_boolean()
        self.out_file.write("@TRUE" + str(self.boolean_counter) + "\n")
        self.out_file.write("D;JGT" + "\n")
        self.out_file.write("@FALSE" + str(self.boolean_counter) + "\n")
        self.out_file.write("D;JLE" + "\n")

    def write_not(self):
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=!M" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")

    def write_and(self):
        self.pop_stack_to_d()
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("D=M&D" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")

    def write_or(self):
        self.pop_stack_to_d()
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("D=M|D" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")

    def set_boolean(self):
        self.pop_stack_to_d()
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("D=M-D" + "\n")

    def write_sub(self):
        """
        Writes a given command to the output file
        :param command: The fully processed ASM command
        """
        self.pop_stack_to_d()
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=M-D" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")

    def pop_stack_to_d(self):
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("D=M" + "\n")

    def write_push_pop(self, command, segment, index):
        """
        Writes a push/pop command
        :param command: The command type (push/pop)
        :param segment: The segment of the given command
        :param index: The index of the given command
        """
        if command == PUSH_CMD:
            self.write_push_cmd(segment, index)
        else:
            self.write_pop_cmd(segment, index)


    def write_push_cmd(self, segment, index):
        """
        Writes a fully push command
        :param segment: The segment of the given push command
        :param index: The index of the given push command
        """
        ram_address = self.get_symbol(segment, index)
        # writes @ram_address
        self.out_file.write("@" + str(ram_address)+"\n")
        if segment == CONST:
            self.out_file.write("D=A"+"\n")
        else:
            self.out_file.write("D=M"+"\n")
        self.out_file.write("@SP"+"\n")
        self.out_file.write("A=M"+"\n")
        self.out_file.write("M=D"+"\n")
        self.out_file.write("@SP"+"\n")
        self.out_file.write("M=M+1"+"\n")

    def write_pop_cmd(self, segment, index):
        """
        Writes a fully pop command
        :param segment: The segment of the given pop command
        :param index: The index of the given pop command
        """
        self.out_file.write("@SP"+"\n")
        self.out_file.write("M=M-1"+"\n")
        self.out_file.write("A=M"+"\n")
        self.out_file.write("D=M"+"\n")
        ram_address = self.get_symbol(segment, index)
        self.out_file.write("@" + str(ram_address)+"\n")
        self.out_file.write("M=D"+"\n")


    def get_symbol(self, segment, index):
        """
        Gets the ram address of given segment + index
        :param segment: The given segment
        :param index: The given index
        :return: if segment is a constant, returns the index.
        Else, returns the ram address of the given segment + index
        """
        if isinstance(segment, int):
            return segment
        if segment == CONST:
            return index
        # get the predefined base register of the given segment
        base_address = CodeWriter.__register_seg_dict__[segment]
        return str(int(base_address) + int(index))


    def close(self):
        """
        closes the CodeWriter's output file
        """
        self.out_file.close()
