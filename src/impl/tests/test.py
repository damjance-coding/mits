
prog = '''
0
if 
    write "test"
    if 
        write "test1"
    endif
endif
'''
parsed = ()

prog = prog.split()

scope = 0






cind = []

for loc in range(len(prog)):
    st = prog[loc]
    if st == "if" :
        cind.append(loc)
    elif st == "endif":
        x = cind.pop()
        prog[x] =("if", loc)


index = 0

print(prog)
while index < (len(prog)) :
    op = prog[index]
    if op[0] == "if":
        # print(op[1])
        if True: 
             
            index = op[1]
            
        index += 1
    elif op != "endif" :
        print(op) 
        index += 1
    else : index += 1