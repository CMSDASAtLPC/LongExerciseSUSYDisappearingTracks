import os

with open("commands", "r") as fo:
    cmds = fo.read()
    for line in cmds.split("\n"):
        print line
        os.system(line)
