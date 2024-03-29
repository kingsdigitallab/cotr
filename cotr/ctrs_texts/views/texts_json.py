import re

from _collections import OrderedDict

from django.shortcuts import render
from django.urls import reverse

from ctrs_texts.models import AbstractedText, EncodedText
from django.db.models import Q

from .. import utils
from ..utils import get_jsonapi_response


def view_api_texts(request):
    '''
    Returns json with a list of AbstractedTexts.
    For each text, some metadata.

    Output format must follow https://jsonapi.org/

    Used for both Text Viewer & Search page

    The list is FLAT.
    Information about hierarchy (MS->V->W)
    is conveyed with the 'group' field.

    http://localhost:8000/api/texts/?group=declaration
    '''

    # returns all texts by default
    abstracted_texts = AbstractedText.objects.all()

    # returns all texts related to a parent/group
    # if ?group=<text.slug>|<text.id> is passed.
    group_slug = request.GET.get('group', None)
    if group_slug:
        abstracted_texts = abstracted_texts.filter(
            Q(slug=group_slug) | Q(group__slug=group_slug) | Q(
                group__group__slug=group_slug
            )
        )

    abstracted_texts = abstracted_texts.exclude(
        short_name__in=['HM1', 'HM2']
    ).select_related(
        'manuscript__repository', 'type'
    ).order_by(
        '-type__slug', 'short_name', 'locus'
    )

    texts = []
    work = None
    for text in abstracted_texts:
        if text.slug == group_slug:
            work = text
        text_data = [
            ['id', f'{text.id}'],
            ['type', text.type.slug],
            ['attributes', {
                'slug': text.slug,
                'name': text.name,
                'group': text.group_id,
                'siglum': text.short_name,
            }],
            ['links', {
                'self': text.get_api_url(request),
                'related': {
                    'href': text.get_api_url(request) + '?format=tei',
                    'title': 'TEI format',
                }
            }]
        ]
        text_data = OrderedDict(text_data)
        if text.manuscript:
            text_data['attributes'].update({
                'city': text.manuscript.repository.city or '',
                'repository': text.manuscript.repository.name,
                'shelfmark': text.manuscript.shelfmark,
                'locus': text.locus,
            })

        texts.append(text_data)

    ret = OrderedDict([
        ['data', texts],
        ['meta', {
            'sentence_numbers': utils.get_sentence_numbers(work)
        }]
    ])

    return get_jsonapi_response(ret, request)


def view_api_text_chunk(
    request, text_slug, view='transcription', unit='', location=''
):
    '''
    Returns json with the requested data chunk.
    A chunk can be anything: XML, json, html, ...
    http://localhost:8000/api/texts/490/transcription/whole/whole/
    '''
    slugs = text_slug.split(',')

    encoded_type = view
    if view in ['histogram']:
        encoded_type = 'transcription'

    if slugs and len(slugs) == 1 and slugs[0].lower() == 'all':
        filters = {}
    else:
        try:
            filters = {'abstracted_text__id__in': [int(s) for s in slugs]}
        except ValueError:
            filters = {'abstracted_text__slug__in': slugs}

    encoded_texts = EncodedText.objects.filter(
        **filters
    ).filter(type__slug=encoded_type)

    data = {}
    if encoded_texts.count() > 0:
        # individual chunk
        encoded_text = encoded_texts[0]

        region_type = encoded_text.abstracted_text.type.slug
        if region_type not in ['work', 'version']:
            region_type = 'version'

        data = OrderedDict([
            ['id', f'{encoded_text.id}'],
            ['type', 'text_chunk'],
            ['links', {'self': encoded_text.get_api_url(request)}],
            ['attributes', OrderedDict([
                ['view', view],
                ['unit', unit],
                ['location', location],
                ['value_max', 17],
                ['region_type', region_type],
                ['description', 'number of unsettled regions per sentence'],
                [
                    'can_show_non_standardised',
                    encoded_text.can_show_non_standardised()
                ],
                ['chunk', utils.get_text_chunk(
                    encoded_text, view, region_type)],
            ])],
        ])

    ret = OrderedDict([
        ['meta', {
            'page': 1,
            'page_count': 1,
            'hit_count': 1,
        }],
        ['data', data],
    ])

    format = request.GET.get('format', 'json')
    if format == 'json':
        ret = get_jsonapi_response(ret)

    elif format in ['tei', 'html']:
        content_type = 'text/html'
        if format == 'tei':
            content_type = 'application/tei'

        content_type += '; charset=utf-8'

        chunk = '\n\n'.join([
            f'\n\n <!-- {et.abstracted_text.get_top_parent().name} > ' +
            f'{et.abstracted_text.id} ' +
            f'({et.abstracted_text.type}) ########## -->\n\n' +
            utils.get_text_chunk(
                et, view, region_type
            )
            for et in encoded_texts
        ])

        language = 'English'
        if encoded_text.type.slug == 'transcription':
            language = 'Latin'

        # get parents = version, work
        parents = []
        p = encoded_text.abstracted_text
        while p:
            parents.append(p)
            p = p.group

        ret = render(
            request,
            'ctrs_texts/tei.xml',
            {
                'text': encoded_text,
                'text_type_name': language + ' edition',
                'api_url': encoded_text.get_api_url(request)+'?format=tei',
                'work': parents[-1],
                'body': get_tei_from_chunk(chunk),
            },
            content_type=content_type
        )
        if format in ['tei']:
            language
            ret['Content-Disposition'] = (
                'attachment; filename="cotr-' +
                f'{encoded_text.abstracted_text.id}-' +
                f'{encoded_text.abstracted_text.slug}-' +
                f'{language.lower()}.xml"'
            )
    else:
        raise Exception(
            'Invalid value for format parameter, use json, tei or html.'
        )

    return ret


def get_tei_from_chunk(html):
    html = f'<body>{html}</body>'
    ret = utils.transform_xml(html, 'ctrs_texts/tei.xslt').decode('utf-8')

    # group sequences of <s> under <ab>
    ret = re.sub(r'<s\b', '<ab><s', ret)
    ret = re.sub(r'</s>', '</s></ab>', ret)
    ret = re.sub(r'</ab>\s*<ab>', '', ret)

    return ret


# -------------------------------------------------------------------


def view_api_text_search_regions(request):
    '''
    Returns the regions and bounding boxes (annotation)
    to be represented as a heatmap over the manuscript image.
    '''

    # TODO: GN remove hard-coded id
    text_ids = request.GET.get('texts', '') or '520'
    text_ids = text_ids.split(',')

    annotations = utils.get_annotations_from_archetype()

    hits = []
    for region in utils.get_regions_with_unique_variants(text_ids):
        annotation = annotations.get(region['key'], {})
        rects = annotation.get('rects', [])
        hit = {
            'type': 'region',
            'id': region['key'],
            'attributes': {
                'rects': rects,
                'readings': region['readings'],
            }
        }
        hits.append(hit)

    ret = OrderedDict([
        ['meta', {
            'page': 1,
            'page_count': 1,
            'hit_count': len(hits),
        }],
        ['data', hits],
    ])

    return utils.get_jsonapi_response(ret, request)


# -------------------------------------------------------------------


def view_api_text_search_sentences(request):
    '''
    '''

    text_ids = request.GET.get('texts', '') or '0'
    text_ids = text_ids.split(',')
    sentence_number = request.GET.get('sn', '1')
    encoding_type = request.GET.get('et', 'transcription')
    work_slug = request.GET.get('group', 'declaration').strip()

    encoded_texts = EncodedText.objects.filter(
        abstracted_text__id__in=text_ids,
        type__slug=encoding_type
    ).order_by(
        'abstracted_text__group__short_name',
        'abstracted_text__short_name'
    )

    texts = []
    for encoded_text in encoded_texts:
        text = encoded_text.abstracted_text

        sentence = utils.get_sentence_from_text(
            encoded_text, sentence_number
        )

        texts.append(get_sentence_data(
            text, sentence, sentence_number, encoding_type, work_slug
        ))

    ret = utils.get_page_response_from_list(texts, request)

    return utils.get_jsonapi_response(ret, request)


def get_sentence_data(text, sentence, sentence_number, encoding_type,
                      work_slug, sentence_code=None):
    if sentence_code is None:
        sentence_code = 's-' + sentence_number
    if sentence_number is None:
        sentence_number = sentence_code.split('-')[-1]

    sentence_id = f'{text.id}:{encoding_type}@{sentence_code}'
    ret = OrderedDict([
        ['id', sentence_id],
        ['type', 'sentence'],
        ['links', {
            'viewer': (
                reverse('text_viewer') +
                f'?group={work_slug}&blocks={sentence_id}'
            )
        }],
        ['attributes', {
            'text': {
                'id': text.id,
                'type': text.type.slug,
                'short_name': text.short_name,
                'name': text.name,
                'work_slug': work_slug,
                'encoding_type': encoding_type,
            },
            'sentence': sentence,
            'sentence_number': sentence_number,
        }],
    ])

    return ret


def view_api_text_search_text(request):
    q = request.GET.get('q', '').strip()

    work_slug = request.GET.get('group', 'declaration').strip()

    text_ids = request.GET.get('texts', None)
    encoding_type = request.GET.get('et', 'transcription')

    encoded_texts = EncodedText.objects.filter(type__slug=encoding_type)

    if text_ids:
        text_ids = text_ids.split(',')
        encoded_texts = encoded_texts.filter(abstracted_text__id__in=text_ids)

    # match only words that begin with the search query
    # needs to use PSQL regex syntax, not Python's
    # https://www.postgresql.org/docs/9.4/functions-matching.html#POSIX-CONSTRAINT-ESCAPES-TABLE
    encoded_texts = encoded_texts.filter(
        plain__iregex=r'\m{}'.format(q)
    ).select_related(
        'abstracted_text',
        'abstracted_text__type'
    ).order_by(
        'abstracted_text__group__short_name',
        'abstracted_text__short_name'
    )

    search_pattern = utils.get_text_search_pattern()
    escaped = '|'.join([search_pattern.format(w) for w in q.split()])
    # pattern to highlight the search results
    # https://regexr.com/532qa
    highlight_pattern = re.compile(
        '({})(?=(?:[^>]|<[^>]*>)*$)'.format(escaped), re.I)

    sentences = []
    for encoded_text in encoded_texts:
        text = encoded_text.abstracted_text
        for sentence_code, sentence in utils.search_text(encoded_text, q):

            # highlight the search results
            if q:
                sentence = highlight_pattern.sub(
                    r'<span class="highlight">\1</span>', sentence)

            sentences.append(get_sentence_data(
                text, sentence, None, encoding_type, work_slug, sentence_code
            ))

    ret = utils.get_page_response_from_list(sentences, request)

    ret['meta']['q'] = q

    # return JsonResponse(ret)
    return utils.get_jsonapi_response(ret, request)
