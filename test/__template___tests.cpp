#include <gmock/gmock.h>
#include <gtest/gtest.h>

namespace dummy_suit {

    class dummy_tests : public testing::Test {
    protected:
        /* ------------------------------------------------Methods--------------------------------------------------- */
        void SetUp() override {

        }

        void TearDown() override {

        }

    };

    TEST_F(dummy_tests, dummy_test) {
        EXPECT_TRUE(true);
    }

} // namespace dummy_suit
