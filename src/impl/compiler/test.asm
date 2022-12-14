
section .bss
  digitSpace resb 100
  digitSpacePos resb 8
   x resb 21

section .data
  string_literal_at_index_0: db 0x48,0x65,0x6c,0x6c,0x6f,0x20,0x77,0x6f,0x72,0x6c,0x64,0x21, 10


section .text
    global _start
_start:
   push 13
   push string_literal_at_index_0
   xor RBP, RBP
   pop rdx
  

.loop_0:
    mov al, byte [rdx + RBP] ; get the nth character of other.
    cmp al, 0x00 ; if we reached the end of the string
    je .endLoop_0 ; end the function
    mov [x + RBP], al ; write the nth character of other to nth position of text
    inc RBP ; increase counter
    jmp .loop_0 ; loop

.endLoop_0:
       push 21
   push x
   mov rax, 1
   mov rdi, 1
   pop rsi,
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

