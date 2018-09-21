import re
import uuid

fdr = open("input.c", 'r')
fdw = open("output.c", 'w')

_map = { }
outstring = ''

# line = fdr.readline()
# while line:
#     while True:
#         m = re.compile('\".*\"', re.S)
#         _str = m.search( line )
#         if None == _str:
#             outstring += line
#             break
#         key = str( uuid.uuid1() )
#         m = re.compile('\".*\"', re.S)
#         outtmp = re.sub(m, key, line, 1)
#         line = outtmp
#         _map[ key ] = _str.group(0)
#     line = fdr.readline()

m = re.compile(r'//.*')
outtmp = re.sub(m, ' ', outstring)
outstring = outtmp

m = re.compile(r'/\*.*?\*/', re.S)
outtmp = re.sub(m, ' ', outstring)
outstring = outtmp

for key in _map.keys():
    outstring = outstring.replace(key, _map[key])

fdw.write(outstring)
fdw.close()