#ifndef BACKTRACE_H
#define BACKTRACE_H
#include <iostream>
#include <vector>
#include <string>

namespace trace {
// reference: https://man7.org/linux/man-pages/man3/backtrace.3.html
class Tracer {
public:
    Tracer(std::string name);
    void trace();
    void print();
    ~Tracer() {}
private:
    int64_t max_depth;
    int64_t real_size;
    const std::string func_name;
    std::vector<void*> stack;
};

}   // namespace trace
#endif

