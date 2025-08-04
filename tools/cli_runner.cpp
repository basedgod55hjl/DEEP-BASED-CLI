#include <iostream>
#include <cstdlib>
#include <string>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "No command provided" << std::endl;
        return 1;
    }
    std::string cmd;
    for (int i = 1; i < argc; ++i) {
        if (i > 1) cmd += " ";
        cmd += argv[i];
    }
    int result = std::system(cmd.c_str());
    if (result != 0) {
        std::cerr << "Command failed with code " << result << std::endl;
    }
    return result;
}
