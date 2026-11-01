# Shandalar Extended — stato della compilazione

## Step 2: analisi statica dei prerequisiti (1 novembre 2026)

Questi risultati **non** dimostrano che la DLL sia compilabile: non abbiamo ancora ottenuto una build eseguibile.

### Evidenze nei sorgenti

- `src/Makefile` definisce il target `ManalinkEh.dll` e include `cards/`, `functions/`, `ManalinkEh.asm`, `capturestackbacktrace` e `Drawcardlib`.
- `src/Makefile-common` richiama GCC, G++, Yasm, dlltool e objcopy. Yasm produce oggetti `win32` x86.
- `src/manalink.lds` contiene riferimenti a indirizzi assoluti: la compatibilità con il `Magic.exe` di destinazione va verificata.
- `src/Makefile-targets` richiede `src/card_id.h`; `src/defs.h` dichiara che tale header viene generato da `csv2dat.exe`.
- `magic_updater/Magic_updater.bat` richiama `csv2dat.exe` e `ct2exe`. Sono presenti i CSV di input `magic_updater/Manalink.csv` e `magic_updater/ct_all.csv`, ma **non** l'eseguibile `csv2dat.exe` nei percorsi controllati e **non** l'header `src/card_id.h` nel ramo `master`. **Aggiornamento:** una copia dell'header contenente 15.639 identificativi è presente in `Program/src/card_id.h`. Sono stati controllati quattro file sorgente, inclusi quelli di espansioni recenti: nessun identificativo utilizzato in questi campioni risultava assente.
- La distribuzione contiene eseguibili Yasm e Make per Windows in `src/`, ma questo non equivale a una toolchain di compilazione completa.

### Primo tentativo di compilazione senza csv2dat.exe

Per una prima prova non occorre rigenerare il database: copiare il file già presente in `Program/src/card_id.h` nella posizione attesa dal Makefile, lavorando su una copia del repository e senza modificare i dati delle carte.

```powershell
Copy-Item .\Program\src\card_id.h .\src\card_id.h
```

Questa copia appartiene a uno snapshot dei sorgenti diverso da `src/`: la compatibilità con gli identificativi e il database finali **non è garantita**, per cui va verificata prima di distribuire una DLL.

### Controllo ripetibile

Dalla radice di una copia completa del repository:

```powershell
python tools/check_build_prereqs.py
```

Oppure specificando il percorso:

```bash
python3 tools/check_build_prereqs.py --root /path/al/repository
```

Lo script è di sola lettura, richiede Python 3 e restituisce codice di uscita 1 se manca almeno un prerequisito. Il superamento del controllo non garantisce una compilazione corretta. È un controllo conservativo: ad esempio, un compilatore MinGW con un nome diverso da `gcc` deve essere reso disponibile nel PATH o verificato a parte.

### Risultato della prova nel nostro ambiente Linux

Il test dello script Python è riuscito. Il controllo dei prerequisiti ha restituito correttamente un esito negativo: mancano MinGW 32 bit, Yasm e dlltool, mentre `gcc` nel PATH è Linux x86-64. Anche un tentativo preliminare di compilazione con `gcc -m32` si interrompe sugli header C a 32 bit mancanti. Il ridotto archivio dei soli sorgenti usato per il test non include `magic_updater/`; la presenza dei relativi CSV è stata invece verificata nel fork online.

Nessuna DLL è stata prodotta e nessuna carta è stata testata in partita.

### Prossimi passi, nell'ordine

1. Tentare una compilazione **senza modifiche funzionali** usando la copia di `card_id.h` già individuata in `Program/src`. In parallelo, cercare `csv2dat.exe` (utile per futuri cambi ai dati delle carte). Il [thread Manalink 3.0](https://slightlymagic.net/forum/viewtopic.php?t=6284) cita l'archivio `srcmok` con i sorgenti del generatore e `MakeCSV2DAT.bat`; per quel generatore servono Turbo Assembler 5 e Watcom Linker. Nel [thread csv2dat](https://slightlymagic.net/forum/viewtopic.php?t=1310) un intervento dell'ottobre 2025 segnala la disponibilità di una copia dell'archivio.
2. Preparare una toolchain MinGW **a 32 bit** con Yasm (e verificare le versioni compatibili).
3. Compilare prima il codice originale, senza modificarne gli effetti.
4. Testare la DLL risultante su una copia dell'installazione di Shandalar.
5. Soltanto dopo, provare Land Equilibrium dalla PR #1.

**Nessuna modifica a `master` fino alla compilazione e ai test.**
