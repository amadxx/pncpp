"""
Tools for wrapping C++ types and classes
"""

__author__ = "Dmitry Pavliuk"
__copyright__ = "Copyright 2016, Dmitry Pavliuk"
__credits__ = ["Dmitry Pavliuk"]
__license__ = "MIT"
__maintainer__ = "Dmitry Pavliuk"
__email__ = "dmitry.pavluk@gmail.com"
__status__ = "Development"

import pncpp.itanium_abi_mangle as mg
import ctypes
import inspect
import warnings


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


def cxx_struct(name=None, virtual=0, owner=None):

    def decorator(cxx_struct):
        fields = []

        if virtual:
            vtable_type = (ctypes.c_void_p * (virtual + 4)) # ?(1), typeinfo(1), destructor(2)
            cxx_struct._vtable_ = vtable_type()
            fields.append(('_vtable_', ctypes.POINTER(vtable_type)))
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


def _new_copy(src):
    dst = type(src)()
    ctypes.pointer(dst)[0] = src
    return dst


def _ptr_copy(dst_ptr, src_ptr):
    dst_ptr[0] = src_ptr[0]

def _vtable_dump(vtable, max=10):
    print("vtable at: %x" % ctypes.cast(vtable, ctypes.c_void_p).value)
    for i, vt_entry in enumerate(vtable):
        print("    %3d: %x" % (i, ctypes.cast(vt_entry, ctypes.c_void_p).value or 0))
        if i > max:
            break


class CXXMethod(object):

    def __init__(self, mtype, fn, ret_type, *args, **kwargs):

        self.name = None
        self.static = False
        self.override = False

        for k, v in kwargs.items():
            setattr(self, k, v)

        self._py_func = fn
        self._ret = ret_type
        self._args = args
        self._type = mtype
        self.c_args = None
        self.parent = None
        self.c_method = None
        self.v_method = None

    def resolve_as_member(self, cls):
        if not issubclass(cls, CXXStruct):
            raise TypeError("Can't call c++ method from non c++ class")

        if cls._cdll == None:
            raise RuntimeError("Class not linked to ctypes CDLL")

        if self.c_method != None:
            return

        m_args = [x.get_mangled_type() for x in self._args]

        # handle relative type references (S_, S0_, S1, ...)
        # Todo: move to separate method
        prev = None
        prev_i = 1
        arg2idx = {}
        for i, m_arg in enumerate(m_args):
            str_arg = str(m_arg)
            if m_arg.is_ref():
                if str_arg in arg2idx:
                    m_args[i] = mg.s_arg(arg2idx[str_arg])
                else:
                    for deref in m_arg.get_deref_list():
                        str_deref = str(deref)
                        if len(str_deref) > 1:
                            arg2idx[str(deref)] = prev_i
                            prev_i += 1

        # functions with no arguments always have void in mangled name
        if len(m_args) == 0:
            m_args.append(mg.m_void)

        # generate method signature
        m_method = \
        [cls._mangled.method(self.name, *m_args),
         cls._mangled.constructor(1, *m_args),
         cls._mangled.destructor(1)][self._type]
        if not hasattr(cls._cdll, str(m_method)):
            warnings.warn("Method not resolved: %s" % m_method)
            return None

        c_method = getattr(cls._cdll, str(m_method))
        c_method.restype = self._ret.get_ctypes_type()
        self.c_args = tuple([ctypes.POINTER(cls.CStructure)] + [x.get_ctypes_type() for x in self._args if x is not None])
        c_method.argtypes = self.c_args
        self.c_method = c_method

        VMType = ctypes.CFUNCTYPE(c_method.restype, *c_method.argtypes)

        self.v_method = VMType(CXXClassMethodAdapter(self._py_func, cls._pyobject_))

        if cls._vtable_:
            vtable_resolved = False
            for i, vt_entry in enumerate(cls._vtable_):
                fptr = ctypes.cast(c_method, ctypes.c_void_p)
                #print "VTABLE RESOLVE [%d]: %x <> %x" % (i, vt_entry or 0, fptr.value)
                if vt_entry == fptr.value:
                    #print "VTABLE RESOLVED [%d]: %x == %x" % (i, vt_entry or 0, fptr.value)
                    if self.override:
                        cls._vtable_[i] = ctypes.cast(self.v_method, ctypes.c_void_p)
                        vtable_resolved = True
                        break
                        #print "VTABLE OVERRIDE [%d]: %x =  %x" % (i, cls._vtable_[i] or 0, fptr.value)
            if self.override and not vtable_resolved:
                raise RuntimeError("Can't override virtual function '%s': not found in vtable" % self.name)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        else:
            return CXXMethodInvoke(obj, self)

    def __call__(self, *args):
        if not self.c_method:
            raise AttributeError("Method not resolved")

        nargs = list(args)
        for i, arg in enumerate(nargs):
            if issubclass(type(arg), CXXStruct):
                c_type = self.c_args[i]
                if issubclass(c_type, ctypes._Pointer):
                    nargs[i] = arg.this
                elif issubclass(c_type, ctypes.Structure):
                    nargs[i] = arg.struct
        if self.override:
            result = self.v_method(*nargs)
        else:
            result = self.c_method(*nargs)
        return result


class CXXClassMethodAdapter(object):

    def __init__(self, fn, py_object_field):
        self._fn = fn
        self._py_object_field = py_object_field

    def __call__(self, p_struct, *args):
        py_object_addr = getattr(p_struct.contents, self._py_object_field)
        py_object = ctypes.cast(py_object_addr, ctypes.POINTER(ctypes.py_object)).contents.value
        return self._fn(py_object, *args)

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
        return self._method(self._obj, *args, **kwargs)


def cxx_method(ret_type, *args, **kwargs):
    def dec(fn):
        return CXXMethod(0, fn, ret_type, *args, **kwargs)
    return dec


def cxx_constructor(*args):
    def dec(fn):
        return CXXMethod(1, fn, t_void, *args)
    return dec


def cxx_destructor(*args):
    def dec(fn):
        return CXXMethod(2, fn, t_void, *args)
    return dec


class CXXStruct(object):

    _cdll = None
    _mangled = None
    _fields_ = None
    _vtable_ = None
    _orig_vtable_ = None
    _pyobject_ = None

    @classmethod
    def link_with(cls, cdll):
        if cls._cdll == None:
            cls._cdll = cdll
            if cls._vtable_:
                cls._orig_vtable_ = type(cls._vtable_).in_dll(cls._cdll, str(cls._mangled.vtable()))
                cls._vtable_ = _new_copy(cls._orig_vtable_)
            for nm, member in inspect.getmembers(cls):
                if issubclass(type(member), CXXMethod):
                    member.resolve_as_member(cls)
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

        if self._pyobject_:
            # save pointer to python object
            setattr(self.struct, self._pyobject_, ctypes.cast(ctypes.pointer(ctypes.py_object(self)), ctypes.c_void_p))

        self.override_vtable()

    def override_vtable(self):

        if hasattr(self.struct, '_vtable_'):
            #print("override before: %x" % (ctypes.cast(self.struct._vtable_, ctypes.c_void_p).value or 0))
            #_vtable_dump(self._orig_vtable_)

            new_vtable_addr = ctypes.cast(self._vtable_, ctypes.c_void_p).value + 0x10  # TODO: describe offset

            self.struct._vtable_ = ctypes.cast(ctypes.c_void_p(new_vtable_addr), ctypes.POINTER(type(self._vtable_)))
            #print("override after: %x" % ctypes.cast(self.struct._vtable_, ctypes.c_void_p).value)
            #_vtable_dump(self._vtable_)

    def __getattr__(self, item):
        if item != "struct" and hasattr(self.struct, item):
            return getattr(self.struct, item)

        return super(CXXStruct, self).__getattribute__(item)

    def __setattr__(self, item, value):
        if item != "struct" and hasattr(self.struct, item):
            return setattr(self.struct, item, value)

        return super(CXXStruct, self).__setattr__(item, value)
