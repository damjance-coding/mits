
## Imports
from lexer import MyLexer
from parser import MyParser
import sys
import randomint
import randomfloat

testlexer = MyLexer()#Lexer
testparser = MyParser()#Parser

#Parsed tokens defined
parsedtokens = ()
#without top level
gen = ()
#top level
toplevel = ()

#Load the file
with open(sys.argv[1],'r') as file:
    lines = [line.strip() for line in file]
    


#Transfer file into tokens
for line in lines:
    
    if len(line) != 0 and line.startswith('//') == False:
        x  = line.strip()
    
        if len(x) != 0 : y  =testparser.parse(testlexer.tokenize(x))
        
        if len(y) != 0 :
            parsedtokens += (y, )
    else: pass
    




#Envoirment variable , that will store functions and variables
env = {'globalvars': {}}



#Create functions and generate top level
def transfertofunctions(x):
    global gen
    for index, currentnode in enumerate(x):
        
        if currentnode[0] == 'define_function':
            gen += (currentnode, )
            pos  = 0
            func = ()
            funcname = currentnode[1]

            #Get the nextelement of the loop
            nextelem = x[(index + pos) % len(x)]
            
            

            while nextelem[0] != "end_function":
                pos += 1
                nextelem = x[(index + pos) % len(x)]
                gen += (nextelem,)


                        
                        
                if nextelem[0] != "end_function": func += (nextelem, )
            if nextelem[0] ==  "end_function":
                env[funcname] = func
                env[f"{funcname}vars"] = {}
                env[f"{funcname}subs"] = {}
            
        if currentnode[0] == 'define_subpr':
            gen += (currentnode, )
            pos  = 0
            subpr = ()
            funcname = currentnode[2]

            #Get the nextelement of the loop
            nextelem = x[(index + pos) % len(x)]
            
            

            while nextelem[0] != "end_subpr":
                pos += 1
                nextelem = x[(index + pos) % len(x)]
                gen += (nextelem,)


                        
                        
                if nextelem[0] != "end_subpr": subpr += (nextelem, )
            if nextelem[0] ==  "end_subpr":
                env[f"{funcname}subs"][currentnode[1]] = (subpr,)
                

    
   



            


# parsed tokens -> fuctions           
transfertofunctions(parsedtokens)



#define top level            
toplevel = tuple(set(gen) ^ set(parsedtokens))





#Top level walk tree
def walktreetoplevel(node):
    

    if node[0] == "create_global_var_float":
        
        if node[1] not in env[f"globalvars"]: env['globalvars'][node[1]] = float(walktreetoplevel(node[2]))
        else: assert False, f"global variable {node[1]} already exists"
    
    elif node[0] == "create_var_bool_global":
        if node[1] not in env["globalvars"]: env['globalvars'][node[1]] = walktreetoplevel(node[2])
        else: assert False, f"Variable {node[1]} already exists"

    elif node[0] == 'create_global_var_int':
        if node[1] not in env["globalvars"]: env[f'globalvars'][node[1]] = walktreetoplevel(node[2])
        else: assert False, f"global variable {node[1]} already exists" 

    elif node[0] == "create_var_int-random-global":
        
        if node[1] not in env["globalvars"]: env['globalvars'][node[1]] = randomint.randint(walktreetoplevel(node[2]), walktreetoplevel(node[3]))
        else: assert False, f"global variable {node[1]} already exists"


    elif node[0] == "create_var_float-random-global":
        
        if node[1] not in env["globalvars"]: env['globalvars'][node[1]] = float(randomfloat.gen_random_range(float(walktreetoplevel(node[2])), float(walktreetoplevel(node[3]))))
        else: assert False, f"Variable {node[1]} already exists"
    
    elif node[0] == "create_global_var_str":
      
      if node[1] not in env["globalvars"]: env['globalvars'][node[1]] = node[2]
      else: assert False, f"Variable {node[1]} already exists"

    elif node[0] == 'add':
            return walktreetoplevel(node[1],) + walktreetoplevel(node[2])
    elif node[0] == 'sub':
           return walktreetoplevel(node[1]) - walktreetoplevel(node[2])
    elif node[0] == 'mul':
            return walktreetoplevel(node[1]) * walktreetoplevel(node[2])
    elif node[0] == 'div':
            return walktreetoplevel(node[1]) / walktreetoplevel(node[2] )

    elif node[0] == 'num':
            return node[1]
    

     ##CODITIONS
    elif node[0] == "con_true":
        return True
    elif node[0] == "con_false":
        return False
    elif node[0] == "con_eqeq":
        return  walktreetoplevel(node[1] ) ==  walktreetoplevel(node[2] )

    elif node[0] == "con_sthan":
        
        return  walktreetoplevel(node[1] ) <  walktreetoplevel(node[2] )

    elif node[0] == "con_gthan":
        return  walktreetoplevel(node[1] ) >  walktreetoplevel(node[2] )
    
    elif node[0] == "str_eq_str":
        return node[1] == node[2]



    elif node[0] == "ind_eq_str":
        return  walktreetoplevel(node[1] ) == node[2]

    elif node[0] == "ind_noteq_str":
        return  walktreetoplevel(node[1] ) != node[2]

    elif node[0] == "str_eq_expr":
        return  walktreetoplevel(node[1] ) == node[2]

    
    elif node[0] == "str_noteq_expr":
        return  walktreetoplevel(node[1] ) != node[2]


    elif node[0] == "str_noteq_str":
        return node[1] != node[2]

    elif node[0] == 'float':
        return node[1]

    elif node[0] == "import_file":
        with open(node[1], 'r') as f: file = [line.strip() for line in f]
        filetokens = ()
        for line in file:
    
            if len(line) != 0 and line.startswith('//') == False:
                x  = line.strip()
    
                if len(x) != 0 : y  =testparser.parse(testlexer.tokenize(x))
        
                if len(y) != 0 :
                    filetokens += (y, )
                else: pass
        transfertofunctions(filetokens)
    else: assert False , "Only global variables and imports are allowed at the top level of the program"





#Generate the top level    
for line in toplevel:
        walktreetoplevel(line)    

#Walk tree founctions that will visint evry node given, and produce the output

 

def walktree(node, funcname):
    if node[0] == "pass":
        pass

    
    elif node[0] == "exit_prog_no_expr":
        exit()
    elif node[0] == "exit_prog":
        exit(walktree(node[1], funcname))
    elif node[0] == "print_expr":
        print(walktree(node[1], funcname))
    elif node[0] == "con_noteq":
        return walktree(node[1], funcname) != walktree(node[2], funcname)
    elif node[0] == "while_loop":
        while walktree(node[1], funcname) == True:
            walktree(node[2], funcname)
    elif node[0] == "if_st":
        
        if walktree(node[1], funcname) == True:
            walktree(node[2], funcname)

        else: walktree(node[3], funcname)

    ##CODITIONS
    elif node[0] == "bool_eqeq_con":
        return env[f'{funcname}vars'][node[1]] == walktree(node[2], funcname)

    elif node[0] == "con_true":
        return True
    elif node[0] == "con_false":
        return False
    elif node[0] == "con_eqeq":
        return walktree(node[1], funcname) == walktree(node[2], funcname)

    elif node[0] == "con_sthan":
        
        return walktree(node[1], funcname) < walktree(node[2], funcname)

    elif node[0] == "con_gthan":
        return walktree(node[1], funcname) > walktree(node[2], funcname)
    
    elif node[0] == "str_eq_str":
        return node[1] == node[2]
    elif node[0] == "con_eqeq_con":
        
        return walktree(node[1], funcname) == walktree(node[2], funcname)
    elif node[0] == "con_eqeq_bool":
        return env[f'{funcname}vars'][node[1]] == walktree(node[2], funcname)
    
    elif node[0] == "bool_noteq_con":
        return env[f'{funcname}vars'][node[1]] != walktree(node[2], funcname)

    elif node[0] == "con_noteq_bool":
        return env[f'{funcname}vars'][node[1]] != walktree(node[2], funcname)

    elif node[0] == "ind_eq_str":
        return walktree(node[1], funcname) == node[2]

    elif node[0] == "ind_noteq_str":
        return walktree(node[1], funcname) != node[2]

    elif node[0] == "str_eq_expr":
        return walktree(node[1], funcname) == node[2]

    
    elif node[0] == "str_noteq_expr":
        return walktree(node[1], funcname) != node[2]


    elif node[0] == "str_noteq_str":
        return node[1] != node[2]

    elif node[0] == "call_sub":
        for sub in env[f"{funcname}subs"][node[1]]:
            for line in sub:
                walktree(line , funcname)

    elif node[0] == "create_var_float":
        
        if node[1] not in env[f"{funcname}vars"]: env[f'{funcname}vars'][node[1]] = float(walktree(node[2], funcname))
        else: assert False, f"Variable {node[1]} already exists"
    elif node[0] == "create_var_int":
      if node[1] not in env[f"{funcname}vars"]: env[f'{funcname}vars'][node[1]] = int(walktree(node[2], funcname) )
      else: assert False, f"Variable {node[1]} already exists"



    elif node[0] == "create_var_float_input":
        
        if node[1] not in env[f"{funcname}vars"]: env[f'{funcname}vars'][node[1]] = float(input(node[2]))
        else: assert False, f"Variable {node[1]} already exists"



    elif node[0] == "create_var_int_input":
      if node[1] not in env[f"{funcname}vars"]: env[f'{funcname}vars'][node[1]] = int(input(node[2]))
      else: assert False, f"Variable {node[1]} already exists"


    elif node[0] == "create_var_str":
      
      if node[1] not in env[f"{funcname}vars"]: env[f'{funcname}vars'][node[1]] = node[2]
      else: assert False, f"Variable {node[1]} already exists"
       

    elif node[0] == "create_var_str_input":
      
      if node[1] not in env[f"{funcname}vars"]: env[f'{funcname}vars'][node[1]] = str(input(node[2]))
      else: assert False, f"Variable {node[1]} already exists"

    elif node[0] == "create_var_bool":
        
        if node[1] not in env[f"{funcname}vars"]: env[f'{funcname}vars'][node[1]] = walktree(node[2], funcname)
        else: assert False, f"Variable {node[1]} already exists"
    elif node[0] == "change_var_value_bool":
        
        env[f'{funcname}vars'][node[1]] = walktree(node[2], funcname)  

    elif node [0] == "print_var":
       
       
        try : print(env[f"{funcname}vars"][node[1]])
        except KeyError: assert False, f"No variable named {node[1]}"
    elif node[0] == 'print':
        print(node[1])

    elif node [0] == "print_global_var":
       
       
        try : print(env[f"globalvars"][node[1]])
        except KeyError: assert False, f"No global variable named {node[1]}"
    elif node[0] == 'call_function':
        func = node[1]
        for line in env[func]:
            walktree(line, func)
   
    elif node[0] == 'add':
            return walktree(node[1], funcname) + walktree(node[2], funcname)
    elif node[0] == 'sub':
           return walktree(node[1], funcname) - walktree(node[2], funcname)
    elif node[0] == 'mul':
            return walktree(node[1], funcname) * walktree(node[2], funcname)
    elif node[0] == 'div':
            return walktree(node[1], funcname) / walktree(node[2] , funcname)

    elif node[0] == 'num':
            return node[1]

    elif node[0] == 'float':
        return node[1]

    elif node[0] == "IDENTIFIER":
        
        return env[f"{funcname}vars"][node[1]]

    elif node[0] == "change_var_value":
        
        if type(env[f"{funcname}vars"][node[1]]) == int:
            
            env[f'{funcname}vars'][node[1]] = int(walktree(node[2], funcname))

        elif type(env[f"{funcname}vars"][node[1]]) == float:
            
            env[f'{funcname}vars'][node[1]] = float(walktree(node[2], funcname))
        else : assert False, "Invalid type change"



    elif node[0] == "change_var_value_input":
        
        if type(env[f"{funcname}vars"][node[1]]) == int:
            
            env[f'{funcname}vars'][node[1]] = int(input(node[2]))

        elif type(env[f"{funcname}vars"][node[1]]) == float:
            
            env[f'{funcname}vars'][node[1]] = float(input(node[2]))


        elif type(env[f"{funcname}vars"][node[1]]) == str:
            
            env[f'{funcname}vars'][node[1]] = str(input(node[2]))
        else : assert False, "Invalid type change"
    
    elif node[0] == "change_var_value_str":

        if type(env[f"{funcname}vars"][node[1]]) == str:
            
            env[f'{funcname}vars'][node[1]] = str(node[2])
        else : assert False, "Invalid type change"

    elif node[0] == "create_var_int-random":
        
        if node[1] not in env[f"{funcname}vars"]: env[f'{funcname}vars'][node[1]] = randomint.randint(walktree(node[2], funcname), walktree(node[3], funcname))
        else: assert False, f"Variable {node[1]} already exists"


    

    elif node[0] == "create_global_var_float":
        
        
        assert False, f"cannot create global variable inside a function"
    

    elif node[0] == 'create_global_var_int':
        assert False, f"cannot create global variable inside a function"

    elif node[0] == "create_var_int-random-global":
        
       assert False, f"cannot create global variable inside a function"


    elif node[0] == "create_var_float-random-global":
        assert False, f"cannot create global variable inside a function"
    
    elif node[0] == "create_global_var_str":
      assert False, f"cannot create global variable inside a function"

    

    elif node[0] == "create_var_float-random":
        
        if node[1] not in env[f"{funcname}vars"]: env[f'{funcname}vars'][node[1]] = float(randomfloat.gen_random_range(float(walktree(node[2], funcname)), float(walktree(node[3], funcname))))
        else: assert False, f"Variable {node[1]} already exists"
        
#Produce the output of the main function
def call_func(func, error):
    try:
        for line in env[func]:
            walktree(line, func)

    except KeyError:
        assert False, error


#Call main
call_func("main", "No entry point main")




