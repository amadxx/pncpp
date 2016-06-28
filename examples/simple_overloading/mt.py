from gxxtypes import *
import ctypes

@cxx_struct(virtual=False)
class ClassA(CXXStruct):

    _fields_ = [
        ("text", ctypes.c_char_p),
        ("value", ctypes.c_int)
    ]

@cxx_struct(virtual=False)
class ClassB(CXXStruct):

    _fields_ = []

    @cxx_method(t_void, ClassA.ptr(), name="foo")
    def foo1(self, a):
        pass

    @cxx_method(t_void, ClassA.ref(), name="foo")
    def foo2(self, a):
        pass

if __name__ == '__main__':

    lib = ctypes.CDLL("mt.dll")  # or 'mt.so'

    ClassA.link_with(lib)
    ClassB.link_with(lib)

    a = ClassA()
    b = ClassB()

    a.text = "foo1"
    a.value = 101
    b.foo1(a)
    print a.text

    a.text = "foo2"
    a.value = 202
    b.foo2(a)
    print a.text

