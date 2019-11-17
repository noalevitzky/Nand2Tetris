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
            res += "{0:015b}".format(int(symbol))
            return res

        elif self.parser.commandType() == C_COMMAND:
            res += "111"
            comp = self.code.comp_to_binary(self.parser.comp())
            dest = self.code.dest_to_binary(self.parser.dest())
            jump = self.code.jump_to_binary(self.parser.jump())
            res += str(comp)
            res += str(dest)
            res += str(jump)
            return res

        else:
            # self.parser.commandType() == L_COMMAND
            res += "111"
            symbol = self.parser.symbol()
            res += "{0:015b}".format(int(symbol))
            return res


if __name__ == "__main__":
    infile_str = sys.argv[1]
    # strip file name
    first_i = infile_str.rfind('/')
    last_i = infile_str.find(".asm")
    file_name = infile_str[first_i + 1:last_i]

    assembler = Assembler(infile_str)
    name = file_name + ".hack"
    outfile = open(name, "w+")

    while assembler.parser.hasMoreCommands():
        assembler.parser.advance()
        line = assembler.get_line()
        outfile.write(line + "\n")

    outfile.close()
