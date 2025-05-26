package(default_visibility = ["//visibility:public"])

py_library(
    name = "oanda",
    srcs = ["oanda.py"],
    deps = [
        "//beancount/core:number",
        "//beancount/prices:source",
        "//beancount/utils:net_utils",
    ],
)

py_test(
    name = "oanda_test",
    srcs = ["oanda_test.py"],
    deps = [
        "//beanprice:date_utils",
        "//beancount/core:number",
        "//beancount/prices:source",
        "//beancount/prices/sources:oanda",
        "//beancount/utils:net_utils",
    ],
)

py_library(
    name = "quandl",
    srcs = ["quandl.py"],
    deps = [
        "//beancount/core:number",
        "//beancount/prices:source",
    ],
)

py_test(
    name = "quandl_test",
    srcs = ["quandl_test.py"],
    deps = [
        "//beancount/core:number",
        "//beancount/prices:source",
        "//beancount/prices/sources:quandl",
        "//beanprice:date_utils",
    ],
)

py_library(
    name = "yahoo",
    srcs = ["yahoo.py"],
    deps = [
        "//beancount/core:number",
        "//beancount/prices:source",
    ],
)

py_test(
    name = "yahoo_test",
    srcs = ["yahoo_test.py"],
    deps = [
        "//beancount/core:number",
        "//beancount/prices/sources:yahoo",
        "//beanprice:date_utils",
    ],
)

py_library(
    name = "tsp",
    srcs = ["tsp.py"],
    deps = [
        "//beancount/core:number",
        "//beancount/prices:source",
    ],
)

py_test(
    name = "tsp_test",
    srcs = ["tsp_test.py"],
    deps = [
        "//beancount/core:number",
        "//beancount/prices/sources:tsp",
    ],
)

py_library(
    name = "coincap",
    srcs = ["coincap.py"],
    deps = [
        "//beancount/core:number",
        "//beancount/prices:source",
    ],
)

py_test(
    name = "coincap_test",
    srcs = ["coincap_test.py"],
    deps = [
        "//beancount/core:number",
        "//beancount/prices/sources:tsp",
    ],
)
