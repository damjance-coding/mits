from sly import Parser
from lexer import MyLexer

class MyParser(Parser):

    tokens = MyLexer.tokens
    
    
    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        
        )

    def error(self, p):
        assert False, f"Syntax Error at line {p.lineno}"
        
        
    

    @_("DEFINE IDENTIFIER")
    def statement(self, p):
        
        return ("define_function", p.IDENTIFIER)    
    @_("EXIT expr")
    def statement(self, p):
        return("exit_prog", p.expr)

    @_("EXIT")
    def statement(self, p):
        return("exit_prog_no_expr",)
   
    @_('DEFINE SUBPR IDENTIFIER ":" IDENTIFIER')
    def statement(self, p):
        return ("define_subpr", p.IDENTIFIER0, p.IDENTIFIER1)

    @_("END SUBPR")
    def statement(self, p):
        return ("end_subpr", )
    @_("CALL SUBPR IDENTIFIER")
    def statement(self, p ):
        return ("call_sub", p.IDENTIFIER)
    @_("END")
    def statement(self, p):

        return ("end_function", )

    @_("IMPORT STRING")
    def statement(self, p):
        return ("import_file", p.STRING)

    @_("PRINT expr")
    def statement(self, p):

        return ("print_expr", p.expr)

    @_("PRINT IDENTIFIER")
    def statement(self, p):
        return ("print_var", p.IDENTIFIER)

    @_("PRINT GLOBAL IDENTIFIER")
    def statement(self, p):
        return ("print_global_var", p.IDENTIFIER)

    @_("CALL IDENTIFIER")
    def statement(self, p):
        
        return ("call_function", p.IDENTIFIER)

    @_('INT IDENTIFIER "=" expr')
    def statement(self, p):
        return ("create_var_int", p.IDENTIFIER, p.expr)

    @_('FL IDENTIFIER "=" RANDOM expr expr')
    def statement(self, p):
        return ("create_var_float-random", p.IDENTIFIER, p.expr0 , p.expr1)

    
    @_('INT IDENTIFIER "=" RANDOM expr expr')
    def statement(self, p):
        return ("create_var_int-random", p.IDENTIFIER, p.expr0, p.expr1)


    @_('GLOBAL FL IDENTIFIER "=" RANDOM expr expr')
    def statement(self, p):
        return ("create_var_float-random-global", p.IDENTIFIER, p.expr0 , p.expr1)

    
    @_('GLOBAL INT IDENTIFIER "=" RANDOM expr expr')
    def statement(self, p):
        return ("create_var_int-random-global", p.IDENTIFIER, p.expr0, p.expr1)


    @_('STR IDENTIFIER "=" STRING')
    def statement(self, p):
        return ("create_var_str", p.IDENTIFIER, p.STRING)

    @_('STR IDENTIFIER "=" INPUT STRING')
    def statement(self, p):
        return ("create_var_str_input", p.IDENTIFIER, p.STRING)

    @_('BOOL IDENTIFIER "=" condition')
    def statement(self, p):
        return ("create_var_bool", p.IDENTIFIER, p.condition)


    @_('GLOBAL BOOL IDENTIFIER "=" condition')
    def statement(self, p):
        return ("create_var_bool_global", p.IDENTIFIER, p.condition)

    @_('INT IDENTIFIER "=" INPUT STRING')
    def statement(self, p):
        return ("create_var_int_input", p.IDENTIFIER, p.STRING)

    @_('FL IDENTIFIER "=" INPUT STRING')
    def statement(self, p):
        return ("create_var_float_input", p.IDENTIFIER, p.STRING)

    @_('GLOBAL INT IDENTIFIER "=" expr')
    def statement(self, p):
        return ("create_global_var_int", p.IDENTIFIER, p.expr)


    @_('GLOBAL STR IDENTIFIER "="  STRING')
    def statement(self, p):
        return ("create_global_var_str", p.IDENTIFIER, p.STRING)

    @_('IDENTIFIER "=" condition')
    def statement(self ,p):
        return("change_var_value_bool", p.IDENTIFIER, p.condition)

    @_('GLOBAL FL IDENTIFIER "=" expr')
    def statement(self, p):
        return ("create_global_var_float", p.IDENTIFIER, p.expr)

    @_('IDENTIFIER "=" expr')
    def statement(self, p):
        return ("change_var_value", p.IDENTIFIER, p.expr)


    @_('IDENTIFIER "=" INPUT STRING')
    def statement(self, p):
        return ("change_var_value_input", p.IDENTIFIER, p.STRING)

    @_('IDENTIFIER "=" STRING')
    def statement(self, p):
        return ("change_var_value_str", p.IDENTIFIER, p.STRING)

    @_("PRINT STRING")
    def statement(self, p):

        return ("print", p.STRING)

    

    @_('expr')
    def statement(self, p):
        return (p.expr,)

    @_('expr "+" expr')
    def expr(self, p):
        return ('add', p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return ('sub', p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return ('mul', p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return ('div', p.expr0, p.expr1)

    @_('NUMBER')
    def expr(self, p):
        return ('num', p.NUMBER)
    @_('FLOAT')
    def expr(self, p):
        
        return ('float', p.FLOAT)
    @_('FL  "=" expr')
    def statement(self, p):
        return ("create_var_float", p.IDENTIFIER, p.expr)
    @_('IDENTIFIER')
    def expr(self, p):
        return ("IDENTIFIER", p.IDENTIFIER)
    

    ##CODITIONS

    @_("TRUE")
    def condition(self, p):
        return("con_true", )

    @_("FALSE")
    def condition(self, p):
        return("con_false", )
    @_('expr EQEQ expr')
    def condition(self, p):
        return ("con_eqeq" , p.expr0 , p.expr1)


    @_('expr NOTEQ expr')
    def condition(self, p):
        return ("con_noteq" , p.expr0 , p.expr1)
    
    @_("IDENTIFIER EQEQ condition")
    def condition(self, p):
        return("bool_eqeq_con", p.IDENTIFIER, p.condition)


    @_("IDENTIFIER NOTEQ condition")
    def condition(self, p):
        return("bool_noteq_con", p.IDENTIFIER, p.condition)

    @_("condition EQEQ  IDENTIFIER")
    def condition(self, p):
        return("con_eqeq_bool", p.IDENTIFIER, p.condition)

    @_("condition NOTEQ  IDENTIFIER")
    def condition(self, p):
        return("con_noteq_bool", p.IDENTIFIER, p.condition)
    @_("condition EQEQ condition")
    def condition(self ,p):
        return("con_eqeq_con", p.condition0, p.condition1)
    @_('expr "<" expr')
    def condition(self, p):
        return ("con_sthan" , p.expr0 , p.expr1)


    @_('expr ">" expr')
    def condition(self, p):
        return ("con_gthan" , p.expr0 , p.expr1)

    @_('STRING EQEQ STRING')
    def condition(self, p):
        return ("str_eq_str" , p.STRING0 , p.STRING1)

    
    @_('STRING NOTEQ STRING')
    def condition(self, p):
        return ("str_noteq_str" , p.STRING0 , p.STRING1)

    @_('expr EQEQ STRING')
    def condition(self, p):
        return ("ind_eq_str" , p.expr , p.STRING)

    @_('expr NOTEQ STRING')
    def condition(self, p):
        return ("ind_noteq_str" , p.expr , p.STRING)


    @_('STRING EQEQ expr')
    def condition(self, p):
        return ("str_eq_expr" , p.expr , p.STRING)
    @_('STRING NOTEQ expr')
    def condition(self, p):
        return ("str_noteq_expr" , p.expr , p.STRING)



    @_("PASS")
    def statement(self, p):
        return ("pass", )
    @_("IF condition THEN statement ELSE statement")
    def statement(self, p):
        return ("if_st", p.condition, p.statement0, p.statement1) 

    @_("WHILE condition THEN statement")
    def statement(self , p):
        return ('while_loop', p.condition, p.statement) 

      


