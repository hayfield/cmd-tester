# @description python script to test the output from command line programs
# @usage tester.py FILE_CONTAINING_TESTS
import subprocess, string
import sys
import shlex

# get the name of the file with the tests in from the command line
def testFile():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        return False

# read the tests in from the file
def readTests():
    buffer = []
    
    try:
        with open(testFile(), 'r') as f:
            for line in f:
                buffer.append("\n".join(line.split("\\n"))[:-1])
    except IOError:
        print "Error reading in test file"
    
    return buffer

# format a test into a nicer format to use later in the processing
def formatTest(line):
    arr = line.split(" ")
    testType = arr.pop(0)
    
    test = dict(type=testType, code=" ".join(arr))
    
    return test

# merge multiple commands in a test that do the same thing
def mergeCommands(test):
    buffer = []
    outBuf = ''
    outCommands = 0
    errBuf = ''
    errCommands = 0
    
    for cmd in test:
        if cmd['type'] == '<<':
            if len(outBuf) > 0:
                outBuf += '\n'
            outBuf += cmd['code']
            outCommands += 1
        elif cmd['type'] == '<<err':
            if len(errBuf) > 0:
                errBuf += '\n'
            errBuf += cmd['code']
            errCommands += 1
        else:
            buffer.append(cmd)
    
    outCmd = dict(type='<<', code=outBuf)
    errCmd = dict(type='<<err', code=errBuf)
    
    if outCommands > 0:
        buffer.append(outCmd)
    if errCommands > 0:
        buffer.append(errCmd)
    
    if outCommands > 1 or errCommands > 1:
        return buffer
    else:
        return test

# nicely format all of the tests
def formatTests(tests):
    buffer = []
    started = False
    
    for el in tests:
        if el == "--newtest":
            if started:
                test = mergeCommands(test)
                buffer.append(test)
            
            started = True
            test = []
        elif started:
            if len(el) > 0:
                test.append(formatTest(el))
    
    if test:
        test = mergeCommands(test)
        buffer.append(test)
    
    return buffer

# run the tests
def runTests(tests):
    
    # loop through the tests
    for test in tests:
        processStarted = False
        passed = True
        execCmd = ""
        s = False
        
        # loop through the commands that each test consists of
        for cmd in test:
            
            # do something based on the type of command being checked for
            # run a process
            if cmd['type'] == 'exec':
                p = subprocess.Popen(shlex.split(cmd['code']), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                execCmd = cmd['code']
            
            # check stdout
            elif cmd['type'] == '<<':
                if not s:
                    s = p.communicate()
                if "\n".join(s[0].splitlines()) != cmd['code']:
                    print "stdout error. Expected: \n" + cmd['code'] + " Actual: \n" + "\n".join(s[0].splitlines())
                    passed = False
            
            # check stderr
            elif cmd['type'] == '<<err':
                if not s:
                    s = p.communicate()
                if "\n".join(s[1].splitlines()) != cmd['code']:
                    print "stderr error. Expected: " + cmd['code'] + " Actual: " + "\n".join(s[1].splitlines())
                    passed = False
            
            # check input
            elif cmd['type'] == '>>':
                s = p.communicate(cmd['code'])
            
            # check the return code
            elif cmd['type'] == 'exit':
                if int(cmd['code']) != p.returncode:
                    print "returncode error"
                    passed = False
        
        # display pass or fail for the test
        if passed:
            print "Pass: " + execCmd
        else:
            print "Fail: " + execCmd

def main():
    if testFile():
        tests = readTests()
        tests = formatTests(tests)
        runTests(tests)

if __name__ == '__main__':
    main()
