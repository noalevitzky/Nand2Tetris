import re
import SymbolTable

SPACE_AMOUNT = 2
INCREASE = 1
DECREASE = -1

# print values
CLASS = "class"
SUBROUTINE_DEC = "subroutineDec"
SUBROUTINE_BOD = "subroutineBody"
IF = "ifStatement"
WHILE = "whileStatement"
DO = "doStatement"
LET = "letStatement"
ELSE = "else"
CLASS_VAR_DEC = "classVarDec"
PARAM_LIST = "parameterList"
VAR_DEC = "varDec"
STATEMENTS = "statements"
RETURN = "returnStatement"
SUBROUTINE_CALL = "subroutineCall"
EXPRESSION = 'expression'
EXP_LIST = 'expressionList'
TERM = 'term'
KEYWORD = "keyword"
SYMBOL = "symbol"
IDENTIFIER = "identifier"
INT_CONST = "integerConstant"
STRING_CONST = "stringConstant"
OPERATION_TABLE = {"+":"add", "-":"sub", "=":"eq", ">":"gt", "<":"lt", "|":"or", "&":"and", "/":"Math.divide()", "*":"Math.multiply()"}


class CompilationEngine:
    # jack language
    ops = '\+|-|\*|\/|&|\||<|>|='
    unary_ops = '-|~'
    keyword_consts = 'true|false|null|this'
    statements = 'let|if|while|do|return'

    # regex patterns
    operations_p = re.compile(ops)
    unary_op_p = re.compile(unary_ops)
    keyword_const_p = re.compile(keyword_consts)
    statements_p = re.compile(statements)

    def _compileSubroutineCall(self):
        """
        Compiles the VM representation of a subroutineCall
        """
        # Check if this method belongs to another class
        first_string = self.get_token()
        self.tokenizer.advance()
        # If the function call is func()
        if self.get_token() == "(":
            func_name = first_string
            func_call_name = self.class_name + "." + func_name
        # If the function call is class.func()
        else:
            # current token is "."
            class_name = first_string
            self.tokenizer.advance()
            func_name = self.get_token()
            self.tokenizer.advance()
            func_call_name = class_name + "." + func_name
        self.tokenizer.advance()
        # Now the current token is the beginning of the arguments list
        # Todo: Modify compileExpressionList to update the self.arg_num
        # Todo: Make sure the CompileExpressionList pushes the arguments for the function call
        self.compileExpressionList()
        self.vm_writer.writeCall(func_call_name, self.arg_num)


        #   if not self.get_token() in '(.':
        #       # write subroutineName / className / varName
        #       name = self.get_token()
        #       self._write_xml()
        #
        #       space = self.cur_indent * SPACE_AMOUNT * " "
        #       if self.symbolTable.kindOf(name) is not None:
        #           # name is varName
        #           self.output_file.write(space + self.symbolTable.kindOf(name) +
        #                                  ' ' + self.symbolTable.indexOf(name) +
        #                                  ' used')
        #       else:
        #           if self.get_token() == '(':
        #               # name is subroutine
        #               self.output_file.write(space + 'subroutine used\n')
        #           elif self.get_token() == '.':
        #               # name is class
        #               self.output_file.write(space + 'class used\n')
        #
        #   if self.get_token() == '(':
        #       # write '('
        #       self._write_xml()
        #       # write expressionList
        #       self.compileExpressionList()
        #       # write ")"
        #       self._write_xml()
        #       return
        #
        #   # else, write .subroutineName(expList)
        #   # write '.'
        #   self._write_xml()
        #
        #   # write SubName
        #   self._write_xml()
        #   space = self.cur_indent * SPACE_AMOUNT * " "
        #   self.output_file.write(space + 'subroutine used\n')
        #
        #   # write '('
        #   self._write_xml()
        #   # write expressionList
        #   self.compileExpressionList()
        #   # write ')'
        #   self._write_xml()
        # _write_xml
        return

    #  ___________ API METHODS _____________ #
    def __init__(self, tokenizer, VMWriter):
        self.cur_indent = 0
        self.vm_writer = VMWriter
        self.tokenizer = tokenizer
        self.symbolTable = SymbolTable.SymbolTable()
        self.class_name = ""
        self.arg_num = 0
        # compile based on tokenizer, to output_file
        self.compileClass()

    def compileClass(self):
        """
        Writes an XML file of a class
        """

        # Start reading from JACK file
        self.tokenizer.advance()
        # Declare the class
        # self._write_open_terminal(CLASS)
        # advance to 'class'
        self.tokenizer.advance()
        # advance to className
        self.tokenizer.advance()
        # save class name
        self.class_name = self.get_token()

        # write '{'
        self.tokenizer.advance()

        # Write classVarDec until subroutine declaration
        # TODO: I think this is useless in project 11
        while self.get_token() in 'static|field':
            self.compileClassVarDec()


        # Write Subroutines until the end of the class
        while self.get_token() != "}":
            self.compileSubroutine()

        # advance to '}'
        self.tokenizer.advance()
        # self._write_close_terminal(CLASS)

        return

    def get_token(self):
        """
        :return: token, based on token type
        """
        t = self.tokenizer.tokenType()
        if t is KEYWORD:
            return self.tokenizer.keyword()
        elif t is SYMBOL:
            return self.tokenizer.symbol()
        elif t is IDENTIFIER:
            return self.tokenizer.identifier()
        elif t is INT_CONST:
            return self.tokenizer.intVal()
        elif t is STRING_CONST:
            return self.tokenizer.stringVal()

    def compileClassVarDec(self):
        """
        Compiles the XML representation of class variables declaration
        """
        # write classVarDec

        # write 'static'|'field'
        kind = self.get_token()
        self.tokenizer.advance()

        # write type
        myType = self.get_token()
        self.tokenizer.advance()
        # todo if type is object of class, class is use??
        # if myType not in ['int', 'char', 'boolean']:
        #     space = self.cur_indent * SPACE_AMOUNT * " "
        #     self.output_file.write(space + 'class used\n')

        # write varName
        name = self.get_token()
        self.tokenizer.advance()
        self.symbolTable.define(name, myType, kind)

        while self.get_token() == ',':
            # write ','
            self.tokenizer.advance()
            # write varName
            name = self.get_token()
            self.tokenizer.advance()
            self.symbolTable.define(name, myType, kind)

        # write ";"
        self.tokenizer.advance()

        return

    def compileSubroutine(self):
        """
        Compiles the VM representation of a subroutine
        """
        # reset symbol table
        self.symbolTable.startSubroutine()

        # write subroutine
        # self._write_open_terminal(SUBROUTINE_DEC)
        # write 'constructor' | 'function' | 'method'
        self.tokenizer.advance()
        # write 'void' | type
        self.tokenizer.advance()

        # write subroutineName
        self.tokenizer.advance()

        # write "("
        self.tokenizer.advance()
        # write parameterList
        self.compileParameterList()
        # write ")"
        self.tokenizer.advance()
        # write subroutineBody
        self.compileSubroutineBody()


        return

    def compileParameterList(self):
        """
        Compiles the XML representation of parameterList
        """
        kind = 'argument'
        if self.get_token() != ')':
            # write type
            myType = self.get_token()
            self.tokenizer.advance()

            # write varName
            name = self.get_token()
            self.tokenizer.advance()
            self.symbolTable.define(name, myType, kind)

            while self.get_token() == ',':
                # write ','
                self.tokenizer.advance()

                # write type
                myType = self.get_token()
                self.tokenizer.advance()

                # write varName
                name = self.get_token()
                self.tokenizer.advance()
                self.symbolTable.define(name, myType, kind)

        return

    def compileSubroutineBody(self):
        """
        Compiles the XML representation of a subroutineBody
        """
        # write "{"
        self.tokenizer.advance()
        while self.get_token() == "var":
            # write varDec
            self.compileVarDec()
        # write statements
        self.compileStatements()
        # write "}" after the last statement (end of method body)
        self.tokenizer.advance()
        return

    def compileVarDec(self):
        """
        Compiles the XML representation of variableDeclaration
        """

        # write 'var'
        kind = self.get_token()
        self.tokenizer.advance()

        # write type
        myType = self.get_token()
        self.tokenizer.advance()

        # write varName
        name = self.get_token()
        self.tokenizer.advance()

        self.symbolTable.define(name, myType, kind)

        while self.get_token() == ',':
            # write ','
            self.tokenizer.advance()

            # write varName
            name = self.get_token()
            self.tokenizer.advance()
            self.symbolTable.define(name, myType, kind)
        # write ';'
        self.tokenizer.advance()
        return

    def compileStatements(self):
        """
        Compiles the XML representation of statements
        """
        # according to the curr_token, call the relevant compilation
        while re.match(self.statements_p, self.get_token()):
            if self.get_token() == "let":
                self.compileLet()
            elif self.get_token() == "if":
                self.compileIf()
            elif self.get_token() == "while":
                self.compileWhile()
            elif self.get_token() == "do":
                self.compileDo()
            elif self.get_token() == 'return':
                self.compileReturn()
        return

    def compileDo(self):
        """
        Compiles the XML representation of a Do statement
        """
        # advance the tokenizer to the function name
        self.tokenizer.advance()
        function_name = self.get_token()
        while self.get_token() != ";":
            self._compileSubroutineCall()
        # write ';'
        self.tokenizer.advance()
        return

    def compileLet(self):
        """
        Compiles the XML representation of a Let statement
        """
        # write 'let'
        self.tokenizer.advance()

        # write varName
        name = self.get_token()
        self.tokenizer.advance()

        if self.get_token() == '[':
            # write '[ expression ]'
            self.tokenizer.advance()
            self.compileExpression()
            self.tokenizer.advance()
        # write '='
        self.tokenizer.advance()
        # write expression
        self.compileExpression()
        # write ';'
        self.tokenizer.advance()
        return

    def compileWhile(self):
        """
        Compiles the XML representation of a While statement
        """
        # write 'while'
        self.tokenizer.advance()
        # write '('
        self.tokenizer.advance()
        # write expression
        self.compileExpression()
        # write ')'
        self.tokenizer.advance()
        # write {
        self.tokenizer.advance()
        # write statements
        self.compileStatements()
        # write '}'
        self.tokenizer.advance()
        return

    def compileReturn(self):
        """
        Compiles the XML representation of a Return statement
        """
        # write 'return'
        self.tokenizer.advance()
        if self.get_token() != ';':
            # write expression
            self.compileExpression()
        # write ';'
        self.tokenizer.advance()
        return

    def compileIf(self):
        """
        Compiles the XML representation of an If statement
        """
        # write 'if'
        self.tokenizer.advance()
        # write '('
        self.tokenizer.advance()
        # write expression
        self.compileExpression()
        # write ')'
        self.tokenizer.advance()
        # write "{"
        self.tokenizer.advance()
        # write statements
        self.compileStatements()
        # write "}"
        self.tokenizer.advance()
        if self.get_token() != "else":
#            self._write_close_terminal(IF)
            return
        # next token is else. write "else"
        self.tokenizer.advance()
        # write "{"
        self.tokenizer.advance()
        # write statements
        self.compileStatements()
        # write "}"
        self.tokenizer.advance()
        return

    def compileExpression(self):
        """
        Compiles the XML representation of an expression
        """
        # write term
        self.compileTerm()
        while re.match(self.operations_p, self.get_token()):
            # write op
            self.vm_writer.writeVM(OPERATION_TABLE[self.get_token()])
            self.tokenizer.advance()
            # write term
            self.compileTerm()
        return

    def compileTerm(self):
        """
        Compiles the XML representation of a term
        """
        if self.get_token() == '(':
            self.tokenizer.advance()
            if self.get_token() == '(':
                self.compileExpression()

            self.tokenizer.advance()
        elif re.match(self.tokenizer.int_const_p, self.get_token()) or \
                re.match(self.tokenizer.str_const_p, self.get_token()) or \
                re.match(self.keyword_const_p, self.get_token()):
            # write integerConstant | stringConstant | keywordConstant
            if self.tokenizer.tokenType() == INT_CONST:
                self.vm_writer.writePush("constant", self.get_token())
            #TODO: handle other constants.
            self.tokenizer.advance()
        elif self.get_token() in ["-", "~"]:
            # write unaryOp term
            self.tokenizer.advance()
            self.compileTerm()
        else:
            # write varName/subroutineName
            name = self.get_token()
            self.tokenizer.advance()

            # if self.symbolTable.kindOf(name) is not None:
            # write varName
            # self.tokenizer.advance()
            # space = self.cur_indent * SPACE_AMOUNT * " "
            # self.output_file.write(space + self.symbolTable.kindOf(name) +
            #                      ' ' + self.symbolTable.indexOf(name) +
            #                      ' used\n')
            # else:
            # write subroutine
            #   self.tokenizer.advance()
            #  space = self.cur_indent * SPACE_AMOUNT * " "
            # self.output_file.write(space + 'subroutine used\n')

            if self.get_token() == '[':
                # write '['
                self.tokenizer.advance()
                # write exp
                self.compileExpression()
                # write ']'
                self.tokenizer.advance()
            elif self.get_token() in '(.':
                self._compileSubroutineCall()
        return

    def compileExpressionList(self):
        """
        Compiles the VM representation of an expressionList
        This method will only be called when handling a function call
        """
        if self.get_token() != ')':
            # write expression
            self.compileExpression()
            while self.get_token() == ',':
                # increase the amount of arguments
                self.arg_num += 1
                # write ','
                self.tokenizer.advance()
                # write expression
                self.compileExpression()

