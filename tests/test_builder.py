import pytest

from jsec.utils import cd
from jsec.builder import BaseBuilder
from jsec.settings import TESTDIR


def test_building():
    builder = BaseBuilder(workdir=TESTDIR / "test_simple_applet", version="jc211")
    proc = builder.execute(BaseBuilder.COMMANDS.build)

    assert 0 == proc.returncode