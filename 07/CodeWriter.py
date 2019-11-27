CONST = "constant"
PUSH = "C_PUSH"
TEMP = "temp"
POINTER = "pointer"
STATIC = "static"
CALC = "13"


# _____________ CodeWriter Class _____________ #

# Translates VM commands into Hack assembly code
class CodeWriter:

    # dict for converting ram segments to ram indices
    __ram_dict = {
        "local": 1,
        "argument": 2,
        "this": 3,
        "that": 4,
        "pointer": 3,  # either this ot that
        "temp": 5,
        "static": 16
    }

    def __init__(self, out_file):
        """
        A constructor for this class
        :param out_file: The output file that's being written
        """
        self.out_file = open(out_file, "w+")
        self.f_name = out_file.replace(".hack", "")     # name for statics vars
        self.stack = []
        self.boolean_counter = 0

    def set_file_name(self, file_name):
        """
        Informs the class that the translation of a new VM file has started.
        :param file_name:
        :return:
        """
        # ???
        pass

    def write_arithmetic(self, command):
        """
        Writes a given command to the output file
        :param command: The fully processed ASM command
        """
        if command == "add":
            self._write_add()
        elif command == "sub":
            self._write_sub()
        elif command == "neg":
            self._write_negate()
        elif command == "eq":
            self._write_eq()
            self._write_false()
            self._write_true()
            self._write_func()
            self.boolean_counter += 1
        elif command == "gt":
            self._write_gt()
            self._write_false()
            self._write_true()
            self._write_func()
            self.boolean_counter += 1
        elif command == "lt":
            self._write_lt()
            self._write_false()
            self._write_true()
            self._write_func()
            self.boolean_counter += 1
        elif command == "and":
            self._write_and()
        elif command == "or":
            self._write_or()
        elif command == "not":
            self._write_not()

    def _write_negate(self):
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=-M" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")

    def _write_add(self):
        self._pop_stack_to_d()
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=M+D" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")

    def _write_false(self):
        self.out_file.write("(FALSE" + str(self.boolean_counter) + ")" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=0" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")
        self.out_file.write("@FUNC" + str(self.boolean_counter) + "\n")
        self.out_file.write("0;JMP" + "\n\n")

    def _write_func(self):
        self.out_file.write("(FUNC" + str(self.boolean_counter) + ")" + "\n")

    def _write_true(self):
        self.out_file.write("(TRUE" + str(self.boolean_counter) + ")" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=-1" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")
        self.out_file.write("@FUNC" + str(self.boolean_counter) + "\n")
        self.out_file.write("0;JMP" + "\n\n")

    def _write_eq(self):
        self._write_bool()
        self.out_file.write("@TRUE" + str(self.boolean_counter) + "\n")
        self.out_file.write("D;JEQ" + "\n")
        self.out_file.write("@FALSE" + str(self.boolean_counter) + "\n")
        self.out_file.write("D;JNE" + "\n")

    def _write_lt(self):
        self._write_bool()
        self.out_file.write("@TRUE" + str(self.boolean_counter) + "\n")
        self.out_file.write("D;JLT" + "\n")
        self.out_file.write("@FALSE" + str(self.boolean_counter) + "\n")
        self.out_file.write("D;JGE" + "\n")

    def _write_gt(self):
        self._write_bool()
        self.out_file.write("@TRUE" + str(self.boolean_counter) + "\n")
        self.out_file.write("D;JGT" + "\n")
        self.out_file.write("@FALSE" + str(self.boolean_counter) + "\n")
        self.out_file.write("D;JLE" + "\n")

    def _write_not(self):
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=!M" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")

    def _write_and(self):
        self._pop_stack_to_d()
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=M&D" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")

    def _write_or(self):
        self._pop_stack_to_d()
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=M|D" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")

    def _write_bool(self):
        self._pop_stack_to_d()
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("D=M-D" + "\n")

    def _write_sub(self):
        self._pop_stack_to_d()
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=M-D" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")

    def _pop_stack_to_d(self):
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
        if command == PUSH:
            self._write_push(segment, index)
        else:
            self._write_pop(segment, index)

    def _read_from_A(self, index):
        """ reads the given index as A """
        self.out_file.write("@" + str(index) + "\n")
        self.out_file.write("D=A" + "\n")

    def _read_from_address(self, address):
        """ reads the given index as M (from R at address) """
        self.out_file.write("@" + str(address) + "\n")
        self.out_file.write("D=M" + "\n")

    def _write_push(self, segment, index):
        """
        Writes a fully push command
        :param segment: The segment of the given push command
        :param index: The index of the given push command
        """
        if segment == CONST:
            # copy A content to D
            self._read_from_A(index)

        elif segment == TEMP or segment == POINTER:
            # copy temp / pointer content to D
            self._read_from_address(self.__ram_dict[segment] + int(index))

        elif segment == STATIC:
            # copy static content to D
            self._read_from_address(self.f_name + "." + str(index))

        else:
            # copy content from address held in pointer to D
            self._read_from_address(self.__ram_dict[segment])
            self.out_file.write("@" + CALC + "\n")
            self.out_file.write("M=D" + "\n")
            self._read_from_A(index)
            self.out_file.write("@" + CALC + "\n")
            self.out_file.write("A=M+D" + "\n")
            self.out_file.write("D=M" + "\n")

        # push D content to stack
        self._push_D()

    def _push_D(self):
        self.out_file.write("@SP" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=D" + "\n")
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M+1" + "\n")

    def _write_pop(self, segment, index):
        """
        Writes a fully pop command
        :param segment: The segment of the given pop command
        :param index: The index of the given pop command
        """
        if segment == TEMP or segment == POINTER:
            # calc dest of temp / pointer
            self._read_from_A(self.__ram_dict[segment] + int(index))
            self.out_file.write("@" + CALC + "\n")
            self.out_file.write("M=D" + "\n")

        elif segment == STATIC:
            # calc dest of static
            self._read_from_A(self.f_name + "." + str(index))
            self.out_file.write("@" + CALC + "\n")
            self.out_file.write("M=D" + "\n")

        else:
            # calc dest of segment
            self._read_from_address(str(self.__ram_dict[segment]))
            self.out_file.write("@" + CALC + "\n")
            self.out_file.write("M=D" + "\n")
            self._read_from_A(index)
            self.out_file.write("@" + CALC + "\n")
            self.out_file.write("M=M+D" + "\n")

        self._pop_to_dest()

    def _pop_to_dest(self):
        # add commands for popping stack val to R13 address content
        self.out_file.write("@SP" + "\n")
        self.out_file.write("M=M-1" + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("D=M" + "\n")
        self.out_file.write("@" + CALC + "\n")
        self.out_file.write("A=M" + "\n")
        self.out_file.write("M=D" + "\n")

    def _get_symbol(self, segment):
        """
        Gets the ram address of given segment + index
        :param segment: The given segment
        :return: if segment is a constant, returns the index.
        Else, returns the ram address of the given segment + index
        """
        if isinstance(segment, int):
            return segment

        # get the predefined base register of the given segment
        base_address = CodeWriter.__ram_dict[segment]
        return str(int(base_address))

    def close(self):
        """
        closes the CodeWriter's output file
        """
        self.out_file.close()
