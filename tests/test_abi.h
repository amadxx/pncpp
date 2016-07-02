class Dummy
{

};

class NonVirtual
{
public:
    void* py_object;
    int result;

    NonVirtual();
    NonVirtual(int result);
    int member_return();
    int foo(int a, int b, int c);
    int foo(int* a, int* b, int* c);
    void foo(int* a, int b, int* c);
    void foo(char* a, short* b, int* c, long z, int* cx, short* bx, char* ax);
    void foo(const char* a, const short* b, const int* c, long z, const int* cx, const short* bx, const char* ax);
    void foo(const char* s1, const char* s2);

    ~NonVirtual();
};

class Virtual
{
public:
    void* py_object;
    int result;

    Virtual();
    virtual void foo(char* a, short* b, int* c, long z, int* cx, short* bx, char* ax);
    virtual ~Virtual();
};