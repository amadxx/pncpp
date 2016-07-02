#include "test_abi.h"

NonVirtual::NonVirtual():result(701)
{

}

NonVirtual::NonVirtual(int result):result(result)
{

}

int NonVirtual::foo(int a, int b, int c)
{
    result = a + b + c;
    return result * 2;
}

int NonVirtual::foo(int* a, int* b, int* c)
{
    result = *a + *b + *c;
    *a = 1;
    *b = 2;
    *c = 3;
    return result * 2;
}

void NonVirtual::foo(int* a, int b, int* c){}
void NonVirtual::foo(char* a, short* b, int* c, long z, int* cx, short* bx, char* ax){};
void NonVirtual::foo(const char* a, const short* b, const int* c, long z, const int* cx, const short* bx, const char* ax){};
void NonVirtual::foo(const char* s1, const char* s2){};

NonVirtual::~NonVirtual()
{
    result = 799;
}

int NonVirtual::member_return()
{
    return result;
}

Virtual::Virtual(){};
void Virtual::foo(char* a, short* b, int* c, long z, int* cx, short* bx, char* ax){};
Virtual::~Virtual(){};