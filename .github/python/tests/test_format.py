# Local Imports
from cproject.format import *

def test__to_screaming_case__snake_case_string():
    assert to_screaming_case("snake_case") == "SNAKE_CASE"
    assert to_screaming_case("hello_world") == "HELLO_WORLD"
    assert to_screaming_case("abc_easy_as_123_abc") == "ABC_EASY_AS_123_ABC"

def test__to_screaming_case__camel_case_string():
    assert to_screaming_case("camelCase") == "CAMEL_CASE"
    assert to_screaming_case("helloWorld") == "HELLO_WORLD"
    assert to_screaming_case("abcEasyAs123Abc") == "ABC_EASY_AS_123_ABC"

