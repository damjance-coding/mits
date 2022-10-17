
section .bss
  digitSpace resb 100
  digitSpacePos resb 8
   x resb 8

section .data
  string_literal_at_index_0: db 0x57,0x65,0x6e,0x74,0x20,0x69,0x6e,0x74,0x6f,0x20,0x6e,0x65,0x73,0x74,0x65,0x64,0x20,0x69,0x66, 10

  string_literal_at_index_1: db 0x77,0x65,0x6e,0x74,0x20,0x69,0x6e,0x74,0x6f,0x20,0x6e,0x65,0x73,0x74,0x65,0x64,0x20,0x69,0x66,0x20,0x65,0x6c,0x73,0x65, 10

  string_literal_at_index_2: db 0x74,0x65,0x73,0x74, 10

  string_literal_at_index_3: db 0x52,0x41,0x44,0x55, 10


section .text
    global _start
_start:
   push 12

   pop rax
   mov [x], rax

  mov rax, [x]
  push rax

   push 13

   mov rcx, 0
   mov rdx, 1
   pop rax
   pop rbx
   cmp rax, rbx
   cmovs rdx, rcx
   push rdx
   
   pop rax
   test rax, rax
   jz addr_9
   
  mov rax, [x]
  push rax

   push 11

   mov rcx, 0
   mov rdx, 1
   pop rax
   pop rbx
   cmp rax, rbx
   cmove rcx, rdx
   push rcx
   
   pop rax
   test rax, rax
   jz addr_5
   
   push 20
   mov rax, 1
   mov rdi, 1
   mov rsi, string_literal_at_index_0
   pop rdx
   syscall

addr_4: 
jnz addr_7
addr_5: 
   push 25
   mov rax, 1
   mov rdi, 1
   mov rsi, string_literal_at_index_1
   pop rdx
   syscall

addr_7: 
addr_8: 
jnz addr_11
addr_9: 
   push 5
   mov rax, 1
   mov rdi, 1
   mov rsi, string_literal_at_index_2
   pop rdx
   syscall

addr_11: 
   push 5
   mov rax, 1
   mov rdi, 1
   mov rsi, string_literal_at_index_3
   pop rdx
   syscall

   mov rax, 60
   mov rdi, 0
   syscall

_printDigit: 

   mov rcx , digitSpace 
   mov rbx, 10
   mov [rcx], rbx
   inc rcx
   mov [digitSpacePos], rcx

_printDigitLoop:

   mov rdx, 0
   mov rbx, 10
   div rbx
   push rax
   add rdx, 48
   mov rcx, [digitSpacePos]
   mov [rcx], dl
   inc rcx
   mov [digitSpacePos], rcx
   pop rax
   cmp rax, 0
   jne _printDigitLoop

_printDigitLoop2:

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
 
    ret 

