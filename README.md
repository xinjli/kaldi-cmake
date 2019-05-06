# kaldi-cmake

This is a simple project to create CMakeLists.txt for kaldi on Linux.
A description of this project is [here](https://www.xinjianl.com/blog/2019/04/23/develop-cmake-for-kaldi/)

I did this to debug kaldi with Clion on Linux.
To make it work on OSX or Windows, you probably need to modify rules based on the kaldi.mk file in your own environment.
I assume the blas library is configured with ATLAS, so my default setup is ATLAS in this project.
To enable other library such as MKL, you need to replace ATLAS configures with other configures in cmake.py. 

## How to use

After following instructions here, you will have separate CMakeLists.txt for each corresponding Makefile in kaldi/src

* clone kaldi
* configure and install everything you need under kaldi/tools
* configure with --shared option in your kaldi/src (static option should also work, but you need to modify cmake.py)
* modify paths in cmake.py 
* python cmake.py
