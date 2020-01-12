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
UNARY_TABLE = {'-': 'neg', '~': 'not'}


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

        # firstToken is var name
        if self.symbolTable.kindOf(firstToken) is not None:
            secondToken = self.get_token()

            if secondToken == '[':
                self.advance_tokenizer()
                self.compileExpression()
                self.advance_tokenizer()

            elif secondToken == '.':
                # push var to stuck, so var.foo could be called
                self.vm_writer.writePush(self.symbolTable.kindOf(firstToken),
                                         self.symbolTable.indexOf(firstToken))
                self.arg_num += 1

                self.advance_tokenizer()
                funcName = self.symbolTable.typeOf(
                    firstToken) + '.' + self.get_token()
                self.advance_tokenizer()
                self.compileExpressionList()
                self.vm_writer.writeCall(funcName, self.arg_num)

            else:
                # simply varName
                self.vm_writer.writePush('pointer', 0)
                self.arg_num += 1
                self.advance_tokenizer()

        # firstToken is subroutine or class Name
        else:
            if self.get_token() == '.':
                # term is className.sub()
                # self.vm_writer.writePush('pointer', 0)
                # self.arg_num += 1
                self.advance_tokenizer()
                funcName = firstToken + '.' + str(self.get_token())
                self.advance_tokenizer()
                self.compileExpressionList()
                if self.symbolTable.kindOf(firstToken) == 'method':
                    self.symbolTable.define('this', self.class_name,
                                            'argument')
                    self.vm_writer.writePush('pointer', 0)
                    self.arg_num += 1
                self.vm_writer.writeCall(funcName, self.arg_num)

            elif self.get_token() == '(':
                # term is subroutine
                funcName = self.class_name + '.' + firstToken
                self.advance_tokenizer()
                self.compileExpressionList()
                self.vm_writer.writePush('pointer', 0)
                self.arg_num += 1
                self.vm_writer.writeCall(funcName, self.arg_num)

        # reset arg_num for following functions
        self.arg_num = 0
        return

    #  ___________ API METHODS _____________ #
    def __init__(self, tokenizer, VMWriter):
        # The local variables amount of a currently compiled function
        self._var_num = 0
        self._cur_subroutine_name = ""
        self._cur_subroutine_kind = ""
        self.cur_indent = 0
        self.vm_writer = VMWriter
        self.tokenizer = tokenizer
        self.symbolTable = SymbolTable.SymbolTable()
        self.class_name = ""
        self.arg_num = 0
        self._while_counter = -1
        self._if_counter = -1
        self._handling_array = False

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
        # advance to 'class'
        self.advance_tokenizer()
        # save class name
        self.class_name = self.get_token()
        # advance beyond {
        self.advance_tokenizer()
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

            return "\"" + str(self.tokenizer.stringVal()) + "\""

    def compileClassVarDec(self):
        """
        Compiles the XML representation of class variables declaration
        """
        # count the first variable
        self._var_num += 1
        # write 'static'|'field'
        kind = self.get_token()
        self.advance_tokenizer()
        # write type
        myType = self.get_token()
        self.advance_tokenizer()
        # todo if type is object of class, class is use??
        # if myType not in ['int', 'char', 'boolean']:

        # define varName
        name = self.get_token()
        self.advance_tokenizer()
        self.symbolTable.define(name, myType, kind)

        while self.get_token() == ',':
            self._var_num += 1
            self.advance_tokenizer()
            # define varName
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
        self.arg_num = 0

        # 'constructor' | 'function' | 'method'
        self._cur_subroutine_kind = self.get_token()
        self.advance_tokenizer()
        self.advance_tokenizer()

        # get subroutineName and advance
        self._cur_subroutine_name = self.class_name + "." + self.get_token()

        self.advance_tokenizer()
        self.advance_tokenizer()
        self.compileParameterList()
        self.advance_tokenizer()

        self.arg_num = 0
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
            # Increase the amount of function local variables
            self.compileVarDec()
        self.write_subroutine_dec()
        self.compileStatements()
        # write "}" after the last statement (end of method body)
        self.advance_tokenizer()
        return

    def write_subroutine_dec(self):
        # write subroutine dec
        if self._cur_subroutine_kind == 'method':
            self.vm_writer.writeFunction(self._cur_subroutine_name,
                                         self._var_num)
            self.vm_writer.writePush('argument', 0)
            self.vm_writer.writePop('pointer', 0)
        elif self._cur_subroutine_kind == 'constructor':
            self.vm_writer.writeFunction(self._cur_subroutine_name, 0)
            self.vm_writer.writePush('constant', self._var_num)
            self.vm_writer.writeCall('Memory.alloc', 1)
            self.vm_writer.writePop('pointer', 0)
        else:
            self.vm_writer.writeFunction(self._cur_subroutine_name,
                                         self._var_num)
        # reset var_num after subroutine declaration
        self._var_num = 0

    def compileVarDec(self):
        """
        Compiles the XML representation of variableDeclaration
        """
        self._var_num += 1

        kind = self.get_token()
        self.advance_tokenizer()
        myType = self.get_token()
        self.advance_tokenizer()

        # define varName
        name = self.get_token()
        self.advance_tokenizer()
        self.symbolTable.define(name, myType, kind)

        while self.get_token() == ',':
            self._var_num += 1
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
        # push result to stack
        self.vm_writer.writePop("temp", 0)
        return

    def compileLet(self):
        """
        Compiles the XML representation of a Let statement
        """
        # write 'let'
        self.advance_tokenizer()

        # varName
        name = self.get_token()
        self.advance_tokenizer()

        if self.get_token() == '[':
            # CURRENTLY ONLY SUPPORTING ARRAYS
            # TODO: Extend this feature to support specific string chars accessing.
            # write '[ expression ]'
            self.advance_tokenizer()
            self.compileExpression()
            self.vm_writer.writePush("local", str(self.symbolTable.indexOf(name)))
            self.vm_writer.writeVM("add")
            self.advance_tokenizer()
            self._handling_array = True
        # write '='
        self.advance_tokenizer()
        # write expression
        self.compileExpression()
        if self._handling_array:
            self.vm_writer.writePop("temp", 0)
            self.vm_writer.writePop("pointer", 1)
            self.vm_writer.writePush("temp", 0)
            self.vm_writer.writePop("that", 0)
            self._handling_array = False
        # write ';'
        else:
            self.vm_writer.writePop(self.symbolTable.kindOf(name),
                                    self.symbolTable.indexOf(name))
        self.advance_tokenizer()
        return

    def compileWhile(self):
        """
        Compiles the XML representation of a While statement
        """
        # advance while index
        self._while_counter += 1
        cur_while_counter = self._while_counter
        self.vm_writer.writeLabel("WHILE_EXP" + str(cur_while_counter))

        # while condition
        self.advance_tokenizer()
        self.advance_tokenizer()
        self.compileExpression()
        self.advance_tokenizer()

        # if-goto
        self.vm_writer.writeVM('not')
        self.vm_writer.writeIf('WHILE_END' + str(cur_while_counter))

        # while body
        self.advance_tokenizer()
        self.compileStatements()
        self.advance_tokenizer()

        # goto
        self.vm_writer.writeGoto("WHILE_EXP" + str(cur_while_counter))
        self.vm_writer.writeLabel('WHILE_END' + str(cur_while_counter))
        return

    def compileReturn(self):
        """
        Compiles the XML representation of a Return statement
        """
        self.advance_tokenizer()
        if self.get_token() == ';':
            # return void
            self.vm_writer.writePush("constant", 0)
        else:
            # push return value
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
        self.vm_writer.writeLabel('IF_FALSE' + str(self._if_counter))
        # else. if false
        if self.get_token() == 'else':
            self.advance_tokenizer()
            self.advance_tokenizer()
            self.compileStatements()
            self.advance_tokenizer()
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
            self._push_string(term)
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
            # term is subroutine | class | var
            firstToken = self.get_token()
            self.advance_tokenizer()

            # firstToken is var name
            if self.symbolTable.kindOf(firstToken) is not None:
                secondToken = self.get_token()
                if secondToken == '[':
                   # write '[ expression ]'
                   self.advance_tokenizer()
                   self.compileExpression()
                   self.vm_writer.writePush("local", str(self.symbolTable.indexOf(firstToken)))
                   self.advance_tokenizer()
                   self.vm_writer.writeVM("add")
                   # add the value to the array
                   #TODO: A bit clunky implementation, needs to be imporved
                   self.vm_writer.writePop("pointer", 1)
                   self.vm_writer.writePush("that", 0)
                elif secondToken == '.':
                    self.advance_tokenizer()
                    funcName = firstToken + '.' + self.get_token()

                    self.advance_tokenizer()
                    self.compileExpressionList()
                    self.vm_writer.writeCall(funcName, self.arg_num)
                    self.arg_num = 0
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
                    self.arg_num = 0

                elif self.get_token() == '(':
                    # term is subroutine
                    funcName = self.class_name + '.' + firstToken
                    self.advance_tokenizer()
                    self.compileExpressionList()
                    self.vm_writer.writeCall(funcName, self.arg_num)
                    self.arg_num = 0

    def _push_string(self, string):
        """
        Pushes the ascii representation of a given string to the stack
        :param string: The string to push to the stack
        """
        string = string[1:len(string)-1]
        str_len = len(string)
        # push first char
        self.vm_writer.writePush("constant", str_len)
        self.vm_writer.writeCall("String.new", 1)
        # push the rest of the chars
        for char in string:
            char_ascii = ord(char)
            self.vm_writer.writePush("constant", char_ascii)
            self.vm_writer.writeCall("String.appendChar", 2)
        return




    def compileExpressionList(self):
        """
        Compiles the VM representation of an expressionList
        This method will only be called when handling a function call
        """
        if self.get_token() == '(':
            self.advance_tokenizer()

        if self.get_token() != ')':

            self.arg_num += 1
            self.compileExpression()
            while self.get_token() == ',':
                self.advance_tokenizer()
                self.arg_num += 1
                self.compileExpression()

        self.advance_tokenizer()
        return
