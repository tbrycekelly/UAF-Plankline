#########################################################
#  configure.ac
#
#  Copyright © 2021 Oregon State University
#
#  Moritz S. Schmid
#  Dominic W. Daprano
#  Kyler M. Jacobson
#  Christopher M. Sullivan
#  Christian Briseño-Avena
#  Jessica Y. Luo
#  Robert K. Cowen
#
#  Hatfield Marine Science Center
#  Center for Genome Research and Biocomputing
#  Oregon State University
#  Corvallis, OR 97331
#
#  This program is distributed WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  This program is distributed under the 
#  GNU GPL v 2.0 or later license.
#
#  Any User wishing to make commercial use of the Software must contact the authors 
#  or Oregon State University directly to arrange an appropriate license.
#  Commercial use includes (1) use of the software for commercial purposes, including 
#  integrating or incorporating all or part of the source code into a product 
#  for sale or license by, or on behalf of, User to third parties, or (2) distribution 
#  of the binary or source code to third parties for use with a commercial 
#  product sold or licensed by, or on behalf of, User.
# 
#  CITE AS:
# 
#  Schmid MS, Daprano D, Jacobson KM, Sullivan CM, Briseño-Avena C, Luo JY, Cowen RK. 2021.
#  A Convolutional Neural Network based high-throughput image 
#  classification pipeline - code and documentation to process
#  plankton underwater imagery using local HPC infrastructure 
#  and NSF’s XSEDE. [Software]. Zenodo. 
#  http://dx.doi.org/10.5281/zenodo.4641158
#
#########################################################

AC_INIT
AC_CONFIG_SRCDIR([configure.ac])
## ----------------------- ##
## 1. Language selection.  ##
## ----------------------- ##


# AC_LANG(Python)
# ---------------
AC_LANG_DEFINE([Python], [py], [PY], [PYTHON], [],
[ac_ext=py
ac_compile='chmod +x conftest.$ac_ext >&AS_MESSAGE_LOG_FD'
ac_link='chmod +x conftest.$ac_ext && cp conftest.$ac_ext conftest >&AS_MESSAGE_LOG_FD'
])


# AC_LANG_PYTHON
# --------------
AU_DEFUN([AC_LANG_PYTHON], [AC_LANG(Python)])


## ----------------------- ##
## 2. Producing programs.  ##
## ----------------------- ##


# AC_LANG_PROGRAM(Python)([PROLOGUE], [BODY])
# -------------------------------------------
m4_define([AC_LANG_PROGRAM(Python)], [dnl
@%:@!$PYTHON
$1
m4_if([$2], [], [], [dnl
if __name__ == '__main__':
$2])])


# _AC_LANG_IO_PROGRAM(Python)
# ---------------------------
# Produce source that performs I/O.
m4_define([_AC_LANG_IO_PROGRAM(Python)],
[AC_LANG_PROGRAM([dnl
import sys
try:
    h = open('conftest.out')
except:
    sys.exit(1)
else:
    close(h)
    sys.exit(0)
], [])])


# _AC_LANG_CALL(Python)([PROLOGUE], [FUNCTION])
# ---------------------
# Produce source that calls FUNCTION
m4_define([_AC_LANG_CALL(Python)],
[AC_LANG_PROGRAM([$1], [$2])])


## -------------------------------------------- ##
## 3. Looking for Compilers and Interpreters.   ##
## -------------------------------------------- ##


AC_DEFUN([AC_LANG_COMPILER(Python)],
[AC_REQUIRE([PC_PROG_PYTHON])])


# PC_INIT([MIN-VERSION], [MAX-VERSION]) 
# -----------------------------
# Initialize pyconfigure, finding a Python interpreter with a given
# minimum and/or maximum version. 
AC_DEFUN([PC_INIT],
[PC_PROG_PYTHON([], [$1], [$2])
dnl If we found something, do a sanity check that the interpreter really
dnl has the version its name would suggest.
m4_ifval([PYTHON],
        [PC_PYTHON_VERIFY_VERSION([>=], [pc_min_ver], [],
                  [AC_MSG_FAILURE([No compatible Python interpreter found. If you're sure that you have one, try setting the PYTHON environment variable to the location of the interpreter.])])])
m4_ifval([PYTHON],
        [PC_PYTHON_VERIFY_VERSION([<=], [pc_max_ver], [],
                  [AC_MSG_FAILURE([No compatible Python interpreter found. If you're sure that you have one, try setting the PYTHON environment variable to the location of the interpreter.])])])
])# PC_INIT

# PC_PROG_PYTHON([PROG-TO-CHECK-FOR], [MIN-VERSION], [MAX-VERSION])
# ---------------------------------
# Find a Python interpreter.  Python versions prior to 2.0 are not
# supported. (2.0 was released on October 16, 2000).
AC_DEFUN_ONCE([PC_PROG_PYTHON],
[AC_ARG_VAR([PYTHON], [the Python interpreter])
dnl The default minimum version is 2.0
m4_define_default([pc_min_ver], m4_ifval([$2], [$2], [2.0]))
dnl The default maximum version is 3.3
m4_define_default([pc_max_ver], m4_ifval([$3], [$3], [4.0]))
dnl Build up a list of possible interpreter names. 
m4_define_default([_PC_PYTHON_INTERPRETER_LIST],
    [[python] \
dnl If we want some Python 3 versions (max version >= 3.0), 
dnl also search for "python3"
     m4_if(m4_version_compare(pc_max_ver, [2.9]), [1], [python3], []) \
dnl If we want some Python 2 versions (min version <= 2.7),
dnl also search for "python2".
     m4_if(m4_version_compare(pc_min_ver, [2.8]), [-1], [python2], []) \
dnl Construct a comma-separated list of interpreter names (python2.6, 
dnl python2.7, etc). We only care about the first 3 characters of the
dnl version strings (major-dot-minor; not 
dnl major-dot-minor-dot-bugfix[-dot-whatever])
     m4_foreach([pc_ver], 
                    m4_esyscmd_s(seq -s[[", "]] -f["[[%.1f]]"] m4_substr(pc_max_ver, [0], [3]) -0.1 m4_substr(pc_min_ver, [0], [3])),
dnl Remove python2.8 and python2.9 since they will never exist
                    [m4_bmatch(pc_ver, [2.[89]], [], [python]pc_ver)])])
dnl Do the actual search at last.
m4_ifval([$1],
    [AC_PATH_PROGS(PYTHON, [$1 _PC_PYTHON_INTERPRETER_LIST])],
    [AC_PATH_PROGS(PYTHON, [_PC_PYTHON_INTERPRETER_LIST])])
])# PC_PROG_PYTHON
  

# PC_PYTHON_PROG_PYTHON_CONFIG(PROG-TO-CHECK-FOR)
# ----------------------------------------------
# Find the python-config program
AC_DEFUN([PC_PYTHON_PROG_PYTHON_CONFIG],
[AC_REQUIRE([PC_PROG_PYTHON])[]dnl
AC_ARG_VAR([PYTHON_CONFIG], [the Python-config program])
dnl python-config's binary name is normally based on the Python interpreter's
dnl binary name (i.e. python2.7 -> python2.7-config)
m4_define([_PYTHON_BASENAME], [`basename $PYTHON`])
m4_ifval([$1],
    [AC_PATH_PROGS(PYTHON_CONFIG, [$1 _PYTHON_BASENAME-config])],
    [AC_PATH_PROG(PYTHON_CONFIG, _PYTHON_BASENAME-config)])
]) # PC_PYTHON_PROG_PYTHON_CONFIG


# PC_PYTHON_VERIFY_VERSION([RELATION], [VERSION], [ACTION-IF-TRUE], [ACTION-IF-FALSE])
# ---------------------------------------------------------------------------
# Run ACTION-IF-TRUE if the Python interpreter PROG has version [RELATION] VERSION.
# i.e if RELATION is "<", check if PROG has a version number less than VERSION.
# Run ACTION-IF-FALSE otherwise.
# Specify RELATION as any mathematical comparison "<", ">", "<=", ">=", "==" or "!="
# This test uses sys.hexversion instead of the string equivalent (first
# word of sys.version), in order to cope with versions such as 2.2c1.
# This supports Python 2.0 or higher. (2.0 was released on October 16, 2000).
AC_DEFUN([PC_PYTHON_VERIFY_VERSION],
[m4_define([pc_python_safe_ver], m4_bpatsubsts($2, [\.], [_]))
AC_CACHE_CHECK([if Python $1 '$2'],
    [[pc_cv_python_req_version_]pc_python_safe_ver],
    [AC_LANG_PUSH(Python)[]dnl
     AC_RUN_IFELSE(
        [AC_LANG_PROGRAM([dnl
import sys
], [dnl
    # split strings by '.' and convert to numeric.  Append some zeros
    # because we need at least 4 digits for the hex conversion.
    # map returns an iterator in Python 3.0 and a list in 2.x
    reqver = list(map(int, '$2'.split('.'))) + [[0, 0, 0]]
    reqverhex = 0
    # xrange is not present in Python 3.0 and range returns an iterator
    for i in list(range(4)):
        reqverhex = (reqverhex << 8) + reqver[[i]]
    # the final 8 bits are "0xf0" for final versions, which are all
    # we'll test against, since it's doubtful that a released software
    # will depend on an alpha- or beta-state Python.
    reqverhex += 0xf0
    if sys.hexversion $1 reqverhex:
        sys.exit()
    else:
        sys.exit(1)
])], 
         [[pc_cv_python_req_version_]pc_python_safe_ver=yes], 
         [[pc_cv_python_req_version_]pc_python_safe_ver=no])
     AC_LANG_POP(Python)[]dnl
    ])
AS_IF([test "$[pc_cv_python_req_version_]pc_python_safe_ver" = "no"], [$4], [$3])
])# PC_PYTHON_VERIFY_VERSION


# PC_PYTHON_CHECK_VERSION
# -----------------------
# Query Python for its version number.  Getting [:3] seems to be
# the best way to do this; it's what "site.py" does in the standard
# library.
AC_DEFUN([PC_PYTHON_CHECK_VERSION],
[AC_REQUIRE([PC_PROG_PYTHON])[]dnl
AC_CACHE_CHECK([for $1 version], 
    [pc_cv_python_version],
    [AC_LANG_PUSH(Python)[]dnl
     AC_LINK_IFELSE([AC_LANG_PROGRAM([dnl
import sys
], [dnl
    sys.stdout.write(sys.version[[:3]])
])],
                   [pc_cv_python_version=`./conftest`],
                   [AC_MSG_FAILURE([failed to run Python program])])
     AC_LANG_POP(Python)[]dnl
    ])
AC_SUBST([PYTHON_VERSION], [$pc_cv_python_version])
])# PC_PYTHON_CHECK_VERSION


# PC_PYTHON_CHECK_PREFIX
# ----------------------
# Use the value of $prefix for the corresponding value of
# PYTHON_PREFIX. This is made a distinct variable so it can be
# overridden if need be.  However, general consensus is that you
# shouldn't need this ability. 
AC_DEFUN([PC_PYTHON_CHECK_PREFIX],
[AC_REQUIRE([PC_PYTHON_PROG_PYTHON_CONFIG])[]dnl
dnl Try to get it with python-config otherwise do it from within Python
AC_CACHE_CHECK([for Python prefix], [pc_cv_python_prefix],
[if test -x "$PYTHON_CONFIG"; then
    pc_cv_python_prefix=`$PYTHON_CONFIG --prefix 2>&AS_MESSAGE_LOG_FD`
else
    AC_LANG_PUSH(Python)[]dnl
    AC_LINK_IFELSE([AC_LANG_PROGRAM([dnl
import sys
], [dnl
    sys.stdout.write(sys.prefix)
])], [pc_cv_python_prefix=`./conftest`;
      if test $? != 0; then
         AC_MSG_FAILURE([could not determine Python prefix])
      fi],
      [AC_MSG_FAILURE([failed to run Python program])])
    AC_LANG_POP(Python)[]dnl
fi])
AC_SUBST([PYTHON_PREFIX], [$pc_cv_python_prefix])])


# PC_PYTHON_CHECK_EXEC_PREFIX
# --------------------------
# Like above, but for $exec_prefix
AC_DEFUN([PC_PYTHON_CHECK_EXEC_PREFIX],
[AC_REQUIRE([PC_PYTHON_PROG_PYTHON_CONFIG])[]dnl
dnl Try to get it with python-config otherwise do it from within Python
AC_CACHE_CHECK([for Python exec-prefix], [pc_cv_python_exec_prefix],
[if test -x "$PYTHON_CONFIG"; then
    pc_cv_python_exec_prefix=`$PYTHON_CONFIG --exec-prefix 2>&AS_MESSAGE_LOG_FD`
else
    AC_LANG_PUSH(Python)[]dnl
    AC_LINK_IFELSE([AC_LANG_PROGRAM([dnl
import sys
], [dnl
    sys.stdout.write(sys.exec_prefix)
])],
        [pc_cv_python_exec_prefix=`./conftest`;
         if test $? != 0; then
            AC_MSG_FAILURE([could not determine Python exec_prefix])
         fi],
         [AC_MSG_FAILURE([failed to run Python program])])
    AC_LANG_POP(Python)[]dnl
fi
])
AC_SUBST([PYTHON_EXEC_PREFIX], [$pc_cv_python_exec_prefix])])


# PC_PYTHON_CHECK_INCLUDES
# ------------------------
# Find the Python header file include flags (ie
# '-I/usr/include/python')
AC_DEFUN([PC_PYTHON_CHECK_INCLUDES],
[AC_REQUIRE([PC_PYTHON_PROG_PYTHON_CONFIG])[]dnl
dnl Try to find the headers location with python-config otherwise guess
AC_CACHE_CHECK([for Python includes], [pc_cv_python_includes],
[if test -x "$PYTHON_CONFIG"; then
    pc_cv_python_includes=`$PYTHON_CONFIG --includes 2>&AS_MESSAGE_LOG_FD`
else
    pc_cv_python_includes="[-I$includedir/$_PYTHON_BASENAME]m4_ifdef(PYTHON_ABI_FLAGS,
    PYTHON_ABI_FLAGS,)"
fi
])
AC_SUBST([PYTHON_INCLUDES], [$pc_cv_python_includes])])


# PC_PYTHON_CHECK_HEADERS([ACTION-IF-PRESENT], [ACTION-IF-ABSENT])
# -----------------------
# Check for the presence and usability of Python.h
AC_DEFUN([PC_PYTHON_CHECK_HEADERS],
[AC_REQUIRE([PC_PYTHON_CHECK_INCLUDES])[]dnl
pc_cflags_store=$CPPFLAGS
CPPFLAGS="$CFLAGS $PYTHON_INCLUDES"
AC_CHECK_HEADER([Python.h], [$1], [$2])
CPPFLAGS=$pc_cflags_store
])


# PC_PYTHON_CHECK_LIBS
# --------------------
# Find the Python lib flags (ie '-lpython')
AC_DEFUN([PC_PYTHON_CHECK_LIBS],
[AC_REQUIRE([PC_PYTHON_PROG_PYTHON_CONFIG])[]dnl
dnl Try to find the lib flags with python-config otherwise guess
AC_CACHE_CHECK([for Python libs], [pc_cv_python_libs],
[if test -x "$PYTHON_CONFIG"; then
    pc_cv_python_libs=`$PYTHON_CONFIG --libs 2>&AS_MESSAGE_LOG_FD`
else
    pc_cv_python_libs="[-l$_PYTHON_BASENAME]m4_ifdef(PYTHON_ABI_FLAGS, PYTHON_ABI_FLAGS,)"
fi
])
AC_SUBST([PYTHON_LIBS], [$pc_cv_python_libs])])


# PC_PYTHON_TEST_LIBS(LIBRARY-FUNCTION, [ACTION-IF-PRESENT], [ACTION-IF-ABSENT])
# -------------------
# Verify that the Python libs can be loaded
AC_DEFUN([PC_PYTHON_TEST_LIBS],
[AC_REQUIRE([PC_PYTHON_CHECK_LIBS])[]dnl
pc_libflags_store=$LIBS
for lflag in $PYTHON_LIBS; do
    case $lflag in
         -lpython*@:}@
        LIBS="$LIBS $lflag"
        pc_libpython=`echo $lflag | sed -e 's/^-l//'`
        ;;
         *@:}@;;
    esac
done
AC_CHECK_LIB([$pc_libpython], [$1], [$2], [$3])])


# PC_PYTHON_CHECK_CFLAGS
# ----------------------
# Find the Python CFLAGS
AC_DEFUN([PC_PYTHON_CHECK_CFLAGS],
[AC_REQUIRE([PC_PYTHON_PROG_PYTHON_CONFIG])[]dnl
dnl Try to find the CFLAGS with python-config otherwise give up
AC_CACHE_CHECK([for Python CFLAGS], [pc_cv_python_cflags],
[if test -x "$PYTHON_CONFIG"; then
    pc_cv_python_cflags=`$PYTHON_CONFIG --cflags 2>&AS_MESSAGE_LOG_FD`
else
    pc_cv_python_cflags=
fi
])
AC_SUBST([PYTHON_CFLAGS], [$pc_cv_python_cflags])])


# PC_PYTHON_CHECK_LDFLAGS
# -----------------------
# Find the Python LDFLAGS
AC_DEFUN([PC_PYTHON_CHECK_LDFLAGS],
[AC_REQUIRE([PC_PYTHON_PROG_PYTHON_CONFIG])[]dnl
dnl Try to find the LDFLAGS with python-config otherwise give up
AC_CACHE_CHECK([for Python LDFLAGS], [pc_cv_python_ldflags],
[if test -x "$PYTHON_CONFIG"; then
    pc_cv_python_ldflags=`$PYTHON_CONFIG --ldflags 2>&AS_MESSAGE_LOG_FD`
else
    pc_cv_python_ldflags=
fi
])
AC_SUBST([PYTHON_LDFLAGS], [$pc_cv_python_ldflags])])


# PC_PYTHON_CHECK_EXTENSION_SUFFIX
# --------------------------------
# Find the Python extension suffix (i.e. '.cpython-32.so')
AC_DEFUN([PC_PYTHON_CHECK_EXTENSION_SUFFIX],
[AC_REQUIRE([PC_PYTHON_PROG_PYTHON_CONFIG])[]dnl
dnl Try to find the suffix with python-config otherwise give up
AC_CACHE_CHECK([for Python extension suffix], [pc_cv_python_extension_suffix],
[if test -x "$PYTHON_CONFIG"; then
     pc_cv_python_extension_suffix=`$PYTHON_CONFIG --extension-suffix 2>&AS_MESSAGE_LOG_FD`
else
    pc_cv_python_extension_suffix=
fi
])
AC_SUBST([PYTHON_EXTENSION_SUFFIX], [$pc_cv_python_extension_suffix])])


# PC_PYTHON_CHECK_ABI_FLAGS
# -------------------------
# Find the Python ABI flags
AC_DEFUN([PC_PYTHON_CHECK_ABI_FLAGS],
[AC_REQUIRE([PC_PYTHON_PROG_PYTHON_CONFIG])[]dnl
dnl Try to find the ABI flags with python-config otherwise give up
AC_CACHE_CHECK([for Python ABI flags], [pc_cv_python_abi_flags],
[if test -x "$PYTHON_CONFIG"; then
     pc_cv_python_abi_flags=`$PYTHON_CONFIG --abiflags 2>&AS_MESSAGE_LOG_FD`
else
    pc_cv_python_abi_flags=
fi
])
AC_SUBST([PYTHON_ABI_FLAGS], [$pc_cv_python_abi_flags])])


# PC_PYTHON_CHECK_PLATFORM
# ------------------------
# At times (like when building shared libraries) you may want
# to know which OS platform Python thinks this is.
AC_DEFUN([PC_PYTHON_CHECK_PLATFORM],
[AC_REQUIRE([PC_PROG_PYTHON])[]dnl
dnl Get the platform from within Python (sys.platform)
AC_CACHE_CHECK([for Python platform], [pc_cv_python_platform],
    [AC_LANG_PUSH(Python)[]dnl
     AC_LINK_IFELSE([AC_LANG_PROGRAM([dnl
import sys
], [dnl
    sys.stdout.write(sys.platform)
])], [pc_cv_python_platform=`./conftest`;
     if test $? != 0; then
        AC_MSG_FAILURE([could not determine Python platform])
     fi],
     [AC_MSG_FAILURE([failed to run Python program])])
    AC_LANG_POP(Python)[]dnl
   ])
AC_SUBST([PYTHON_PLATFORM], [$pc_cv_python_platform])
])


# PC_PYTHON_CHECK_SITE_DIR
# ---------------------
# The directory to which new libraries are installed (i.e. the
# "site-packages" directory.
AC_DEFUN([PC_PYTHON_CHECK_SITE_DIR],
[AC_REQUIRE([PC_PROG_PYTHON])AC_REQUIRE([PC_PYTHON_CHECK_PREFIX])[]dnl
AC_CACHE_CHECK([for Python site-packages directory],
    [pc_cv_python_site_dir],
    [AC_LANG_PUSH(Python)[]dnl
    if test "x$prefix" = xNONE
     then
       pc_py_prefix=$ac_default_prefix
     else
       pc_py_prefix=$prefix
     fi
     AC_LINK_IFELSE([AC_LANG_PROGRAM([dnl
import sys
from platform import python_implementation
# sysconfig in CPython 2.7 doesn't work in virtualenv
# <https://github.com/pypa/virtualenv/issues/118>
try:
    import sysconfig
except:
    can_use_sysconfig = False
else:
    can_use_sysconfig = True
if can_use_sysconfig:
    if python_implementation() == "CPython" and sys.version[[:3]] == '2.7':
        can_use_sysconfig = False
if not can_use_sysconfig:        
    from distutils import sysconfig
    sitedir = sysconfig.get_python_lib(False, False, prefix='$pc_py_prefix')
else:
    sitedir = sysconfig.get_path('purelib', vars={'base':'$pc_py_prefix'})
], [dnl
    sys.stdout.write(sitedir)
])], [pc_cv_python_site_dir=`./conftest`],
     [AC_MSG_FAILURE([failed to run Python program])])
     AC_LANG_POP(Python)[]dnl
     case $pc_cv_python_site_dir in
     $pc_py_prefix*)
       pc__strip_prefix=`echo "$pc_py_prefix" | sed 's|.|.|g'`
       pc_cv_python_site_dir=`echo "$pc_cv_python_site_dir" | sed "s,^$pc__strip_prefix/,,"`
       ;;
     *)
       case $pc_py_prefix in
         /usr|/System*) ;;
         *)
      pc_cv_python_site_dir=lib/python$PYTHON_VERSION/site-packages
      ;;
       esac
       ;;
     esac
     ])
AC_SUBST([pythondir], [\${prefix}/$pc_cv_python_site_dir])])# PC_PYTHON_CHECK_SITE_DIR

# PC_PYTHON_SITE_PACKAGE_DIR
# --------------------------
# $PACKAGE directory under PYTHON_SITE_DIR
AC_DEFUN([PC_PYTHON_SITE_PACKAGE_DIR],
[AC_REQUIRE([PC_PYTHON_CHECK_SITE_DIR])[]dnl
AC_SUBST([pkgpythondir], [\${pythondir}/$PACKAGE_NAME])])


# PC_PYTHON_CHECK_EXEC_DIR
# ------------------------
# directory for installing python extension modules (shared libraries)
AC_DEFUN([PC_PYTHON_CHECK_EXEC_DIR],
[AC_REQUIRE([PC_PROG_PYTHON])AC_REQUIRE([PC_PYTHON_CHECK_EXEC_PREFIX])[]dnl
  AC_CACHE_CHECK([for Python extension module directory],
    [pc_cv_python_exec_dir],
    [AC_LANG_PUSH(Python)[]dnl
    if test "x$pc_cv_python_exec_prefix" = xNONE
     then
       pc_py_exec_prefix=$pc_cv_python_prefix
     else
       pc_py_exec_prefix=$pc_cv_python_exec_prefix
     fi
     AC_LINK_IFELSE([AC_LANG_PROGRAM([dnl
import sys
from platform import python_implementation
# sysconfig in CPython 2.7 doesn't work in virtualenv
# <https://github.com/pypa/virtualenv/issues/118>
try:
    import sysconfig
except:
    can_use_sysconfig = False
else:
    can_use_sysconfig = True
if can_use_sysconfig:
    if python_implementation() == "CPython" and sys.version[[:3]] == '2.7':
        can_use_sysconfig = False
if not can_use_sysconfig:        
    from distutils import sysconfig
    sitedir = sysconfig.get_python_lib(False, False, prefix='$pc_py__exec_prefix')
else:
    sitedir = sysconfig.get_path('purelib', vars={'platbase':'$pc_py_exec_prefix'})
], [dnl
    sys.stdout.write(sitedir)
])], [pc_cv_python_exec_dir=`./conftest`],
     [AC_MSG_FAILURE([failed to run Python program])])
     AC_LANG_POP(Python)[]dnl
     case $pc_cv_python_exec_dir in
     $pc_py_exec_prefix*)
       pc__strip_prefix=`echo "$pc_py_exec_prefix" | sed 's|.|.|g'`
       pc_cv_python_exec_dir=`echo "$pc_cv_python_exec_dir" | sed "s,^$pc__strip_prefix/,,"`
       ;;
     *)
       case $pc_py_exec_prefix in
         /usr|/System*) ;;
         *)
       pc_cv_python_exec_dir=lib/python$PYTHON_VERSION/site-packages
       ;;
       esac
       ;;
     esac
    ])
AC_SUBST([pyexecdir], [\${exec_prefix}/$pc_cv_python_pyexecdir])]) #PY_PYTHON_CHECK_EXEC_LIB_DIR


# PC_PYTHON_EXEC_PACKAGE_DIR
# --------------------------
# $PACKAGE directory under PYTHON_SITE_DIR
AC_DEFUN([PC_PYTHON_EXEC_PACKAGE_DIR],
[AC_REQUIRE([PC_PYTHON_CHECK_EXEC_DIR])[]dnl
AC_SUBST([pkgpyexecdir], [\${pyexecdir}/$PACKAGE_NAME])])


## -------------------------------------------- ##
## 4. Looking for specific libs & functionality ##
## -------------------------------------------- ##


# PC_PYTHON_CHECK_MODULE(LIBRARY, [ACTION-IF-FOUND], [ACTION-IF-NOT-FOUND])
# ----------------------------------------------------------------------
# Macro for checking if a Python library is installed
AC_DEFUN([PC_PYTHON_CHECK_MODULE],
[AC_REQUIRE([PC_PROG_PYTHON])[]dnl
m4_define([pc_python_safe_mod], m4_bpatsubsts($1, [\.], [_]))
AC_CACHE_CHECK([for Python '$1' library],
    [[pc_cv_python_module_]pc_python_safe_mod],
    [AC_LANG_PUSH(Python)[]dnl
     AC_RUN_IFELSE(
    [AC_LANG_PROGRAM([dnl
import sys
try:
    import $1
except:
    sys.exit(1)
else:
    sys.exit(0)
], [])],
    [[pc_cv_python_module_]pc_python_safe_mod="yes"],
    [[pc_cv_python_module_]pc_python_safe_mod="no"])
     AC_LANG_POP(Python)[]dnl
    ])
AS_IF([test "$[pc_cv_python_module_]pc_python_safe_mod" = "no"], [$3], [$2])
])# PC_PYTHON_CHECK_MODULE


# PC_PYTHON_CHECK_FUNC([LIBRARY], FUNCTION, ARGS, [ACTION-IF-FOUND], [ACTION-IF-NOT-FOUND])
# ---------------------------------------------------------------------------------------
# Check to see if a given function call, optionally from a module, can
# be successfully called
AC_DEFUN([PC_PYTHON_CHECK_FUNC],
[AC_REQUIRE([PC_PROG_PYTHON])[]dnl
m4_define([pc_python_safe_mod], m4_bpatsubsts($1, [\.], [_]))
AC_CACHE_CHECK([for Python m4_ifnblank($1, '$1.$2()', '$2()') function],
    [[pc_cv_python_func_]pc_python_safe_mod[_$2]],
    [AC_LANG_PUSH(Python)[]dnl
     AC_RUN_IFELSE(
    [AC_LANG_PROGRAM([dnl
import sys
m4_ifnblank([$1], [dnl
try:
    import $1
except:
    sys.exit(1)
], [])], 
[
m4_ifnblank([$1], [
    try:
        $1.$2($3)], [
    try:
        $2($3)])
    except:
        sys.exit(1)
    else:
        sys.exit(0)
])],
    [[pc_cv_python_func_]pc_python_safe_mod[_$2]="yes"],
    [[pc_cv_python_func_]pc_python_safe_mod[_$2]="no"])
     AC_LANG_POP(Python)[]dnl
    ])
AS_IF([test "$[pc_cv_python_func_]pc_python_safe_mod[_$2]" = "no"], [$5], [$4])
])# PC_PYTHON_CHECK_FUNC


# Check python version 3.4
AM_PATH_PYTHON([3.4])

#############################
# Check for python modules
#############################
PC_PYTHON_CHECK_MODULE([os], [], AC_MSG_ERROR([Module os is not installed please install before continuing]))
PC_PYTHON_CHECK_MODULE([sys], [], AC_MSG_ERROR([Module sys is not installed please install before continuing]))
PC_PYTHON_CHECK_MODULE([subprocess], [], AC_MSG_ERROR([Module subprocess is not installed please install before continuing]))
PC_PYTHON_CHECK_MODULE([fnmatch], [], AC_MSG_ERROR([Module fnmatch is not installed please install before continuing]))
PC_PYTHON_CHECK_MODULE([datetime], [], AC_MSG_ERROR([Module datetime is not installed please install before continuing]))
PC_PYTHON_CHECK_MODULE([configparser], [], AC_MSG_ERROR([Module configparser is not installed please install before continuing]))
PC_PYTHON_CHECK_MODULE([shutil], [], AC_MSG_ERROR([Module shutil is not installed please install before continuing]))
PC_PYTHON_CHECK_MODULE([cv2], [], AC_MSG_ERROR([Module cv2 is was not found please install or add to your pythonpath before continuing]))
PC_PYTHON_CHECK_MODULE([skimage], [], AC_MSG_ERROR([Module skimage is was not found please install or add to your pythonpath before continuing]))
PC_PYTHON_CHECK_MODULE([glob], [], AC_MSG_ERROR([Module glob is was not found please install or add to your pythonpath before continuing]))
PC_PYTHON_CHECK_MODULE([csv], [], AC_MSG_ERROR([Module csv is was not found please install or add to your pythonpath before continuing]))
PC_PYTHON_CHECK_MODULE([math], [], AC_MSG_ERROR([Module math is was not found please install or add to your pythonpath before continuing]))
PC_PYTHON_CHECK_MODULE([time], [], AC_MSG_ERROR([Module time is was not found please install or add to your pythonpath before continuing]))
PC_PYTHON_CHECK_MODULE([multiprocessing], [], AC_MSG_ERROR([Module multiprocessing is was not found please install or add to your pythonpath before continuing]))
PC_PYTHON_CHECK_MODULE([signal], [], AC_MSG_ERROR([Module signal is was not found please install or add to your pythonpath before continuing]))
PC_PYTHON_CHECK_MODULE([numpy], [], AC_MSG_ERROR([Module numpy is was not found please install or add to your pythonpath before continuing]))
PC_PYTHON_CHECK_MODULE([tarfile], [], AC_MSG_ERROR([Module tarfile is was not found please install or add to your pythonpath before continuing]))
PC_PYTHON_CHECK_MODULE([argparse], [], AC_MSG_ERROR([Module argparse is was not found please install or add to your pythonpath before continuing]))

#############################
# Checking for commands
#############################
AC_CHECK_PROG(CP, cp, yes)
if test x"$CP" != x"yes" ; then
    AC_MSG_ERROR([Please install cp command before continuing.])
fi

AC_CHECK_PROG(MKDIR, mkdir, yes)
if test x"$MKDIR" != x"yes" ; then
    AC_MSG_ERROR([Please install mkdir before continuing.])
fi

AC_CHECK_PROG(RM, rm, yes)
if test x"$RM" != x"yes" ; then
    AC_MSG_ERROR([Please install rm before continuing.])
fi

AC_CHECK_PROG(BASHPROG,bash,yes)
if test x"$BASHPROG" != x"yes" ; then
    AC_MSG_ERROR([Please install bash before continuing.])
fi

AC_CHECK_PROG(TAR,tar,yes)
if test x"$TAR" != x"yes" ; then
    AC_MSG_ERROR([Please install tar before continuing.])
fi

AC_CHECK_PROG(RSYNC,rsync,yes)
if test x"$RSYNC" != x"yes" ; then
    AC_MSG_ERROR([Please install rsync before continuing.])
fi

AC_CHECK_PROG(SSH,ssh,yes)
if test x"$SSH" != x"yes" ; then
    AC_MSG_ERROR([Please install ssh before continuing.])
fi

AC_CHECK_PROG(NOHUP,nohup,yes)
if test x"$NOHUP" != x"yes" ; then
    AC_MSG_ERROR([Please install nohup before continuing.])
fi

AC_CHECK_PROG(TOUCH,touch,yes)
if test x"$TOUCH" != x"yes" ; then
    AC_MSG_ERROR([Please install touch before continuing.])
fi

AC_CHECK_PROG(AWK,awk,yes)
if test x"$AWK" != x"yes" ; then
    AC_MSG_ERROR([Please install awk before continuing.])
fi

AC_ARG_WITH([ppc64le],
  [AS_HELP_STRING([--with-ppc64le],
    [enable use of the ppc64le binary])],
  [ARHCITECTURE=ppc64le],
  [
AC_ARG_WITH([ppc64],
  [AS_HELP_STRING([--with-ppc64],
    [enable use of the ppc64le binary])],
  [ARHCITECTURE=ppc64le],
  [ARCHITECTURE=x86])])
AM_CONDITIONAL(X86, test "x$ARCHITECTURE" = xx86)

#############################
# Checking for libraries
#############################
AC_PATH_PROG(FFMPEG,ffmpeg,no)
AS_IF([test "$ac_cv_path_FFMPEG" == "no"], [AC_MSG_ERROR([Please install ffmpeg before continuing.])])

AC_PATH_PROG(FFPROBE,ffprobe,no)
AS_IF([test "$ac_cv_path_FFPROBE" == "no"], [AC_MSG_ERROR([Please install ffprobe before continuing.])])

AC_PATH_PROG(ISIIS_SEG_FF,isiis_seg_ff,no)
AS_IF([test "$ac_cv_path_ISIIS_SEG_FF" == "no"], [AC_MSG_ERROR([Make sure the isiis_seg_ff binary is in the PATH])])

AM_COND_IF([X86], 
[
AC_SUBST(ARCHITECTURE, x86)
AC_PATH_PROG(ISIIS_SCNN,isiis_scnn,no, [./SCNNx86])
AS_IF([test "$ac_cv_path_ISIIS_SCNN" == "no"], [AC_MSG_ERROR([Make sure the isiis_scnn binary for x86 is in the PATH or in the directory SCNNx86/])]) ],
[
AC_SUBST(ARCHITECTURE, ppc64le)
AC_PATH_PROG(ISIIS_SCNN,isiis_scnn,no, [./SCNNppc64le])
AS_IF([test "$ac_cv_path_ISIIS_SCNN" == "no"], [AC_MSG_ERROR([Make sure the isiis_scnn binary for ppc64le is in the PATH or in the directory SCNNppc64le/])]) ]
)

#############################
# Checking for libraries
#############################
CFLAGS="$CFLAGS -I/usr/include"
CXXFLAGS="$CXXFLAGS -I/usr/include"
LDFLAGS="$LDFLAGS -L/usr/lib64"
AC_LANG_PUSH([C++])
AC_CHECK_LIB([m],[main],[],[AC_MSG_ERROR([Library m not found, please install if not on system.])],[])ac_cv_lib_m=ac_cv_lib_m_main

AC_CHECK_LIB([opencv_core],[main],[],[AC_MSG_ERROR([Library opencv_core not found, please install if not on system.])],[])ac_cv_lib_opencv_core=ac_cv_lib_opencv_core_main

AC_CHECK_LIB([opencv_imgproc],[main],[],[AC_MSG_ERROR([Library opencv_imgproc not found, please install if not on system.])],[])ac_cv_lib_opencv_imgproc=ac_cv_lib_opencv_imgproc_main

AC_CHECK_LIB([opencv_highgui],[main],[],[AC_MSG_ERROR([Library opencv_highgui not found, please install if not on system.])],[])ac_cv_lib_opencv_highgui=ac_cv_lib_opencv_highgui_main

AC_CHECK_LIB([gomp],[main],[],[AC_MSG_ERROR([Library gomp not found, please install if not on system.])],[])ac_cv_lib_gomp=ac_cv_lib_gomp_main

AC_CHECK_LIB(stdc++, __atomic_flag_wait_explicit, [], [AC_MSG_ERROR([Library m not found, please install if not on system.])])
AC_CHECK_LIB([gcc_s],[main],[],[AC_MSG_ERROR([Library gcc_s not found, please install if not on system.])],[])ac_cv_lib_gcc_s=ac_cv_lib_gcc_s_main

AC_CHECK_LIB([pthread],[main],[],[AC_MSG_ERROR([Library pthread not found, please install if not on system.])],[])ac_cv_lib_pthread=ac_cv_lib_pthread_main

AC_CHECK_LIB([c],[main],[],[AC_MSG_ERROR([Library c not found, please install if not on system.])],[])ac_cv_lib_c=ac_cv_lib_c_main

AC_CHECK_LIB([cublas],[main],[],[AC_MSG_ERROR([Library cublas not found, please install if not on system.])],[])ac_cv_lib_cublas=ac_cv_lib_cublas_main

AC_CHECK_LIB([rt],[main],[],[AC_MSG_ERROR([Library rt not found, please install if not on system.])],[])ac_cv_lib_rt=ac_cv_lib_rt_main

AC_CHECK_LIB([armadillo],[main],[],[AC_MSG_ERROR([Library armadillo not found, please install if not on system.])],[])ac_cv_lib_armadillo=ac_cv_lib_armadillo_main

AC_CHECK_LIB([dl],[main],[],[AC_MSG_ERROR([Library dl not found, please install if not on system.])],[])ac_cv_lib_dl=ac_cv_lib_dl_main


# Conditionally find library for isiis_scnn binary
AM_COND_IF([X86], 
[
AC_CHECK_LIB([opencv_imgcodecs],[main],[],[AC_MSG_ERROR([Library opencv_imgcodecs not found, please install if not on system.])],[])ac_cv_lib_opencv_imgcodecs=ac_cv_lib_opencv_imgcodecs_main
 # only needed x86
], [])

AC_LANG_POP()

#############################
# Create variables and make them accessable to the configure file
#############################
AC_SUBST(PYTHON)
AC_SUBST(pythondir)
AC_SUBST(FFPROBE)
AC_SUBST(FFMPEG)
AC_SUBST(ISIIS_SCNN)

AC_CONFIG_FILES([Makefile])
AC_OUTPUT
