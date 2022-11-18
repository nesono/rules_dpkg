workspace(name = "rules_dpgk")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "com_github_ali5h_rules_pip",
    sha256 = "10285a51c6624519bd2ae079ea079eb97fe7d909003fc999b2d4bb28252057c8",
    strip_prefix = "rules_pip-4.0.0",
    urls = ["https://github.com/ali5h/rules_pip/archive/4.0.0.tar.gz"],
)

load("@com_github_ali5h_rules_pip//:defs.bzl", "pip_import")

pip_import(
    name = "pip_deps",

    # default value is "python"
    python_interpreter = "python3",
    requirements = "//tools/dpkg:requirements.txt",

    # or specify a python runtime label
    # python_runtime="@python3_x86_64//:bin/python3",

    # set compile to true only if requirements files is not already compiled
    # compile = True
)

load("@pip_deps//:requirements.bzl", "pip_install")

pip_install()
