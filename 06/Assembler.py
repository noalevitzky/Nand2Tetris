import os
import sys
from pathlib import Path

# ___________ CONSTANTS FOR PROGRAM ___________ #

A_COMMAND = "A"
C_COMMAND = "C"
L_COMMAND = "L"
BIT_NUM_OUTSET = "{0:015b}"
EMPTY_STRING = ""
A_CMD_FIRST_CHAR = "@"
L_CMD_FIRST_CHAR = "("
JMP_INDICATOR = ';'
DEST_INDICATOR = '='
COMMENT_INDICATOR = '/'
DEST_IDX = 0
JMP_IDX = 1
NULL_BINARY = "null"
COMP_JMP_IDX = 0
COMP_DEST_IDX = 1
FIRST_CHAR = 0
A_CMD_FIRST_CHAR_IDX = 0
L_CMD_FIRST_CHAR_IDX = 0
INIT_FREE_RAM = 16;


# _______________ PARSER CLASS _______________ #

class Parser:
    """
    A constructor for the Parser.
    @:param file_name: Name of the ASM file to be parsed.
    """
    def __init__(self, file_name):
        self.f = open(file_name)
        self.curr_command = EMPTY_STRING

    """
    Checks if there are more lines to read from the File
    """
    def hasMoreCommands(self):
        # check if EOF is reached
        return self.f.tell() != os.fstat(self.f.fileno()).st_size

    """
    Strips a readed line from un-important chars 
    """
    def _strip(self):
        # remove trailing spaces
        self.curr_command = self.curr_command.rstrip()
        i = self.curr_command.find('/')
        if i != -1:
            self.curr_command = self.curr_command[0:i]
        self.curr_command = self.curr_command.strip()

    """
    Advance the current line being read to be the next line
    """
    def advance(self):
        self.curr_command = self.f.readline()
        # If the current line is not a command, proceed to the next line
        while self.curr_command in " \n" or \
                (self.curr_command[0] == COMMENT_INDICATOR):
            self.curr_command = self.f.readline()
        self._strip()

    """
    Checks what's the type of the current command
    @:return: The command's type
    """
    def commandType(self):
        if self.curr_command[A_CMD_FIRST_CHAR_IDX] == A_CMD_FIRST_CHAR:
            return A_COMMAND
        elif self.curr_command[L_CMD_FIRST_CHAR_IDX] == L_CMD_FIRST_CHAR:
            return L_COMMAND
        return C_COMMAND

    """
    @:return: The symbol of the current A_CMD/L_CMD line being read.
    """
    def symbol(self):
        return self.curr_command[1:]

    """
    @:return: The dest component in the current C_CMD
    """
    def dest(self):
        if self.has_dest():
            # Return the string before the "=" sign
            return self.curr_command.split(DEST_INDICATOR)[DEST_IDX].strip()
        return NULL_BINARY

    """
    @:return: The comp component in the current command
    """
    def comp(self):
        # Access the relevant comp index according to the C command structure
        if self.has_dest():
            return self.curr_command.split(DEST_INDICATOR)[COMP_DEST_IDX].\
                                                                        strip()
        return self.curr_command.split(JMP_INDICATOR)[COMP_JMP_IDX].strip()

    """
    @:return: The jump component in the current command
    """
    def jump(self):
        if self.has_jump():
            return self.curr_command.split(JMP_INDICATOR)[JMP_IDX].strip()
        return NULL_BINARY

    """
    @:return: True if the current command contains a jump component
    """
    def has_jump(self):
        return JMP_INDICATOR in self.curr_command

    """
    @:return: True if the current command contains a dest component
    """
    def has_dest(self):
        return DEST_INDICATOR in self.curr_command

    """
    Closes the current file being read
    """
    def close_file(self):
        self.f.close()


# _______________ CODE CLASS _______________ #

class Code:
    """
    Dictionary for the comp component
    """
    _d_comp = {
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "!D": "0001101",
        "!A": "0110001",
        "-D": "0001111",
        "-A": "0110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "D+A": "0000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D&A": "0000000",
        "D|A": "0010101",
        "M": "1110000",
        "!M": "1110001",
        "M+1": "1110111",
        "M-1": "1110010",
        "D+M": "1000010",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&M": "1000000",
        "D|M": "1010101",
        "D<<": "0110000",
        "D>>": "0010000",
        "A<<": "0100000",
        "A>>": "0000000",
        "M<<": "1100000",
        "M>>": "1000000"
    }

    """
    Dictionary for the dest component
    """
    _d_dest = {
        "null": "000",
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "AMD": "111"
    }

    """
    Dictionary for the jump component
    """
    _d_jump = {
        "null": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111"
    }

    """
    A constructor for the Code class
    """
    def __init__(self):
        pass

    """
    Retrieves the binary representation of the given comp component
    """
    def comp_to_binary(self, routine):
        return self._d_comp.get(routine)

    """
    Retrieves the binary representation of the given dest component
    """
    def dest_to_binary(self, routine):
        return self._d_dest.get(routine)

    """
    Retrieves the binary representation of the given jump component
    """
    def jump_to_binary(self, routine):
        return self._d_jump.get(routine)


class Assembler:

    """
    Dictionary for the symbol map
    """
    _d_symbols = {
        "SP": "0",
        "LCL": "1",
        "ARG": "2",
        "THIS": "3",
        "THAT": "4",
        "R0": "0",
        "R1": "1",
        "R2": "2",
        "R3": "3",
        "R4": "4",
        "R5": "5",
        "R6": "6",
        "R7": "7",
        "R8": "8",
        "R9": "9",
        "R10": "10",
        "R11": "11",
        "R12": "12",
        "R13": "13",
        "R14": "14",
        "R15": "15",
        "SCREEN": "16384",
        "KBD": "24576",
    }

    """
    A constructor for the Assembler class.
    @:param: infile: The name of the ASM file.
    """
    def __init__(self, infile):
        self.parser = Parser(infile)
        self.code = Code()
        self._next_free_ram = INIT_FREE_RAM

    """
    @:return: A fully processed line
    """
    def get_line(self):
        res = EMPTY_STRING
        if self.parser.commandType() == A_COMMAND:
            return self.process_a_cmd_line(res)
        elif self.parser.commandType() == C_COMMAND:
            return self.process_c_cmd_line(res)

    """
    Processes an A command line
    @:param: res: a pre processed line
    """
    def process_a_cmd_line(self,res):
        res += "0"
        symbol = self.parser.symbol()
        if symbol.isdigit():
            res += BIT_NUM_OUTSET.format(int(symbol))
        elif symbol in self._d_symbols:
            # symbol is found in dict
            res += BIT_NUM_OUTSET.format(int(self._d_symbols[symbol]))
        else:
            # symbol is not in dict
            # assign ram address to symbol, add to dict
            self._d_symbols[symbol] = self._next_free_ram
            self._next_free_ram += 1
            res += BIT_NUM_OUTSET.format(self._d_symbols[symbol])
        return res

    """
    Processes a C command line
    @:param: res: a pre processed line
    """
    def process_c_cmd_line(self, res):
        if (">>" in self.parser.curr_command) or \
                ("<<" in self.parser.curr_command):
            res += "101"
        else:
            res += "111"

        comp = self.code.comp_to_binary(self.parser.comp())
        dest = self.code.dest_to_binary(self.parser.dest())
        jump = self.code.jump_to_binary(self.parser.jump())
        res += str(comp)
        res += str(dest)
        res += str(jump)
        return res

    """
    Processes a L command line
    @:param: res: a pre processed line
    """
    def process_l_cmd_line(self, res):
        # self.parser.commandType() == L_COMMAND
        res += "111"
        symbol = self.parser.symbol()
        res += BIT_NUM_OUTSET.format(int(symbol))
        return res

    """
    Performs a first pass on the file, adds L commands to the Assembler's 
    dictionary
    """
    def first_pass(self):
        row = 0
        while self.parser.hasMoreCommands():
            self.parser.advance()
            if self.parser.commandType() == L_COMMAND:
                # add to d_symbol
                curr_l_cmd = \
                    self.parser.curr_command[1:len(self.parser.curr_command)-1]
                self._d_symbols[curr_l_cmd] = row
            else:
                row += 1

    """
    Processes the files lines and writes them to a file
    """
    def second_pass(self):
        while self.parser.hasMoreCommands():
            self.parser.advance()
            # if the command is L command, pass
            while self.parser.commandType() == L_COMMAND:
                self.parser.advance()
            line = self.get_line()
            outfile.write(line + "\n")

    """
    Adds a new value to the Assembler's dictionary
    @:param: symbol: The key that will be added
    @:param: val: The value of the key that will be added
    """
    def set_dict(self, symbol, val):
        self._d_symbols[symbol] = val

    def get_dict(self, symbol):
        return self._d_symbols[symbol]


if __name__ == "__main__":
    # get the file name
    infile_str = sys.argv[1]
    file_name = Path(infile_str)

    if file_name.is_file():
        file_name = str(file_name)
    else:
        # is folder
        file_name = str(file_name.absolute())

    assembler = Assembler(file_name)

    # first pass (map symbols)
    assembler.first_pass()
    assembler.parser.close_file()

    # second pass (writes processed lines)
    assembler = Assembler(infile_str)
    outfile = open(file_name.replace(".asm", ".hack"), "w+")

    assembler.second_pass()
    assembler.parser.close_file()
    outfile.close()
