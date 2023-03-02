# Copyright 2023 by Serena Rosignoli. All rights reserved.
### HOW-TO ###
# - Run the script in PyMOL (Open PyMOL -> File -> Run Script...)
# - Use the PyMOL interpreter to run the desired conda function by making use of 'rosconda' command
# - Write the conda function WITHOUT specifying 'conda' at the begginning of the line; e.g. to run 'conda list' just type 'rosconda list'

import io as io
import sys, shlex

def rosconda(command):

    try:
        import conda.cli
    except ImportError:
        raise pymol.CmdException('conda wrapper only functional in PyMOL bundles')


    args = shlex.split(command)

    if args:
        if args[0] in ('install', 'update'):
            args[1:1] = ['--yes', '--prefix', sys.prefix]

    from contextlib import redirect_stderr
    #with open('conda_filename.log', 'w') as stderr, redirect_stderr(stderr):
    versione = cmd.get_version()

    with io.StringIO() as stderr, redirect_stderr(stderr):
        r = conda.cli.main('conda', *args)
        s = stderr.getvalue()

    if r and re.search("CommandNotFoundError", s):
        #print("not found")
        with io.StringIO() as stderr, redirect_stderr(stderr):
            r = conda.cli.main(*args)
            s = stderr.getvalue()

    print(s)
    print(r)

cmd.extend(rosconda)
