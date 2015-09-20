#!/usr/bin/python

'''
This is a sample build script to show how to write cpp rules
that cppbuild can use to generate Makefile.
'''

from defs import *


cpp_binary(
  name = 'hello',
  srcs = [ 'hello.cpp' ],
)
