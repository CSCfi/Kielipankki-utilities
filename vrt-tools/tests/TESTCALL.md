# How to test-call command-line VRT tools from Python
-----------------------------------------------------

_Thunk thoughts on ways to test-call tools_

To *test* that a command-line tool can be run as intended, it is best
to run it as intended and to examine the outcome. The automation of
such tests means writing scripts that carry out the steps. The script
should not fail when the tool fails.

Various VRT tools read and write, even overwrite, files, in addition
to reading from and writing to the three standard streams.

`from subprocess import Popen, PIPE, TimeoutExpired`
`from tempfile import TemporaryDirectory`

An idea is to capture whole stdout and stderr, without deadlock even
if the process behaves badly. (It is not known that any of the current
tools would ever write excessive diagnostics on a small input.)

Handle timeout.

Idea is to clean up. (Apparently `pytest` will do at least files, not
sure about any processes yet.)

## Standard streams: stdin, stdout, stderr

The simplest non-trivial way to invoke a tool is to send it some input
and receive some output, together with any diagnostic output and a
return code (often called status), in the "standard streams" - input,
output, error stream, and the return code.

```python
proc = Popen([ 'cat' ], stdin = PIPE, stdout = PIPE, stderr = PIPE)
```

Input can be specified as a bytes object (a "byte string"). A timeout
can be specified (in seconds), after which an exception is raised.
(When the test author forgets to send any input, the tool just hangs
there, waiting for the input. Or the tool may have failed somehow
without terminating.)

```python
out, err = proc.communicate(input = b'one two\n', timeout = 10)
```

The observed output and diagnostic output can then be compared to the
expected output and no error message. Most of the time, the expected
succesful return code is `0`. (One should also test that the tools
fail when they are expected to fail.)

```python
assert out == b'one two\n' and err == b''
assert proc.returncode == 0
```

However! The child process is not terminated on timeout. So the
protocol is to terminate the child process when it does not terminate
on its own.

```python
proc = Popen([ 'cat' ], stdin = PIPE, stdout = PIPE, stderr = PIPE)
try:
    out, err = proc.communicate(input = b'one two\n', timeout = 10)
except TimeoutExpired:
    proc.kill()
    out, err = proc.communicate()
    raise # presumably!
```

Python documentation suggests `proc.kill()` as above but
`proc.terminate()` might be less brutal. There is also
`proc.send_signal(signal)` to send any signal.

## Sending a file to tool stdin

Instead of literal data from the test script, the contents of a file
can be directed to the stdin of the tool.

```python
proc = Popen([ 'cat' ], stdin = open('roska.vrt', 'br'), stdout = PIPE, stderr = PIPE)
out, err = proc.communicate()
```

It is not very important to close the input file in the test script,
assuming the script itself is short-lived and does not hold lots of
objects like `proc` that keep file objects alive.

To properly close the file and release the underlying file handle to
the operating system, a context manager (`with`) can be used. Then it
is presumed important that the communication with the process happens
before the closing of the input file: within the `with`.

```python
with open('roska.vrt', 'br') as ins:
    proc = Popen([ 'cat' ], stdin = ins, stdout = PIPE, stderr = PIPE)
    out, err = proc.communicate()
```

Even the actual command to close the input file can actually be given.

```python
ins = open('roska.vrt', 'br')
proc = Popen([ 'cat' ], stdin = ins, stdout = PIPE, stderr = PIPE)
out, err = proc.communicate()
ins.close()
```

## Sending tool stdout to a file

The stdout of the tool can be directed to a file. It is poorly
understood (by the author) what the significance of the closing of the
output file in the test script is. Presumably any relevant buffering
is done by the tool, not by the test script.

```python
with open('roska.out', 'bw') as ous:
    proc = Popen([ 'cat' ], stdin = Pipe, stdout = ous, stderr = PIPE)
    out, err = proc.communicate()
```

Is that right? The closing of `ous`, that is.

```python
assert out == b'' == err
```

The diagnostic stream (stderr) of the tool can be directed to a file
in the same way, or ignored by sending it to `subprocess.DEVNULL`
though the wisdom of doing that in a test script is questionable.

## Have the tool read from or write to a file

If the tool reads its input from a file, or writes its output to a
file, there presumably is nothing in its stdout. Set stdin to `None`
(default), then capture stdout anyway but expect it to be empty.

```python
proc = Popen([ 'sort', '--output-file=roska.out', 'roska.vrt' ],
             stdin = None,
	     stdout = PIPE,
	     stderr = PIPE)
out, err = proc.communicate()
```

## Temporary files

A significant component of VRT-tools interface is to write the output
to a temporary file first and then leave the result in the original
input file or in its sibling file, depending on the options.

It is best to create a temporary directory for the test and then,
hopefully, fail or succeed in that directory. It is too hard to make
sure that the tool does not create stray files somewhere else in the
file system.

Apparently `pytest` comes with a high-level facility for this.

On a lower level, a `TemporaryDirectory` object has a `cleanup()`
method to remove the temporary files. The object can be used as a
context manager (with `with`).

```python
with TemporaryDirectory(prefix = 'sort-',
                        suffix = '.tmp',
			dir = 'scratch') as tmp:
    proc = Popen([ 'sort', '-o', os.path.join(tmp, 'roska.out'), 'roska.vrt'],
                 stdin = None,
		 stdout = PIPE,
		 stderr = PIPE)
    out, err = proc.communicate()

    # test directory contents here
```

Without the context-manager magic, the `cleanup()` method of the
`TemporaryDirectory` object can be called explicitly, or left to
Python to call when the `TemporaryDirectory` object is eventually
collected.

```python
tmp = TemporaryDirectory(prefix = 'sort-', suffix = '.tmp')
proc = Popen([ 'sort', '-o', os.path.join(tmp, 'roska.out'), 'roska.vrt' ],
             stdout = PIPE, stderr = PIPE)
out, err = proc.communicate()
...
tmp.cleanup()
```

## More advanced needs

It would be desirable to test how certain tools handle a failure of
their underying child process.

An idea is to somehow get hold of the child process and terminate it
by sending it a signal. Can this be done?
