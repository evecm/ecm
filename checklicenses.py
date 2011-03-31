# The MIT License - EVE Corporation Management
#
# Copyright (c) 2010 Robin Jarry
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__date__ = "2011 3 29"
__author__ = "diabeteman"

#------------------------------------------------------------------------------
import os.path,sys

MISSING = 0
INSERTED = 0

#------------------------------------------------------------------------------
def check_file(file, license, modify):
    global MISSING, INSERTED
    if file.endswith(".py"):
        try:
            fd = open(file, "r")
            buffer = fd.read()
            fd.close()
            if license not in buffer:
                MISSING += 1
                if modify:
                    fd = open(file, "w")
                    if buffer.startswith("#!"):
                        lines = buffer.splitlines() 
                        header = lines[0] + "\n"
                        buffer = "\n".join(lines[1:])
                    else:
                        header = ""
                        
                    fd.write(header + license + '\n\n' + buffer)
                    fd.close()
                    print "License inserted in", file
                    INSERTED += 1
                else:
                    print "No license header in", file
        except Exception as e:
            print e
            

def check_dir((license, modify), dir, files):
    for file in files:
        file = os.path.join(dir, file)
        if os.path.isfile(file):
            check_file(file, license, modify)
                

def main():
    dir_path = os.path.abspath(os.path.dirname(__file__))
    fd = open(os.path.join(dir_path, "src/ecm/LICENSE"), "r")
    license = fd.read()
    fd.close()
    
    # add comments at the beginning of each line
    license = "\n".join(["# " + line for line in license.splitlines()])
    
    modify = len(sys.argv) > 1 and sys.argv[1] == "--modify"
    
    os.path.walk(os.path.join(dir_path, "src"), check_dir, (license, modify))

    print
    print MISSING, "license headers missing.", INSERTED, "inserted"


if __name__ == "__main__":
    main()