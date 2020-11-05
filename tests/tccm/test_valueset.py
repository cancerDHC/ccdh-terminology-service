from tccm.valueset.valuesetdefinition import *
import pytest


def test_valueset_def():
    vsd = ValueSetDefinition()
    vsd.entry = []
    entry = ValueSetDefinitionEntry()
    de = FormalDefinition()
    de.codeSystem = CompleteCodeSystemReference()
    entry.include
