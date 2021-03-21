import re

from _collections import OrderedDict

from django.shortcuts import render

from ctrs_texts.models import AbstractedText, EncodedText
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string, get_template

from .. import utils


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
            ['id', text.id],
            ['type', text.type.slug],
            ['attributes', {
                'slug': text.slug,
                'name': text.name,
                'group': text.group_id,
                'siglum': text.short_name,
            }],
            ['links', {'self': text.get_api_url(request)}]
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
        ['jsonapi', '1.0'],
        ['data', texts],
        ['meta', {
            'sentence_numbers': utils.get_sentence_numbers(work)
        }]
    ])

    return JsonResponse(ret)


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
            ['id', encoded_text.id],
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
        ['jsonapi', '1.0'],
        ['meta', {
            'page': 1,
            'page_count': 1,
            'hit_count': 1,
        }],
        ['data', data],
    ])

    format = request.GET.get('format', 'json')
    if format == 'json':
        ret = JsonResponse(ret)
    elif format in ['tei', 'html']:
        content_type = 'text/html'
        if format == 'tei':
            content_type = 'application/tei'

        content_type += '; charset=utf-8'

        chunk = '\n\n'.join([
            f'\n\n<!-- {et.abstracted_text.id}' +
            f'{et.abstracted_text.type} ########## -->\n' +
            utils.get_text_chunk(
                et, view, region_type
            )
            for et in encoded_texts
        ])

        text_type_name = 'translated'

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
                'text_type_name': text_type_name,
                'api_url': encoded_text.get_api_url(request)+'?format=tei',
                'work': parents[-1],
                'body': get_tei_from_chunk(chunk),
            },
            content_type=content_type
        )
    else:
        raise Exception(
            'Invalid value for format parameter, use json, tei or html.'
        )

    return ret


def get_tei_from_chunk(html):
    html = f'<div class="chunk">{html}</div>'
    return utils.transform_xml(html, 'ctrs_texts/tei.xslt').decode('utf-8')


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
        sentence = utils.get_sentence_from_text(
            encoded_text, sentence_number
        )

        html = render_to_string('ctrs_texts/search_sentence.html', {
            'text': encoded_text.abstracted_text,
            'sentence': sentence,
            'sentence_number': 's-'+sentence_number,
            'work_slug': work_slug,
            'encoding_type': encoding_type
        })

        text_data = {
            'html': html,
        }
        texts.append(text_data)

    ret = utils.get_page_response_from_list(texts, request)

    return JsonResponse(ret)


# -------------------------------------------------------------------


def view_api_text_search_regions(request):
    '''
    '''

    # TODO: GN remove hard-coded id
    text_ids = request.GET.get('texts', '') or '520'
    text_ids = text_ids.split(',')

    annotations = utils.get_annotations_from_archetype()

    hits = [{
        'type': 'heatmap',
        'id': 0,
        'html': render_to_string('ctrs_texts/search_region.html', {}),
        'regions': utils.get_regions_with_unique_variants(text_ids),
        'annotations': annotations,
    }]

    ret = OrderedDict([
        ['jsonapi', '1.0'],
        ['meta', {
            'page': 1,
            'page_count': 1,
            'hit_count': len(hits),
        }],
        ['data', hits],
    ])

    return JsonResponse(ret)


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

    # major optimisation: load the template outside the loop
    hit_template = get_template('ctrs_texts/search_sentence.html')

    sentences = []
    for encoded_text in encoded_texts:
        for sentence in utils.search_text(encoded_text, q):
            context = {
                'text': encoded_text.abstracted_text,
                'sentence': sentence[1],
                'sentence_number': sentence[0],
                'work_slug': work_slug,
                'encoding_type': encoding_type
            }
            html = hit_template.render(context)
            # print(sentence)

            # highlight the search results
            if q:
                html = highlight_pattern.sub(
                    r'<span class="highlight">\1</span>', html)

            sentence_data = {
                'html': html,
            }

            sentences.append(sentence_data)

    ret = utils.get_page_response_from_list(sentences, request)

    ret['meta']['q'] = q

    return JsonResponse(ret)
