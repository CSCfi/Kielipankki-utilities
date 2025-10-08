# asr-apptainer

## Building

This directory contains recipes for ASR containers. Building them may
require a lot of memory, and not all build environments are compatible.
The ones we are now distributing are built on Pouta Ubuntu VMs and have
been tested to work on SD Desktop.

Non-root building should be possible like this:

```bash
srun apptainer build --fakeroot samiasr.sif samiasr.def
```

If `/tmp` is small, and you need another temporary space, like on HPC, you
can do eg.

```
export APPTAINER_TMPDIR=$TMPDIR
export APPTAINER_CACHEDIR=$TMPDIR
apptainer build --fakeroot --bind="$TMPDIR:/tmp" samiasr.sif samiasr.def
```

## Running

These containers have just the libraries, models and Python, not a
processing script. By default a processing script (eg. `samiasr.py`) is
given to them as an argument:

```bash
apptainer run samiasr_cpu.sif samiasr.py input.wav
```

## Models

Credit for the Sàmi model goes to Yaroslav Getman and Tamas Grosz,

https://huggingface.co/GetmanY1/wav2vec2-large-sami-cont-pt-22k-finetuned
