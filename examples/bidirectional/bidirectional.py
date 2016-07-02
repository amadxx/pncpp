from pncpp import *
import ctypes

@cxx_struct(virtual=3)  # 3 is count of virtual methods except destructor
class SampleClass(CXXStruct):

    _pyobject_ = "py_object"

    _fields_ = [
        (_pyobject_, ctypes.c_void_p),
        ("cpp_member", ctypes.c_int)
    ]

    def __init__(self, cpp_member, python_member):
        super(SampleClass, self).__init__()
        self._construct(cpp_member)
        self.python_member = python_member
        self.override_vtable()

    @cxx_constructor(t_int)
    def _construct(self, cpp_member):
        pass

    @cxx_method(t_void, override=True)
    def python_function(self):
        self.print_text("    python_function(): ", "This is python function")

    @cxx_method(t_void)
    def cpp_function(self):
        """This function implemented in C++"""

    @cxx_method(t_void)
    def run_cpp(self):
        """This function implemented in C++"""

    @cxx_method(t_void, t_char_p.const(), t_char_p.const())
    def print_text(self, text1, text2):
        """This function implemented in C++"""

    @cxx_method(t_void, override=True)
    def run_python(self):

        print "SampleClass::run_python (Python code):"
        print "    cpp_member: ", self.cpp_member
        print "    python_member: ", self.python_member

        self.cpp_function()
        self.python_function()

    @cxx_method(t_int, override=True)
    def get_python_member(self):
        return self.python_member

    @cxx_destructor()
    def destroy(self):
        pass

    @cxx_method(t_void)
    def run(self):
        """This function implemented in C++"""

    def __del__(self):
        self.destroy()

if __name__ == '__main__':

    lib = ctypes.CDLL("bidirectional.dll")
    SampleClass.link_with(lib)

    obj = SampleClass(cpp_member=42, python_member=77)
    obj.run()
    obj.destroy()