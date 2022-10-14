
section .data
   ; "Hello world"
  string_at_index_1 db "Hello world" 
  string_at_index_1_len equ $ - string_at_index_1 

section .text
    global _start
_start:
   ; write "Hello world"
   mov rax, 1 
   mov rdi, 1 
   mov rsi, string_at_index_1
   mov rdx, string_at_index_1_len
   syscall

   mov rax, 60
   mov rdi, 0
   syscall
