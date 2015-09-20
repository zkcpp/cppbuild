# cppbuild

This is a script to generate Makefile automatically for C++ projects.

Each directory in the C++ project should have a script build.py which
defines the dependencies and build rules. A sample build.py script
is included in this package as well.

The package also includes a tutorial to show how to build a simple
project.

The first step is to create a new directory, which is "tutorial" in
this case. A simple C++ file and a build rule (build.py) is created
under this directory.

To use this package, correct PYTHONPATH environment needs to point to
the place where defs.py is (at the root directory of cppbuild).

A user usually invokes the build script from the parent dir of
tutorial directory: "python tutorial/build.py", the package will
figure out the relative directory of the project and use it as
part of the output path.

After the python script generates a Makefile at the parent dir of
the project, one can build it with command:

$ make _bin/tutorial/hello

And run it with command "_bin/tutorial/hello".
