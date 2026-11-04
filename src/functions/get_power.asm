%include "ManalinkEh.mac"

section .text

global _get_power
_get_power:
  push ebp
  mov ebp, esp
  push -1
  push 0x32
  push CardID
  push PlayerID
  call dword [exe_target_4352d0]
  add esp, 0x10
  leave
  ret
  align 32

global _get_toughness
_get_toughness:
  push ebp
  mov ebp, esp
  push -1
  push 0x33
  push CardID
  push PlayerID
  call dword [exe_target_4352d0]
  add esp, 0x10
  leave
  ret
  align 32

; Absolute Magic.exe entry points: indirect calls preserve all input registers.
section .data
exe_target_4352d0: dd 0x4352d0
