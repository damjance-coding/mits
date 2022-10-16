from sly import Parser
from lexer import Lex

class Pars(Parser):

    tokens = Lex.tokens

    precedence = (
        ('left', '+', '-',),
        ('left', '*', '/'),
        
        ('right', 'UMINUS'),
        )


    @_('FUNCTION IDENTIFIER "(" ")"  "{" ')
    def statement(self ,p):
        return ("op_declare_function", p.IDENTIFIER)
    @_("RETURN expr", "RETURN condition")
    def statement(self ,p):
        return ("return", p[1])
    @_("INCLUDE STRING")
    def statement(self , p):
        return ("include", p.STRING)
    @_('"}"')
    def statement(self ,p):
        return ("op_close_end", )
    @_('TRY "{"  ')
    def statement(self ,p):
        return ("try_start", )
    @_('THROW IDENTIFIER , expr')
    def statement(self ,p) :
        return ("throw", p.IDENTIFIER , p.expr)
    @_("ERROR IDENTIFIER END")
    def statement(self ,p):
        return ("define_error", p.IDENTIFIER)
    @_('EXCEPT "{"  ')
    def statement(self ,p):
        return ("except_start", )

    @_('ASSERT "(" condition ")" "," expr')
    def statement(self , p):
        return ("assertion", p.condition, p.expr)
    @_("TYPEOF expr")
    def expr(self ,p):
        return ("typeof", p.expr)

   
    @_('"}" END')
    def statement(self ,p):
        return ("op_close",) 

    @_('IDENTIFIER ARRAY "=" expr')
    def statement(self ,p):
        
         return ("add_new_to_arr", p.IDENTIFIER, p.ARRAY, p.expr)
    @_('expr')
    def statement(self, p):
        return (p.expr)
    

    @_('expr "+" expr')
    def expr(self, p):
        return ('expr_add', p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return ('expr_sub', p.expr0, p.expr1)

    @_('expr "%" expr')
    def expr(self, p):
        return ('expr_prec', p.expr0, p.expr1)

    @_('expr "^" expr')
    def expr(self, p):
        return ('expr_pow', p.expr0, p.expr1)
    

    @_('expr "*" expr')
    def expr(self, p):
        return ('expr_mul', p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return ('expr_div', p.expr0, p.expr1)
    
    @_("TRUE")
    def condition(self ,p):
        return ("true",)

    
    @_("FALSE")
    def condition(self ,p):
        return ("false",)

    @_("STRING")
    def expr(self ,p):
        return ("expr_string", p.STRING)

    @_('NUMBER')
    def expr(self, p):
        return ('expr_int', p.NUMBER)

    @_("WRITE expr", 'WRITE condition')
    def statement(self ,p):
        return ("op_write", p[1])

    @_("ARROWOP IDENTIFIER")
    def statement(self , p):
        return ("callmacro", p.IDENTIFIER)
    @_('expr ARROWOP IDENTIFIER "(" ")"')
    def statement(self , p):
        return ("pass_param", p.expr, p.IDENTIFIER)

    @_("ARROWOP GLOBAL IDENTIFIER")
    def statement(self , p):
        return ("callmacro_global", p.IDENTIFIER)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return ("expr_neg_num", p.expr)
    #IDENTIFIER "=" condition'
    @_('INT32 IDENTIFIER "=" expr',)
    def var_assign(self , p):
        return ("var_assign_int32", p.IDENTIFIER , p.expr)

    @_('INT64 IDENTIFIER "=" expr',)
    def var_assign(self , p):
        return ("var_assign_int64", p.IDENTIFIER , p.expr)

    @_('STR IDENTIFIER "=" expr',)
    def var_assign(self , p):
        return ("var_assign_str", p.IDENTIFIER , p.expr)

    # @_('GLOBAL IDENTIFIER "=" expr', 'GLOBAL IDENTIFIER "=" condition')
    # def var_assign(self , p):
    #     return ("global_var_assign", p.IDENTIFIER , p[3])

    @_('"(" expr ")"')
    def expr(self ,p):
        return p.expr
    @_("IDENTIFIER")
    def expr(self , p):
        return ("identifier", p.IDENTIFIER)

    @_("GLOBAL IDENTIFIER")
    def expr(self , p):
        return ("global_identifier", p.IDENTIFIER)
   
    @_("FLOAT")
    def expr(slef ,p):
        return ("expr_float", p.FLOAT)

    @_("ARRAY")
    def expr(self ,p):
        return ("expr_array", p.ARRAY)


    @_('expr ARRAY')
    def expr(self , p):
        return ("expr_pos", p.expr, p.ARRAY)

    @_("expr EQEQ expr")
    def condition(self ,p):
    
        return ("con_eq_eq", p.expr0, p.expr1) 
    @_("ARGC")
    def expr(self , p):
        return ("argc", )
    @_("ARGV")
    def expr(self ,p):
        return ("argv",)

    @_("PARAM expr")
    def expr(self ,p):
        return ("param", p.expr)

    @_('expr ">" expr')
    def condition(self ,p):
        return ("con_g_than", p.expr0, p.expr1)

    @_('expr EQGTHAN expr')
    def condition(self ,p):
        return ("con_eq_or_g_than", p.expr0, p.expr1)

    @_('IDENTIFIER "+" "+" ')
    def statement(self , p):
        return ("plusplus", p.IDENTIFIER)

    @_('expr EQSTHAN expr')
    def condition(self ,p):
        return ("con_eq_or_s_than", p.expr0, p.expr1)

    @_("expr NOTEQ expr")
    def condition(self ,p):
        return ("con_not_eq", p.expr0, p.expr1) 

    @_('expr "<" expr')
    def condition(self ,p):
        return ("con_s_than", p.expr0, p.expr1)

    @_('IF "(" condition ")" "{"  ')
    def statement(self ,p):
        return ("op_if_start", p.condition , )  

    # @_('IF "(" condition ")" "{" statement "}" ELSE  "{" statement "}" ')
    # def statement(self ,p):
    #     return ("op_if_else", p.condition , p.statement0 , p.statement1)

    @_('ELSE "{" ')
    def statement(self ,p):
        return ("else", ) 
            
    @_('WHILE "(" condition ")" "{" ')
    def statement(self , p):
         return ("op_start_while", p.condition )

    @_('FOR IDENTIFIER IN expr  "{"  ')
    def statement(self ,p):
        return ("for_start", (p.IDENTIFIER , p.expr,))
    @_('IDENTIFIER "(" ")"')
    def expr(self ,p):
        return("function_call", p.IDENTIFIER)

    @_("condition")
    def statement(self ,p):
        return p.condition

    @_("var_assign")
    def statement(self , p):
        return p.var_assign

   