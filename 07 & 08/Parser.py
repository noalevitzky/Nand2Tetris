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
COMMENT_INDICATOR = '/'


# _____________ Parser Class _____________ #

# Handles the parsing of a single .vm file, and encapsulates access to the
# input code. It reads VM commands, parses them, and provides convenient
# access to their components.
# In addition, it removes all white space and comments
class Parser:
    # dictionary for command types
    _command_dict = {
        "add": "C_ARITHMETIC",
        "sub": "C_ARITHMETIC",
        "neg": "C_ARITHMETIC",
        "eq": "C_ARITHMETIC",
        "gt": "C_ARITHMETIC",
        "lt": "C_ARITHMETIC",
        "and": "C_ARITHMETIC",
        "or": "C_ARITHMETIC",
        "not": "C_ARITHMETIC",
        "push": "C_PUSH",
        "pop": "C_POP",
        "label": "C_LABEL",
        "goto": "C_GOTO",
        "if-goto": "C_IF",
        "function": "C_FUNCTION",
        "return": "C_RETURN",
        "call": "C_CALL",
    }

    def __init__(self, file):
        """
        :param file: file / stream to open
        """
        self.f = open(file)
        self._cur_command = ""

    def has_more_commands(self):
        """
        :return: true if there are more commands in input
        """
        return self.f.tell() != os.fstat(self.f.fileno()).st_size

    def advance(self):
        """
        reads next command from input
        """
        if self.has_more_commands():
            self._cur_command = self.f.readline()

            # If the current line is not a command, proceed to the next line
            while self.has_more_commands() and \
                    (self._cur_command in " \n" or
                     self._cur_command[0] == COMMENT_INDICATOR):
                self._cur_command = self.f.readline()

            # remove extra spaces
            self._cur_command = " ".join(self._cur_command.split())

    def get_cur_command(self):
        return self._cur_command

    def command_type(self):
        """
        :return: command type
        """
        return self._command_dict[self._cur_command.split()[0]]

    def arg1(self):
        """
        :return: string representation of first argument of current command.
        in case of arithmetic command, returns command itself.
        should not be called if command is return.
        """
        command = self._cur_command.split()[0]

        if self._command_dict[command] == C_RETURN:
            return None
        elif self._command_dict[command] == C_ARITHMETIC:
            return command
        else:
            return self._cur_command.split()[1]

    def arg2(self):
        """
        :return: string representation of second argument of current command.
        in case of arithmetic command, returns command itself.
        should not be called if command is return.
        """
        command = self._cur_command.split()[0]

        # return second arg if command is push / pop / function / call
        if self._command_dict[command] == C_PUSH or \
                self._command_dict[command] == C_POP or \
                self._command_dict[command] == C_FUNCTION or \
                self._command_dict[command] == C_CALL:
            return self._cur_command.split()[2]

        return None

