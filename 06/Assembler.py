import sys
import Parser
import Code

A_COMMAND = "A"
C_COMMAND = "C"
L_COMMAND = "L"
BIT_NUM_OUTSET = "{0:015b}"


class Assembler:

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

    def __init__(self, infile):
        self.parser = Parser.Parser(infile)
        self.code = Code.Code()
        self._next_free_ram = 16

    def get_line(self):
        res = ""
        if self.parser.commandType() == A_COMMAND:
            return self.process_a_cmd_line(res)
        elif self.parser.commandType() == C_COMMAND:
            return self.process_c_cmd_line(res)

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

    def process_c_cmd_line(self, res):
        res += "111"
        comp = self.code.comp_to_binary(self.parser.comp())
        dest = self.code.dest_to_binary(self.parser.dest())
        jump = self.code.jump_to_binary(self.parser.jump())
        res += str(comp)
        res += str(dest)
        res += str(jump)
        return res

    def process_l_cmd_line(self, res):
        # self.parser.commandType() == L_COMMAND
        res += "111"
        symbol = self.parser.symbol()
        res += BIT_NUM_OUTSET.format(int(symbol))
        return res

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

    def get_symbol(self):
        symbol = self.parser.symbol()
        if type(symbol) != int:
            return self._d_symbols[symbol]
        return symbol

    def second_pass(self):
        while self.parser.hasMoreCommands():
            self.parser.advance()
            while self.parser.commandType() == L_COMMAND:
                self.parser.advance()
            line = self.get_line()
            outfile.write(line + "\n")

    def set_dict(self, symbol, val):
        self._d_symbols[symbol] = val

    def get_dict(self, symbol):
        return self._d_symbols[symbol]


if __name__ == "__main__":
    infile_str = sys.argv[1]

    # strip file name
    first_i = infile_str.rfind('/')
    last_i = infile_str.find(".asm")
    file_name = infile_str[first_i + 1:last_i]

    assembler = Assembler(infile_str)

    # first pass (map symbols)
    assembler.first_pass()
    assembler.parser.close_file()

    # second pass
    assembler = Assembler(infile_str)
    name = file_name + ".hack"
    outfile = open(name, "w+")

    assembler.second_pass()
    assembler.parser.close_file()
    outfile.close()
