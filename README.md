cmd-tester
==========

A thing to test the output of command line programs where you can work out the expected output in advance.

### Test format

* `//` at the start of a line can be used to indicate a comment
* `--newtest` on a line indicates the start of a new test
* `exec` at the start of a line indicates something that should be executed
* `<<` at the start of a line indicates something that should be output on stdout
* `<<err` at the start of a line indicates something that should be output on stderr
