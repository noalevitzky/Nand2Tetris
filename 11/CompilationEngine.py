import re
import SymbolTable

SPACE_AMOUNT = 2
INCREASE = 1
DECREASE = -1

# print values
CLASS = "class"
# SUBROUTINE_DEC = "subroutineDec"
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
OPERATION_TABLE = {"+": "add", "-": "sub", "=": "eq", ">": "gt", "<": "lt",
                   "|": "or", "&": "and", "/": "call Math.divide 2",
                   "*": "call Math.multiply 2"}
UNARY_TABLE = {'-': 'neg', '~': 'not'}  # todo is ~ == not?


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
        firstToken = self.get_token()
        self.advance_tokenizer()
        # self.vm_writer.writePush('pointer', 0)

        # firstToken is var name
        if self.symbolTable.kindOf(firstToken) is not None:
            secondToken = self.get_token()
            if secondToken == '[':
                self.advance_tokenizer()
                self.compileExpression()
                self.advance_tokenizer()
                # todo push address of secondToken[expression] to stack
                # todo write pop to that segement

            elif secondToken == '.':
                self.vm_writer.writePush(self.symbolTable.kindOf(firstToken),
                                         self.symbolTable.indexOf(firstToken))
                self.advance_tokenizer()
                funcName = self.symbolTable.typeOf(firstToken) + '.' + self.get_token()
                self.advance_tokenizer()
                self.compileExpressionList()
                self.vm_writer.writeCall(funcName, self.arg_num)

            else:
                # simply varName
                self.vm_writer.writePush('pointer', 0)
                self.advance_tokenizer()

        # firstToken is subroutine or class Name
        else:
            if self.get_token() == '.':
                # term is className.sub()
                # self.vm_writer.writePush('pointer', 0)
                self.advance_tokenizer()
                funcName = firstToken + '.' + str(self.get_token())
                self.advance_tokenizer()
                self.compileExpressionList()
                self.vm_writer.writeCall(funcName, self.arg_num)

            elif self.get_token() == '(':
                # term is subroutine
                funcName = self.class_name + '.' + firstToken
                self.advance_tokenizer()
                self.compileExpressionList()
                self.vm_writer.writePush('pointer', 0)
                self.vm_writer.writeCall(funcName, self.arg_num)


    #  ___________ API METHODS _____________ #
    def __init__(self, tokenizer, VMWriter):
        self.cur_indent = 0
        self.vm_writer = VMWriter
        self.tokenizer = tokenizer
        self.symbolTable = SymbolTable.SymbolTable()
        self.class_name = ""
        self.arg_num = 0
        self._while_counter = -1
        self._if_counter = -1

        # compile based on tokenizer, to output_file
        self.compileClass()

    def advance_tokenizer(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
        return

    def compileClass(self):
        """
        Writes an XML file of a class
        """
        # Start reading from JACK file
        self.advance_tokenizer()
        # Declare the class
        # self._write_open_terminal(CLASS)
        # advance to 'class'
        self.advance_tokenizer()
        # save class name
        self.class_name = self.get_token()
        # advance to {
        self.advance_tokenizer()
        # write '{'
        self.advance_tokenizer()

        # Write classVarDec until subroutine declaration
        # TODO: I think this is useless in project 11
        while self.get_token() in 'static|field':
            self.compileClassVarDec()

        # Write Subroutines until the end of the class
        while self.get_token() != "}":
            self.compileSubroutine()

        # advance to '}'
        self.advance_tokenizer()
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
        self.advance_tokenizer()

        # write type
        myType = self.get_token()
        self.advance_tokenizer()
        # todo if type is object of class, class is use??
        # if myType not in ['int', 'char', 'boolean']:
        #     space = self.cur_indent * SPACE_AMOUNT * " "
        #     self.output_file.write(space + 'class used\n')

        # write varName
        name = self.get_token()
        self.advance_tokenizer()
        self.symbolTable.define(name, myType, kind)

        while self.get_token() == ',':
            # write ','
            self.advance_tokenizer()
            # write varName
            name = self.get_token()
            self.advance_tokenizer()
            self.symbolTable.define(name, myType, kind)

        # write ";"
        self.advance_tokenizer()

        return

    def compileSubroutine(self):
        """
        Compiles the VM representation of a subroutine
        """
        # reset
        self.symbolTable.startSubroutine()
        self._while_counter = -1
        self._if_counter = -1

        # 'constructor' | 'function' | 'method'
        subroutineKind = self.get_token()
        self.advance_tokenizer()

        # advance type
        self.advance_tokenizer()

        # get subroutineName and advance
        func_name = self.class_name + "." + self.get_token()
        self.advance_tokenizer()
        self.advance_tokenizer()
        self.compileParameterList()
        self.advance_tokenizer()

        # write subroutine dec
        numArgs = self.arg_num

        if subroutineKind == 'method':
            numArgs += 1
            self.vm_writer.writePush('pointer', 0)
            self.symbolTable.define('this', self.class_name, 'argument')
            self.vm_writer.writeFunction(func_name, numArgs)
            self.vm_writer.writePush('argument', 0)
            self.vm_writer.writePop('pointer', 0)

        elif subroutineKind == 'constructor':
            self.vm_writer.writeFunction(func_name, numArgs)
            self.vm_writer.writePush('constant', numArgs)
            self.vm_writer.writeCall('Memory.alloc', 1)
            self.vm_writer.writePop('pointer', 0)

        else:
            self.vm_writer.writeFunction(func_name, numArgs)

        self.compileSubroutineBody()
        return

    def compileParameterList(self):
        """
        Compiles the XML representation of parameterList
        """
        self.arg_num = 0

        kind = 'argument'
        if self.get_token() != ')':
            self.arg_num += 1
            # write type
            myType = self.get_token()
            self.advance_tokenizer()

            # write varName
            name = self.get_token()
            self.advance_tokenizer()
            self.symbolTable.define(name, myType, kind)

            while self.get_token() == ',':
                # write ','
                self.arg_num += 1
                self.advance_tokenizer()

                # write type
                myType = self.get_token()
                self.advance_tokenizer()

                # write varName
                name = self.get_token()
                self.advance_tokenizer()
                self.symbolTable.define(name, myType, kind)

        return

    def compileSubroutineBody(self):
        """
        Compiles the XML representation of a subroutineBody
        """
        # write "{"
        self.advance_tokenizer()
        while self.get_token() == 'var':
            # write varDec
            self.compileVarDec()

        # write statements
        self.compileStatements()
        # write "}" after the last statement (end of method body)
        self.advance_tokenizer()
        return

    def compileVarDec(self):
        """
        Compiles the XML representation of variableDeclaration
        """
        # write 'var'
        kind = self.get_token()
        self.advance_tokenizer()

        # write type
        myType = self.get_token()
        self.advance_tokenizer()

        # write varName
        name = self.get_token()
        self.advance_tokenizer()

        self.symbolTable.define(name, myType, kind)
        while self.get_token() == ',':
            # write ','
            self.advance_tokenizer()

            # write varName
            name = self.get_token()
            self.advance_tokenizer()
            self.symbolTable.define(name, myType, kind)
        # write ';'
        self.advance_tokenizer()
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
        self.advance_tokenizer()
        self._compileSubroutineCall()

        # write ';'
        self.advance_tokenizer()
        self.vm_writer.writePop("temp", 0)
        return

    def compileLet(self):
        """
        Compiles the XML representation of a Let statement
        """
        # write 'let'
        self.advance_tokenizer()

        # write varName
        name = self.get_token()
        self.advance_tokenizer()

        if self.get_token() == '[':
            # write '[ expression ]'
            self.advance_tokenizer()
            self.compileExpression()
            self.advance_tokenizer()
        # write '='
        self.advance_tokenizer()
        # write expression
        self.compileExpression()
        # write ';'
        self.advance_tokenizer()

        self.vm_writer.writePop(self.symbolTable.kindOf(name),
                                self.symbolTable.indexOf(name))
        return

    def compileWhile(self):
        """
        Compiles the XML representation of a While statement
        """
        # advance while index
        self._while_counter += 1
        self.vm_writer.writeLabel("WHILE_EXP" + str(self._while_counter))

        # while condition
        self.advance_tokenizer()
        self.advance_tokenizer()
        self.compileExpression()
        self.advance_tokenizer()

        # if-goto
        self.vm_writer.writeVM('not')
        self.vm_writer.writeIf('WHILE_END' + str(self._while_counter))

        # while body
        self.advance_tokenizer()
        self.compileStatements()
        self.advance_tokenizer()

        # goto
        self.vm_writer.writeGoto("WHILE_EXP" + str(self._while_counter))
        self.vm_writer.writeLabel('WHILE_END' + str(self._while_counter))

        self._while_counter -= 1
        return

    def compileReturn(self):
        """
        Compiles the XML representation of a Return statement
        """
        self.advance_tokenizer()
        if self.get_token() == ';':
            self.vm_writer.writePush("constant", 0)
        else:
            self.compileExpression()
        self.advance_tokenizer()
        self.vm_writer.writeVM("return")
        return

    def compileIf(self):
        """
        Compiles the XML representation of an If statement
        """
        self._if_counter += 1

        # compile if condition
        self.advance_tokenizer()
        self.advance_tokenizer()
        self.compileExpression()
        self.advance_tokenizer()

        # if goto and else
        self.vm_writer.writeIf('IF_TRUE' + str(self._if_counter))
        self.vm_writer.writeGoto('IF_FALSE' + str(self._if_counter))

        # if true
        self.vm_writer.writeLabel('IF_TRUE' + str(self._if_counter))
        self.advance_tokenizer()
        self.compileStatements()
        self.advance_tokenizer()
        self.vm_writer.writeGoto('IF_END' + str(self._if_counter))

        # else. if false
        self.vm_writer.writeLabel('IF_FALSE' + str(self._if_counter))
        self.advance_tokenizer()
        self.advance_tokenizer()
        self.compileStatements()
        self.advance_tokenizer()

        # advance index
        self.vm_writer.writeLabel('IF_END' + str(self._if_counter))
        self._if_counter -= 1
        return

    def compileExpression(self):
        """
        Compiles the XML representation of an expression
        """
        # write term
        self.compileTerm()
        while re.match(self.operations_p, self.get_token()):
            current_operation = (OPERATION_TABLE[self.get_token()])
            self.advance_tokenizer()
            self.compileTerm()
            self.vm_writer.writeVM(current_operation)
        return

    def _pushKeyword(self, key):
        if key == 'true':
            self.vm_writer.writePush('constant', 0)
            self.vm_writer.writeVM('not')
        elif key == 'false':
            self.vm_writer.writePush('constant', 0)
        elif key == 'null':
            pass
            # todo push null
        elif key == 'this':
            self.vm_writer.writePush('pointer', 0)
        return

    def compileTerm(self):
        """
        Compiles the XML representation of a term
        """
        term = self.get_token()

        # term  is (expression)
        if term == '(':
            self.advance_tokenizer()
            self.compileExpression()
            self.advance_tokenizer()

        # term is int
        elif re.match(self.tokenizer.int_const_p, term):
            self.vm_writer.writePush("constant", term)
            self.advance_tokenizer()

        # term is string
        elif re.match(self.tokenizer.str_const_p, term):
            # todo push string
            self.advance_tokenizer()

        # term is keyword
        elif re.match(self.keyword_const_p, term):
            self._pushKeyword(term)
            self.advance_tokenizer()

        elif self.get_token() in ["-", "~"]:
            unaryOp = term
            self.advance_tokenizer()
            self.compileTerm()
            # write unaryOp term
            self.vm_writer.writeVM(UNARY_TABLE[unaryOp])

        else:
            firstToken = self.get_token()
            self.advance_tokenizer()

            # firstToken is var name
            if self.symbolTable.kindOf(firstToken) is not None:
                secondToken = self.get_token()
                if secondToken == '[':
                    self.advance_tokenizer()
                    self.compileExpression()
                    self.advance_tokenizer()
                    # todo push address of secondToken[expression] to stack
                    # todo write pop to that segement

                elif secondToken == '.':
                    self.advance_tokenizer()
                    funcName = firstToken + '.' + self.get_token()
                    self.advance_tokenizer()
                    self.compileExpressionList()
                    self.vm_writer.writeCall(funcName, self.arg_num)

                else:
                    # simply varName
                    self.vm_writer.writePush(self.symbolTable.kindOf(term),
                                             self.symbolTable.indexOf(term))

            # firstToken is subroutine or class Name
            else:
                if self.get_token() == '.':
                    # term is className.sub()
                    self.advance_tokenizer()
                    funcName = firstToken + '.' + self.get_token()
                    self.advance_tokenizer()
                    self.compileExpressionList()
                    self.vm_writer.writeCall(funcName, self.arg_num)
                elif self.get_token() == '(':
                    # term is subroutine
                    funcName = self.class_name + '.' + firstToken
                    self.advance_tokenizer()
                    self.compileExpressionList()
                    self.vm_writer.writeCall(funcName, self.arg_num)

    def compileExpressionList(self):
        """
        Compiles the VM representation of an expressionList
        This method will only be called when handling a function call
        """
        self.arg_num = 0
        if self.get_token() == '(':
            self.advance_tokenizer()

        if self.get_token() != ')':
            self.compileExpression()
            while self.get_token() == ',':
                self.arg_num += 1
                self.advance_tokenizer()
                self.compileExpression()

        self.arg_num += 1
        self.advance_tokenizer()
        return
