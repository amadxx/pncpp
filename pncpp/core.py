"""
Tools for wrapping C++ types and classes
"""

__author__ = "Dmitry Pavliuk"
__copyright__ = "Copyright 2016, Dmitry Pavliuk"
__credits__ = ["Dmitry Pavliuk"]
__license__ = "MIT"
__version__ = "0.0.2"
__maintainer__ = "Dmitry Pavliuk"
__email__ = "dmitry.pavluk@gmail.com"
__status__ = "Development"

import pncpp.itanium_abi_mangle as mg
import ctypes
import inspect


class CXXType(object):
    def __init__(self, ctype, mtype, ptr):
        self._ctype = ctype
        self._mtype = mtype
        self._is_ptr = ptr

    def get_ctypes_type(self):
        return self._ctype

    def get_mangled_type(self):
        return self._mtype

    def const(self):
        return CXXType(self.get_ctypes_type(), self.get_mangled_type().const(), self.is_ptr())

    def ptr(self):
        return CXXType(ctypes.POINTER(self.get_ctypes_type()), self.get_mangled_type().ptr(), True)

    def ref(self):
        return CXXType(ctypes.POINTER(self.get_ctypes_type()), self.get_mangled_type().ref(), True)

    def is_ptr(self):
        return self._is_ptr


class VoidType(CXXType):

    def __init__(self):
        super(VoidType, self).__init__(None, mg.m_void, False)

    def const(self):
        raise Exception("void can't be const")

    def ptr(self):
        return CXXType(ctypes.c_void_p, self.get_mangled_type().ptr(), True)

    def ref(self):
        raise Exception("void can't be referenced")


class SelfTypeRefProxy(CXXType):
    def __init__(self, parent, ref=0, const=False):
        super(SelfTypeRefProxy, self).__init__(None, mg.m_void, False)
        self._parent = parent
        self._ref = ref
        self.const = const

    def get_ctypes_type(self):
        return [self._parent.self_class.CStructure, ctypes.POINTER(self._parent.self_class.CStructure)][ self._ref > 0 ]

    def get_mangled_type(self):
        result = mg.s_arg(self._parent.idx)
        if self.const:
            result = result.const()
        result = [result, result.ptr(), result.ref()][self._ref]
        return result

    def ptr(self):
        return SelfTypeRefProxy(self._parent, 1, self.const)

    def ref(self):
        return SelfTypeRefProxy(self._parent, 2, self.const)

    def const(self):
        return SelfTypeRefProxy(self._parent, self._ref, True)

    def is_ptr(self):
        return self._ref > 0


class SelfTypeProxy(SelfTypeRefProxy):
    def __init__(self, idx = 0):
        super(SelfTypeProxy, self).__init__(self, 0, False)
        self.self_class = None
        self.idx = idx


def cxx_struct(name=None, virtual=True, owner=None):

    def decorator(cxx_struct):
        fields = []
        if virtual:
            fields.append(('__vtable', ctypes.c_void_p))
        fields.extend(cxx_struct._fields_)

        cls_name = [cxx_struct.__name__, name][name != None]
        if owner:
            mangled_name = owner._mangled.struct(cls_name)
        else:
            mangled_name = mg.struct(cls_name)
        cxx_struct._mangled = mangled_name
        cxx_struct.CStructure = type("%s_CStructure" % cxx_struct.__name__, (ctypes.Structure,), {"_fields_": fields})

        for nm, member in inspect.getmembers(cxx_struct):
            if issubclass(type(member), CXXMethod):
                if member.name == None:
                    member.name = nm
                member.parent = cxx_struct
            elif issubclass(type(member), SelfTypeProxy):
                member.self_class = cxx_struct

        return cxx_struct

    return decorator


class CXXMethod(object):

    def __init__(self, mtype, ret_type, *args, **kwargs):

        self.name = None
        self.static = False

        for k, v in kwargs.iteritems():
            setattr(self, k, v)

        self._ret = ret_type
        self._args = args
        self._type = mtype
        self.c_args = None
        self.parent = None
        self.c_method = None

    def _resolve_as_member(self, cls):
        if not issubclass(cls, CXXStruct):
            raise TypeError("Can't call c++ method from non c++ class")

        if cls._cdll == None:
            raise RuntimeError("Class not linked to ctypes CDLL")

        if self.c_method != None:
            return

        m_args = [x.get_mangled_type() for x in self._args]
        if len(m_args) == 0:
            m_args.append(mg.m_void)
        m_method = \
        [cls._mangled.method(self.name, *m_args),
         cls._mangled.constructor(1, *m_args),
         cls._mangled.destructor(1)][self._type]

        c_method = getattr(cls._cdll, str(m_method))
        c_method.restype = self._ret.get_ctypes_type()
        self.c_args = tuple([ctypes.POINTER(cls.CStructure)] + [x.get_ctypes_type() for x in self._args if x is not None])
        c_method.argtypes = self.c_args
        self.c_method = c_method

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        else:
            self._resolve_as_member(objtype)
            return CXXMethodInvoke(obj, self)

    def __call__(self, *args):
        nargs = list(args)
        for i, arg in enumerate(nargs):
            if issubclass(type(arg), CXXStruct):
                c_type = self.c_args[i]
                if issubclass(c_type, ctypes._Pointer):
                    nargs[i] = arg.this
                elif issubclass(c_type, ctypes.Structure):
                    nargs[i] = arg.struct

        result = self.c_method(*nargs)
        return result


t_void = VoidType()
t_wchar = CXXType(ctypes.c_wchar, mg.m_wchar_t, False)
t_wchar_p = CXXType(ctypes.c_wchar_p, mg.m_wchar_t.ptr(), False)
t_bool = CXXType(ctypes.c_bool, mg.m_bool, False)

t_char = CXXType(ctypes.c_char, mg.m_char, False)
t_char_p = CXXType(ctypes.c_char_p, mg.m_char.ptr(), False)
t_signed_char = CXXType(ctypes.c_char, mg.m_signed_char, False)
t_unsigned_char = CXXType(ctypes.c_char, mg.m_unsigned_char, False)

t_short = CXXType(ctypes.c_short, mg.m_short, False)
t_unsigned_short = CXXType(ctypes.c_ushort, mg.m_unsigned_short, False)

t_int = CXXType(ctypes.c_int, mg.m_int, False)
t_unsigned_int = CXXType(ctypes.c_uint, mg.m_unsigned_int, False)

t_long = CXXType(ctypes.c_long, mg.m_long, False)
t_unsigned_long = CXXType(ctypes.c_ulong, mg.m_unsigned_long, False)

t_long_long = CXXType(ctypes.c_longlong, mg.m_long_long, False)
t_unsigned_long_long = CXXType(ctypes.c_ulonglong, mg.m_unsigned_long_long, False)


class CXXMethodInvoke(object):

    def __init__(self, obj, method):
        self._obj = obj
        self._method = method

    def __call__(self, *args, **kwargs):
        self._method(self._obj, *args, **kwargs)


def cxx_method(ret_type, *args, **kwargs):
    def dec(fn):
        return CXXMethod(0, ret_type, *args, **kwargs)
    return dec


def cxx_constructor(*args):
    def dec(fn):
        return CXXMethod(1, t_void, *args)
    return dec


def cxx_destructor(*args):
    def dec(fn):
        return CXXMethod(2, t_void, *args)
    return dec


class CXXStruct(object):

    _cdll = None
    _mangled = None
    _fields_ = None

    @classmethod
    def link_with(cls, cdll):
        if cls._cdll == None:
            cls._cdll = cdll
        else:
            raise Exception("Already linked with CDLL")

    class CStructure(ctypes.Structure):
        pass

    @classmethod
    def get_ctypes_type(cls):
        return cls.CStructure

    @classmethod
    def get_mangled_type(self):
        return self._mangled.type()

    @classmethod
    def const(cls):
        return CXXType(cls.get_ctypes_type(), cls.get_mangled_type().const(), cls.is_ptr())

    @classmethod
    def ptr(cls):
        return CXXType(ctypes.POINTER(cls.get_ctypes_type()), cls.get_mangled_type().ptr(), True)

    @classmethod
    def ref(cls):
        return CXXType(ctypes.POINTER(cls.get_ctypes_type()), cls.get_mangled_type().ref(), True)

    @staticmethod
    def is_ptr():
        return False

    def __init__(self):
        self.struct = self.CStructure()
        self.this = ctypes.pointer(self.struct)

    def __getattr__(self, item):
        if item != "struct" and hasattr(self.struct, item):
            return getattr(self.struct, item)

        return super(CXXStruct, self).__getattribute__(item)

    def __setattr__(self, item, value):
        if item != "struct" and hasattr(self.struct, item):
            return setattr(self.struct, item, value)

        return super(CXXStruct, self).__setattr__(item, value)
