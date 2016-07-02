__author__ = 'Dimon'

import unittest
import subprocess
from pncpp import *
import platform
import ctypes

if platform.system() == "Windows":
    so_ext = ".dll"
elif platform.system() == "Linux":
    so_ext = ".so"
else:
    raise Exception("Unsupported system: %s" % platform.system())


def libname(name):
    return "%s%s" % (name, so_ext)


def compile_files(target, *sources):
    out_name = libname(target)
    subprocess.call(["g++"] + list(sources) + ["-shared", "-fpic", "-fdump-class-hierarchy", "-o", out_name])


def load_lib(name):
    return ctypes.CDLL(libname(name))


def prepare_lib(target, *sources):
    compile_files(target, *sources)
    proc = subprocess.Popen(["objdump", "-t", libname(target)], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    with open("%s_symbols.txt" % target, "w") as f:
        f.write(output)
    return load_lib(target)


def link_classes(lib, *classes):
    for cls in classes:
        cls.link_with(lib)


@cxx_struct(virtual=0)
class NonVirtual(CXXStruct):

    _pyobject_ = "py_object"
    _fields_ = [
        (_pyobject_, ctypes.c_void_p),
        ('result', ctypes.c_int)
    ]

    @cxx_constructor()
    def constructor_empty(self):
        pass

    @cxx_constructor(t_int)
    def constructor_int(self, result):
        pass

    @cxx_method(t_int)
    def member_return(self):
        pass

    @cxx_method(t_int, t_int, t_int, t_int, name="foo")
    def foo_i_iii(self, a, b, c):
        pass

    @cxx_method(t_int, t_int.ptr(), t_int.ptr(), t_int.ptr(), name="foo")
    def foo_i_PiPiPi(self, a, b, c):
        pass

    @cxx_method(t_void, t_int.ptr(), t_int, t_int.ptr(), name="foo")
    def foo_v_PiiPi(self, a, b, c):
        pass

    @cxx_method(t_void, t_char.ptr(), t_short.ptr(), t_int.ptr(), t_long, t_int.ptr(), t_short.ptr(), t_char.ptr(), name="foo")
    def foo_v_ptr_csi_l_isc(self, a, b, c, z, cx, bx, ax):
        pass

    @cxx_method(t_void, t_char.const().ptr(), t_short.const().ptr(), t_int.const().ptr(), t_long,
                t_int.const().ptr(), t_short.const().ptr(), t_char.const().ptr(), name="foo")
    def foo_v_const_ptr_csi_l_isc(self, a, b, c, z, cx, bx, ax):
        pass


    @cxx_method(t_void, t_char.const().ptr(), t_char.const().ptr(), name="foo")
    def foo_v_KP_cc(self, s1, s2):
        pass

    @cxx_destructor()
    def destructor(self):
        pass


@cxx_struct(virtual=1)
class Virtual(CXXStruct):

    _pyobject_ = "py_object"
    _fields_ = [
        (_pyobject_, ctypes.c_void_p),
        ('result', ctypes.c_int)
    ]

    @cxx_constructor
    def constructor(self):
        pass

    @cxx_method(t_void, t_char.ptr(), t_short.ptr(), t_int.ptr(), t_long, t_int.ptr(), t_short.ptr(), t_char.ptr(), name="foo")
    def foo_v_ptr_csi_l_isc(self, a, b, c, z, cx, bx, ax):
        pass

lib_test_abi = prepare_lib("test_abi", "test_abi.cpp")
link_classes(lib_test_abi, NonVirtual, Virtual)

class ABITest(unittest.TestCase):

    def setUp(self):
        pass

    def test_constructor(self):
        obj = NonVirtual()
        obj.constructor_empty()
        self.assertEqual(obj.result, 701)

    def test_destructor(self):
        obj = NonVirtual()
        obj.destructor()
        self.assertEqual(obj.result, 799)

    def test_custom_constructor(self):
        obj = NonVirtual()
        obj.constructor_int(702)
        self.assertEqual(obj.result, 702)

    def test_member_py_access(self):
        obj = NonVirtual()
        obj.result = 720
        self.assertEqual(obj.result, 720)

    def test_member_cpp_access(self):
        obj = NonVirtual()
        obj.result = 721
        self.assertEqual(obj.member_return(), 721)

    def test_mangle_args_i_iii(self):
        obj = NonVirtual()
        result = obj.foo_i_iii(1, 5, 4)
        self.assertEqual(obj.result, 10)
        self.assertEqual(result, 10*2)

    def test_mangle_args_i_PiPiPi(self):
        obj = NonVirtual()
        a = ctypes.c_int(4)
        b = ctypes.c_int(1)
        c = ctypes.c_int(5)
        result = obj.foo_i_PiPiPi(ctypes.byref(a), ctypes.byref(b), ctypes.byref(c))
        self.assertEqual(a.value, 1)
        self.assertEqual(b.value, 2)
        self.assertEqual(c.value, 3)
        self.assertEqual(obj.result, 10)
        self.assertEqual(result, 10*2)

    def test_mangle_args_v_PiiPi(self):
        obj = NonVirtual()
        i = ctypes.c_int(4)
        pi = ctypes.pointer(i)
        obj.foo_v_PiiPi(pi, i, pi)

    def test_mangle_v_ptr_csi_l_isc(self):
        obj = NonVirtual()
        a = ctypes.pointer(ctypes.c_char("0"))
        b = ctypes.pointer(ctypes.c_short(0))
        c = ctypes.pointer(ctypes.c_int(0))
        obj.foo_v_ptr_csi_l_isc(a, b, c, 777, c, b, a)

    def test_mangle_v_const_ptr_csi_l_isc(self):
        obj = NonVirtual()
        a = ctypes.pointer(ctypes.c_char("0"))
        b = ctypes.pointer(ctypes.c_short(0))
        c = ctypes.pointer(ctypes.c_int(0))
        obj.foo_v_const_ptr_csi_l_isc(a, b, c, 777, c, b, a)

    def test_mangle_v_KP_cc(self):
        obj = NonVirtual()
        obj.foo_v_KP_cc("String1", "String2")

    def test_virtual_mangle_v_ptr_csi_l_isc(self):
        obj = Virtual()
        a = ctypes.pointer(ctypes.c_char("0"))
        b = ctypes.pointer(ctypes.c_short(0))
        c = ctypes.pointer(ctypes.c_int(0))
        obj.foo_v_ptr_csi_l_isc(a, b, c, 777, c, b, a)

if __name__ == '__main__':
    unittest.main()
