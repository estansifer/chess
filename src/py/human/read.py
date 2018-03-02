import sys

def readline(message, validator = None, fin = None, fout = None):
    if validator is None:
        validator = lambda x : True
    if fin is None:
        fin = sys.stdin
    if fout is None:
        fout = sys.stdout

    while True:
        fout.write(message)
        fout.flush()
        line = fin.readline()
        fout.write('\n')
        fout.flush()

        if validator(line):
            return line

def read_boolean(message, default = None, fin = None, fout = None):
    if default is None:
        validator = lambda x : len(x.strip()) > 1 and (x.strip()[0] in 'yYnN')
    else:
        validator = lambda x : len(x.strip()) == 0 or (x.strip()[0] in 'yYnN')

    line = readline(message, validator, fin, fout).strip()

    if len(line) == 0:
        return default
    else:
        return line[0] in 'yY'

def read_intrange(message, N, fin = None, fout = None):
    def validator(x):
        x = x.strip()
        try:
            n = int(x)
            return (n > 0) and (n <= N)
        except:
            return False

    line = readline(message, validator, fin, fout).strip()
    return int(line)

def wait(message = 'Press return to continue or (q) to quit\n'):
    if message is not None:
        sys.stdout.write(message)
        sys.stdout.flush()
    line = sys.stdin.readline().strip().lower()
    if len(line) > 0 and line[0] == 'q':
        sys.exit(0)
