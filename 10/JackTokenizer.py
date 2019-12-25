import re
from enum import Enum

LT = '<'
GT = '>'
AMP = '&'
QUOT = '\"'

# jack lexical elements
keywords = 'class|constructor|function|method|field|static|var|int|char|' \
           'boolean|void|true|false|null|this|let|do|if|else|while|return'
symbols = '{|}|\(|\)|\[|]|\.|,|;|\+|-|\*|/|&|\||<|>|=|~'
identifiers = '[a-zA-Z_]{1}[a-zA-Z_\d]*'
int_const = '[\d]+'
str_const = '\"[^\r\n\"]+\"'
all_tokens = keywords + '|' + symbols + '|' + identifiers + '|' + int_const \
             + '|' + str_const
comments = '//[^\n]*\n|/\*(.|\n)*?\*/'

# regex patterns
keyword_p = re.compile(keywords)
symbol_p = re.compile(symbols)
identifier_p = re.compile(identifiers)
int_const_p = re.compile(int_const)
str_const_p = re.compile(str_const)
all_tokens_p = re.compile(all_tokens)
comments_p = re.compile(comments)

# token types
tokenTypes = Enum('tokenTypes', 'KEYWORD SYMBOL IDENTIFIER INT_CONST '
                                'STRING_CONST')
tokenDict = {
    tokenTypes.KEYWORD: "keyword",
    tokenTypes.SYMBOL: "symbol",
    tokenTypes.IDENTIFIER: "identifier",
    tokenTypes.INT_CONST: "integerConstant",
    tokenTypes.STRING_CONST: "stringConstant",
}


class JackTokenizer:

    def __init__(self, input_file):
        self._tokens = []
        self._cur_token = None
        self._cur_type = None
        self._process_lines(input_file)
        self._cur_i = -1

    def _process_lines(self, input_file):
        """
        saves all words in file to a list.
        ignoring comments ("\\", "\**", "\*")
        """
        with open(input_file, 'r') as f:
            content = re.sub(comments_p, ' ', f.read())
        self._tokens = re.findall(all_tokens_p, content)
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
        self._cur_i += 1
        self._cur_token = self._tokens[self._cur_i]

    def tokenType(self):
        """
        :return: type of current token, one of the followings:
        KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST
        """
        if keyword_p.match(self._cur_token):
            return tokenTypes.KEYWORD
        elif symbol_p.match(self._cur_token):
            return tokenTypes.SYMBOL
        elif identifier_p.match(self._cur_token):
            return tokenTypes.IDENTIFIER
        elif str_const_p.match(self._cur_token):
            return tokenTypes.STRING_CONST
        elif int_const_p.match(self._cur_token):
                return tokenTypes.INT_CONST
        else:
            return "illegal token (tokenType function)"

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
        if self._cur_token == LT:
            return "&lt;"
        elif self._cur_token == GT:
            return "&gt;"
        elif self._cur_token == QUOT:
            return "&quot;"
        elif self._cur_token == AMP:
            return "&amp;"
        return self._cur_token

    def identifier(self):
        """
        :return: returns the identifier which is the current token.
        Should be called only when tokenType() is IDENTIFIER
        """
        return self._cur_token

    def intVal(self):
        """
        :return: returns the integer value of the current token.
        Should be called only when tokenType() is INT_CONST
        """
        return self._cur_token

    def stringVal(self):
        """
        :return: returns the string value of the current token,
        without the double quotes.
        Should be called only when tokenType() is STRING_CONST
        """
        return self._cur_token[1:-1]


n = open("my.xml", "w+")
test = JackTokenizer("SquareGame.jack")
while test.hasMoreTokens():
    test.advance()
    n.write("<" + tokenDict[test.tokenType()] + "> ")
    type = test.tokenType()
    if type == tokenTypes.KEYWORD:
        n.write(test.keyword())
    elif type == tokenTypes.SYMBOL:
        n.write(test.symbol())
    elif type == tokenTypes.IDENTIFIER:
        n.write(test.identifier())
    elif type == tokenTypes.INT_CONST:
        n.write(test.intVal())
    elif type == tokenTypes.STRING_CONST:
        n.write(test.stringVal())
    n.write(" </" + tokenDict[test.tokenType()] + ">\n")

