# gxxtypes
Simple wrapper (based on ctypes) for C++ shared librares.

See [wiki](https://github.com/amadxx/gxxtypes/wiki) for more information.

# Overview 

Gxxtypes allows to easily wrap C++ classes in shared libraries loaded by ctypes on Linux and Windows.

It calls methods directrly using ctypes, so nothing should be modified in library.

GCC style name mangling is used to generate function name signature, so only libraries compiled by gcc are supported.

## Wrapping a C++ class example

C++ code:
    
    #include <iostream>
    
    using namespace std;
    
    class HelloWorld
    {
        public:
            const char* text;
            HelloWorld(const char* text);
            void print_text(int some_int);
            ~HelloWorld();
    };
    
    HelloWorld::HelloWorld(const char* text):text(text)
    {
        cout<<"HelloWorld::HelloWorld("<<this<<")"<<endl;
    }
    
    void HelloWorld::print_text(int some_int)
    {
        cout<<"print_text: "<<text<<endl;
        cout<<"some_int: "<<some_int<<endl;
    }
    
    HelloWorld::~HelloWorld()
    {
        cout<<"HelloWorld::~HelloWorld("<<this<<")"<<endl;
    }

Python wrapper:

    from gxxtypes import *
    import ctypes
    
    @cxx_struct(virtual=False)
    class HelloWorld(CXXStruct):
    
        _fields_ = [("text", ctypes.c_char_p)]
    
        def __init__(self, text):
            super(HelloWorld, self).__init__()
            self.construct(text)
    
        @cxx_constructor(t_char.const().ptr())
        def construct(self, text):
            pass
    
        @cxx_method(t_void, t_int)
        def print_text(self, some_int):
            pass
    
        @cxx_destructor()
        def destroy(self):
            pass

Usage:

    if __name__ == '__main__':

        hw_lib = ctypes.CDLL("hw.dll")  # or 'hw.so'
    
        HelloWorld.link_with(hw_lib)
    
        x = HelloWorld("Hello, world!")
        x.print_text(42)
        x.text = "Other text from python"
        x.print_text(777)
    
        x.destroy()

Output:

    HelloWorld::HelloWorld(0x24f0090)
    print_text: Hello, world!
    some_int: 42
    print_text: Other text from python
    some_int: 777
    HelloWorld::~HelloWorld(0x24f0090)
