#pragma once

#include <exception>
#include <functional>
#include <iostream>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace dee::thinking::test {

class Suite {
public:
    explicit Suite(std::string name) : name_(std::move(name)) {}

    void check(bool condition, const char* expression, const char* file, int line,
               const std::string& detail = {}) {
        ++checks_;
        if (condition) return;
        ++failures_;
        std::cerr << file << ':' << line << ": CHECK failed: " << expression;
        if (!detail.empty()) std::cerr << " (" << detail << ')';
        std::cerr << '\n';
    }

    template <class Left, class Right>
    void equal(const Left& left, const Right& right, const char* left_expr,
               const char* right_expr, const char* file, int line) {
        ++checks_;
        if (left == right) return;
        ++failures_;
        std::ostringstream detail;
        detail << left_expr << " != " << right_expr;
        std::cerr << file << ':' << line << ": CHECK_EQ failed: " << detail.str() << '\n';
    }

    template <class Function>
    void throws(Function&& function, const char* expression, const char* file, int line) {
        ++checks_;
        try {
            std::invoke(std::forward<Function>(function));
        } catch (const std::exception&) {
            return;
        } catch (...) {
            return;
        }
        ++failures_;
        std::cerr << file << ':' << line << ": CHECK_THROWS failed: " << expression << '\n';
    }

    int finish() const {
        std::cout << name_ << ": " << checks_ << " checks, " << failures_ << " failures\n";
        return failures_ == 0 ? 0 : 1;
    }

private:
    std::string name_;
    int checks_{};
    int failures_{};
};

}  // namespace dee::thinking::test

#define DEE_CHECK(SUITE, EXPR) (SUITE).check(static_cast<bool>(EXPR), #EXPR, __FILE__, __LINE__)
#define DEE_CHECK_DETAIL(SUITE, EXPR, DETAIL) \
    (SUITE).check(static_cast<bool>(EXPR), #EXPR, __FILE__, __LINE__, (DETAIL))
#define DEE_CHECK_EQ(SUITE, LEFT, RIGHT) \
    (SUITE).equal((LEFT), (RIGHT), #LEFT, #RIGHT, __FILE__, __LINE__)
#define DEE_CHECK_THROWS(SUITE, EXPR) \
    (SUITE).throws([&]() { (void)(EXPR); }, #EXPR, __FILE__, __LINE__)
