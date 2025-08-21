#include <iostream>
using namespace std;

int main(int argc, char *argv[]) {
    if (argv == nullptr || argv[0] == nullptr) {
        cout << "E: No command line arguments provided." << endl;
        cout << "Usage: DevToolbox <command>" << endl;
        cout << "Opening Navigator..." << endl;
        system("bin/navigator.exe");
        return 0;
    }
}