## cpp_inspector

This repository is under construction.
C++ coding style checker based on clang AST.
Most rules are based on Google C++ Coding style (https://google.github.io/styleguide/cppguide.html).

#### Feature

- Class
- - Class name should be camel case.
- - Data member should be private.
- - Class methods should be named like `YourClass`, excepts getter/setter.

- Variables
- - Variables which are assigned once should be `const`.
- - Variables which are assigned once and literal is assigned should be `constexpr`.
- - Local Variables should be named like `local_variable`.
- - Class Variables should be named like `class_variable_`.
- - Disallow class type global variables.

- Functions
- - Functions should be named like `YourFucntion`.
- - Reference arguments should be `const`.
- - Output arguments should be located last.

- Other
- - Disallow cstyle cast.
- - Disallow sizeof(datatype).
- - Iteretor should be increment by `++iter`, not `iter++`.
- - Raw pointers not should be allocated by new. You should use `std::unique_ptr` or other smart pointer.


#### Install

```
git clone https://github.com/fukatani/cpp_inspector.git
```

#### Example

```
cd cpp_inspector
python3 ./cpp_inspector/cpp_inspector.py /your_cpp_code.cpp

>>> line 11: Data member name should end with '_' https://google.github.io/styleguide/cppguide.html#Variable_Names
>>> line 34: Use C++ style cast 'static_cast<int>' instead of C style cast '(int)' ) https://google.github.io/styleguide/cppguide.html#Casting
>>> line 44: Prefer sizeof(varname) to sizeof(type) https://google.github.io/styleguide/cppguide.html#sizeof
>>> line 8: Data member should be private https://google.github.io/styleguide/cppguide.html#Access_Control
>>> line 14: Class name should be camel case https://google.github.io/styleguide/cppguide.html#Type_Names
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
cmake -G "Unix Makefiles" ../llvm
make
```

Also you need set PYTHONPATH.

```
export PYTHONPATH=$PYTHONPATH:/path/to/clang/python
```

