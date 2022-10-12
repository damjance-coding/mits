from sly import Lexer

class MyLexer(Lexer):

    tokens = {PRINT , STRING, DEFINE, IDENTIFIER , END, CALL , INT , NUMBER, STR, FL, FLOAT, GLOBAL, RANDOM, IF , EQEQ, SUBPR, ELSE , PASS , INPUT, WHILE, NOTEQ, EXIT, IMPORT, TRUE , FALSE, BOOL, ASSERT, AR, ARRAY, POS, APPEND,RM, SYSTEM, LPREN, RPREN }


    literals = { '=', '+', '-', '/', '*',  ':', '<', '>', '%', '^', ',',  }
    ignore = ' \t '
    ignore_comment = r'\//.*'
    
    

   

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

   
    
    
    @_(r"\d+\.\d*")
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t
    LPREN = r"("
    RPREN = r")"
    
    FL = r"float"
    SYSTEM = r"system"
    RM = r"rm"
    APPEND = r"append"
    POS = r'pos'
    ARRAY  = r'\[.*?\]'
    AR = r"arr"
    ASSERT = r"assert"
    BOOL = r"bool"
    TRUE = r"True"
    FALSE = r"False"
    IMPORT = r"import"
    EXIT = r"exit"
    NOTEQ = r"!="
    WHILE = r'while'
    ELSE = r"else"
    PASS = r'pass'
    SUBPR = r"subprocess"
    EQEQ = r'=='
    RANDOM = r'random'
    GLOBAL = r"global"
    IF = r"if"
    INPUT = r'input'
    
    STR = r"str"
    INT = r"int"
    DEFINE = r"define"
    END = r"end"
    PRINT = r"print"
    CALL = r"call"
    @_(r'''("[^"\\]*(\\.[^"\\]*)*"|'[^'\\]*(\\.[^'\\]*)*')''')
    def STRING(self, t):
        t.value = self.remove_quotes(t.value)
        return t

    # Notice Identifier comes after string because most words in a string would be matched with the identifier pattern
    IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'

    def remove_quotes(self, text: str):
        if text.startswith('\"') or text.startswith('\''):
            return text[1:-1]
        return text