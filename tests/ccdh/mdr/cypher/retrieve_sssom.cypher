MATCH (c:DataElementConcept)(n:DataElement)<-[:DOMAIN_OF]-(:ValueDomain)
        <-[:PART_OF]-(p:PermissibleValue)-[:MAPS_TO]->(v:ValueMeaning)

WHERE n.context='GDC' AND n.entity='Sample' AND n.attribute='sample_type'
RETURN n.context + '.' + n.entity + '.' + n.attribute as subject_match_context,
       p.value as subject_label, p.identifier as subject_id,
       v.identifier as object_id, v.display as object_label