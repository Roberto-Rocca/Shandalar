%include "ManalinkEh.mac"

section .text

global _get_card_instance
_get_card_instance:
	push ebp
	mov ebp, esp
	push esi
	mov ecx, CardID
	mov eax, PlayerID
	call dword [exe_target_401a80]
	mov eax, esi
	pop esi
	leave
	ret
	align 32

global _get_displayed_card_instance
_get_displayed_card_instance:
	push ebp
	mov ebp, esp
	push esi
	mov ecx, CardID
	mov eax, PlayerID
	call dword [exe_target_401ab0]
	mov eax, esi
	pop esi
	leave
	ret
	align 32

; Absolute Magic.exe entry points: indirect calls preserve all input registers.
section .data
exe_target_401a80: dd 0x401a80
exe_target_401ab0: dd 0x401ab0
