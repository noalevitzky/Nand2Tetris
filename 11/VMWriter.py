SPACE = " "

class VMWriter:

    def __init__(self,output_file):
        """
        Creates a new VMWriter object and prepares to write to a given file
        :param output_file: The file to write to the VM code
        """
        self.output_file = output_file

    def writeVM(self, to_write):
        """
        Writes a given string to to the output_file
        :param to_write: The string to write
        """
        self.output_file.write(to_write + "\n")

    def writePush(self, segment, index):
        """
        Writes a VM push command
        :param segment: The segment to write
        :param index: The index of the segment
        """
        to_write = "push " + segment + SPACE + index
        self.writeVM(to_write)

    def writePop(self, segment, index):
        """
        Writes a VM pop command
        :param segment: The segment to write
        :param index: The index of the segment
        """
        to_write = "pop " + segment + SPACE + index
        self.writeVM(to_write)

    def writeArithmetic(self, command):
        """
        Writes a VM arithmetic command
        :param command: The command to write
        """
        self.writeVM(command)

    def writeLabel(self, label):
        """
        Writes a VM label command
        :param label: The label to write
        """
        to_write = ("label " + label)
        self.writeVM(to_write)

    def writeGoto(self, label):
        """
        Writes a VM goto command
        :param label:
        :return:
        """
        to_write = ("goto " + label)
        self.writeVM(to_write)

    def writeIf(self, label):
        """
        Writes a VM if-goto command
        :param label: The label to write
        """
        to_write = "if-goto " + label
        self.writeVM(to_write)

    def writeCall(self, name, nArgs):
        """
        Writes a VM call command
        :param name: The name of the function
        :param nArgs: The amount of function arguments
        """
        to_write = "call " + name + SPACE + nArgs
        self.writeVM(to_write)

    def writeFunction(self, name, nLocals):
        """
        Writes a VM function command
        :param name: The name of the function
        :param nLocals: The amount of local variables the function has
        """
        to_write = "function " + name + SPACE + nLocals
        self.writeVM(to_write)

    def writeReturn(self):
        """
        Writes a VM return command
        """
        self.writeVM("return")

    def close(self):
        """
        Closes the output file
        """
        self.output_file.close()