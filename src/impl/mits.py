
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






for line in prog.splitlines():
   
    if len(line) != 0 and  line.startswith("//") == False and line.isspace() == False:
        y = p.parse(l.tokenize(line))
        parsed_tokens += (y,)
    else : pass


def crossreference_functions(obj) :
    tokens = obj
    stack = []
    for index , token in enumerate(tokens) :
        if token[0] == "op_declare_function":
            stack.append((index , token[0], token[1]))

        elif token[0] == "op_close" :
            pos = stack.pop()
            tokens = list(tokens)
            tokens[pos[0]] = (pos[1], pos[2], index)
            tokens = tuple(tokens)

    return tokens

parsed_tokens_and_function = crossreference_functions(parsed_tokens)


def transfer_to_functions(obj):
    for pos , op in enumerate(obj) :
       
        if op[0] == "op_declare_function":
            index = pos + 1
            body = ()

            while index < op[2] :
                body += (obj[index],)
                index += 1
            env[f"{op[1]}"] = body
            env[f"{op[1]}vars"] = {}
            env[f"{op[1]}params"] = []
            env[f"{op[1]}returnvalue"] =  []

transfer_to_functions(parsed_tokens_and_function)

def define_top_level(obj, obj1) :
    body = ()
    for pos , op in enumerate(obj) :
       
        if op[0] == "op_declare_function":
            index = pos + 1
           
            body += (obj1[pos],)

            while index < op[2] :
                body += (obj1[index],)
                index += 1
            body += (obj1[op[2]],)

    return body


toplevel = tuple(set(define_top_level(parsed_tokens_and_function, parsed_tokens)) ^ set(parsed_tokens))


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

        importtokens = crossreference_functions(importtokens)
        transfer_to_functions(importtokens)

        
        

    else : raise InstructionErr(f"InstructionErr : Invald instruction {node[1]}")



for line in toplevel:
     walktreetoplevel(line)


        

def crossreference_blocks(obj):
    block = obj
    stack = []
    ifindex = []
    elseindex  = []

    for index , node in enumerate(block) :
        if node[0] == "op_if_start":
            ifindex.append(index)
            stack.append((node[0], node[1] , index))
        elif node[0] == "op_start_while" :
            
            stack.append((node[0], node[1] , index))

        elif node[0] == "for_start" :
            stack.append((node[0], node[1] , index))
        elif node[0] == "op_close_end":
            pos = stack.pop()
            block = list(block)
            
            if block[pos[2]][0] == "op_if_start" or block[pos[2]][0] == "op_start_while"  or block[pos[2]][0] == "for_start" or block[pos[2]][0] == "else":
                
                if block[pos[2]][0] == "else":
                    elseind = elseindex.pop()
                    ifidn = ifindex.pop()
                    p = block[ifidn]
                    block[ifidn] = (p[0], p[1], p[2], elseind, index)
                    block = tuple(block)
                else :
                    block[pos[2]] = (pos[0], pos[1], index)
                    block = tuple(block)
            else :
                assert False , "missmatching `}`"
        elif node[0] == "else":
            stack.append(("else", "elem1", index))
            elseindex.append(index)


    return block

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
        
                walktree(crossreference_blocks(env[f"{funcname}macros"][node[1]][0]) , funcname)
                    
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
              
                if res == False :
                        pos = node[2]
                
                pos += 1

            else : 
            #   print(node)
                if res == False :
                        pos = node[3] + 1
                        body = ()
                        while pos < node[4] :
                            body += (obj[pos],) 
                            pos += 1
                        
                        body = crossreference_blocks(body)
                        walktree(body, funcname)
                else :
                    pos += 1
                    body = ()
                    while pos < node[2]:
                        body += (obj[pos],)
                        pos += 1
                    if pos == node[2] :
                        pos = node[4] + 1
                    body = crossreference_blocks(body)
                    walktree(body, funcname)
                pos += 1
                    

        elif node[0] == "else":
            pos += 1
        elif node[0] == "op_close_end" : pos += 1
        elif node[0] == "param":
            v = env[f"{funcname}params"][walktree((node[1],), funcname)]
            pos += 1
            return v

    
        elif node[0] == "for_start":
            
            val = walktree((node[1][1],), funcname)
            varname = node[1][0]
           

            index = pos
            body = ()
            index += 1
            while index < node[2]:
                    body += (obj[index],)
                    index += 1
           
            body = crossreference_blocks(body)
           
            for v in val :
                env[f"{funcname}vars"][varname] = v
                walktree(body, funcname)
            if index == node[2]:
                    pos = node[2] + 1

            # pos += 1

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
         
            
            if walktree((node[1],), funcname) == False:
                pos = node[2] + 1
                
            else :
                index = pos
                body = ()
                index += 1
                while index < node[2]:
                    body += (obj[index],)
                    index += 1
               
                body = crossreference_blocks(body)
                
                while walktree((node[1],) , funcname)  : walktree(body, funcname)
                
                # if index == node[2]:
                #     pos = node[2] 

            # pos += 1

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
                env[node[1]] = crossreference_blocks(env[node[1]])
                walktree(env[node[1]], node[1])
            try:
                
                val_to_return = env[f"{node[1]}returnvalue"][0]
            except : val_to_return = None
            env[f"{node[1]}params"] = []
            env[f"{node[1]}returnvalue"] = [] 
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

    


env["main"]= crossreference_blocks(env["main"])


walktree(env["main"], "main")
