'''
This is a sample build script to show how to write cpp rules
that cppbuild can use to generate Makefile.
'''

from defs import *

cpp_library(
  name = 'hello_lib.a',
  srcs = [
           'Foo.cpp',
         ]
)


cpp_binary(
  name = 'hello',
  deps = [
           'build:hello_lib.a',
         ],
)
