# kaldi-cmake

This is a simple project to create CMakeLists.txt for kaldi on Linux.
A description of this project is [here](https://www.xinjianl.com/blog/2019/04/23/develop-cmake-for-kaldi/)

I did this to debug kaldi with Clion on Linux. To make it work on OSX or Windows, you probably need to modify rules based on the kaldi.mk file in your own environment.

## Tutorial
After following instructions here, you will have separate CMakeLists.txt for each corresponding Makefile in kaldi/src.

### Prepare
First, clone kaldi from github. 

Then configure and install everything you need under kaldi/tools. (in particular, openfst lib should be built here)

Next, configure with --shared option in your kaldi/src (static option should also work, but you need to modify cmake.py)

Depending on your blas libraries, you want to choose either MKL option or ATLAS option. 
Other BLAS options are not available yet but I guess can be implemented in a similar way.

### (Option 1) MKL
Fix following paths in `cmake-mkl.py`
* kaldi-root: your path to kaldi-root
* OPENFSTINC: your path to openfst's include path. usually kaldi-root/tools/openfst-(version)/include'
* OPENFSTLIBS: your path to openfst's shared library path. usually kaldi-root/tools/openfst-(version)/lib/libfst.so
* ATLASINC: your path to atlas include path. check this path in your kaldi-root/src/kaldi.mk
* ATLASLIBS: your path to atlas libraries. check this path in your kaldi-root/src/kaldi.mk

```bash
 python cmake-mkl.py
```

### (Option 2) ATLAS
Fix following paths in `cmake-atlas.py` 
* kaldi-root: your path to kaldi-root
* OPENFSTINC: your path to openfst's include path. usually kaldi-root/tools/openfst-(version)/include'
* OPENFSTLIBS: your path to openfst's shared library path. usually kaldi-root/tools/openfst-(version)/lib/libfst.so
* MKLINC:  your path to MKL include path. usually ${MKLROOT}/include where MKLROOT is defined in your kaldi-root/src/kaldi.mk
* MKLLIBS: your path to MKL libraries. Those are not explicitly listed in kaldi.mk but can be guessed from compiler's flag. Check MKL_STA_SEQ/MKL_STA_MUL/MKL_DYN_SEQ/MKL_DYN_MUL in kaldi.mk to find all your dependencies.

```bash
 python cmake-atlas.py
```

### Cuda support
As you might notice in the cmake script, I disabled all cuda related directories. If you want to use cuda as well, you might want to try following first 

Step 1: First change project line in cmake.py to the following style.
```
# change project line to support cuda
project (kaldi LANGUAGES CUDA CXX)
```

Step 2: Then add CUDACXX to your environment variable. You can add this variable to clion's settings directly (build, execution, deployment/cmake/environment)
```
# change following path to your nvcc path. The default path is the following one I guess
CUDACXX=/usr/local/cuda/bin/nvcc
```

### Debug
Sometimes cmake might fail due to some errors unfortunately. 
In this case, you cannot simply rerun cmake python script again as the first cmake has already rewrite all Makefiles which our script depends on  

If you want to rerun this python script to generate CMakeLists.txt again. Make sure you restore all original Makefiles before rerunning.

```bash
# restore all original Makefiles to rerun cmake script 
find kaldiroot/src/ -name Makefile -exec git checkout {} \;
```

