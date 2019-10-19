import sys
from pathlib import Path

DOUBLE_PRECISION = 0

# kaldi root
kaldi_root = 'your-kaldi-root-path'

# variables to openfst (change them to your path in kaldi.mk)
OPENFSTINC = 'your OPENFSTINC defined in kaldi.mk'
OPENFSTLIBS = 'your OPENFSTLIBS *so* in kaldi.mk'

# variables to atlas (change them to your path in kaldi.mk)
ATLASINC = 'your ATLASINC defined in kaldi.mk'
ATLASLIBS = 'your ATLASLIBS *so* in kaldi.mk'

dependency_libs = (OPENFSTLIBS +' ' + ATLASLIBS).split()

def generate_cmake(makefile_path, cmake_path):
    """
    This is to parse Makefile under each subdirectory to generate corresponding CMakeLists.txt

    :param makefile_path: path to Makefile
    :param cmake_path: path to CMakeLists.txt
    :return:
    """

    makefile = open(str(makefile_path), 'r')

    cmake = open(cmake_path, 'w')

    print("Converting ", makefile_path, " --> ", cmake_path)

    ############################################################################## 
    # Step 1: Parsing Makefile
    #
    # This step is to parse makefile into libname, bin_files and obj_files
    # each of them are corresponding to the library name, executable/test binary, 
    # object file respectively
    ############################################################################## 

    bin_files = []
    obj_files = []
    libname = None

    # this is to enable atlas and openfst dependency
    addlibs = [lib for lib in dependency_libs]

    # this is to enable pthread flags
    addlibs.append("${CMAKE_THREAD_LIBS_INIT}")

    # denote current mode: bin, obj, libname or addlibs
    mode = "mode"

    # if current line finish with \, then next line will continue to use the same mode
    mode_continous = False

    # parse contents in makefile
    for line in makefile:

        line = line.strip()

        # skip comments
        if line.startswith("#"):
            continue
        else:
            line = line.split('#')[0]

        elems = []

        if mode_continous:
            elems = line.split()

            # check whether the mode is continuing
            if elems[-1] != '\\':
                mode_continous = False

        else:
            # decide which mode is now and split line into elems
            if line.startswith("TESTFILES") or line.startswith("BINFILES"):
                mode = "bin"
                elems = line.split()[2:]
            elif line.startswith("OBJFILES"):
                # delete .o extension
                mode = "obj"
                elems = line.split()[2:]

            elif line.startswith("LIBNAME"):
                mode = "libname"
                elems = line.split()[2:]
            elif line.startswith("ADDLIBS"):
                mode = "addlibs"
                elems = line.split()[2:]
            else:
                mode = "None"
                elems = line.split()

        # no essential component in this line
        if len(elems) == 0 or mode == "None":
            continue

        # remove the new line symbol if necessary
        if elems[-1] == '\\':
            elems = elems[:-1]
            mode_continous = True

        # remove empty fields after split

        # update for each mode
        if mode == "bin":
            bin_files.extend(elems)

        elif mode == 'obj':
            # delete .o extension and ignore cu-kernels.cu / chain-kernels.cu
            obj_files.extend([obj[:-2] for obj in elems if len(obj) > 2 and obj != 'cu-kernels.o' and obj != 'chain-kernels.o'])

        elif mode == 'libname':
            assert len(elems) == 1
            libname = elems[0]

        elif mode == 'addlibs':

            # clean paths
            for relative_path in elems:
                path = Path(relative_path)
                addlibs.append(path.stem)

        # clear current mode
        if not mode_continous:
            mode = "None"

    # debug
    print("libname: ", libname)
    print("addlibs: ", addlibs)
    print("bin: ", bin_files)
    print("obj    : ", obj_files)

    ############################################################################## 
    # Step 2: CMakeLists.txt generation
    # 
    # Makefile parsing done
    # start generate CMakeLists.txt here with roughly following rules:
    # 
    # - libname, obj_files -> add_library
    # - addlibs            -> target_link_libraries
    # - bin_files          -> add_executable 
    ############################################################################## 

    # ensure all bins are generated under the same directory
    # this is to keep compatibility with original kaldi project
    cmake.write('set(EXECUTABLE_OUTPUT_PATH "${CMAKE_CURRENT_SOURCE_DIR}")\n\n')

    # generate library rules if libname is provided
    if libname:
        cmake.write('add_library('+libname+' '+'.cc '.join(obj_files)+'.cc)\n\n')

        for addlib in addlibs:
            cmake.write("target_link_libraries("+libname+" "+addlib+")\n")

    # generate bins rules
    parent_name = makefile_path.parent.name

    for bin_file in bin_files:

        # three nnet are conflicting, add parent name to prefix to prevent this issue
        if bin_file.startswith("nnet"):
            exe_file = parent_name +'-' + bin_file
        else:
            exe_file = bin_file

        cmake.write("add_executable("+exe_file+" "+bin_file+".cc)\n")

        # link libname if exists
        if libname:
            cmake.write("target_link_libraries("+exe_file+" "+libname+")\n")
        else:
            # link external libraries
            for addlib in addlibs:
                cmake.write("target_link_libraries("+exe_file+" "+addlib+")\n")


    print("-"*80)

    cmake.close()

if __name__ == '__main__':

    src_dir = Path(kaldi_root) / 'src'

    # directories we do not want to generate CMakeLists.txt
    exclude_dirs = set(["doc", "gst-plugin", "makefiles", ".git", "probe", "tfrnnlm", "tfrnnlmbin", "online", "onlinebin", "cudadecoder", "cudadecoderbin"])

    kaldi_cmake = open(kaldi_root + '/CMakeLists.txt', 'w')

    # write project header
    kaldi_cmake.write("cmake_minimum_required (VERSION 2.8)\n\nproject (kaldi)\n\n\ninclude_directories(src)\n\n")

    # write kaldi flags
    kaldi_cmake.write("find_package( Threads )\n")
    kaldi_cmake.write("add_compile_definitions(HAVE_CXXABI_H)\n")
    kaldi_cmake.write("add_compile_definitions(HAVE_EXECINFO_H=1)\n")
    kaldi_cmake.write("add_compile_definitions(KALDI_DOUBLEPRECISION=0)\n")    
    kaldi_cmake.write("set (CMAKE_CXX_STANDARD 11)\n")

    # write cmake dependency to atlas
    kaldi_cmake.write("add_compile_definitions(HAVE_ATLAS)\n\ninclude_directories("+ATLASINC+")\n\n")
    kaldi_cmake.write("include_directories("+OPENFSTINC+")\n\n")

    # process subdirectory to generate cmakelists.txt iteratively
    for sub_dir in src_dir.iterdir():

        # skip execluded dirs
        if str(sub_dir.name) in exclude_dirs:
            continue
        makefile_path = sub_dir / 'Makefile'
        cmake_path = sub_dir / 'CMakeLists.txt'

        if makefile_path.exists():
            generate_cmake(makefile_path, cmake_path)
            kaldi_cmake.write("add_subdirectory("+str(sub_dir)+")\n")

    kaldi_cmake.close()


