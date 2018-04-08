#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os, sys

if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
  print "Useage:   ./script dirname"
  sys.exit()



for filename in os.listdir(sys.argv[1]):
  if filename.endswith('.txt'):
    tmp, check, change = '', False, False
    for i in open(filename):
      if i.startswith('/*') and i.strip().endswith('*/'):
        continue
      elif i.startswith('/*'):
        check = True
       
      if check:
        if i.strip().endswith('*/'):
          check = False
      else:
        change = True
        tmp += i
    
    if change:
      with open(filename, 'w') as f:
        f.write(tmp)