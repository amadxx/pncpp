#include <iostream>

using namespace std;

class ClassA
{
    public:
        const char* text;
        int value;
};

class ClassB
{
    public:
        void foo(ClassA& a);
        void foo(ClassA* a);
};

void ClassB::foo(ClassA& a)
{
    cout<<"(ref) Text:  "<<a.text<<endl;
    cout<<"(ref) Value: "<<a.value<<endl;
    a.text = "foo(ClassA&)";
}

void ClassB::foo(ClassA* a)
{
    cout<<"(ptr) Text:  "<<a->text<<endl;
    cout<<"(ptr) Value: "<<a->value<<endl;
    a->text = "foo(ClassA*)";
}