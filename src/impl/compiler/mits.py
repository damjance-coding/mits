from tokenize import String
from errors import *
from lexer import Lex
from parser import Pars
import sys


l = Lex() # Lexer
p = Pars() # Parser

from typeconv import *

parsed_tokens = ()

prog = open(sys.argv[1], "r").read()
env = {"errors" : {}, "globalvars": {}}
gen = ()

#All the assembly sections
section_bss = [
    "section .bss\n", 
    "  digitSpace resb 100\n", 
    "  digitSpacePos resb 8\n"
    ]

section_text = [
    "section .text\n", 
    "    global _start\n",  
    "_start:\n"
    ]

section_data = [
    "section .data\n"
    ]


def TestInt64orInt32(num):
    if num < 2147483648:
        return 32
    else :
        return 64

def LexAndParse():
    global parsed_tokens
    for line in prog.splitlines():
   
        if len(line) != 0 and  line.startswith("//") == False and line.isspace() == False:
            y = p.parse(l.tokenize(line))
            parsed_tokens += (y,)
        else : pass

LexAndParse()

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


# toplevel = tuple(set(define_top_level(parsed_tokens_and_function, parsed_tokens)) ^ set(parsed_tokens))


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

    elif node[0] == 'define_error':
        if node[1] not in env["errors"]:
            env["errors"][node[1]] = ""
        else : assert False , "Redeclaring errors is not allowed"

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



# for line in toplevel:
#      walktreetoplevel(line)


        

def crossreference_blocks(obj):
    block = obj
    stack = []

    ifindex = []
    elseindex  = []
    tryindex = []
    exceptindex = []

    for index , node in enumerate(block) :
        if node[0] == IF_STM:
            ifindex.append(index)
            stack.append((node[0], node[1] , index))
        elif node[0] == WHILE_ST :
            
            stack.append((node[0], node[1] , index))

        elif node[0] == ELSE_ST:
            elseindex.append(index)
            stack.append((ELSE_ST, "elem1", index))

        elif node[0] == "for_start" :
            stack.append((node[0], node[1] , index))
        elif node[0] == CLOSE_CB:
            pos = stack.pop()
            block = list(block)
            
            if block[pos[2]][0] == IF_STM or block[pos[2]][0] == WHILE_ST  or block[pos[2]][0] == "for_start" or block[pos[2]][0] == ELSE_ST or block[pos[2]][0] == "try_start" or block[pos[2]][0] == "except_start":
                
                if block[pos[2]][0] == ELSE_ST:
                    elseind = elseindex.pop()
                    ifidn = ifindex.pop()
                    p = block[ifidn]
                    block[ifidn] = (p[0], p[1], p[2], elseind, index)
                    block = tuple(block)

                if block[pos[2]][0] == "except_start":
                    elseind = exceptindex.pop()
                    try : ifidn = tryindex.pop()
                    except : raise Exception("Missmatching `except`")
                    p = block[ifidn]
                    block[ifidn] = (p[0], p[1], p[2], elseind, index)
                    block = tuple(block)
                else :
                    block = list(block)
                    block[pos[2]] = (pos[0], pos[1], index)
                    block = tuple(block)
            else :
                assert False , "missmatching `}`"
        elif node[0] == "try_start":
            stack.append(("try_start", "elem1", index))
            tryindex.append(index)

        elif node[0] == "except_start":
            stack.append(("except_start", "elem1", index))
            exceptindex.append(index)


    return block

string_literals = []

string_at_index = -1

Intigers = []
Strings  = []


IDENTIFIER = "identifier"

KEYWORD_WRITE    = "op_write"
EXPR_INT64_OR_INT32_IDENTIFIER = 3
EXPR_STRING_OR_IDENTIFIER = 4

EXPR_NUM_OR_OP   = 2

ELSE_ST = "else"
IF_STM = "op_if_start"
WHILE_ST = "op_start_while"


CLOSE_CB = "op_close_end"

PLUSPLUS = "plusplus"
MINUSMINUS = "minusminus"

CONDITION_EQ_EQ = "con_eq_eq"
CONDITION_GT    = "con_g_than"
CONDITION_ST    = "con_s_than"

VAR_ASSIGN_INT32  = "var_assign_int32"
VAR_ASSIGN_INT64  = "var_assign_int64"
VAR_ASSIGN_STR    =  "var_assign_str"

VAR_ASSIGN_UINT64 = "var_assign_uint64"
VAR_ASSIGN_UINT32 = "var_assign_uint32"
VAR_ASSIGN_USTR   = "var_assign_ustr"

CHANGE_VAR_VAL    = "var_assign_change_var_val"



OPERATION_DIV    = "expr_div"
OPERATION_ADD    = "expr_add"
OPERATION_SUB    = "expr_sub"
OPERATION_MUL    = "expr_mul"
OPERATION_STRING = "expr_string"
OPERATION_NUM    = "expr_int"
OPERATION_STRING = "expr_string"





def type_check_program(program):
    global Strings
    global Intigers
    for node in program:
        if node[0] == VAR_ASSIGN_INT32:
            if node[2][0] == OPERATION_STRING:
                raise TypeError(f"ERROR: Cannot assign value of type  `string` to variable `{node[1]}` of type `int32`")
            elif node[2][0] == IDENTIFIER:
                if node[2][1] in Intigers:
                    Intigers.append(node[2][1])
                elif node[2][1] in Strings:
                    raise TypeError(f"ERROR: Cannot assign value of variable `{node[2][1]}` of type  `string` to variable `{node[1]}` of type `int32`")
                else : raise TypeError(f"ERROR: Unknow variable {node[2][1]}")
            elif node[2][0] == OPERATION_NUM:
                if TestInt64orInt32(node[2][1]) == 64:
                    raise ValueError("ERROR: Value too high for type `int32`")
                else : Intigers.append(node[1])    
            else : Intigers.append(node[1])
        elif node[0] == VAR_ASSIGN_INT64:
            if node[2][0] == OPERATION_STRING:
                raise TypeError(f"ERROR: Cannot assign value of type  `string` to variable `{node[1]}` of type `int64`")
            elif node[2][0] == IDENTIFIER:
                if node[2][1] in Intigers:
                    Intigers.append(node[2][1])
                elif node[2][1] in Strings:
                    raise TypeError(f"ERROR: Cannot assign value of variable `{node[2][1]}` of type  `string` to variable `{node[1]}` of type `int64`")
                else : raise TypeError(f"ERROR: Unknow variable {node[2][1]}")

        elif node[0] == VAR_ASSIGN_UINT64:
            Intigers.append(node[1])
                
        elif node[0] == VAR_ASSIGN_UINT32:
            Intigers.append(node[1])
        elif node[0] == VAR_ASSIGN_USTR:
            Strings.append(node[1])         
        elif node[0]  == VAR_ASSIGN_STR:
          
          if len(node)  ==  3:
            if node[2][0] == OPERATION_ADD or node[2][0] == OPERATION_DIV or node[2][0] == OPERATION_MUL or node[2][0] == OPERATION_SUB or node[2][0] == OPERATION_NUM:
                raise TypeError(f"ERROR: Cannot assign value of type int/float to variable `{node[1]}` of type `string`")
            elif node[2][0] == IDENTIFIER:
                if node[2][1] in Strings:
                    Strings.append(node[1])
                elif node[2][1] in Intigers:
                    raise TypeError(f"ERROR: Cannot assign value of variable `{node[2][1]}` of type  `int` to variable `{node[1]}` of type `str`")
                else : raise TypeError(f"ERROR: Unknow variable {node[2][1]}")
            else : Strings.append(node[1])
          else : 
            if node[3][0] == OPERATION_ADD or node[3][0] == OPERATION_DIV or node[3][0] == OPERATION_MUL or node[3][0] == OPERATION_SUB or node[3][0] == OPERATION_NUM:
                raise TypeError(f"ERROR: Cannot assign value of type int/float to variable `{node[1]}` of type `string`")
            elif node[2][0] == IDENTIFIER:
                if node[2][1] in Strings:
                    Strings.append(node[1])
                elif node[2][1] in Intigers:
                    raise TypeError(f"ERROR: Cannot assign value of variable `{node[2][1]}` of type  `int` to variable `{node[1]}` of type `str`")
                else : raise TypeError(f"ERROR: Unknow variable {node[2][1]}")
            else : Strings.append(node[1])
        elif node[0] == CHANGE_VAR_VAL:
            if node[1] in Intigers:
                if node[2][0] == OPERATION_STRING:
                    raise TypeError(f"ERROR: Cannot assign value of type  `string` to variable `{node[1]}` of type `int64`")
                elif node[2][0] == IDENTIFIER:
                    if node[2][1] in Intigers:
                        pass
                    elif node[2][1] in Strings:
                        raise TypeError(f"ERROR: Cannot assign value of variable `{node[2][1]}` of type  `string` to variable `{node[1]}` of type `int64`")
                    else : raise TypeError(f"ERROR: Unknow variable {node[2][1]}")
            elif node[1] in Strings :
                if node[2][0] == OPERATION_ADD or node[2][0] == OPERATION_DIV or node[2][0] == OPERATION_MUL or node[2][0] == OPERATION_SUB or node[2][0] == OPERATION_NUM:
                    raise TypeError(f"ERROR: Cannot assign value of type  int/float to variable `{node[1]}` of type `string`")
                elif node[2][0] == IDENTIFIER:
                    if node[2][1] in Strings:
                       pass
                    elif node[2][1] in Intigers:
                        raise TypeError(f"ERROR: Cannot assign value of variable `{node[2][1]}` of type  `int` to variable `{node[1]}` of type `str`")
                    else : raise TypeError(f"ERROR: Unknow variable {node[2][1]}")
            else :
                raise NameErr(f"ERROR: Unknow variable `{node[1]}`")

type_check_program(parsed_tokens_and_function)

loop_endloop_index = -1

while_loop_index = -1

string_bytes = {}

def walktree(obj, funcname):
    global string_at_index
    global Intigers
    global Strings
    global string_literals
    global loop_endloop_index
    global while_loop_index
    global string_bytes
    pos = 0
    
    
    while pos < len(obj):
        node = obj[pos]
        if node[0] == KEYWORD_WRITE:
          
          op_id = walktree((node[1],), funcname)
 
         
          
          if op_id[0] == EXPR_NUM_OR_OP or op_id[0] == EXPR_INT64_OR_INT32_IDENTIFIER:   
            section_text.append("   pop rax\n")
            section_text.append("   call _printDigit\n")
            section_text.append("\n")
            pos += 1
          
          elif op_id[0] == EXPR_STRING_OR_IDENTIFIER:
            
            section_text.append("   mov rax, 1\n")
            section_text.append("   mov rdi, 1\n")
            section_text.append("   pop rsi,\n")
            section_text.append("   pop rdx\n")
            section_text.append("   syscall\n")
            pos += 1
           
        
        elif node[0] == OPERATION_NUM:
            if TestInt64orInt32(node[1]) == 32:
                section_text.append(f"   push {node[1]}\n")
                section_text.append("\n")
                pos += 1
                return (EXPR_NUM_OR_OP,)
            elif  TestInt64orInt32(node[1]) == 64:
                section_text.append(f"   mov rax,{node[1]}\n")
                section_text.append(f"   push rax\n")
                section_text.append("   xor rax,rax\n")
                section_text.append("\n")
                pos += 1
                return (EXPR_NUM_OR_OP,)
            else : 
                assert False, "Error inside of TestInt64orInt32() fucntion!"
        elif node[0] == OPERATION_ADD:
            walktree((node[1],), funcname)
            walktree((node[2],), funcname)
            section_text.append("   pop rax\n")
            section_text.append("   pop rbx\n")
            section_text.append("   add rax, rbx\n")
            section_text.append("   push rax\n")
            section_text.append("\n")
            pos += 1
            return (EXPR_NUM_OR_OP,)
        
        elif node[0] == OPERATION_SUB:
            walktree((node[1],), funcname)
            walktree((node[2],), funcname)
            section_text.append("   pop rbx\n")
            section_text.append("   pop rax\n")
            section_text.append("   sub rax, rbx\n")
            section_text.append("   push rax\n")
            section_text.append("\n")
            pos += 1
            return (EXPR_NUM_OR_OP,)

        
        elif node[0] == OPERATION_MUL:
            walktree((node[1],), funcname)
            walktree((node[2],), funcname)
            section_text.append("   pop rax\n")
            section_text.append("   pop rbx\n")
            section_text.append("   mul rbx\n")
            section_text.append("   push rax\n")
            section_text.append("\n")
            pos += 1
            return (EXPR_NUM_OR_OP,)

        
        elif node[0] == OPERATION_DIV:
            walktree((node[1],), funcname)
            walktree((node[2],), funcname)
            section_text.append("   pop rbx\n")
            section_text.append("   pop rax\n")
            section_text.append("   div rbx\n")
            section_text.append("   push rax\n")
            section_text.append("\n")
            pos += 1
            return (EXPR_NUM_OR_OP,)
        elif node[0] == VAR_ASSIGN_INT32:
            section_bss.append(f"   {node[1]} resb 4\n")
            walktree((node[2],), funcname)
            section_text.append("   pop rax\n")
            section_text.append(f"   mov [{node[1]}], rax\n")
            section_text.append("\n")
            
            pos += 1

        elif node[0] == VAR_ASSIGN_INT64:
            section_bss.append(f"   {node[1]} resb 8\n")
            walktree((node[2],), funcname)
            section_text.append("   pop rax\n")
            section_text.append(f"   mov [{node[1]}], rax\n")
            section_text.append("\n")
          
            pos += 1
             
        elif node[0] == VAR_ASSIGN_STR:
          if len(node) == 3:
                loop_endloop_index += 1
                section_bss.append(f"   {node[1]} resb {len(node[2][1]) + 1}\n")
                walktree((node[2],), funcname)
                section_text.append("   xor RBP, RBP\n")       
                section_text.append("   pop rdx\n")
                section_text.append("  \n")
                section_text.append(f'''
.loop_{loop_endloop_index}:
    mov al, byte [rdx + RBP] ; get the nth character of other.
    cmp al, 0x00 ; if we reached the end of the string
    je .endLoop_{loop_endloop_index} ; end the function
    mov [{node[1]} + RBP], al ; write the nth character of other to nth position of text
    inc RBP ; increase counter
    jmp .loop_{loop_endloop_index} ; loop

.endLoop_{loop_endloop_index}:
    ''') 
                
                string_bytes[node[1]] = len(node[2][1]) + 1
                pos += 1
          else: 
                
                assert node[2][0] == OPERATION_NUM, "Not implemented"
                loop_endloop_index += 1
                section_bss.append(f"   {node[1]} resb {node[2][1] + 1}\n")
                walktree((node[3],), funcname)
                section_text.append("   xor RBP, RBP\n")       
                section_text.append("   pop rdx\n")
                section_text.append("  \n")
                section_text.append(f'''
.loop_{loop_endloop_index}:
    mov al, byte [rdx + RBP] ; get the nth character of other.
    cmp al, 0x00 ; if we reached the end of the string
    je .endLoop_{loop_endloop_index} ; end the function
    mov [{node[1]} + RBP], al ; write the nth character of other to nth position of text
    inc RBP ; increase counter
    jmp .loop_{loop_endloop_index} ; loop

.endLoop_{loop_endloop_index}:
    ''') 
                
                string_bytes[node[1]] = node[2][1] + 1
                pos += 1
        elif node[0] == IDENTIFIER:
            if node[1] in Intigers:
                section_text.append(f"  mov rax, [{node[1]}]\n")
                section_text.append("  push rax\n")
                section_text.append("\n")
                pos += 1
                return (EXPR_INT64_OR_INT32_IDENTIFIER,)
            elif node[1] in Strings:
                section_text.append("   push %d\n" % string_bytes[node[1]])
                section_text.append("   push %s\n" % node[1])                
                return (EXPR_STRING_OR_IDENTIFIER,)
        
        elif node[0] ==  OPERATION_STRING:
            if node[1] not in string_literals:
                string_at_index += 1
                
                section_data.append(f'  string_literal_at_index_{string_at_index}: db %s, 10\n' % ",".join(map(hex, list(bytes(node[1], "utf-8")))))
                section_text.append(f"   push %d" % (len(node[1]) + 1) + "\n")
                section_text.append(f"   push string_literal_at_index_{string_at_index}\n")
                section_data.append("\n")
                pos += 1
                string_literals.append(node[1])
                return (EXPR_STRING_OR_IDENTIFIER, string_at_index)
            else :
                section_text.append("   push %d" % (len(node[1]) + 1) + "\n")
                section_text.append(f"   push string_literal_at_index_{string_literals.index(node[1])}\n")
                pos += 1
                return (EXPR_STRING_OR_IDENTIFIER, string_literals.index(node[1]))



        elif node[0] == CONDITION_EQ_EQ:
           
           
         if node[1][0] == OPERATION_STRING and node[2][0] == OPERATION_STRING or node[1][1] in Strings or node[2][1] in Strings:
          
           walktree((node[1],), funcname)
           walktree((node[2],), funcname)
           section_text.append("   mov RBP, 0\n")
           section_text.append("   mov rdx, 1\n")
           section_text.append("    pop rsi\n")
           section_text.append("    pop rcx\n")
           section_text.append("   pop rdi\n")
           section_text.append("   repe cmpsb\n")
           section_text.append("   cmove RBP, rdx\n")
           section_text.append("   push RBP\n")
           pos += 1


         else :
            walktree((node[1],), funcname)
            walktree((node[2],), funcname)
            section_text.append("   mov rcx, 0\n")
            section_text.append("   mov rdx, 1\n")
            section_text.append("   pop rax\n")
            section_text.append("   pop rbx\n")
            section_text.append("   cmp rax, rbx\n")
            section_text.append("   cmove rcx, rdx\n")
            section_text.append("   push rcx\n")
            section_text.append("   \n")
            pos += 1
         return

        elif node[0] == CONDITION_ST:
            walktree((node[1],), funcname)
            walktree((node[2],), funcname)
            section_text.append("   mov rcx, 0\n")
            section_text.append("   mov rdx, 1\n")
            section_text.append("   pop rax\n")
            section_text.append("   pop rbx\n")
            section_text.append("   cmp rax, rbx\n")
            section_text.append("   cmovs rdx, rcx\n")
            section_text.append("   push rdx\n")
            section_text.append("   \n")

            pos += 1
        elif node[0] == CONDITION_GT:
            walktree((node[1],), funcname)
            walktree((node[2],), funcname)
            section_text.append("   mov rcx, 0\n")
            section_text.append("   mov rdx, 1\n")
            section_text.append("   pop rax\n")
            section_text.append("   pop rbx\n")
            section_text.append("   cmp rax, rbx\n")
            section_text.append("   cmovg rdx, rcx\n")
            section_text.append("   push rdx\n")
            section_text.append("   \n")

            pos += 1
        elif node[0] == CLOSE_CB:
            if len(node) != 3:
                section_text.append(f"addr_{pos}: \n")
            else :
                assert node[2] == WHILE_ST
                section_text.append(f"    jmp while_loop_at_index_{while_loop_index}\n")
                section_text.append(f"addr_{pos}: \n")
            pos += 1
        elif node[0] == IF_STM:
            if len(node) != 5: 
              if node[1][0] == CONDITION_EQ_EQ or node[1][0] == CONDITION_GT or node[1][0] == CONDITION_ST:

                    walktree((node[1],), funcname)

                    section_text.append("   pop rax\n")
                    section_text.append("   test rax, rax\n")
                    section_text.append(f"   jz addr_{node[2]}\n")
                    section_text.append("   \n")

                    pos += 1
              else :
                    
                    assert False, "Not implemented"
            else :
                if node[1][0] == CONDITION_EQ_EQ or node[1][0] == CONDITION_GT or node[1][0] == CONDITION_ST:


                    walktree((node[1],), funcname)

                    section_text.append("   pop rax\n")
                    section_text.append("   test rax, rax\n")
                    section_text.append(f"   jz addr_{node[3]}\n")
                   
                    section_text.append("   \n")

                    pos += 1
                else :
                    assert False, "Not implemented"

        elif node[0] == ELSE_ST:
            section_text.append(f"jnz addr_{node[2]}\n")
            section_text.append(f"addr_{pos}: \n")
            pos += 1


        elif node[0] == CHANGE_VAR_VAL:
            if node[1] in Intigers:
                walktree((node[2],), funcname)
                section_text.append("   pop rax\n")
                section_text.append(f"   mov [{node[1]}], rax\n")
                section_text.append("   xor rax, rax\n")
                section_text.append("\n")
                pos += 1
            elif node[1] in Strings :
               
                loop_endloop_index += 1
                walktree((node[2],), funcname)
                section_text.append("   xor RBP, RBP\n")       
                
                section_text.append("   pop rdx\n")
                section_text.append(f'''
.loop_{loop_endloop_index}:
    mov al, byte [rdx + RBP] ; get the nth character of other.
    cmp al, 0x00 ; if we reached the end of the string
    je .endLoop_{loop_endloop_index} ; end the function
    mov [{node[1]} + RBP], al ; write the nth character of other to nth position of text
    inc RBP ; increase counter
    jmp .loop_{loop_endloop_index} ; loop

.endLoop_{loop_endloop_index}:
    ''')
                section_text.append("   push 25\n")
              
                pos += 1
             
                
            

        elif node[0] == WHILE_ST:
            while_loop_index += 1
            section_text.append(f"while_loop_at_index_{while_loop_index}:\n")
            walktree((node[1],), funcname)
            section_text.append(f"   jz addr_{node[2]}\n")
            obj = list(obj)
            obj[node[2]] = (CLOSE_CB, "elem1", WHILE_ST)
            obj = tuple(obj)
            pos += 1

        elif node[0] == VAR_ASSIGN_UINT64:
            section_bss.append(f"    {node[1]} resb 8\n")
            pos += 1

        elif node[0] == VAR_ASSIGN_USTR:
            if node[2][0] == OPERATION_NUM:
                string_bytes[node[1]] = node[2][1]
                section_bss.append(f"    {node[1]} resb {node[2][1]}\n")
                pos += 1
            else : assert False, "Not implemented"
          
        elif node[0] == VAR_ASSIGN_UINT32:
            section_bss.append(f"    {node[1]} resb 4\n")
            pos += 1

        elif node[0] == PLUSPLUS:
            section_text.append(f"   inc byte [{node[1]}]\n")
            pos += 1                
        elif node[0] == MINUSMINUS:
            section_text.append(f"   dec byte [{node[1]}]\n")
            pos += 1
        else : assert False , f"Not implemented instruction inside of compilation {node}"
        
    


env["main"]= crossreference_blocks(env["main"])


walktree(env["main"], "main")
filename = sys.argv[1]
out = open(f"{filename[:4]}.asm", "w+")

def generate_assembly():

    out.write("\n")

    section_text.append("   mov rax, 60\n")
    section_text.append("   mov rdi, 0\n")
    section_text.append("   syscall\n")

    for line in section_bss : 
        out.write(line)

    
    out.write("\n")

    for line in section_data:
        out.write(line)


    out.write("\n")

    for line in section_text:
        out.write(line)

    out.write("\n")


    print_digit_set = [
    "_printDigit: \n", "\n", 
    "   mov rcx , digitSpace \n", 
    "   mov rbx, 10\n", 
    "   mov [rcx], rbx\n", 
    "   inc rcx\n", 
    "   mov [digitSpacePos], rcx\n", 
    "\n","_printDigitLoop:\n", "\n", 
    "   mov rdx, 0\n", 
    "   mov rbx, 10\n", 
    "   div rbx\n", 
    "   push rax\n", 
    "   add rdx, 48\n", 
    "   mov rcx, [digitSpacePos]\n", 
    "   mov [rcx], dl\n", 
    "   inc rcx\n", 
    "   mov [digitSpacePos], rcx\n", 
    "   pop rax\n", "   cmp rax, 0\n", 
    "   jne _printDigitLoop\n", 
    "\n","_printDigitLoop2:\n",

    '''
    mov rcx, [digitSpacePos]
 
    mov rax, 1
    mov rdi, 1
    mov rsi, rcx
    mov rdx, 1
    syscall
 
    mov rcx, [digitSpacePos]
    dec rcx
    mov [digitSpacePos], rcx
 
    cmp rcx, digitSpace
    jge _printDigitLoop2
 
    ret \n''']
    for line in print_digit_set :
        out.write(line)
    out.write("\n")

generate_assembly()

