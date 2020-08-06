from collections import OrderedDict
import time
from difflib import SequenceMatcher

from django.http import JsonResponse, HttpResponse
import re
from collections import Counter


from ctrs_texts.utils import get_xml_from_unicode, get_unicode_from_xml


def view_api_regions_compare(request):
    t0 = time.time()
    parent_siglum = request.GET.get('parent', 'v1').lower()
    work_slug = request.GET.get('group', 'declaration').lower()
    text_ids = request.GET.get('texts', '').strip()
    if text_ids:
        text_ids = text_ids.split(',')
    else:
        text_ids = []

    ret = api_regions(work_slug, parent_siglum, text_ids)

    use_global_distance = True

    for region in ret['data']:
        readings = region['readings']

        # group readings
        # groups = {READING: [INDEX, FREQ]}
        # TODO: any faster/better way of achieving this?
        groups = Counter([r['t'] for r in readings])
        top_reading = groups.most_common(1)[0][0]
        groups = dict([[g[0], [i, g[1]]] for i, g in enumerate(groups.most_common())])
        present_count = max(sum([1 for r in readings if r['t']]), 2)

        for i in range(len(readings)):
            dist = 0
            if use_global_distance:
                # distance with all the rest
                for j in range(len(readings)):
                    dist += get_reading_distance(readings[i]['t'], readings[j]['t'])
            else:
                # distance with the most frequent group
                # this brings more contrasts in the colors
                # but it is arbitrary when second grp has same freq
                dist = get_reading_distance(readings[i]['t'], top_reading)
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
                r['dist'] = (r['dist'] - min_dist) * max_dist / (max_dist - min_dist)

        region['groups'] = len(groups)

    t1 = time.time()

    ret['meta']['stats'] = {
        'duration': t1-t0
    }

    return JsonResponse(ret)


def get_reading_distance(reading1, reading2):
    return get_reading_distance_levenstein(reading1, reading2)


def get_reading_distance_levenstein(reading1, reading2):
    if not(reading1 and reading2):
        # special case for missing end of V6
        return 0
    return 1 - SequenceMatcher(None, reading1, reading2).quick_ratio()


def get_reading_distance_binary(reading1, reading2):
    ret = 1

    if reading1.lower() == reading2.lower():
        return 0

    return ret


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

    texts = texts.order_by('abstracted_text__short_name')

    regions = []

    texts_count = texts.count()

    ti = 0
    for text in texts:
        ri = 0
        xml = get_xml_from_unicode(text.content, add_root=True, ishtml=True)
        for para in xml.findall('.//p'):
            number = ''
            for sentence_element in para.findall('.//span[@data-dpt="sn"]'):
                number = re.sub(r'^s-(\d+)$', r'\1',
                                sentence_element.attrib.get('data-rid', ''))

            regs = para.findall(
                './/span[@data-dpt-group="' + region_type + '"]')

            for reg in regs:
                if len(regions) <= ri:
                    regions.append({
                        'readings': [{'t': ''} for i in range(texts_count)],
                        'sentence': number,
                        'region': reg.attrib.get('data-rid', ''),
                    })
                regions[ri]['readings'][ti] = {
                    't': get_unicode_from_xml(
                        reg,
                        encoding='utf-8',
                        text_only=True,
                        remove_root=False
                    ).strip(),
                }
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
        region_index, reading, version_siglum, ms_siglum,
        ms_index, ms_abstracted
    ):
        if not(abstracted_texts) or ms_abstracted != abstracted_texts[-1]:
            abstracted_texts.append(ms_abstracted)

        if len(regions) <= region_index:
            regions.append({
                'readings': [{'t': ''} for i in range(readings_per_region)],
                # TODO
                'sentence': 1,
                # TODO
                'region': 'v1',
            })
        regions[region_index]['readings'][ms_index]['t'] = reading

    from ctrs_texts import utils
    utils.parse_mss_wregions(text_ids, ms_wreading_callback)

    return regions, abstracted_texts


def view_api_regions_all_plaintext(request):
    work_slug = request.GET.get('group', 'declaration').lower()

    region_type = 'version'

    from ctrs_texts.models import EncodedText
    texts = EncodedText.objects.filter(
        type__slug='transcription',
        abstracted_text__type__slug='manuscript',
        abstracted_text__group__group__slug__iexact=work_slug
    ).exclude(abstracted_text__short_name__startswith='HM')

    texts = texts.order_by('abstracted_text__short_name')

    ret = ''

    for text in texts:
        xml = get_xml_from_unicode(text.content, add_root=True, ishtml=True)
        for reg in xml.findall(
                    './/span[@data-dpt-group="' + region_type + '"]'):

            ret += get_unicode_from_xml(
                    reg,
                    encoding='utf-8',
                    text_only=True,
                    remove_root=False
                ).strip()+' .\n'

    return HttpResponse(ret)
