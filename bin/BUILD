package(default_visibility = ["//visibility:public"])

# Note: The genrule targets rename the scripts to .py generated files.
# Note: subpar does not yet support C extensions.

genrule(
    name = "bean_price_py",
    srcs = ["bean-price"],
    outs = ["bean_price.py"],
    cmd = "cat $(locations :bean-price) > $@",
)

py_binary(
    name = "bean_price",
    srcs = ["bean_price.py"],
    deps = [
        "//beancount/prices:price",
        "//beancount:loader_with_plugins",
    ],
)
