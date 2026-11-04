# -*- makefile -*-

include Makefile-common

# Flags
# Match the original working ManalinkEh.dll PE header flags (DllCharacteristics=0).
# Modern MinGW defaults add ASLR and NX flags, not used by the original DLL.
LFLAGS := $(LFLAGS) -Wl,-Tmanalink.lds --entry _DllEntry -Wl,--disable-dynamicbase -Wl,--disable-nxcompat

# Input files
SUBDIRS = cards functions
AFILES := $(filter-out functions/get_card_instance.asm functions/display_error_message.asm,$(AFILES))
AFILES := $(AFILES) ManalinkEh.asm
LIBS = gdi32 msimg32
LOCAL_LIBS = capturestackbacktrace Drawcardlib

# Output files
OUTPUT = ManalinkEh.dll

include Makefile-targets

clean::
	-$(RM) ManalinkEh.ao