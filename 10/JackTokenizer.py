import re

LT = '<'
GT = '>'
AMP = '&'
QUOT = '\"'

KEYWORD = "keyword"
SYMBOL = "symbol"
IDENTIFIER = "identifier"
INT_CONST = "integerConstant"
STRING_CONST = "stringConstant"


class JackTokenizer:
    # jack lexical elements
    keywords = "class|constructor|function|method|field|static|var|int|char |boolean|void|true|false|null|this|let|do |if|else|while|return"
    symbols = '{|}|\(|\)|\[|]|\.|,|;|\+|-|\*|/|&|\||<|>|=|~'
    identifiers = '[a-zA-Z_]{1}[a-zA-Z_\d]*'
    int_const = '[\d]+'
    str_const = '\"[^\r\n]+\"'
    all_tokens = keywords + '|' + symbols + '|' + identifiers + '|' + int_const + '|' + str_const
    comments = '//[^\n]*\n|/\*(.|\n)*?\*/'
    # regex patterns
    keyword_p = re.compile(keywords)
    symbol_p = re.compile(symbols)
    identifier_p = re.compile(identifiers)
    int_const_p = re.compile(int_const)
    str_const_p = re.compile(str_const)
    all_tokens_p = re.compile(all_tokens)
    comments_p = re.compile(comments)

    def __init__(self, input_file):
        self._tokens = []
        self._cur_token = None
        self._cur_type = None
        self._process_lines(input_file)
        self._cur_i = -1

    def _process_lines(self, input_file):
        """
        saves all words in file to a list.ignoring comments ("\\", "\**", "\*")
        """
        # open file
        with open(input_file, 'r') as f:
            # remove comments from text
            content = re.sub(self.comments_p, ' ', f.read())
        # create an array of all tokens
        self._tokens = re.findall(self.all_tokens_p, content)
        if "uble" in self._tokens:
            print("there is a bug in the processing of the file")
        return

    def hasMoreTokens(self):
        """
        :return: true if there are more tokens in the input, false otherwise
        """
        return self._cur_i < (len(self._tokens) - 1)

    def advance(self):
        """
        gets the next token from the input and makes it the current token.
        This method should only be called if hasMoreTokens() is true.
        Initially there is no current token.
        """
        # update cur_token
        self._cur_i += 1
        self._cur_token = self._tokens[self._cur_i]

        # update cur_type
        if re.match(self.keyword_p, self._cur_token):
            self._cur_type = KEYWORD
        elif re.match(self.symbol_p, self._cur_token):
            self._cur_type = SYMBOL
        elif re.match(self.identifier_p, self._cur_token):
            self._cur_type = IDENTIFIER
        elif re.match(self.int_const_p, self._cur_token):
            self._cur_type = INT_CONST
        elif re.match(self.str_const_p, self._cur_token):
            self._cur_type = STRING_CONST

    def tokenType(self):
        """
        :return: type of current token, one of the followings:
        KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST
        """
        return self._cur_type

    def keyword(self):
        """
        :return: returns the keyword which is the current token.
        Should be called only when tokenType() is KEYWORD.
        keywords: CLASS, METHOD, FUNCTION, CONSTRUCTOR, INT, BOOLEAN, CHAR,
        VOID, VAR, STATIC, FIELD, LET, DO, IF, ELSE, WHILE, RETURN, TRUE,
        FALSE, NULL, THIS.
        """
        return str(self._cur_token)

    def symbol(self):
        """
        :return: returns the character which is the current token.
        Should be called only when tokenType() is SYMBOL.
        """
        # replace symbols that are used in jack language
        if self._cur_token == LT:
            return "&lt;"
        elif self._cur_token == GT:
            return "&gt;"
        elif self._cur_token == QUOT:
            return "&quot;"
        elif self._cur_token == AMP:
            return "&amp;"
        return str(self._cur_token)

    def identifier(self):
        """
        :return: returns the identifier which is the current token.
        Should be called only when tokenType() is IDENTIFIER
        """
        return str(self._cur_token)

    def intVal(self):
        """
        :return: returns the integer value of the current token.
        Should be called only when tokenType() is INT_CONST
        """
        return str(self._cur_token)

    def stringVal(self):
        """
        :return: returns the string value of the current token,
        without the double quotes.
        Should be called only when tokenType() is STRING_CONST
        """
        return str(self._cur_token)[1:-1]
