#include <gmock/gmock.h>
#include <gtest/gtest.h>

namespace dummy_suit {

    class DummyTestFixture : public testing::Test {
    protected:
        /* ------------------------------------------------Methods--------------------------------------------------- */
        void SetUp() override {

        }

        void TearDown() override {

        }

    };

    TEST_F(DummyTestFixture, DummyTest) {
        EXPECT_TRUE(true);
    }

} // namespace dummy_suit
