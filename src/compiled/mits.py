from lexer import MyLexer
from parser  import MyParser
import sys

file = sys.argv[1]
mitslexer = MyLexer()
mitsparser = MyParser()
gen = ()
env = {"globalvars":{}}

section_text = '''


section .text
    global _start



'''

start = '''

_start:
    call main

'''

asm_code = '''


'''

with open(file,'r') as file:
    lines = [line.strip() for line in file]

parsedtokens = ()

for line in lines:
    if len(line) != 0 and line.startswith('//') == False:
        x  = line.strip()
        
        if len(x) != 0 : y  = mitsparser.parse(mitslexer.tokenize(x))
        
        if len(y) != 0 :
            parsedtokens += (y, )
    else: pass

print(parsedtokens)


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

transfertofunctions(parsedtokens)
print(env)

def walktree(node, funcname):
    if node[0] == "print":
        pass