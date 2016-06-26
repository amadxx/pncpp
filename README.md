# gxxtypes
Simple wrapper (based on ctypes) for C++ shared librares compiled by GCC.

See [wiki](https://github.com/amadxx/gxxtypes/wiki) for more information.

# Overview 

## Wrapping a C++ class exapmle

C++ code:
    
    // MyClass.h
    class MyClass
    {
        MyClass();
        int foo(short);
        ~MyClass();
    };

    // MyClass.cpp
    MyClass::MyClass()
    {
    }

    int foo(short x)
    {
        return x*3;
    }

    MyClass::~MyClass()
    {
    }

Python wrapper:

    from gxxtypes import *
    
    cxx_struct(virtual=False)
    class MyClass:

        def __init__():
            super(MyClass, self).__init__()

        @cxx_constructor()
        def construct():
            pass

        @cxx_method(t_int, t_short)
        def foo(x):
            pass

        @cxx_destructor()
        def destruct():
            pass
