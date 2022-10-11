from errors import *
from lexer import Lex
from parser import Pars
import sys


l = Lex()
p = Pars()
from typeconv import *
parsed_tokens = ()

prog = open(sys.argv[1], "r").read()
env = {"macros" : {}, "globalvars": {}}
gen = ()

sys.setrecursionlimit(2000)

def transfertofunctions(x):
    global gen
    for index, currentnode in enumerate(x):
        
        if currentnode[0] == 'op_declare_function':
            gen += (currentnode, )
            pos  = 0
            func = ()
            funcname = currentnode[1]

            #Get the nextelement of the loop
            nextelem = x[(index + pos) % len(x)]
            
            

            while nextelem[0] != "op_close":
                pos += 1
                nextelem = x[(index + pos) % len(x)]
                gen += (nextelem,)


                        
                        
                if nextelem[0] != "op_close": func += (nextelem, )
                if nextelem[0] ==  "op_close":
                  if funcname not in env:
                    env[funcname] = func
                    env[f"{funcname}vars"] = {}
                    env[f"{funcname}macros"] = {}
                    env[f"{funcname}params"] = []
                    env[f"{funcname}returnvalue"] = []
                  else : raise NameErr(f"NameErr : Function `{funcname}` alredy exists")

        if currentnode[0] == 'op_declare_global_macro':
                gen += (currentnode, )
                pos  = 0
                subpr = ()
                

            #Get the nextelement of the loop
                nextelem = x[(index + pos) % len(x)]
            
            

                while nextelem[0] != "op_close":
                    pos += 1
                    nextelem = x[(index + pos) % len(x)]
                    gen += (nextelem,)


                        
                        
                    if nextelem[0] != "op_close": subpr += (nextelem, )
                if nextelem[0] ==  "op_close":
                    if currentnode[1] not in env["macros"]:
                        env["macros"][currentnode[1]] = (subpr,)           
                    else : raise NameErr(f"NameErr : Global macro `{currentnode[1]}` alredy exists") 


        if currentnode[0] == 'op_declare_local_macro':
                gen += (currentnode, )
                pos  = 0
                subpr = ()
                funcname = currentnode[2]

            #Get the nextelement of the loop
                nextelem = x[(index + pos) % len(x)]
            
            

                while nextelem[0] != "op_close":
                    pos += 1
                    nextelem = x[(index + pos) % len(x)]
                    gen += (nextelem,)


                        
                        
                    if nextelem[0] != "op_close": subpr += (nextelem, )
                if nextelem[0] ==  "op_close":
                    if currentnode[1] not in env[f"{funcname}macros"]:
                        env[f"{funcname}macros"][currentnode[1]] = (subpr,)           
                    else : raise NameErr(f"NameErr : Function {funcname} alredy have macro `{currentnode[1]}` alredy exists")



for line in prog.splitlines():
   
    if len(line) != 0 and  line.startswith("//") == False and line.isspace() == False:
        y = p.parse(l.tokenize(line))
        parsed_tokens += (y,)
    else : pass



# print(parsed_tokens)
transfertofunctions(parsed_tokens)


toplevel = tuple(set(gen) ^ set(parsed_tokens))

def walktreetoplevel(node):
    if node[0] == "expr_string":
        res = [i for j in node[1].split() for i in (j, ' ')][:-1]
       
        str = ""
        
        for i in res:
            if i == "\\n":
                i = i.replace("\\n", "\n")
                str += i
            elif i == "\\t":
                i = i.replace("\\t", "\t")
                str += i
            elif i == "\\r":
                i = i.replace("\\r", "\r")
                str += i
            
            elif i.startswith("{") and i.endswith("}"):
                
                x = i[1:-1]
                v = p.parse(l.tokenize(x))
                str += walktreetoplevel(v)
            else :  str += i

        return str
    elif node[0] == "expr_int":
        return int(node[1])
    elif node[0] == "expr_add":
        return walktreetoplevel(node[1]) + walktreetoplevel(node[2])
    elif node[0] == "expr_sub":
         return walktreetoplevel(node[1]) - walktreetoplevel(node[2])
    elif node[0] == "expr_mul":
         return walktreetoplevel(node[1]) * walktreetoplevel(node[2])
    elif node[0] == "expr_mul":
         return walktreetoplevel(node[1])  / walktreetoplevel(node[2])
    elif node[0] == "expr_neg_num":
        return -walktreetoplevel(node[1])
    

    elif node[0] == "global_var_assign":
       
        env["globalvars"][node[1]] = walktreetoplevel(node[2])
        
    
    elif node[0] == "expr_float":
        return node[1]

    elif node[0] == "con_eq_eq":
         return walktreetoplevel(node[1]) == walktreetoplevel(node[2])
    elif node[0] == "con_not_eq":
        return walktreetoplevel(node[1]) != walktreetoplevel(node[2])
    elif node[0] == "con_g_than":
        return walktreetoplevel(node[1]) > walktreetoplevel(node[2])
    elif node[0] == "con_eq_or_g_than":
        return walktreetoplevel(node[1]) >= walktreetoplevel(node[2])
    elif node[0] == "con_s_than":
        return walktreetoplevel(node[1]) < walktreetoplevel(node[2])
    elif node[0] == "global_identifier":
        if node[1] in env[f"globalvars"]:
            return env[f"globalvars"][node[1]]
        else : raise NameErr(f"NameErr: Global variable `{node[1]}` does not exist")
    elif node[0] == "con_eq_or_s_than":
        return walktreetoplevel(node[1]) <= walktreetoplevel(node[2])
    elif node[0] == "include":
        with open(node[1], "r") as f:
            x = f.read()
        importtokens = ()
        for line in x.splitlines():
            if len(line) != 0 and  line.startswith("//") == False and line.isspace() == False:
                y = p.parse(l.tokenize(line))
                importtokens += (y,)
            else : pass

        transfertofunctions(importtokens)
        

    else : raise InstructionErr(f"InstructionErr : Invald instruction {node[1]}")




for line in toplevel:
     
        walktreetoplevel(line)



def crossreference(obj1) :
    stack = []
    ifindex = []
    obj = obj1
    index = 0
    for line in obj :
        for op in (line,) :
            if op[0] == "op_if_start":
                ifindex.append(index)
                stack.append(("op_if_start", index, op[1]),)

            elif op[0] == "op_close_end":
                
                    x = stack.pop()
                    if x[0] != "else":
                        obj = list(obj)
                        obj[x[1]] = (x[0], x[2], index)
                        obj = tuple(obj)
                    else :
                        y = ifindex.pop()
                        obj = list(obj)
        
                        obj[y] = (obj[y][0], obj[y][1], obj[y][2] , x[1], index)
                      
                        obj = tuple(obj)
            elif op[0] == "else":
                stack.append(("else", index,  (True,)))
                

            elif op[0] == "for_start":
                stack.append(("for_start", index, op[1]),)
            elif op[0] == "op_start_while":
                stack.append(("op_start_while", index, op[1]),)
              
            

            index += 1
    return obj
        


def walktree(obj, funcname):
    
    pos = 0
    while pos < len(obj):
        node = obj[pos]
        if node[0] == "op_write":
            x = walktree((node[1],), funcname)
            print(x)
            pos += 1
        elif node[0] == "expr_string":
            res = [i for j in node[1].split() for i in (j, ' ')][:-1]
       
            str = ""
        
            for i in res:
                if i == "\\n":
                    i = i.replace("\\n", "\n")
                    str += i
                elif i == "\\t":
                    i = i.replace("\\t", "\t")
                    str += i
                elif i == "\\r":
                    i = i.replace("\\r", "\r")
                    str += i

                elif i == "\\s":
                    i = i.replace("\\s", " ")
                    str += i

                elif i.startswith("{") and i.endswith("}"):
                
                    x = i[1:-1]
                    v = p.parse(l.tokenize(x))
                    str += walktree((v,), funcname)
                else :  str += i
            pos += 1
            return str
                

        elif node[0] == "expr_int":
            pos += 1
            return int(node[1])
            
        elif node[0] == "expr_add":
            pos += 1
            return walktree((node[1],), funcname) + walktree((node[2],), funcname)

        elif node[0] == "expr_prec":
            pos += 1
            return walktree((node[1],), funcname) % walktree((node[2],), funcname)

        elif node[0] == "expr_prec":
            pos += 1
            return walktree((node[1],), funcname) ^ walktree((node[2],), funcname)
           
        elif node[0] == "expr_sub":
            pos += 1
            return walktree((node[1],), funcname) - walktree((node[2],), funcname)
            
        elif node[0] == "expr_mul":
            pos += 1
            return walktree((node[1],), funcname) * walktree((node[2],), funcname)
        elif node[0] == "expr_mul":
            pos += 1
            return walktree((node[1],), funcname)  / walktree((node[2],), funcname)
        elif node[0] == "expr_neg_num":
            pos += 1
            return -walktree((node[1],), funcname)

        elif node[0] == "argv":
            pos += 1
            return sys.argv[1:]

        elif node[0] == "argc":
            pos += 1
            return len(sys.argv) - 1

        elif node[0] == "expr_pos":
            
            modf = walktree((("expr_array", node[2]),), funcname)
        # print(modf)
            pos += 1
            if len(modf) == 1 :
                return walktree((node[1],), funcname)[modf[0]]
            else : raise IndexErr(f"IndexErr : invalid index `{modf}`")
            
        elif node[0] == "expr_array":
            x = node[1].strip('][').split(', ')
            arr = []
        
            for elem in x:
                if elem.isspace() == False and elem != '':
                    arr.append(walktree((p.parse(l.tokenize(elem)),), funcname))
            pos += 1
            return arr

        elif node[0] == "var_assign":

            env[f"{funcname}vars"][node[1]] = walktree((node[2],), funcname)
            pos += 1
        elif node[0] == "expr_float":
            pos += 1
            return node[1]

        elif node[0] == "callmacro":
            if node[1] in env[f"{funcname}macros"]:
        
                walktree(crossreference(env[f"{funcname}macros"][node[1]][0]) , funcname)
                    
            else : raise NameErr(f"NameErr : function `{funcname}` does not have a macro named `{node[1]}`")
            pos += 1

        elif node[0] == "callmacro_global":
            if node[1] in env["macros"]:
                for mac in env["macros"][node[1]]:
                    for op in mac:
                
                        walktree(op, funcname)
                
                        env[f"{funcname}returnvalue"] = [walktree(op[1], funcname)]
                    

            else : raise NameErr(f"NameErr : No global macro named {node[1]}")
            pos += 1
        elif node[0] == "op_if_start":
           
            res = walktree((node[1],), funcname)
           
            if len(node) != 5:
            # try :
               
            
              
            #    
                
                
            # except: 
              
                if res == False :
                        pos = node[2]
                
                pos += 1

            else : 
              
                if res == False :
                    pos = node[3]
                else : 
                   
                    x = ()
                    pos += 1
                   
                    while pos != node[3] and pos < len(obj):
                        
                        x += (obj[pos],)
                        
                       
                        pos += 1
  
                    
                    print(x)
                    # y = ()
                    # # y += (p.parse(l.tokenize("else {")),)
                    # # y += (p.parse(l.tokenize(" } ")),)
                    # x += y
                    x = crossreference(x)
                    walktree(x, funcname)
                  
                    
                  
                    if pos == node[3] :
                        
                        pos = node[4]
                    

        elif node[0] == "else":
            pos += 1
        elif node[0] == "op_close_end" : pos += 1
        elif node[0] == "param":
            v = env[f"{funcname}params"][walktree((node[1],), funcname)]
            pos += 1
            return v

    
        elif node[0] == "for_start":
        
            VarToLoop = walktree((node[1][1],), funcname)
            NewVarName = node[1][0]
        
            
            test = ()
            pos += 1
            while pos != node[2] :
                    
                    
                  
                    test += (obj[pos],)
                    pos += 1
            
            test = crossreference(test)
       
            for i in VarToLoop :
                env[f"{funcname}vars"][NewVarName] = i
                walktree(test, funcname)

            pos += 1

        elif node[0] == "con_eq_eq":
            
             pos += 1
             return walktree((node[1],), funcname) == walktree((node[2],), funcname)
        elif node[0] == "con_not_eq":
            pos += 1
            return walktree((node[1],), funcname) != walktree((node[2],), funcname)
        elif node[0] == "con_g_than":
            pos += 1
            return walktree((node[1],), funcname) > walktree((node[2],), funcname)
        elif node[0] == "con_eq_or_g_than":
            pos += 1
            return walktree((node[1],), funcname) >= walktree((node[2],), funcname)
        elif node[0] == "con_s_than":
            pos += 1
            return walktree((node[1],), funcname) < walktree((node[2],), funcname)

        elif node[0] == "con_eq_or_s_than":
            pos += 1
            return walktree((node[1],), funcname) <= walktree((node[2],), funcname)
        elif node[0] == "op_start_while":
            # wip = pos
            
            if walktree((node[1],), funcname) == False:
                pos = node[2]
            else : 
                pos += 1
                test = ()
                while pos != node[2] :
                    
                    
                  
                    test += (obj[pos],)
                    pos += 1
                 
                
                test = crossreference(test)
                while walktree((node[1],), funcname) == True:
                    walktree(test, funcname)
                    # pos += 1
                  
                   
                    
                    

                   
            pos += 1

        elif node[0] == "plusplus" :
           
            
            env[f"{funcname}vars"][node[1]] += 1
            pos += 1

        elif node[0] == "identifier":
        
            var = node[1]
            pos += 1
            if var in env[f"{funcname}vars"] :
                return env[f"{funcname}vars"][var]
            else : raise NameErr(f"NameErr : No variable named `{node[1]}`")

        elif node[0] == "function_call":
            if node[1] in env:
                env[node[1]] = crossreference(env[node[1]])
                walktree(env[node[1]], node[1])
            try:
                val_to_return = env[f"{node[1]}returnvalue"][0]
            except : val_to_return = None
            env[f"{node[1]}params"] = []
            env[f"{node[1]}returnvalue"] = [] # 
            pos += 1
            return  val_to_return

           
           
        elif node[0] == "return":
            env[f"{funcname}returnvalue"] = [walktree((node[1],), funcname)]
            pos += 1
            return
       
        elif node[0] == "add_new_to_arr":
            if type(env[f"{funcname}vars"][node[1]]) == list:
               
                modf = walktree((("expr_array", node[2]),), funcname)
                if len(modf) == 1:
                    if len(env[f"{funcname}vars"][node[1]]) - 1 == modf[0]:
                        env[f"{funcname}vars"][node[1]][modf[0]] = walktree((node[3],), funcname)
                    elif len(env[f"{funcname}vars"][node[1]]) == modf[0] : env[f"{funcname}vars"][node[1]].append(walktree((node[3],), funcname))
                else : raise IndexErr(f"IndexErr : invalid index `{modf}`")
            else : raise IndexErr(f"IndexErr : invalid index `{modf}`")
            pos += 1
        elif node[0] == "op_close" : pos += 1
        elif node[0] == "try_except":
            try : walktree((node[1],), funcname)
            except : walktree((node[2],), funcname)
            pos += 1
       
        elif node[0] == "true" or node[0] == "false":
            if node[0] == "true" :
                pos += 1
                return True
            else :
                pos += 1
                return False
            
        elif node[0] == "pass_param":
            if node[2] in env :
                env[f"{node[2]}params"].append(walktree((node[1],), funcname))
            else : raise NameErr(f"NameErr : No function named `{node[2]}`")
            pos += 1
        elif node[0] == "global_identifier":
            if node[1] in env["globalvars"]:
                pos += 1
                return env["globalvars"][node[1]]
            else : raise NameErr(f"NameErr: Global variable `{node[1]}` does not exist")

        elif node[0] == "typeof":
            pos += 1
            return typeconv(type(walktree((node[1],), funcname)))

        elif node[0] == "global_var_assign":
            pos += 1
            raise TopLevelErr(f"TopLevelError : cannot create global variable `{node[1]}` inside a function")
        else : raise InstructionErr(f"InstructionErr : Invald instruction {node}")

    


env["main"]= crossreference(env["main"])


walktree(env["main"], "main")
