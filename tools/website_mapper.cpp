#include <curl/curl.h>
#include <iostream>
#include <regex>
#include <string>
#include <vector>

// Callback to write received data into a std::string
size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    size_t totalSize = size * nmemb;
    std::string* buffer = static_cast<std::string*>(userp);
    buffer->append(static_cast<char*>(contents), totalSize);
    return totalSize;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <url>" << std::endl;
        return 1;
    }

    std::string url = argv[1];
    CURL* curl = curl_easy_init();
    if (!curl) {
        std::cerr << "Failed to initialize libcurl" << std::endl;
        return 1;
    }

    std::string html;
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &html);

    CURLcode res = curl_easy_perform(curl);
    if (res != CURLE_OK) {
        std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << std::endl;
        curl_easy_cleanup(curl);
        return 1;
    }
    curl_easy_cleanup(curl);

    std::regex linkRegex("<a[^>]*href=[\"']([^\"']+)[\"']", std::regex::icase);
    std::regex buttonRegex("<button[^>]*>(.*?)</button>", std::regex::icase);

    std::smatch match;
    std::vector<std::string> links;
    std::vector<std::string> buttons;

    std::string::const_iterator searchStart(html.cbegin());
    while (std::regex_search(searchStart, html.cend(), match, linkRegex)) {
        links.push_back(match[1]);
        searchStart = match.suffix().first;
    }

    searchStart = html.cbegin();
    while (std::regex_search(searchStart, html.cend(), match, buttonRegex)) {
        buttons.push_back(match[1]);
        searchStart = match.suffix().first;
    }

    std::cout << "Links found:\n";
    for (const auto& link : links) {
        std::cout << " - " << link << std::endl;
    }

    std::cout << "\nButtons found:\n";
    for (const auto& button : buttons) {
        std::cout << " - " << button << std::endl;
    }

    return 0;
}
