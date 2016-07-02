#include <iostream>

using namespace std;

class SampleClass
{
    void* py_object; // for backward conversion to python object
public:
    int cpp_member;

    SampleClass(int cpp_member);
    virtual int get_python_member();
    virtual void python_function();
    void cpp_function();
    void run_cpp();
    virtual void run_python();
    void run();
    void print_text(const char* text1, const char* text2);
    virtual ~SampleClass();
};

SampleClass::SampleClass(int cpp_member):cpp_member(cpp_member)
{
    cout<<"SampleClass::SampleClass("<<cpp_member<<")"<<endl;
}

SampleClass::~SampleClass()
{
    cout<<"SampleClass::~SampleClass()"<<endl;
}

void SampleClass::python_function()
{
    // This function implemented in python
}

void SampleClass::cpp_function()
{
    print_text("    cpp_function(): ", "This is CPP function");
}

void SampleClass::run_cpp()
{
    cout<<"SampleClass::run_cpp (C++ code):"<<endl;
    cout<<"    cpp_member: "<<cpp_member<<endl;
    cout<<"    python_member: "<<get_python_member()<<endl;

    cpp_function();
    python_function();
}

void SampleClass::print_text(const char* text1, const char* text2)
{
    cout<<text1<<text2<<endl;
}

void SampleClass::run_python()
{
    // This function implemented in python
}

void SampleClass::run()
{
    run_cpp();
    run_python();
}

int SampleClass::get_python_member()
{
    // This function implemented in python
    return 0;
}