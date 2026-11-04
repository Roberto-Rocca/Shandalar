%include "ManalinkEh.mac"

section .text

global _ability_effect_keyword
_ability_effect_keyword:
  push ebp
  mov ebp, esp

  push dword [ebp + 0xC]
  push dword [ebp + 0x8]
  push dword [0x715B38]
  push dword [0x7876E8]
  push dword [0x7A3610]

  call dword [exe_target_4a09a0]
  add esp, 0x14
  leave
  ret
  align 32
; Absolute Magic.exe entry points: indirect calls preserve all input registers.
section .data
exe_target_4a09a0: dd 0x4a09a0
