import Parser
import Code
import sys

A_COMMAND = "A"
C_COMMAND = "C"
L_COMMAND = "L"


class Assembler:
    def __init__(self, infile):
        self.parser = Parser.Parser(infile)
        self.code = Code.Code()

    def get_line(self):
        res = ""
        if self.parser.commandType() == A_COMMAND:
            res += "0"
            symbol = self.parser.symbol()
            res += str(bin(int(symbol)))
            return res

        elif self.parser.commandType() == C_COMMAND:
            res += "111"
            dest = self.code.dest_to_binary(self.parser.dest())
            comp = self.code.comp_to_binary(self.parser.comp())
            jump = self.code.jump_to_binary(self.parser.jump())
            res += dest
            res += comp
            res += jump
            return res

        # else:
        #     # self.parser.commandType() == L_COMMAND
        #     res += "111"
        #     symbol = self.parser.symbol()
        #     res += str(bin(int(symbol)))
        #     return res


def main(self):
    infile_str = sys.argv[1]

    # strip file name
    first_i = infile_str.rfind('/')
    last_i = infile_str.find(".asm")
    file_name = infile_str[first_i + 1:last_i - 1]

    assembler = Assembler(infile_str)
    name = file_name + ".hack"
    outfile = open(name, "w+")

    while self.parser.hasMoreCommands():
        self.parser.advance()
        outfile.write(assembler.get_line())

    outfile.close()
