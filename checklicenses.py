# Copyright (c) 2010-2012 Robin Jarry
# 
# This file is part of EVE Corporation Management.
# 
# EVE Corporation Management is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or (at your 
# option) any later version.
# 
# EVE Corporation Management is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
# more details.
# 
# You should have received a copy of the GNU General Public License along with 
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2011 3 29"
__author__ = "diabeteman"

#------------------------------------------------------------------------------
import os.path,sys

MISSING = 0
INSERTED = 0
LICENSE = ''

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
                        
                    fd.write(header + LICENSE + '\n\n' + buffer)
                    fd.close()
                    print "License inserted in", file
                    INSERTED += 1
                else:
                    print "No license header in", file
        except Exception, e:
            print e
            

def check_dir((license, modify), dir, files):
    if os.path.basename(dir) == "lib":
        return
    for file in files:
        file = os.path.join(dir, file)
        if os.path.isfile(file):
            check_file(file, license, modify)
                

def main():
    global LICENSE 
    
    dir_path = os.path.abspath(os.path.dirname(__file__))
    fd = open(os.path.join(dir_path, "LICENSE"), "r")
    LICENSE = fd.read().strip()
    fd.close()
    
    # Only first line matters
    license = LICENSE.splitlines()[0]
    # we store the license in a global variable to insert it in files if needed
    LICENSE = '\n'.join([ '# ' + line for line in LICENSE.splitlines() ])
    
    modify = len(sys.argv) > 1 and sys.argv[1] == "--modify"
    
    os.path.walk(os.path.join(dir_path, "src"), check_dir, (license, modify))

    print
    print MISSING, "license headers missing.", INSERTED, "inserted"


if __name__ == "__main__":
    main()
