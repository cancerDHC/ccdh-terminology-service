from linkml_model import EnumDefinition, PermissibleValue
from faker import Faker
from linkml_runtime.dumpers.yaml_dumper import YAMLDumper

fake = Faker()


def test_create_enum():
    enum = EnumDefinition(name='test')
    for i in range(10):
        pv = PermissibleValue(
            text=fake.name()
        )
        enum.permissible_values[fake.name()] = pv
    ds = YAMLDumper().dumps(enum)
    assert ds is not None



