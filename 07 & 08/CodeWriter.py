CONST = "constant"
PUSH = "C_PUSH"
TEMP = "temp"
POINTER = "pointer"
STATIC = "static"
CALC = "13"
CLOSING_BRACKET = ")"
ARG = "argument"
SP_INIT = "256"

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
A_D = "A=D"

# _____D Commands______ #
D_A = "D=A"
D_M = "D=M"
D_M_MINUS_D = "D=M-D"
D_MINUS_M = "D=D-M"
D_PLUS_M = "D=D+M"
D_MINUS_A = "D=D-A"
D_PLUS_A = "D=D+A"

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

# _____function Commands______ #
LABEL = "(%s)"
IF_GOTO = "if-false-goto %s"


# _____________ CodeWriter Class _____________ #

# Translates VM commands into Hack assembly code
class CodeWriter:
    # dict for converting ram segments to ram indices
    __ram_dict = {
        "sp": 0,
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
        self._return_address_counter = 0
        self.cur_file = ""
        self.cur_func = ""

    def set_file_name(self, file_name):
        """
        Informs the class that the translation of a new VM file has started.
        :param file_name:
        :return:
        """
        self.cur_file = file_name

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
        cmd_block = [AT_SP, M_MINUS_1, A_M, M_NEGATE, AT_SP, M_PLUS_1]
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
        cmd_block = [AT_SP, M_MINUS_1, A_M, M_NOT, AT_SP, M_PLUS_1]
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
        cmd_block = [AT + str(index), D_A]
        self.write_block(cmd_block)

    def _read_from_address(self, address):
        """ reads the given index as M (from R at address) """
        cmd_block = [AT + str(address), D_M]
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
            self._read_from_address(self.cur_file.replace(".vm", "") + "." +
                                    str(index))

        else:
            # copy content from address held in pointer to D
            if segment in self.__ram_dict.keys():
                self._read_from_address(self.__ram_dict[segment])
            else:
                self._read_from_address(segment)
            cmd_block_1 = [AT + CALC, M_D]
            self.write_block(cmd_block_1)
            self._read_from_A(index)
            cmd_block_2 = [AT + CALC, A_M_PLUS_D, D_M]
            self.write_block(cmd_block_2)

        # push D content to stack
        self._push_D()

    def _push_D(self):
        cmd_block = [AT_SP, A_M, M_D, AT_SP, M_PLUS_1]
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
            self._read_from_A(self.cur_file.replace(".vm", "") + "." +
                              str(index))
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

    def end_file(self):
        self.out_file.write("\n\n")

    def close(self):
        """
        closes the CodeWriter's output file
        """
        cmd_block = [AT_END, JMP, END, JMP]
        self.write_block(cmd_block)
        self.out_file.close()

    def write_init(self):
        """
        Writes the assembly code that effects the VM initialization
        (also called bootstrap code). This code should be placed in the
        ROM beginning in address 0x0000.
        """
        # cmd_block = [AT + SP_INIT, D_A, AT_SP, M_D, AT + "Sys.init", JMP, "\n"]
        cmd_block = [AT + SP_INIT, D_A, AT_SP, M_D, "\n"]
        self.write_block(cmd_block)

        self.write_call("Sys.init", "0")


    def write_label(self, label_name):
        """
        Writes the assembly code that is the translation of the given
        label command.
        :param label_name: name of label
        """
        name = self.cur_func + ":" + label_name
        full_label = LABEL % name
        self.write_block([full_label])

    def write_goto(self, dest):
        """
        Writes the assembly code that is the translation of the given
        goto command.
        :param dest: goto destination
        """
        name = self.cur_func + ":" + dest
        cmd_block = [AT + name, JMP]
        self.write_block(cmd_block)

    def write_if(self, dest):
        """
        Writes the assembly code that is the translation of the given
        if-goto command.
        """
        cmd_block = self._pop_stack_to_d([])
        name = self.cur_func + ":" + dest
        cmd_block.extend([AT + name, JNE])
        self.write_block(cmd_block)

    def _push_frame(self, segment):
        cmd_block = [AT + str(self.__ram_dict[segment]), D_M]
        self.write_block(cmd_block)
        self._push_D()

    def write_call(self, func_name, num_of_arg):
        """
        Writes the assembly code that is the translation of the given
        Call command.
        """
        # save frame of calling function
        self._write_push(CONST, "RETURN_ADD" +
                         str(self._return_address_counter))
        self._push_frame("local")
        self._push_frame("argument")
        self._push_frame("this")
        self._push_frame("that")

        # reposition args
        cmd_arg = [AT_SP, D_M, AT + num_of_arg, D_MINUS_A, AT + "5",
                   D_MINUS_A, AT + str(self.__ram_dict["argument"]), M_D]
        self.write_block(cmd_arg)

        # reposition lcl
        cmd_lcl = [AT_SP, D_M, AT + str(self.__ram_dict["local"]), M_D]
        self.write_block(cmd_lcl)

        # transfer control
        cmd_block = [AT + func_name, JMP]
        self.write_block(cmd_block)

        # write label
        name = "RETURN_ADD" + str(self._return_address_counter)
        full_label = LABEL % name
        self.write_block([full_label])
        self._return_address_counter += 1

    def write_return(self):
        """
        Writes the assembly code that is the translation of the given
        Return command
        """
        # write frame temporary var and save ret temp var
        cmd_block = [AT + "LCL", D_M, AT + "frame", M_D]
        cmd_block.extend([AT + "frame", D_M, AT + "5", D_MINUS_A, A_D, D_M,
                          AT + "ret", M_D])
        self.write_block(cmd_block)

        # pop to argument
        self._write_pop("argument", 0)

        # restore sp
        res_sp = [AT + "ARG", D_M, AT + "1", D_PLUS_A, AT_SP, M_D]
        self.write_block(res_sp)

        # restore frames
        restore = [AT + "frame", D_M, AT + "1", D_MINUS_A, A_D, D_M,
                   AT + "THAT", M_D]
        restore.extend([AT + "frame", D_M, AT + "2", D_MINUS_A, A_D, D_M,
                        AT + "THIS", M_D])
        restore.extend([AT + "frame", D_M, AT + "3", D_MINUS_A, A_D, D_M,
                        AT + "ARG", M_D])
        restore.extend([AT + "frame", D_M, AT + "4", D_MINUS_A, A_D, D_M,
                        AT + "LCL", M_D])
        self.write_block(restore)

        # goto ret
        self.write_block([AT + "ret", A_M, JMP])

    def write_function(self, func_name, num_of_var):
        """
        Writes the assembly code that is the trans. of the given
        Function command.
        """
        # declare label
        self.cur_func = func_name
        full_label = LABEL % func_name
        self.write_block([full_label])

        # push local variables initialized to 0
        for i in range(int(num_of_var)):
            self._write_push(CONST, 0)
