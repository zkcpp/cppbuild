'''
  cppbuild - an automatic make file generating script.
'''

import os
import imp
import sys
import atexit
import os.path


'''global variables'''

fd = None
inited = False
dependency_name = None
entry_relative_dir = None
current_relative_dir = None
output_dir_prefix = '_bin'

# Make sure that a rule only appears once
rules = set()

# all test cases
tests = []

build_all = []


'''helper functions'''

def open_file():
  '''Open the single Makefile'''

  global fd
  fname = os.getcwd() + '/Makefile'
  fd = open(fname, 'w+')


def output_global_symbols():

  s = '''#Automatically generated by a python script


AR=/usr/bin/ar crT  
CC=/usr/bin/g++-4.9
CFLAGS=-I. -std=c++1y -g\
 -Wall\
 -Wno-sign-compare\
 -Wno-return-type\
 -Wno-unused-result\
 -fno-strict-aliasing\
 -Werror


phony:
	echo 'nothing to build'

clean:
	find . -name "*.pyc" | xargs -r rm && rm -rf _bin/*

'''

  fd.write(s)


def make_output_dir(relative_path):
  return '/'.join([output_dir_prefix, relative_path])


def print_build_all():
  if (build_all):
    fd.write('\nall: ' + ' '.join(build_all) + '\n\t\n\n')

def print_test_all():
  global tests
  if len(tests) > 0:
    init()

    srcs = set()
    deps = set()
    cflags = set() 
    linkopt = set()

    for x in tests:
      if 'srcs' in x and x['srcs'] is not None:
        for y in x['srcs']:
          srcs.add(y)
      if 'deps' in x and x['deps'] is not None:
        for y in x['deps']:
          deps.add(y)
      if 'linkopt' in x and x['linkopt'] is not None:
        for y in x['linkopt']:
          linkopt.add(y)

    output_linker_line(
      '\t$(CC) -o ', 'testall', list(srcs), list(deps), list(linkopt))

    if len(srcs) > 0:
      for a in list(srcs):
        output_cc_line(a, list(cflags))


def init():
  global inited
  global entry_relative_dir
  global current_relative_dir

  if not inited:
    open_file()
    output_global_symbols()
    sys.path.append(os.getcwd())
    entry_relative_dir = sys.argv[0].rsplit('/', 1)[0]
    current_relative_dir = entry_relative_dir
    atexit.register(print_test_all)
    atexit.register(print_build_all)
    inited = True


def output_cc_line(source_name, cflags):

  '''will throw if source does not have two components'''
  (base, postfix) = source_name.rsplit('.', 1)

  if cflags is not None:
    cfstr = ' '.join(cflags)
  else:
    cfstr = ''

  target = make_output_dir(current_relative_dir + '/' + base + '.o')

  srcfile = current_relative_dir + '/' + source_name
  srcheader = current_relative_dir + '/' + base + '.h'

  global rules
  if target in rules:
    return

  rules.add(target)

  fd.write('\n' + target + ': ' + srcfile)

  #add header file as dependency if it exists
  if (os.path.isfile(srcheader)):
    fd.write(' ' + srcheader)

  fd.write('\n\t' + 'mkdir -p ' + make_output_dir(current_relative_dir) +
    ' && $(CC) -o ' + target + ' -c $(CFLAGS) ' + cfstr + ' ' +
    srcfile + '\n')


def output_linker_line(lead_str, name, srcs, deps, linkopt):

  objs = []
  if srcs is not None:
    for s in srcs:
      (base, postfix) = s.rsplit('.', 1)
      target = make_output_dir(current_relative_dir + '/' + base + '.o')
      objs.append(target)

  objstr = ' '.join(objs)

  if linkopt is not None:
    loptstr = ' '.join(linkopt)
  else:
    loptstr = ''

  depstr = ''
  depstr_list = []
  relative_str_list = []

  if deps is not None:
    for d in deps:
      (path, libname) = d.rsplit(':', 1)
      depstr_list.append(make_output_dir(path + '/' + libname))
      relative_str_list.append(make_output_dir(path + '/' + libname))

  depstr = ' '.join(depstr_list)

  fullname = make_output_dir(current_relative_dir + '/' + name)
  global rules
  if fullname in rules:
    return
  rules.add(fullname)
  fd.write(fullname + ': ' + objstr + ' ' + ' '.join(relative_str_list) + '\n')
  fd.write('\tmkdir -p ' + make_output_dir(current_relative_dir) + ' && ' +
    ' '.join([lead_str, fullname, objstr, depstr, loptstr, '\n\n']))


def add_dependency(dep):
  (base, libname) = dep.rsplit(':', 1)
  '''if this is target, do not reload the module'''
  if base == entry_relative_dir:
    return

  mname = '.'.join(base.split('/'))
  fname = os.getcwd() + '/' + base + '/build.py'
  global dependency_name
  global current_relative_dir
  saved_current_relative_dir = current_relative_dir
  saved_name = dependency_name
  current_relative_dir = base
  dependency_name = libname
  m = imp.load_source(mname, fname)
  dependency_name = saved_name
  current_relative_dir = saved_current_relative_dir


'''definition functions'''

def cpp_library(
  name = '',
  srcs = None,
  deps = None,
  cflags = None,
  linkopt = None):
  '''defines how to specify a library rule'''

  init()

  if dependency_name is not None:
    if dependency_name != name:
      return
  else:
    global build_all
    fullname = make_output_dir(current_relative_dir + '/' + name)
    build_all.append(fullname)

  if deps is not None:
    for d in deps:
      add_dependency(d)

  output_linker_line('\t$(AR) ', name, srcs, deps, linkopt)
  if srcs != None:
    for a in srcs:
      output_cc_line(a, cflags)


def cpp_binary(
  name = '',
  srcs = None,
  deps = None,
  cflags = None,
  linkopt = None):
  '''defines how to specify a binary rule'''

  init()

  if dependency_name is not None:
    if dependency_name != name:
      return

  if deps is not None:
    for d in deps:
      add_dependency(d)

  output_linker_line('\t$(CC) -o ', name, srcs, deps, linkopt)
  if srcs != None:
    for a in srcs:
      output_cc_line(a, cflags)


def cpp_unittest(
  name = '',
  srcs = None,
  deps = None,
  cflags = None,
  linkopt = None):
  '''define unit test rule'''

  init()

  global tests
  tests.append({
    'srcs': srcs,
    'deps': deps,
    'cflags': cflags,
    'linkopt': linkopt
  })

  cpp_binary(name, srcs, deps, cflags, linkopt)

