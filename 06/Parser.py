import os

EMPTY_STRING = ""
A_COMMAND = "A"
C_COMMAND = "C"
L_COMMAND = "L"
A_CMD_FIRST_CHAR = "@"
L_CMD_FIRST_CHAR = "("
JMP_INDICATOR = ';'
DEST_INDICATOR = '='
DEST_IDX = 0
JMP_IDX = 1
NULL_BINARY = "null"
COMP_JMP_IDX = 0
COMP_DEST_IDX = 1
FIRST_CHAR = 0


class Parser:
    def __init__(self, file_name):
        self.f = open(file_name)
        self.curr_command = ""

    def hasMoreCommands(self):
        # check if EOF is reached
        return self.f.tell() != os.fstat(self.f.fileno()).st_size

    def _strip(self):
        self.curr_command = self.curr_command.rstrip()
        i = self.curr_command.find('/')
        if i != -1:
            self.curr_command = self.curr_command[0:i]
        self.curr_command = self.curr_command.strip()

    def advance(self):
        self.curr_command = self.f.readline()
        while self.curr_command in " \n" or (self.curr_command[0] == "/"):
            self.curr_command = self.f.readline()
        self._strip()

    def commandType(self):
        if self.curr_command[0] == A_CMD_FIRST_CHAR:
            return A_COMMAND
        elif self.curr_command[0] == L_CMD_FIRST_CHAR:
            return L_COMMAND
        return C_COMMAND

    def symbol(self):
        return self.curr_command[1:]

    def dest(self):
        if self.has_dest():
            # Return the string before the "=" sign
            return self.curr_command.split(DEST_INDICATOR)[DEST_IDX]
        return NULL_BINARY

    def comp(self):
        # Access the relevant comp index according to the C command structure
        if self.has_dest():
            return self.curr_command.split("=")[1]
        return self.curr_command.split(";")[0]

    def jump(self):
        if self.has_jump():
            return self.curr_command.split(JMP_INDICATOR)[JMP_IDX]
        return NULL_BINARY

    def has_jump(self):
        return JMP_INDICATOR in self.curr_command

    def has_dest(self):
        return DEST_INDICATOR in self.curr_command

    def close_file(self):
        self.f.close()
