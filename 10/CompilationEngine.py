import JackTokenizer

SPACE_AMOUNT = 8
INCREASE = 1
DECREASE = -1
KEYWORD = "keyword"
SYMBOL = "symbol"
IDENTIFIER = "identifier"
INT_CONST = "int_Const"
CLASS = "class"
SUBROUTINE_DEC = "subroutineDec"
SUBROUTINE_BOD = "subroutineBody"
IF = "if"
WHILE = "while"
DO = "do"
LET = "let"
ELSE = "else"
CLASS_VAR_DEC = "classVarDec"
PARAM_LIST = "parameterList"
VAR_DEC = "varDec"
STATEMENTS = "statements"
RETURN = "return"
SUBROUTINE_CALL = "subroutineCall"


class CompilationEngine:

    #### ___________ NON-API METHODS ___________ ####

    def write_open_terminal(self, name):
        to_write = "<" + name + ">"
        # TODO: use Noa's implementation to write
        self.mod_indent(INCREASE)
        return

    def write_close_terminal(self, name):
        self.mod_indent(DECREASE)
        to_write = "</" + name + ">"
        # TODO: use Noa's implementation to write
        return

    def mod_indent(self, action):
        # increase or decrease the current indentation according to the action
        if self.curr_indentation == 0:
            self.curr_indentation += 1
        self.curr_indentation += action * SPACE_AMOUNT
        return

    def write_xml(self):
        """
        Writes a single terminal output
        :return:
        """
        start = "<" + JackTokenizer.tokenDict[
            self.tokenizer.tokenType()] + "> "
        end = " </" + JackTokenizer.tokenDict[self.tokenizer.tokenType()] + ">"
        self.output_file.write(start + self.tokenizer.get_token() + end + "\n")
        self.tokenizer.advance()

    def compileSubroutineCall(self):
        """
        Compiles the XML representation of a subroutineCall
        """
        # Both cases are being handled the same, write terminals until an opening bracket is reached
        self.write_open_terminal(SUBROUTINE_CALL)
        while self.tokenizer.get_token() != "(":
            self.write_xml()
        # write "("
        self.write_xml()
        self.compileExpressionList()
        # write ")"
        self.write_xml()
        return

    #### ___________ API METHODS _____________ ####

    def __init__(self, input_file, output_file):

        self.curr_indentation = 0
        self.input_file = input_file
        # XML file
        self.output_file = open(output_file, 'w')
        self.tokenizer = JackTokenizer.JackTokenizer(input_file)
        # self.curr_indentation = 1

    def compileClass(self):
        """
        Writes an XML file of a class
        """
        # Start reading from JACK file
        self.tokenizer.advance()
        # Declare the class
        self.write_open_terminal(CLASS)
        # increase the indentation of the XML file
        self.mod_indent(INCREASE)
        while self.tokenizer.get_token() != "{":
            self.write_xml()
            self.tokenizer.advance()
        self.write_xml()
        # Write classVarDec until subroutine declerations
        while self.tokenizer.get_token() not in ['constructor', 'function',
                                                 'method']:
            self.compileClassVarDec()
        # Write Subroutines untill the end of the class
        while self.tokenizer.get_token() != "}":
            self.compileSubroutine()
        self.mod_indent(DECREASE)
        self.write_close_terminal(CLASS)
        return

    def compileClassVarDec(self):
        """
        Compiles the XML representation of class variables declaration
        """
        self.write_open_terminal(CLASS_VAR_DEC)
        while self.tokenizer.get_token() != ";":
            self.write_xml()
        # write ";"
        self.write_xml()
        self.write_close_terminal(CLASS_VAR_DEC)
        return

    def compileSubroutine(self):
        """
        Compiles the XML representation of a subroutine
        """
        self.write_close_terminal(SUBROUTINE_DEC)
        while self.tokenizer.get_token() != "(":
            self.write_xml()
        # write "("
        self.write_xml()
        self.compileParameterList()
        # write ")"
        self.write_xml()
        self.compileSubroutineBody()
        self.write_close_terminal(SUBROUTINE_DEC)
        return

    def compileParameterList(self):
        """
        Compiles the XML representation of parameterList
        """
        self.write_open_terminal(PARAM_LIST)
        # write the parameter list without it's brackets
        while self.tokenizer.get_token() != ")":
            self.write_xml()
        self.write_close_terminal(PARAM_LIST)
        return

    def compileSubroutineBody(self):
        """
        Compiles the XML representation of a subroutineBody
        """
        self.write_close_terminal(SUBROUTINE_BOD)
        # write "{"
        self.write_xml()
        while self.tokenizer.get_token() == "var":
            self.compileVarDec()
        self.compileStatements()
        # write "}" after the last statement (end of method body)
        self.write_xml()
        return

    def compileVarDec(self):
        """
        Compiles the XML representation of variableDeclaration
        """
        self.write_open_terminal(VAR_DEC)
        # while we are still in the variable declaration
        while self.tokenizer.get_token() != ";":
            self.write_xml()
        self.write_xml()
        self.write_close_terminal(VAR_DEC)
        return

    def compileStatements(self):
        """
        Compiles the XML representation of statements
        """
        self.write_open_terminal(STATEMENTS)
        # according to the curr_token, call the relevant compilation
        if self.tokenizer.get_token() == "let":
            self.compileLet()
        elif self.tokenizer.get_token() == "if":
            self.compileIf()
        elif self.tokenizer.get_token() == "while":
            self.compileWhile()
        elif self.tokenizer.get_token() == "do":
            self.compileDo()
        self.compileReturn()
        self.write_close_terminal(STATEMENTS)
        return

    def compileDo(self):
        """
        Compiles the XML representation of a Do statement
        """
        # TODO: implement subroutineCall
        self.write_open_terminal(DO)
        self.write_xml()
        self.compileSubroutineCall()
        self.write_close_terminal(DO)
        return

    def compileLet(self):
        """
        Compiles the XML representation of a Let statement
        """
        # TODO: handle expressions
        self.write_open_terminal(LET)
        while self.tokenizer.get_token() != ";":
            self.write_xml()
        self.write_close_terminal(LET)
        return

    def compileWhile(self):
        """
        Compiles the XML representation of a While statement
        """
        # TODO: handle expressions
        self.write_open_terminal(WHILE)
        while self.tokenizer.get_token() != "}":
            self.write_xml()
        self.write_close_terminal(WHILE)
        return

    def compileReturn(self):
        """
        Compiles the XML representation of a Return statement
        """
        # TODO: handle expressions
        self.write_open_terminal(RETURN)
        while self.tokenizer.get_token() != ";":
            self.write_xml()
        self.write_close_terminal()
        return

    def compileIf(self):
        """
        Compiles the XML representation of an If statement
        """
        # TODO: implement expressions
        self.write_open_terminal(IF)
        while self.tokenizer.get_token() != "{":
            self.write_xml()
        # write "{"
        self.write_xml()
        self.compileStatements()
        # write "}"
        self.write_xml()
        if self.tokenizer.peek_next() != "else":
            self.write_close_terminal(IF)
            return
        # next token is else. write "else"
        self.write_xml()
        # write "{"
        self.write_xml()
        self.compileStatements()
        # write "}"
        self.write_xml()
        self.write_close_terminal(IF)
        return

    def compileExpression(self):
        """
        Compiles the XML representation of an expression
        """
        # TODO: compile expressions
        pass

    def compileTerm(self):
        """
        Compiles the XML representation of a term
        """
        # TODO: compile expressions
        pass

    def compileExpressionList(self):
        """
        Compiles the XML representation of an expressionList
        """
        # TODO: compile expressions
        pass
