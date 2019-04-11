# kaldi-cmake

This is a simple project to create CMakeLists.txt for kaldi on Linux.
A description of this project is [here](https://www.xinjianl.com/develop/code-kaldi/kaldi-cmake/)

I did this to debug kaldi with Clion on Linux.
To make it work on OSX or Windows, you probably need to modify rules based on kaldi.mk
I assume the blas library is configured with ATLAS and setup its shared library in this project.
To enable other library such as MKL, you need to replace ATLAS options to other options

## How to use

After following instructions, you can generate CMakeLists.txt for each corresponding Makefile in kaldi/src

* clone kaldi
* configure and install everything you need under tools
* configure shared in your src
* modify paths in cmake.py 
* python cmake.py
