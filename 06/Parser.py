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
NULL_BINARY = "000"
COMP_JMP_IDX = 0
COMP_DEST_IDX = 1
FIRST_CHAR = 0


class Parser:
    def __init__(self, file_name):
        self.f = open(file_name)
        self.curr_command = EMPTY_STRING

    def hasMoreCommands(self):
        return self.f.read() is not None

    def advance(self):
        if self.hasMoreCommands():
            self.curr_command = self.f.read()

    def commandType(self):
        if self.curr_command[FIRST_CHAR] == A_CMD_FIRST_CHAR:
            return A_COMMAND
        elif self.curr_command[FIRST_CHAR] == L_CMD_FIRST_CHAR:
            return L_COMMAND
        return C_COMMAND


    def symbol(self):
        return None

    def dest(self):
        if self.has_dest():
            # Return the string before the "=" sign
            return self.curr_command.split(DEST_INDICATOR)[DEST_IDX]
        return NULL_BINARY

    def comp(self):
        # Access the relevant comp index according to the C command structure
        if self.has_dest():
            return self.curr_command.split(DEST_INDICATOR)[COMP_DEST_IDX]
        return self.curr_command.split(JMP_INDICATOR)[COMP_JMP_IDX]

    def jump(self):
        if self.has_jump():
            return self.curr_command.split(JMP_INDICATOR)[JMP_IDX]
        return NULL_BINARY

    def has_jump(self):
        return JMP_INDICATOR in self.curr_command

    def has_dest(self):
        return DEST_INDICATOR in self.curr_command
