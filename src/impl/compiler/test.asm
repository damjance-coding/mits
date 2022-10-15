
section .bss
  digitSpace resb 100
  digitSpacePos resb 8
   z resb 8
   y resb 8

section .data

section .text
    global _start
_start:
   push 15

   push 3

   pop rax
   pop rbx
   mul rbx
   push rax

   pop rax
   mov [z], rax

   push 15

   push 15

   pop rax
   pop rbx
   add rax, rbx
   push rax

   pop rax
   mov [y], rax

  mov rax, [y]
  push rax

   pop rax
   call _printDigit

  mov rax, [z]
  push rax

   pop rax
   call _printDigit

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

