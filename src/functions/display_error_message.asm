%include "ManalinkEh.mac"

section .text

; void display_error_message(const char* msg);
; Displays msg in the small horizontal window and sleeps for 2 seconds.
;
; This really doesn't belong here, but neither does the misnamed is_not_dead()
; above, and this is a more general version of that.
global _display_error_message
_display_error_message:
  push	ebp
  mov	ebp, esp
  mov	eax, dword [ebp+0x08]
  call dword [exe_target_471d30]
  leave
  ret
  align	32

; Absolute Magic.exe entry points: indirect calls preserve all input registers.
section .data
exe_target_471d30: dd 0x471d30
