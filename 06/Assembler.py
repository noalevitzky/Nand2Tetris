import Parser
import Code
import sys

A_COMMAND = "A"
C_COMMAND = "C"
L_COMMAND = "L"


class Assembler:
    _symbols = {
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
        self._next_free_ram = 15

    def get_line(self):

        res = ""
        if self.parser.commandType() == A_COMMAND:
            res += "0"
            symbol = self.parser.symbol()
            if symbol.isdigit():
                res += "{0:015b}".format(int(symbol))
                return res
            elif self._symbols[symbol] is not None:
                # symbol is found in dict
                res += "{0:015b}".format(int(self._symbols[symbol]))
                return res
            else:
                # symbol is not in dict
                self._next_free_ram += 1
                self._symbols[symbol] = self._next_free_ram
                return "{0:015b}".format(self._next_free_ram)

        elif self.parser.commandType() == C_COMMAND:
            res += "111"
            print(self.parser.comp())
            comp = self.code.comp_to_binary(self.parser.comp())
            dest = self.code.dest_to_binary(self.parser.dest())
            jump = self.code.jump_to_binary(self.parser.jump())
            res += str(comp)
            res += str(dest)
            res += str(jump)
            print(res)
            return res

    def first_pass(self):
        row = -1
        while self.parser.hasMoreCommands():
            self.parser.advance()
            row += 1
            if self.parser.commandType() == L_COMMAND:
                self.set_dict(self.parser.curr_command, row + 1)

    def second_pass(self):
        print("second pass started")
        while self.parser.hasMoreCommands():
            self.parser.advance()
            while self.parser.commandType() == L_COMMAND:
                self.parser.advance()
            line = self.get_line()
            outfile.write(line + "\n")

    def set_dict(self, symbol, val):
        self._symbols[symbol] = val

    def get_dict(self, symbol):
        return self._symbols[symbol]


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
