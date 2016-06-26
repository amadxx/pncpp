#include <iostream>

using namespace std;

class HelloWorld
{
    public:
        const char* text;
        HelloWorld(const char* text);
        void print_text(int some_int);
        ~HelloWorld();
};

HelloWorld::HelloWorld(const char* text):text(text)
{
    cout<<"HelloWorld::HelloWorld("<<this<<")"<<endl;
}

void HelloWorld::print_text(int some_int)
{
    cout<<"print_text: "<<text<<endl;
    cout<<"some_int: "<<some_int<<endl;
}

HelloWorld::~HelloWorld()
{
    cout<<"HelloWorld::~HelloWorld("<<this<<")"<<endl;
}