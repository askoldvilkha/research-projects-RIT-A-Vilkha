#!/usr/bin/env python

from __future__ import print_function

import os.path
import pkgutil
import re
import sys
from importlib import import_module

import pytest

# Set environment variables as needed
import os
if not('GW_SURROGATE' in os.environ.keys()):
   os.environ["GW_SURROGATE"]=''
if not('EOB_BASE' in os.environ.keys()):
   os.environ["EOB_BASE"]=''


pkgname = "RIFT"
package = import_module(pkgname)

# files to ignore
EXCLUDE = re.compile("({})".format("|".join([
    r"\Atests\Z",
    r"\Atest_",
    r"\Aconftest\Z",
    r"\A_",
])))

# ignorable failures
IGNORE = re.compile("({})".format("|".join([
    r"\ANo module named torch\Z",
    r"\ANo module named cupy\Z",
])))


def iter_all_modules(path, exclude=EXCLUDE):
    name = os.path.basename(path)
    for _, modname, ispkg in pkgutil.iter_modules(path=[path]):
        if exclude and exclude.search(modname):
            continue
        yield "{}.{}".format(name, modname)
        if ispkg:
            for mod2 in iter_all_modules(os.path.join(path, modname), exclude=exclude):
                yield "{}.{}".format(name, mod2)


@pytest.mark.parametrize("modname", iter_all_modules(package.__path__[0]))
def test_import(modname):
    try:
        import_module(modname)
    except Exception as exc:
        if IGNORE.search(str(exc)):
            pytest.skip(str(exc))
        raise


if __name__ == "__main__":
    if "-v" not in " ".join(sys.argv[1:]):  # default to verbose
        sys.argv.append("-v")
    sys.argv.append("-rs")
    sys.exit(pytest.main(args=[__file__] + sys.argv[1:]))