from flask_marshmallow import Marshmallow

ma = Marshmallow()


class DataElementSchema(ma.Schema):
    class Meta:
        fields = ('context', 'entity', 'attribute', 'type', 'description', '_links')
        ordered = True
    _links = ma.Hyperlinks({
        'self': ma.AbsoluteURLFor("harmonization_data_element", values=dict(context='<context>', entity='<entity>', attribute='<attribute>')),
        'entity': ma.AbsoluteURLFor("harmonization_data_element_list", values=dict(context='<context>', entity='<entity>')),
        'mapping': ma.AbsoluteURLFor("harmonization_data_element_mapping", values=dict(context='<context>', entity='<entity>', attribute='<attribute>'))
    })


class MappingSchema(ma.Schema):
    class Meta:
        fields = ('subject_id', 'prefix_id', 'object_id', 'subject_label', 'subject_match_field', 'object_label', 'object_match_field')
        ordered = True


class MappingSetSchema(ma.Schema):
    class Meta:
        fields = ('creator_id', 'license', 'mapping_provider', 'comment', 'curie_map', 'mappings')
        ordered = True
    curie_map = ma.Constant({
        'NCIT': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#'
    })
    mappings = ma.List(ma.Nested(MappingSchema))
