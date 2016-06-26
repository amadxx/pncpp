# gxxtypes
Simple wrapper (based on ctypes) for C++ shared librares compiled by GCC 

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

## Built-in types
<table>
<tr><th>Type</th><th>Representation</th></tr>
<tr><td>void</td><td>t_void</td></tr>
<tr><td>void*</td><td>t_void.ptr()</td></tr>
<tr><td>char</td><td>t_bool</td></tr>
<tr><td>char*</td><td>t_bool.ptr()</td></tr>
<tr><td>char&</td><td>t_bool.ref()</td></tr>
<tr><td>const char*</td><td>t_bool.const().ptr()</td></tr>
<tr><td>const char&</td><td>t_bool.const().ref()</td></tr>
<tr><td>signed char</td><td>t_signed_char</td></tr>
<tr><td>unsigned char</td><td>t_unsigned_char</td></tr>
<tr><td>short</td><td>t_short</td></tr>
<tr><td>unsigned short</td><td>t_unsigned_short</td></tr>
<tr><td>int</td><td>t_int</td></tr>
<tr><td>unsigned int</td><td>t_unsigned_int</td></tr>

<tr><td>long</td><td>t_long</td></tr>
<tr><td>unsigned long</td><td>t_unsigned_long</td></tr>

<tr><td>long long</td><td>t_long_long</td></tr>
<tr><td>unsigned long long</td><td>t_unsigned_long_long</td></tr>

</table>
