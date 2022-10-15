import subprocess
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
            
            if block[pos[2]][0] == "op_if_start" or block[pos[2]][0] == "op_start_while"  or block[pos[2]][0] == "for_start" or block[pos[2]][0] == "else" or block[pos[2]][0] == "try_start" or block[pos[2]][0] == "except_start":
                
                if block[pos[2]][0] == "else":
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

string_at_index = 0


INSTRUNCTION_WRITE_STRING = 0
INSTRUNCTION_WRITE_EXPR = 1

KEYWORD_WRITE = "op_write"

EXPRESSION_STRING = "expr_string"
EXPRESSION_ADD = "expr_add"
EXPRESSION_SUB = "expr_sub"
EXPRESSION_MUL = "expr_mul"
EXPRESSION_DIV = "expr_div"
EXPRESSION_IDENTIFIER = "identifier"

def walktree(obj, funcname):
    global string_at_index
    
    pos = 0
    while pos < len(obj):
        node = obj[pos]
        if node[0] == KEYWORD_WRITE:
          write_instruction_values = walktree((node[1],), funcname)
          if write_instruction_values[0] == INSTRUNCTION_WRITE_STRING:   
            
            section_text.append(f'   ; write "{write_instruction_values[0]}"\n')
            section_text.append("    mov rax, 1 \n")
            section_text.append("    mov rdi, 1 \n")
            section_text.append(f'   mov rsi, string_at_index_{string_at_index}\n')
            section_text.append(f'   mov rdx, string_at_index_{string_at_index}_len\n')
            section_text.append("   syscall\n")
            section_text.append("\n")
            pos += 1

          elif write_instruction_values[0] == INSTRUNCTION_WRITE_EXPR:
            section_text.append(f"   ; write {write_instruction_values[1]} {write_instruction_values[2]} {write_instruction_values[3]} , poping it from the rax\n")
            section_text.append("   call _printDigit\n")
            section_text.append(f"\n")
            pos += 1

        elif node[0] == EXPRESSION_STRING:
            string = node[1]
            string_at_index += 1
            section_data.append(f'   ; "{string}"\n')
            section_data.append(f'  string_at_index_{string_at_index} db "{string}" \n')
            section_data.append(f'  string_at_index_{string_at_index}_len equ $ - string_at_index_{string_at_index} \n')
            section_data.append(f"\n")
            
            pos += 1
            return (INSTRUNCTION_WRITE_STRING, string)
        
        elif node[0] == EXPRESSION_ADD:
            if node[1][0] and node[2][0] != EXPRESSION_IDENTIFIER :
                section_text.append(f"   ; push {node[1][1]} + {node[2][1]} to the rax\n")
                section_text.append(f"   mov rax, {node[1][1]}\n")
                section_text.append(f"   mov rbx, {node[2][1]}\n")
                section_text.append(f"   add rax, rbx\n")
                section_text.append("\n")
                pos += 1
            
                return (INSTRUNCTION_WRITE_EXPR, node[1][1], "+" , node[2][1])
            
            else : assert False , f"Not implemented"

        elif node[0] == EXPRESSION_SUB :

            if node[1][0] and node[2][0] != EXPRESSION_IDENTIFIER :
                section_text.append(f"   ; push {node[1][1]} - {node[2][1]} to rax \n")
                section_text.append(f"    mov rax, {node[1][1]}\n")
                section_text.append(f"    mov rbx, {node[2][1]}\n")
                section_text.append(f"    sub rax, rbx\n")
                section_data.append(f"\n")
                pos += 1
                return (INSTRUNCTION_WRITE_EXPR, node[1][1], "-" , node[2][1])

            else : assert False , f"Not implemented"

        elif node[0] == EXPRESSION_MUL :

          if node[1][0] and node[2][0] != EXPRESSION_IDENTIFIER :
                section_text.append(f"   ; push {node[1][1]} * {node[2][1]} to rax \n")
                section_text.append(f"    mov rax, {node[1][1]}\n")
                section_text.append(f"    mov rbx, {node[2][1]}\n")
                section_text.append(f"    mul rbx\n")
                section_data.append(f"\n")
                pos += 1
                return (INSTRUNCTION_WRITE_EXPR, node[1][1], "*" , node[2][1])

          else : assert False , f"Not implemented"

        
        elif node[0] == EXPRESSION_DIV :
                section_text.append(f"   ; push {node[1][1]} / {node[2][1]} to rax \n")
                section_text.append(f"    mov rax, {node[1][1]}\n")
                section_text.append(f"    mov rbx, {node[2][1]}\n")
                section_text.append(f"    div rbx\n")
                section_data.append(f"\n")
                pos += 1
                return (INSTRUNCTION_WRITE_EXPR, node[1][1], "/" , node[2][1])

        else : assert False , f"Not implemented instruction inside of compilation {node[1]}"
        
    


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
    "_printDigit: \n", 
    " mov rcx , digitSpace \n", 
    " mov rbx, 10\n", 
    " mov [rcx], rbx\n", 
    " inc rcx\n", 
    " mov [digitSpacePos], rcx\n", 
    "\n","_printDigitLoop:\n", 
    " mov rdx, 0\n", 
    " mov rbx, 10\n", 
    " div rbx\n", 
    " push rax\n", 
    " add rdx, 48\n", 
    " mov rcx, [digitSpacePos]\n", 
    " mov [rcx], dl\n", 
    " inc rcx\n", 
    " mov [digitSpacePos], rcx\n", 
    " pop rax\n", " cmp rax, 0\n", 
    " jne _printDigitLoop\n", 
    "\n","_printDigitLoop2:\n",

    '''mov rcx, [digitSpacePos]
 
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
