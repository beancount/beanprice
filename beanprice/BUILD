package(default_visibility = ["//visibility:public"])

py_library(
    name = "__init__",
    srcs = ["__init__.py"],
)


py_library(
    name = "net_utils",
    srcs = ["net_utils.py"],
)

py_test(
    name = "net_utils_test",
    srcs = ["net_utils_test.py"],
    deps = [
        ":net_utils",
    ],
)


py_library(
    name = "price",
    srcs = ["price.py"],
    deps = [
        "//beancount/core:amount",
        "//beancount/core:data",
        "//beancount/core:number",
        "//beancount:loader",
        "//beancount/parser:printer",
        "//beancount/prices:__init__",
        "//beancount/ops:find_prices",
        "//beancount/utils:date_utils",
        "//beancount/parser:version",
    ],
)

# Again, the problem here is that this code calls the binary.
py_test(
    name = "price_test",
    srcs = ["price_test.py"],
    deps = [
        "//beancount/core:number",
        "//beancount:loader",
        "//beancount/parser:cmptest",
        "//beancount/ops:find_prices",
        "//beancount/prices:price",
        "//beancount/prices:source",
        "//beancount/prices/sources:oanda",
        "//beancount/prices/sources:yahoo",
        "//beancount/utils:test_utils",
        "//beancount:plugins_for_tests",
    ],
)

py_library(
    name = "source",
    srcs = ["source.py"],
    deps = [
        "//beancount/core:number",
    ],
)
