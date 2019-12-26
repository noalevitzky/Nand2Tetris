import re

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

    #  ___________ NON-API METHODS ___________ #
    def _write_open_terminal(self, name):
        """
        writes opening name tag
        :param name: to be printed
        :return: none
        """
        self.output_file.write(" " * self.cur_indent * SPACE_AMOUNT +
                               "<" + name + ">\n")
        self._mod_indent(INCREASE)
        return

    def _write_close_terminal(self, name):
        """
        writes closing name tag
        :param name: to be printed
        :return: none
        """
        self._mod_indent(DECREASE)
        to_write = " " * self.cur_indent * SPACE_AMOUNT + \
                   "</" + name + ">" + "\n"
        self.output_file.write(to_write)
        return

    def _mod_indent(self, action):
        """
        increase or decrease the current indentation according to the action
        :param action: increase or decrease
        :return: none
        """
        self.cur_indent += action
        return

    def _write_xml(self):
        """
        Writes a single terminal output
        :return: none
        """
        key = self.tokenizer.tokenType()
        start = "<" + key + "> "
        end = " </" + key + ">"
        space = self.cur_indent * SPACE_AMOUNT * " "
        self.output_file.write(space + start + str(self.get_token()) +
                               end + "\n")
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
        return

    def _compileSubroutineCall(self):
        """
        Compiles the XML representation of a subroutineCall
        """
        # write subroutineName / className / varName
        if not self.get_token() in '(.':
            self._write_xml()
        if self.get_token() == '(':
            # write '('
            self._write_xml()
            # write expressionList
            self.compileExpressionList()
            # write ")"
            self._write_xml()
            return
        # else, write className|VarName.subroutineName(expList)
        # write '.'
        self._write_xml()
        # write SubName
        self._write_xml()
        # write '('
        self._write_xml()
        # write expressionList
        self.compileExpressionList()
        # write ')'
        self._write_xml()
        return

    #  ___________ API METHODS _____________ #
    def __init__(self, tokenizer, output_file):
        self.cur_indent = 0
        self.output_file = open(output_file, 'w')
        self.tokenizer = tokenizer
        # compile based on tokenizer, to output_file
        self.compileClass()

    def compileClass(self):
        """
        Writes an XML file of a class
        """
        # Start reading from JACK file
        self.tokenizer.advance()
        # Declare the class
        self._write_open_terminal(CLASS)
        # write 'class'
        self._write_xml()
        # write className
        self._write_xml()
        # write '{'
        self._write_xml()
        # Write classVarDec until subroutine declaration
        while self.get_token() in 'static|field':
            self.compileClassVarDec()
        # Write Subroutines until the end of the class
        while self.get_token() != "}":
            self.compileSubroutine()
        # write '}'
        self._write_xml()
        self._write_close_terminal(CLASS)
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
        self._write_open_terminal(CLASS_VAR_DEC)
        # write 'static'/'field'
        self._write_xml()
        # write type
        self._write_xml()
        # write varName
        self._write_xml()
        while self.get_token() == ',':
            # write ','
            self._write_xml()
            # write varName
            self._write_xml()
        # write ";"
        self._write_xml()
        self._write_close_terminal(CLASS_VAR_DEC)
        return

    def compileSubroutine(self):
        """
        Compiles the XML representation of a subroutine
        """
        # write subroutine
        self._write_open_terminal(SUBROUTINE_DEC)
        # write 'constructor' | 'function' | 'method
        self._write_xml()
        # write 'void' | type
        self._write_xml()
        # write subroutineName
        self._write_xml()
        # write "("
        self._write_xml()
        # write parameterList
        self.compileParameterList()
        # write ")"
        self._write_xml()
        # write subroutineBody
        self.compileSubroutineBody()
        self._write_close_terminal(SUBROUTINE_DEC)
        return

    def compileParameterList(self):
        """
        Compiles the XML representation of parameterList
        """
        # write parameterList
        self._write_open_terminal(PARAM_LIST)
        if self.get_token() != ')':
            # write type
            self._write_xml()
            # write varName
            self._write_xml()
            while self.get_token() == ',':
                # write ','
                self._write_xml()
                # write type
                self._write_xml()
                # write varName
                self._write_xml()
        self._write_close_terminal(PARAM_LIST)
        return

    def compileSubroutineBody(self):
        """
        Compiles the XML representation of a subroutineBody
        """
        # write subroutineBody
        self._write_open_terminal(SUBROUTINE_BOD)
        # write "{"
        self._write_xml()
        while self.get_token() == "var":
            # write varDec
            self.compileVarDec()
        # write statements
        self.compileStatements()
        # write "}" after the last statement (end of method body)
        self._write_xml()
        self._write_close_terminal(SUBROUTINE_BOD)
        return

    def compileVarDec(self):
        """
        Compiles the XML representation of variableDeclaration
        """
        # write varDec
        self._write_open_terminal(VAR_DEC)
        # write 'var'
        self._write_xml()
        # write type
        self._write_xml()
        # write varName
        self._write_xml()
        while self.get_token() == ',':
            # write ','
            self._write_xml()
            # write varName
            self._write_xml()
        # write ';'
        self._write_xml()
        self._write_close_terminal(VAR_DEC)
        return

    def compileStatements(self):
        """
        Compiles the XML representation of statements
        """
        self._write_open_terminal(STATEMENTS)
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
        self._write_close_terminal(STATEMENTS)
        return

    def compileDo(self):
        """
        Compiles the XML representation of a Do statement
        """
        # write doStatement
        self._write_open_terminal(DO)
        # write 'do'
        self._write_xml()
        # write subroutine
        self._compileSubroutineCall()
        # write ';'
        self._write_xml()
        self._write_close_terminal(DO)
        return

    def compileLet(self):
        """
        Compiles the XML representation of a Let statement
        """
        # write letStatement
        self._write_open_terminal(LET)
        # write 'let'
        self._write_xml()
        # write varName
        self._write_xml()
        if self.get_token() == '[':
            # write '[ expression ]'
            self._write_xml()
            self.compileExpression()
            self._write_xml()
        # write '='
        self._write_xml()
        # write expression
        self.compileExpression()
        # write ';'
        self._write_xml()
        self._write_close_terminal(LET)
        return

    def compileWhile(self):
        """
        Compiles the XML representation of a While statement
        """
        # write whileStatement
        self._write_open_terminal(WHILE)
        # write 'while'
        self._write_xml()
        # write '('
        self._write_xml()
        # write expression
        self.compileExpression()
        # write ')'
        self._write_xml()
        # write {
        self._write_xml()
        # write statements
        self.compileStatements()
        # write '}'
        self._write_xml()
        self._write_close_terminal(WHILE)
        return

    def compileReturn(self):
        """
        Compiles the XML representation of a Return statement
        """
        # write returnStatement
        self._write_open_terminal(RETURN)
        # write 'return'
        self._write_xml()
        if self.get_token() != ';':
            # write expression
            self.compileExpression()
        # write ';'
        self._write_xml()
        self._write_close_terminal(RETURN)
        return

    def compileIf(self):
        """
        Compiles the XML representation of an If statement
        """
        # write ifStatement
        self._write_open_terminal(IF)
        # write 'if'
        self._write_xml()
        # write '('
        self._write_xml()
        # write expression
        self.compileExpression()
        # write ')'
        self._write_xml()
        # write "{"
        self._write_xml()
        # write statements
        self.compileStatements()
        # write "}"
        self._write_xml()
        if self.get_token() != "else":
            self._write_close_terminal(IF)
            return
        # next token is else. write "else"
        self._write_xml()
        # write "{"
        self._write_xml()
        # write statements
        self.compileStatements()
        # write "}"
        self._write_xml()
        self._write_close_terminal(IF)
        return

    def compileExpression(self):
        """
        Compiles the XML representation of an expression
        """
        # write expression
        self._write_open_terminal(EXPRESSION)
        # write term
        self.compileTerm()
        while re.match(self.operations_p, self.get_token()):
            # write op
            self._write_xml()
            # write term
            self.compileTerm()
        self._write_close_terminal(EXPRESSION)
        return

    def compileTerm(self):
        """
        Compiles the XML representation of a term
        """
        # write term
        self._write_open_terminal(TERM)
        if self.get_token() == '(':
            # write '(expression)'
            # write '('
            self._write_xml()
            # write exp
            self.compileExpression()
            # write ')'
            self._write_xml()
        elif re.match(self.tokenizer.int_const_p, self.get_token()) or \
                re.match(self.tokenizer.str_const_p, self.get_token()) or \
                re.match(self.keyword_const_p, self.get_token()):
            # write integerConstant | stringConstant | keywordConstant
            self._write_xml()
        elif re.match(self.unary_op_p, self.get_token()):
            # write unaryOp term
            self._write_xml()
            self.compileTerm()
        else:
            # write varName/subroutineName
            self._write_xml()
            if self.get_token() == '[':
                # write '['
                self._write_xml()
                # write exp
                self.compileExpression()
                # write ']'
                self._write_xml()
            elif self.get_token() in '(.':
                self._compileSubroutineCall()
        self._write_close_terminal(TERM)
        return

    def compileExpressionList(self):
        """
        Compiles the XML representation of an expressionList
        """
        self._write_open_terminal(EXP_LIST)
        if self.get_token() != ')':
            # write expression
            self.compileExpression()
            while self.get_token() == ',':
                # write ','
                self._write_xml()
                # write expression
                self.compileExpression()
        self._write_close_terminal(EXP_LIST)
