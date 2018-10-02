# -*- coding:utf-8 -*-
import re

p = "./raw_content.txt"
f = open(p, "r")
content = f.read()
pattern = u"^图\d.*"
result = re.findall(pattern, content) 
print result
