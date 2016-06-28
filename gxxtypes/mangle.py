"""
Utility classes for C++ name mangling (GCC convention)
"""

__author__ = "Dmitry Pavliuk"
__copyright__ = "Copyright 2016, Dmitry Pavliuk"
__credits__ = ["Dmitry Pavliuk"]
__license__ = "MIT"
__version__ = "0.0.2"
__maintainer__ = "Dmitry Pavliuk"
__email__ = "dmitry.pavluk@gmail.com"
__status__ = "Development"


class Name(object):

    def __init__(self, *parts):
        self.parts = list(parts)

    def __str__(self):

        packed_ns = []

        for x in self.parts:
            if issubclass(type(x), basestring):
                packed_ns.append("%d%s" % (len(x), x))
            else:
                packed_ns.append(str(x))

        return ["N%sE", "%s"][len(self.parts) == 1] % ("".join(packed_ns))


class Ref:

    BY_VALUE = 0
    BY_POINTER = 1
    BY_REFERENCE = 2

    mflags = ["", "P", "R"]


class BType(object):
    def __init__(self, short_typename):
        self.short_typename = short_typename

    def __str__(self):
        return self.short_typename


class TemplateArg(object):

    def __init__(self, idx):
        self.idx = idx

    def __str__(self):
        if (self.idx == 0):
            return "T_"
        else:
            return "T%d_" % (self.idx - 1)


class Type(object):

    def __init__(self, type_obj, reference_type = 0, const = False):
        self.flags = ""
        self.type_obj = type_obj
        self.flags += Ref.mflags[reference_type]
        self._const = const
        self._reference_type = reference_type
        if const:
            self.flags += "K"

    def val(self):
        return Type(self.type_obj, Ref.BY_VALUE, self._const)

    def ptr(self):
        return Type(self.type_obj, Ref.BY_POINTER, self._const)

    def ref(self):
        return Type(self.type_obj, Ref.BY_REFERENCE, self._const)

    def const(self):
        return Type(self.type_obj, self._reference_type, True)

    def __str__(self):
        return "%s%s" % (self.flags, self.type_obj)



def mkstype(c):
    return Type(BType(c))


def t_arg(idx, reference_type = 0, const = False):
    return Type(TemplateArg(idx), reference_type, const)


def s_arg(idx):
        if (idx == 0):
            return  mkstype("S_")
        else:
            return mkstype("S%d_" % (idx - 1))

# <builtin-type> ::= v	# void
# 	 ::= w	# wchar_t
# 	 ::= b	# bool
# 	 ::= c	# char
# 	 ::= a	# signed char
# 	 ::= h	# unsigned char
# 	 ::= s	# short
# 	 ::= t	# unsigned short
# 	 ::= i	# int
# 	 ::= j	# unsigned int
# 	 ::= l	# long
# 	 ::= m	# unsigned long
# 	 ::= x	# long long, __int64
# 	 ::= y	# unsigned long long, __int64
# 	 ::= n	# __int128
# 	 ::= o	# unsigned __int128
# 	 ::= f	# float
# 	 ::= d	# double
# 	 ::= e	# long double, __float80
# 	 ::= g	# __float128
# 	 ::= z	# ellipsis
# 	 ::= Dd # IEEE 754r decimal floating point (64 bits)
# 	 ::= De # IEEE 754r decimal floating point (128 bits)
# 	 ::= Df # IEEE 754r decimal floating point (32 bits)
# 	 ::= Dh # IEEE 754r half-precision floating point (16 bits)
# 	 ::= Di # char32_t
# 	 ::= Ds # char16_t
# 	 ::= Da # auto
# 	 ::= Dc # decltype(auto)
# 	 ::= Dn # std::nullptr_t (i.e., decltype(nullptr))
# 	 ::= u <source-name>	# vendor extended type

m_void = mkstype("v")
m_bool = mkstype("b")
m_wchar_t = mkstype("w")
m_char = mkstype("c")
m_signed_char = mkstype("a")
m_unsigned_char = mkstype("h")
m_short = mkstype("s")
m_unsigned_short = mkstype("t")
m_int = mkstype("i")
m_unsigned_int = mkstype("j")
m_long = mkstype("l")
m_unsigned_long = mkstype("m")
m_long_long = mkstype("x")
m_unsigned_long_long = mkstype("y")
m__int128 = mkstype("n")
m_unsigned__int128 = mkstype("o")
m_float = mkstype("f")
m_double = mkstype("d")
m_long_double = mkstype("e")


class Template(object):
    def __init__(self, *types):
        self.types = types

    def __str__(self):
        return "I%sE" % "".join([str(t) for t in self.types])


class Args(object):

    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return "%s" % "".join([str(t) for t in self.args])


class FnSig(object):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __str__(self):
        return "_Z%s%s" % (self.name, self.args)


class TypeSig(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "_Z%s" % (self.name)

    def method(self, name, *args):
        parts = self.name.parts + [name]
        return FnSig(Name(*parts), *args)

    def struct(self, name):
        args = self.name.parts + [name]
        return TypeSig(Name(*args))

    def constructor(self, idx, *args):
        return self.method(Constructor(idx), *args)

    def destructor(self, idx):
        return self.method(Destructor(idx), m_void)

    def template(self, *types):
        return TemplateProxy(self.name.parts, types)

    def type(self):
        return Type(self.name, Ref.BY_VALUE)

    def ptr_type(self, const = False):
        return Type(self.name, Ref.BY_POINTER, const)

    def ref_type(self, const = False):
        return Type(self.name, Ref.BY_REFERENCE, const)


def struct(name):
    return TypeSig(Name(name))


def method(name, *args):
    return FnSig(Name(name), Args(*args))


def template(*types):
    return TemplateProxy([], types)


class TemplateProxy(object):
    def __init__(self, parent_ns, types):
        self.template = Template(*types)
        self.parent_ns = parent_ns

    def struct(self, name):
        ns_parts = self.parent_ns + [name, self.template]
        name = Name(*ns_parts)
        return TypeSig(name)

    def method(self, name, *args):
        ns_parts = self.parent_ns + [name, self.template]
        name_ = Name(*ns_parts)
        args = Args(*args)
        return FnSig(name_, args)

    def constructor(self, idx, *args):
        return self.method(Constructor(idx), *args)

    def destructor(self, idx, *args):
        return self.method(Destructor(idx), *args)


class Constructor(object):

    def __init__(self, idx):
        self.idx = idx

    def __str__(self):
        return "C%d" % self.idx


class Destructor(object):
    def __init__(self, idx):
        self.idx = idx

    def __str__(self):
        return "D%d" % self.idx

