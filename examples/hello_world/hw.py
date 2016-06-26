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

if __name__ == '__main__':
    hw_lib = ctypes.CDLL("hw.dll")  # or 'hw.so'

    HelloWorld.link_with(hw_lib)

    x = HelloWorld("Hello, world!")
    x.print_text(42)
    x.struct.text = "Other text from python"
    x.print_text(777)

    x.destroy()

