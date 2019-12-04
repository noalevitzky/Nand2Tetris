import Parser
import CodeWriter
from pathlib import Path
import sys
import os

C_ARITHMETIC = "C_ARITHMETIC"
C_PUSH = "C_PUSH"
C_POP = "C_POP"
C_LABEL = "C_LABEL"
C_GOTO = "C_GOTO"
C_IF = "C_IF"
C_FUNCTION = "C_FUNCTION"
C_RETURN = "C_RETURN"
C_CALL = "C_CALL"


# _____________ VMtranslator Program _____________ #

# construct a Parser to parse the VM input file and a CodeWriter to
# generate code into the corresponding output file.  march through the VM
# commands in the input file, and generate assembly code for each one of them.
def write_file(file_str, cw):
    """
    :param file_str: input file
    :param cw: code writer object
    write command into the output file, using the cw
    """
    parser = Parser.Parser(file_str)

    while parser.has_more_commands():
        parser.advance()
        if parser.get_cur_command() != "":
            c_type = parser.command_type()

            if c_type == C_PUSH or c_type == C_POP:
                # write push / pop command
                segment = parser.arg1()
                index = parser.arg2()
                cw.write_push_pop(c_type, segment, index)

            elif c_type == C_ARITHMETIC:
                # write arithmetic command
                command = parser.arg1()
                cw.write_arithmetic(command)

            elif c_type == C_LABEL:
                label = parser.arg1()
                cw.write_label(label)

            elif c_type == C_GOTO:
                dest = parser.arg1()
                cw.write_goto(dest)

            elif c_type == C_IF:
                dest = parser.arg1()
                cw.write_if(dest)

            elif c_type == C_FUNCTION:
                name = parser.arg1()
                num_of_var = parser.arg2()
                cw.write_function(name, num_of_var)

            elif c_type == C_CALL:
                name = parser.arg1()
                num_of_arg = parser.arg2()
                cw.write_call(name, num_of_arg)

            elif c_type == C_RETURN:
                cw.write_return()

    cw.end_file()


if __name__ == '__main__':
    """
    translates VM file / directory to asm file
    """
    path_name = sys.argv[1]
    path = Path(path_name)
    code_writer = None

    if path.is_dir():
        # path is a directory
        outfile = path_name + "/" + os.path.basename(path_name) + ".asm"
        code_writer = CodeWriter.CodeWriter(outfile)
        code_writer.write_init()

        for filename in os.listdir(path_name):
            name, ext = os.path.splitext(filename)
            if ext == ".vm":
                code_writer.set_file_name(filename)
                write_file(path_name + "/" + filename, code_writer)

    else:
        outfile = path_name.replace(".vm", ".asm")
        code_writer = CodeWriter.CodeWriter(outfile)
        code_writer.write_init()

        # path is a single file
        write_file(path, code_writer)

    # close output file
    code_writer.close()
