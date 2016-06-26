# gxxtypes
Simple wrapper (based on ctypes) for C++ shared librares compiled by GCC.

See [wiki](https://github.com/amadxx/gxxtypes/wiki) for more information.

# Overview 

Gxxtypes allows to easily wrap C++ classes in shared libraries loaded by ctypes on Linux and Windows.

It calls methods directrly using ctypes, so anythyng should be modified in library.

GCC style name mangling is used to generate function name signature, so only libraries compiled by gcc are supported.

## Wrapping a C++ class example

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
