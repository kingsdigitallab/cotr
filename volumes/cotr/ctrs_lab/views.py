from collections import OrderedDict
import time

from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from collections import Counter
from ctrs_texts.utils import get_regions_from_content_xml, StringDiff


def view_api_regions_compare(request):
    t0 = time.time()
    parent_siglum = request.GET.get('parent', 'v1').lower()
    work_slug = request.GET.get('group', 'declaration').lower()
    text_ids = request.GET.get('texts', '').strip()
    if text_ids:
        text_ids = text_ids.split(',')
    else:
        text_ids = []
    diff_method = request.GET.get('diff', 'difflib_quick_ratio').strip()
    diff_unit = request.GET.get('unit', 'region').strip()

    # call the region api
    ret = api_regions(work_slug, parent_siglum, text_ids)

    texts_count = len(ret['meta']['sources'])

    regions = ret['data']
    if diff_unit == 'sentence':
        # merge regions by sentence
        for i in range(len(regions)-2, -1, -1):
            if regions[i + 1]['sentence'] == regions[i]['sentence']:
                for j in range(0, texts_count):
                    reading = regions[i+1]['readings'][j]['t'].strip()
                    if reading:
                        reading = '… ' + reading
                    regions[i]['readings'][j]['t'] += reading
                del regions[i+1]

    use_global_distance = True

    # initialise the diff matrix
    diff_matrix = [[0 for t in range(texts_count)] for t in range(texts_count)]
    diff_matrix_max = 0

    differ = StringDiff(diff_method)

    for region in regions:
        readings = region['readings']

        # group readings
        # groups = {READING: [INDEX, FREQ]}
        # TODO: any faster/better way of achieving this?
        groups = Counter([r['t'] for r in readings])
        top_reading = groups.most_common(1)[0][0]
        groups = dict([
            [g[0], [i, g[1]]]
            for i, g
            in enumerate(groups.most_common())
        ])
        present_count = max(sum([1 for r in readings if r['t']]), 2)

        # assign distance to each reading
        # TODO: we should do that at the group level, not for each reading
        for i in range(len(readings)):
            dist = 0
            if use_global_distance:
                # distance with all the rest
                for j in range(len(readings)):
                    rs = [readings[j]['t'], readings[i]['t']]
                    adist = differ.get_distance(*rs)
                    dist += adist
                    diff_matrix[i][j] += adist
                    diff_matrix_max = max(diff_matrix[i][j], diff_matrix_max)
            else:
                # distance with the most frequent group
                # this brings more contrasts in the colors
                # but it is arbitrary when second grp has same freq
                dist = differ.get_distance(readings[i]['t'], top_reading)
            if use_global_distance:
                readings[i]['dist'] = dist / (present_count - 1)
            else:
                readings[i]['dist'] = dist

            readings[i]['grp'] = groups[readings[i]['t']][0]

        dists = [r['dist'] for r in readings if r['dist']] or [0]
        min_dist = min(dists)
        max_dist = max(dists)

        if max_dist != min_dist:
            for r in readings:
                # rescale between 0 and max (to get more contrast)
                r['dist'] = round(
                    (r['dist'] - min_dist) * max_dist / (max_dist - min_dist),
                    3
                )

        region['groups'] = len(groups)

    t1 = time.time()

    ret['meta']['stats'] = {
        'duration': t1-t0
    }

    ret['meta']['diff_matrix'] = diff_matrix
    ret['meta']['diff_matrix_max'] = diff_matrix_max

    return JsonResponse(ret)


def view_api_regions(request):
    # todo: error management
    work_slug = request.GET.get('group', 'declaration').lower()
    parent_siglum = request.GET.get('parent', 'v1').lower()
    text_ids = request.GET.get('texts', '').split(',')

    ret = api_regions(work_slug, parent_siglum, text_ids)

    return JsonResponse(ret)


def api_regions(work_slug='declaration', parent_siglum='v1', text_ids=None):

    if parent_siglum == 'custom':
        regions, texts = api_regions_many_parents(text_ids)
    else:
        regions, texts = api_regions_one_parent(work_slug, parent_siglum)

    # format is inspired by Guthenberg Model (see CollateX)
    # However the table contains groups of tokens (rather than individual ones)
    # and only the groups where at least one witness disagrees.
    ret = [
        ['meta', {
            'sources': [
                {
                    'siglum_parent': abstracted_text.group.short_name,
                    'siglum': abstracted_text.short_name,
                    'title': str(abstracted_text),
                    'id': abstracted_text.pk,
                }
                for abstracted_text in texts
            ]}],
        ['data', regions],
    ]
    ret = OrderedDict(ret)

    return ret


def api_regions_one_parent(work_slug='declaration', parent_siglum='v1'):
    region_type = 'version'

    from ctrs_texts.models import EncodedText
    texts = EncodedText.objects.filter(
        type__slug='transcription',
    ).exclude(abstracted_text__short_name__startswith='HM')

    if parent_siglum == 'w':
        region_type = 'work'
        texts = texts.filter(abstracted_text__group__slug__iexact=work_slug)
    else:
        texts = texts.filter(abstracted_text__group__group__slug__iexact=work_slug)
        texts = texts.filter(abstracted_text__group__short_name__iexact=parent_siglum)

    texts.select_related('abstracted_text__group')
    texts = texts.order_by('abstracted_text__short_name')
    texts = list(texts)

    regions = []

    ti = 0
    for text in texts:
        ri = 0
        for reg in get_regions_from_content_xml(text.content_xml, region_type):
            if len(regions) <= ri:
                regions.append({
                    'readings': [{'t': ''} for i in range(len(texts))],
                    'sentence': reg['sentence'],
                    'region': reg['region'],
                })
            regions[ri]['readings'][ti] = {'t': reg['text']}
            ri += 1

        ti += 1

    return regions, [t.abstracted_text for t in texts]


def api_regions_many_parents(text_ids=None):

    regions = []
    abstracted_texts = []

    # pre-allocate the reading (more efficient & avoids holes)
    from ctrs_texts.models import AbstractedText
    readings_per_region = AbstractedText.objects.filter(
        type__slug='manuscript',
        id__in=text_ids,
    ).count()

    # reading callback to populate regions
    def ms_wreading_callback(
        region_data, version_siglum, ms_siglum,
        ms_index, ms_abstracted
    ):
        if not(abstracted_texts) or ms_abstracted != abstracted_texts[-1]:
            abstracted_texts.append(ms_abstracted)

        if len(regions) <= region_data['index']:
            regions.append({
                'readings': [{'t': ''} for i in range(readings_per_region)],
                'sentence': region_data['sentence'],
                'region': region_data['region'],
            })
        regions[region_data['index']]['readings'][ms_index]['t'] = \
            region_data['text']

    from ctrs_texts import utils
    utils.parse_mss_wregions(text_ids, ms_wreading_callback)

    return regions, abstracted_texts


def view_api_regions_all_plaintext(request):
    '''returns all the tokens in all teh regions.
    This is used to extract embeddings from word2vec models.
    TODO: export also the w-regions from the versions.
    '''
    work_slug = request.GET.get('group', 'declaration').lower()

    ret = ''

    from ctrs_texts.models import EncodedText
    texts = EncodedText.objects.filter(
        Q(type__slug='transcription') &
        Q(abstracted_text__group__slug__iexact=work_slug) |
        Q(abstracted_text__group__group__slug__iexact=work_slug)
    ).exclude(
        abstracted_text__short_name__startswith='HM',
        abstracted_text__type__slug='work',
    ).select_related('abstracted_text__type')

    texts = texts.order_by('abstracted_text__short_name')

    for text in texts:
        # ret += str(text)
        ret += ' .\n'.join([
            reg['text']
            for reg
            in get_regions_from_content_xml(
                text.content_xml,
                'version'
                if text.abstracted_text.type.slug == 'manuscript'
                else 'work'
            )
        ])
        ret += ' .\n'

    return HttpResponse(ret)
