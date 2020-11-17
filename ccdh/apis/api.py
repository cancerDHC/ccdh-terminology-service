from flask import Response, stream_with_context
from flask_restx import Api
from ccdh.apis.resources import ns as ccdh_ns

api = Api(
    title='CCDH Terminology Harmonization API',
    version='0.1',
    description='An api to facilitate the CCDH terminology value harmonization process',
)

api.add_namespace(ccdh_ns, path='/ccdh')


@api.representation('text/tab-separated-values+sssom')
def sssom(data, code, headers):
    resp = Response(stream_with_context(generate_sssom_tsv(data)))
    resp.headers.extend(headers)
    return resp


def generate_sssom_tsv(data):
    for key in data:
        if key == 'mappings':
            row_num = 0
            for mapping in data[key]:
                if row_num == 0:
                    yield '\t'.join(mapping.keys()) + '\n'
                row_num += 1
                yield '\t'.join([str(i) if i else '' for i in mapping.values()]) + '\n'
        elif key == 'curie_map':
            yield '#curie_map:\n'
            for curie, uri in data[key].items():
                yield f'#  {curie}: "{uri}"\n'
        else:
            yield f'#{key}: {data[key]}\n'
