## cpp_inspector

This repository is under construction.
C++ coding style checker based on clang AST.
Most rules are based on Google C++ Coding style (https://google.github.io/styleguide/cppguide.html).

#### Feature

- Class
- Class name should be camel case.
- Data member should be private.
- Class methods should be named like `YourFucntion`, excepts getter/setter.

- Variables
- Variables which are assigned once should be `const`.
- Variables which are assigned once and literal is assigned should be `constexpr`.
- Local Variables should be named like `local_variable`.
- Class Variables should be named like `class_variable_`.
- Disallow class type global variables.

- Functions
- Functions should be named like `YourFucntion`.
- Reference arguments should be `const`.
- Output arguments should be located last.

- Other
- Disallow cstyle cast.
- Disallow sizeof(datatype).
- Iteretor should be increment by `++iter`, not `iter++`.
- Raw pointers not should be allocated by new. You should use `std::unique_ptr` or other smart pointer.
/グローバル変数命名規則


#### Install

```
git clone https://github.com/fukatani/cpp_inspector.git
```

#### Example

```
cd cpp_inspector
python3 ./cpp_inspector/cpp_inspector.py /your_cpp_code.cpp

>>> a
```

#### Requirements

- Python 3.4 or later
- Clang with python bindings

You can install clang python bindings as follows.

```
sudo apt-get install subversion
svn co http://llvm.org/svn/llvm-project/llvm/trunk llvm
cd llvm/tools
svn co http://llvm.org/svn/llvm-project/cfe/trunk clang
svn co http://llvm.org/svn/llvm-project/clang-tools-extra/trunk extra
cd ../..
mkdir build
cd build
cmake -G "Unix Makefiles" ..
make
```

Also you need set PYTHONPATH.

```
export PYTHONPATH=$PYTHONPATH:/path/to/clang/python
```

