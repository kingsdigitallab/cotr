from collections import OrderedDict
from difflib import SequenceMatcher

from django.http import JsonResponse, HttpResponse
import re
from collections import Counter


from ctrs_texts.utils import get_xml_from_unicode, get_unicode_from_xml


def view_api_regions_compare(request):
    parent_siglum = request.GET.get('parent', 'v1').lower()
    work_slug = request.GET.get('group', 'declaration').lower()

    ret = api_regions(parent_siglum, work_slug)

    use_global_distance = True

    for region in ret['data']:
        readings = region['readings']

        # group readings
        # groups = {READING: [INDEX, FREQ]}
        # TODO: any faster/better way of achieving this?
        groups = Counter([r['t'] for r in readings])
        top_reading = groups.most_common(1)[0][0]
        groups = dict([[g[0], [i, g[1]]] for i, g in enumerate(groups.most_common())])

        min_dist = 1000
        max_dist = 0

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
                readings[i]['dist'] = dist / (len(readings) - 1)
            else:
                readings[i]['dist'] = dist
            min_dist = min(readings[i]['dist'], min_dist)
            max_dist = max(readings[i]['dist'], max_dist)
            readings[i]['grp'] = groups[readings[i]['t']][0]

        if max_dist != min_dist:
            for r in readings:
                # rescale between 0 and max
                r['dist'] = (r['dist'] - min_dist) * max_dist / (max_dist - min_dist)

        region['groups'] = len(groups)

    return JsonResponse(ret)


def get_reading_distance(reading1, reading2):
    return get_reading_distance_levenstein(reading1, reading2)


def get_reading_distance_levenstein(reading1, reading2):
    return 1 - SequenceMatcher(None, reading1, reading2).quick_ratio()


def get_reading_distance_binary(reading1, reading2):
    ret = 1

    if reading1.lower() == reading2.lower():
        return 0

    return ret


def view_api_regions(request):
    # todo: error management
    parent_siglum = request.GET.get('parent', 'v1').lower()
    work_slug = request.GET.get('group', 'declaration').lower()

    ret = api_regions(parent_siglum, work_slug)

    return JsonResponse(ret)


def api_regions(parent_siglum='v1', work_slug='declaration'):
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

    # format is inspired by Guthenberg Model (see CollateX)
    # However the table contains groups of tokens (rather than individual ones)
    # and only the groups where at least one witness disagrees.
    ret = OrderedDict([
        ['meta', {
            'sources': [
                {
                    'siglum': t.abstracted_text.short_name,
                    'title': str(t.abstracted_text),
                    'id': t.abstracted_text.pk,
                }
                for t in texts
            ]}],
        ['data', regions],
    ])

    return ret


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
