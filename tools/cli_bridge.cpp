#include <array>
#include <cstdio>
#include <iostream>
#include <memory>
#include <string>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: cli_bridge <args>\n";
        return 1;
    }
    std::string cmd = "python3 enhanced_based_god_cli.py";
    for (int i = 1; i < argc; ++i) {
        cmd += " ";
        cmd += argv[i];
    }
    std::array<char, 256> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd.c_str(), "r"), pclose);
    if (!pipe) {
        std::cerr << "Failed to run command\n";
        return 1;
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    std::cout << result;
    return 0;
}
