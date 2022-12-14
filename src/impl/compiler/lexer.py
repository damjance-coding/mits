from sly import Lexer


class Lex(Lexer):

 

    tokens = {FUNCTION , IDENTIFIER , WRITE, STRING ,  NUMBER,  ARROWOP, EQEQ, IF, ELSE, NOTEQ, EQGTHAN , EQSTHAN, WHILE, FLOAT, GLOBAL, INCLUDE, ARRAY, ARGV, ARGC,PARAM, RETURN, TRUE, FALSE,   FOR , IN, TYPEOF, END, TRY, EXCEPT, ASSERT, ERROR, THROW, INT32, INT64, STR,  }
    literals = {"{", "}", "+", "-", "*", "/", "(", ")", "=", "<", ">", ",", "[", "]", ":", "%", "^"}

    ignore = '\t \n'

    @_(r'//.*')
    def COMMENT(self, t):
        pass
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)
    
    STR   = r"str"
    INT32 = r"int32"
    INT64 = r"int64"
   
    
    ERROR = r"Error"
    INCLUDE = r'#include'
    WHILE = r"while"
    ARROWOP = r"->"
    FUNCTION = r"function"
    WRITE = r"write"
    NOTEQ = r"!="
    ARRAY = r'\[.*?\]'
    IF = r"if"
    ELSE = r"else"
    ASSERT = r"assert"
    EQEQ = r"=="
    EQGTHAN = r'>='
    EQSTHAN = r'<='
    GLOBAL = r"global"
    ARGV = r"argv"
    ARGC = r"argc"
    PARAM = r"param"
    RETURN = r'return'
    THROW = r'throw'
    TRUE = 'true'
    FALSE= 'false'
    TRY = r"try"
    EXCEPT = r"except"
    FOR  = "for"
    IN = "in"
    TYPEOF = r"typeof"
    END = r"fin"
    # PassVariable = r'PassValue'
    @_(r"\d+\.\d*")
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    @_(r'''("[^"\\]*(\\.[^"\\]*)*"|'[^'\\]*(\\.[^'\\]*)*')''')
    def STRING(self, t):
        t.value = self.remove_quotes(t.value)
        return t

    @_(r"(0|[1-9][0-9]*)")
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'

    def remove_quotes(self, text: str):
        if text.startswith('\"') or text.startswith('\''):
            return text[1:-1]
        return text