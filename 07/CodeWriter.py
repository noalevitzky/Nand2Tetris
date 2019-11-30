CONST = "constant"
PUSH = "C_PUSH"
TEMP = "temp"
POINTER = "pointer"
STATIC = "static"
CALC = "13"
CLOSING_BRACKET = ")"

# _______________ Assembly Commands _______________#

# _____M Commands______ #
M_MINUS_1 = "M=M-1"
M_PLUS_1 = "M=M+1"
M_ZERO = "M=0"
M_NEGATE = "M=-M"
M_NOT = "M=!M"
M_IS_MINUS_1 = "M=-1"
M_D = "M=D"
M_PLUS_D = "M=M+D"
M_MINUS_D = "M=M-D"
M_M_AND_D = "M=M&D"
M_OR_D = "M=M|D"

# _____ A Commands______ #
A_M = "A=M"
A_M_PLUS_D = "A=M+D"

# _____D Commands______ #
D_A = "D=A"
D_M = "D=M"
D_M_MINUS_D = "D=M-D"
D_MINUS_M = "D=D-M"

# _____@ Commands______ #
AT = "@"
AT_SP = "@SP"
AT_FUNC = "@FUNC"
AT_TRUE = "@TRUE"
AT_FALSE = "@FALSE"
AT_TEMP = "@R14"
AT_Y_LE = "@Y_LE"
AT_Y_GT = "@Y_GT"
AT_END = "@END"

# _____Jump Commands______ #
JMP = "0;JMP"
JEQ = "D;JEQ"
JGT = "D;JGT"
JGE = "D;JGE"
JLT = "D;JLT"
JLE = "D;JLE"
JNE = "D;JNE"

# _____Boolean & function Commands______ #
FALSE = "(FALSE"
TRUE = "(TRUE"
FUNC = "(FUNC"
Y_GT = "(Y_GT"
Y_LE = "(Y_LE"
END = "(END)"


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
        self.f_name = out_file.replace(".hack", "")  # name for statics vars
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
            return
        elif command == "sub":
            self._write_sub()
            return
        elif command == "neg":
            self._write_negate()
            return
        elif command == "and":
            self._write_and()
            return
        elif command == "or":
            self._write_or()
            return
        elif command == "not":
            self._write_not()
            return
        elif command == "eq":
            self._write_eq()
        elif command == "gt":
            self._write_gt()
        elif command == "lt":
            self._write_lt()
        self._write_false()
        self._write_true()
        self._write_func()
        self.boolean_counter += 1

    def _write_negate(self):
        """
        Writes the negation of the stack's last item
        """
        cmd_block = []
        # fill the cmd_block with the rest of the relevant commands
        cmd_block.extend([AT_SP, M_MINUS_1, A_M, M_NEGATE, AT_SP, M_PLUS_1])
        # write the commands to the out file
        self.write_block(cmd_block)

    def _write_add(self):
        """
        Writes the addition of the stack's last two item
        """
        cmd_block = self._pop_stack_to_d([])
        # fill the cmd_block with the rest of the relevant commands
        cmd_block.extend([AT_SP, M_MINUS_1, A_M, M_PLUS_D, AT_SP, M_PLUS_1])
        # write the commands to the out file
        self.write_block(cmd_block)

    def _write_false(self):
        """
        Writes a false function
        """
        cmd_block = []
        # get the current false function number
        current_false = self.get_current_func_name(FALSE)
        current_func = AT_FUNC + str(self.boolean_counter)
        # write the commands to the out file
        cmd_block.extend(
            [current_false, AT_SP, A_M, M_ZERO, AT_SP, M_PLUS_1, current_func,
             JMP])
        self.write_block(cmd_block)

    def get_current_func_name(self, func_name):
        """
        Completes the string of the given func_name according the the
        current boolean counter
        :param func_name: the name of the given function
        :return: The completed function name
        """
        return func_name + str(self.boolean_counter) + CLOSING_BRACKET

    def _write_func(self):
        """
        Writes the current function's name
        """
        self.write_block([self.get_current_func_name(FUNC)])

    def _write_true(self):
        """
        Writes a current "true" loop
        """
        cmd_block = []
        # get the current true loop name
        current_true = self.get_current_func_name(TRUE)
        # get the current func loop name
        current_func = AT_FUNC + str(self.boolean_counter)
        cmd_block.extend(
            [current_true, AT_SP, A_M, M_IS_MINUS_1, AT_SP, M_PLUS_1,
             current_func,
             JMP])
        # write the commands to the out file
        self.write_block(cmd_block)

    def _write_eq(self):

        cmd_block = self._get_bool([])
        current_true = AT_TRUE + str(self.boolean_counter)
        current_false = AT_FALSE + str(self.boolean_counter)
        cmd_block.extend([current_true, JEQ, current_false, JNE])
        self.write_block(cmd_block)

    def _write_lt(self):
        cmd_block = self._pop_stack_to_d([])
        cmd_block.extend([AT_TEMP, M_D])
        curr_func_ygt = AT_Y_GT + str(self.boolean_counter)
        curr_func_yle = AT_Y_LE + str(self.boolean_counter)
        # get the fitting commands for the ylt loop and yge loop
        curr_loop_ygt = self.lt_get_ygt_loop(
            AT_TRUE + str(self.boolean_counter),
            AT_FALSE + str(self.boolean_counter))
        curr_loop_yle = self.lt_get_yle_loop(
            AT_TRUE + str(self.boolean_counter),
            AT_FALSE + str(self.boolean_counter))
        cmd_block.extend([curr_func_ygt, JGT, curr_func_yle, JLE])
        cmd_block.extend(curr_loop_ygt)
        cmd_block.extend(curr_loop_yle)
        self.write_block(cmd_block)

    def lt_get_ygt_loop(self, curr_true, curr_false):
        cmd_block = [self.get_current_func_name(Y_GT)]
        cmd_block.extend(self._pop_stack_to_d([]))
        cmd_block.extend(
            [curr_true, JLE, AT_TEMP, D_MINUS_M, curr_true, JLT, curr_false,
             JGE])
        return cmd_block

    def lt_get_yle_loop(self, curr_true, curr_false):
        cmd_block = [self.get_current_func_name(Y_LE)]
        cmd_block.extend(self._pop_stack_to_d([]))
        cmd_block.extend(
            [curr_false, JGT, AT_TEMP, D_MINUS_M, curr_true, JLT, curr_false,
             JGE])
        return cmd_block

    def _write_gt(self):
        cmd_block = self._pop_stack_to_d([])
        cmd_block.extend([AT_TEMP, M_D])
        curr_func_ygt = AT_Y_GT + str(self.boolean_counter)
        curr_func_yle = AT_Y_LE + str(self.boolean_counter)
        # get the fitting commands for the ygt loop and yle loop
        curr_loop_ygt = self.gt_get_ygt_loop(
            AT_TRUE + str(self.boolean_counter),
            AT_FALSE + str(self.boolean_counter))
        curr_loop_yle = self.gt_get_yle_loop(
            AT_TRUE + str(self.boolean_counter),
            AT_FALSE + str(self.boolean_counter))
        cmd_block.extend(
            [curr_func_ygt, JGT, curr_func_yle, JLE])
        cmd_block.extend(curr_loop_ygt)
        cmd_block.extend(curr_loop_yle)
        self.write_block(cmd_block)

    def gt_get_ygt_loop(self, curr_true, curr_false):
        cmd_block = [self.get_current_func_name(Y_GT)]
        cmd_block.extend(self._pop_stack_to_d([]))
        cmd_block.extend(
            [curr_false, JLE, AT_TEMP, D_MINUS_M, curr_true, JGT, curr_false,
             JLE])
        return cmd_block

    def gt_get_yle_loop(self, curr_true, curr_false):
        cmd_block = [self.get_current_func_name(Y_LE)]
        cmd_block.extend(self._pop_stack_to_d([]))
        cmd_block.extend(
            [curr_true, JGT, AT_TEMP, D_MINUS_M, curr_true, JGT, curr_false,
             JLE])
        return cmd_block

    def _write_not(self):
        cmd_block = []
        cmd_block.extend([AT_SP, M_MINUS_1, A_M, M_NOT, AT_SP, M_PLUS_1])
        self.write_block(cmd_block)

    def _write_and(self):
        cmd_block = self._pop_stack_to_d([])
        cmd_block.extend([AT_SP, M_MINUS_1, A_M, M_M_AND_D, AT_SP, M_PLUS_1])
        self.write_block(cmd_block)

    def _write_or(self):
        cmd_block = self._pop_stack_to_d([])
        cmd_block.extend([AT_SP, M_MINUS_1, A_M, M_OR_D, AT_SP, M_PLUS_1])
        self.write_block(cmd_block)

    def _get_bool(self, cmd_block):
        curr_block = self._pop_stack_to_d(cmd_block)
        curr_block.extend([AT_SP, M_MINUS_1, A_M, D_M_MINUS_D])
        return curr_block

    def _write_sub(self):
        cmd_block = self._pop_stack_to_d([])
        cmd_block.extend([AT_SP, M_MINUS_1, A_M, M_MINUS_D, AT_SP, M_PLUS_1])
        self.write_block(cmd_block)

    def _pop_stack_to_d(self, cmd_block):
        """
        Adds assembly commands that pop the stack's last item to D.
        :param cmd_block: List of the Assembly commands
        :return: A list of the given Assembly followed by popping the
         stack's last item to D
        """
        cmd_block.extend([AT_SP, M_MINUS_1, A_M, D_M])
        return cmd_block

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
        cmd_block = []
        cmd_block.extend([AT + str(index), D_A])
        self.write_block(cmd_block)

    def _read_from_address(self, address):
        """ reads the given index as M (from R at address) """
        cmd_block = []
        cmd_block.extend([AT + str(address), D_M])
        self.write_block(cmd_block)

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
            cmd_block_1, cmd_block_2 = [], []
            cmd_block_1.extend([AT + CALC, M_D])
            self.write_block(cmd_block_1)

            self._read_from_A(index)
            cmd_block_2.extend([AT + CALC, A_M_PLUS_D, D_M])
            self.write_block(cmd_block_2)

        # push D content to stack
        self._push_D()

    def _push_D(self):
        cmd_block = []
        cmd_block.extend([AT_SP, A_M, M_D, AT_SP, M_PLUS_1])
        self.write_block(cmd_block)

    def _write_pop(self, segment, index):
        """
        Writes a fully pop command
        :param segment: The segment of the given pop command
        :param index: The index of the given pop command
        """
        cmd_block = []
        if segment == TEMP or segment == POINTER:
            # calc dest of temp / pointer
            self._read_from_A(self.__ram_dict[segment] + int(index))
            cmd_block.extend([AT + CALC, M_D])
            self.write_block(cmd_block)

        elif segment == STATIC:
            # calc dest of static
            self._read_from_A(self.f_name + "." + str(index))
            cmd_block.extend([AT + CALC, M_D])
            self.write_block(cmd_block)

        else:
            # calc dest of segment
            self._read_from_address(str(self.__ram_dict[segment]))
            cmd_block.extend([AT + CALC, M_D])
            self.write_block(cmd_block)

            self._read_from_A(index)
            cmd_block.clear()
            cmd_block.extend([AT + CALC, M_PLUS_D])
            self.write_block(cmd_block)
        self._pop_to_dest()

    def _pop_to_dest(self):
        # add commands for popping stack val to R13 address content
        cmd_block = []
        cmd_block.extend([AT_SP, M_MINUS_1, A_M, D_M, AT + CALC, A_M, M_D])
        self.write_block(cmd_block)

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

    def write_block(self, cmd_block):
        """
        Writes a full block of assembly commands
        :param cmd_block: A list containing all the block's assembly commands
        """
        for line in cmd_block:
            self.out_file.write(line + "\n")

    #        self.out_file.write("\n")

    def close(self):
        """
        closes the CodeWriter's output file
        """
        cmd_block = []
        cmd_block.extend([AT_END, JMP, END, JMP])
        self.write_block(cmd_block)
        self.out_file.close()
