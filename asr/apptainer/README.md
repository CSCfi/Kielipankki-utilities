# asr-apptainer

## Building

This directory contains recipes for ASR containers. Building them may
require a lot of memory, and not all build environments are compatible.
The ones we are now distributing are built on Pouta Ubuntu VMs and have
been tested to work on SD Desktop.

Non-root building (on HPC) should be possible like this:

```bash
srun apptainer build --fakeroot samiasr.sif samiasr.def
```

On VMs, just run with sudo and no fakeroot.

If `/tmp` is small, and you need another temporary space, like on HPC, you
can do eg.

```
export APPTAINER_TMPDIR=$TMPDIR
export APPTAINER_CACHEDIR=$TMPDIR
apptainer build --fakeroot --bind="$TMPDIR:/tmp" samiasr.sif samiasr.def
```

## Running

Basic operation with apptainer run:

```bash
apptainer run samiasr.sif input1.wav input2.wav ...
```

See `--help` to see supported args.

If you do want to modify the runscript, you can extract it like this:

```bash
apptainer exec samiasr.sif get_runscript samiasr.py
```

This will write samiasr.py to the present working directory. You can edit
it, and then run your modified version with eg.

```bash
apptainer exec samiasr.sif python samiasr-modified.py input.wav
```

## Models

Credit for the Sàmi model goes to Yaroslav Getman and Tamas Grosz,

https://huggingface.co/GetmanY1/wav2vec2-large-sami-cont-pt-22k-finetuned
