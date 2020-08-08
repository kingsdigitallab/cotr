import json
import os
import re
from collections import Counter
from difflib import SequenceMatcher

import lxml.etree as ET
from _collections import OrderedDict
from django.conf import settings
from django.utils.text import slugify
from lxml import html


class StringDiff:
    """
    Helper class to compare two strings efficiently
    """

    def __init__(self, method='difflib_quick_ratio'):
        self.method = method
        self.difflib_matcher = SequenceMatcher(None, '', '', False)
        self._diff_cache = {}

    def get_distance(self, s1, s2):
        """Returns 0.0 if s1 == s2; 1.0 if totally different"""
        if not(s1 and s2):
            return 0
        if 1:
            # TODO: optimise
            s1 = s1.lower()
            s2 = s2.lower()
        if s1 == s2:
            return 0

        ret = 1

        if self.method != 'binary':
            cache_key = s1 + '|' + s2
            ret = self._diff_cache.get(cache_key, None)
            if ret is None:
                self.difflib_matcher.set_seqs(s1, s2)

                if self.method == 'difflib_quick_ratio':
                    ret = self.difflib_matcher.quick_ratio()
                elif self.method == 'difflib_ratio':
                    ret = self.difflib_matcher.ratio()

                ret = 1 - ret
                self._diff_cache[cache_key] = ret
                self._diff_cache[s2+'|'+s1] = ret

        return ret


def get_regions_from_content_xml(content_xml, region_type='version'):
    '''content_xml a lxml etree node for the text
    For each region of type region_type, yields
    {
        'xml': the xml element for that region,
        'text': the plain text content of that region,
        'sentence': the sentence number/code,
        'region': the id of the region,
        'index': index of the region,
    }
    '''
    reg_pattern = './/span[@data-dpt-group="' + region_type + '"]'
    ri = 0
    for para in content_xml.findall('.//p'):
        number = ''
        sentence_element = para.find('.//span[@data-dpt="sn"]')
        if sentence_element is not None:
            number = re.sub(
                r'^s-(\d+)$', r'\1',
                sentence_element.attrib.get('data-rid', '')
            )

        for reg in para.iterfind(reg_pattern):
            yield {
                'xml': reg,
                'text': get_unicode_from_xml(reg, text_only=True).strip(),
                'sentence': number,
                'region': reg.attrib.get('data-rid', ''),
                'index': ri,
            }
            ri += 1


def get_xml_from_unicode(document, ishtml=False, add_root=False):
    # document = a unicode object containing the document
    # ishtml = True will be more lenient about the XML format
    #          and won't complain about named entities (&nbsp;)
    # add_root = True to surround the given document string with
    #         <root> element before parsing. In case there is no
    #        single containing element.

    document = document or ''

    if add_root:
        document = r'<root>%s</root>' % document

    parser = None
    if ishtml:
        from io import StringIO
        parser = ET.HTMLParser()
        # we use StringIO otherwise we'll have encoding issues
        d = StringIO(document)
    else:
        from io import BytesIO
        d = BytesIO(document.encode('utf-8'))
    ret = ET.parse(d, parser)

    return ret


def get_unicode_from_xml(xmltree, encoding='utf-8',
                         text_only=False, remove_root=False):
    # if text_only = True => strip all XML tags
    # EXCLUDE the TAIL
    if text_only:
        return get_xml_element_text(xmltree)
    else:
        # import regex as re

        if hasattr(xmltree, 'getroot'):
            xmltree = xmltree.getroot()
        ret = ET.tostring(xmltree, encoding=encoding).decode('utf-8')
        if xmltree.tail is not None and ret[0] == '<':
            # remove the tail
            ret = re.sub(r'[^>]+$', '', ret)

        if remove_root:
            r = [
                ret.find('<root>'),
                ret.rfind('</root>')
            ]
            if r[0] > 0 and r[1] > r[0]:
                ret = ret[r[0] + len('<root>'):r[1]]

        return ret


def get_xml_element_text(element):
    # returns all the text within element and its descendants
    # WITHOUT the TAIL.
    #
    # element is etree Element object
    #
    # '<r>t0<e1>t1<e2>t2</e2>t3</e1>t4</r>'
    # e = (xml.findall(el))[0]
    # e.text => t1
    # e.tail => t4 (! part of e1)
    # get_xml_element_text(element) => 't1t2t3'

    return ''.join(element.itertext())


def append_xml_element(
    parent_element, tag_name, text=None, prepend=False, **attributes
):
    '''
    Create a new xml element and add it to parent_element.

    If an attribute name is a python reserved word (e.g. class),
    just add _ at the end (e.g. class_).

    Note that _ in attribute name is converted to -.
    E.g. data_something => data-something
    '''

    if attributes:
        attributes = {
            k.rstrip('_').replace('_', '-'): v
            for k, v
            in attributes.items()
        }

    ret = ET.Element(tag_name, attrib=attributes)
    if prepend:
        parent_element.insert(0, ret)
        ret.tail = parent_element.text
        parent_element.text = None
    else:
        parent_element.append(ret)

    if text is not None:
        ret.text = text

    return ret


def get_sentence_from_text(encoded_text, sentence_number):
    ret = ''

    # ac-139 we remove all auxiliary sentences first
    content = re.sub(
        '<p[^>]+data-dpt-type="auxiliary".*?</p>',
        '',
        encoded_text.content
    )

    pattern = ''.join([
        r'(?usi)(<p>\s*<span[^>]+data-rid="s-',
        re.escape(str(sentence_number)),
        r'".*?</p>)\s*(<p>\s*<span data-dpt="[cs]n"|$)'
    ])

    match = re.search(pattern, content)

    if match:
        ret = remove_separator_paragraphs(match.group(1))

    return ret


def remove_separator_paragraphs(text_string):
    '''Return the text_string without
    separating pragraph such as <p>___</p>'''
    return re.sub(r'(?i)<p>[^a-z<]*</p>', '', text_string)


def get_regions_with_unique_variants(text_ids):
    ret = []

    # build ret: list of all wregions in HM1, in their order of appearance.
    # for each region, ['key'] is a key that will match the annotation key
    # see _get_annotations_from_archetype()
    wpattern = './/span[@data-dpt-group="work"]'

    keys_freq = Counter()

    from ctrs_texts.models import EncodedText

    for encoded_text in EncodedText.objects.filter(
        abstracted_text__short_name__in=['HM1'],
        type__slug='transcription'
    ):
        content = encoded_text.content_xml
        for wregion in content.findall(wpattern):
            key = slugify(get_unicode_from_xml(wregion, text_only=True))[:20]
            key = key or '∅'
            keys_freq.update([key])
            freq = keys_freq[key]
            if freq > 1:
                key = '{}:{}'.format(key, freq)
            ret.append({
                'key': key,
                'readings': OrderedDict()
            })

    def ms_wreading_callback(
        region_data, version_siglum, ms_siglum,
        ms_index, ms_abstracted
    ):
        region_index = region_data['index']
        reading = region_data['text']
        if region_index < len(ret):
            if reading not in ret[region_index]['readings']:
                ret[region_index]['readings'][reading] = []
            ret[region_index]['readings'][reading].append(
                [version_siglum, ms_siglum]
            )
        else:
            print('WARNING: w-region #{} of {} not found in {}'.format(
                region_index, version_siglum, 'heatmap text (HM1)'
            ))

    parse_mss_wregions(text_ids, ms_wreading_callback)

    return ret


def parse_mss_wregions(text_ids, ms_wreading_callback):
    '''
    text_ids: a list of mss ids (AbstractedText)
    wregions_callback: a callback with the signature:
        (region_data, version_siglum, ms_siglum, ms_index)

    region_data = see get_regions_from_content_xml()

    For each MS in text_ids, the callback is called on all the wregion
    of its parent version.
    The callback is receives info about a wregion
    where the + sign (nested vregion) has been replaced
    with the reading from the MS.

    e.g.
        wregion i in Version = [abc [+:vregion j] cde]
        vregion j in MS k    = [xyz]
        => reading           = [abc xyz cde]
        region_index         = i
        ms_index             = k
    '''

    # for each selected manuscript, get its parent w-regions
    # where all v-regions have been substituted with the content from the MS

    # TODO: simplify the code

    if not text_ids:
        return

    vpattern = './/span[@data-dpt-group="version"]'

    ms_index = 0

    # get all the requested texts (encoded)
    from ctrs_texts.models import EncodedText
    encoded_texts = EncodedText.objects.filter(
        abstracted_text_id__in=text_ids,
        type__slug='transcription',
        abstracted_text__type__slug='manuscript',
    ).order_by(
       'abstracted_text__group__short_name',
       'abstracted_text__short_name'
    ).select_related('abstracted_text__group')

    # get all their parents (encoded version)
    encoded_parents = {
        ep.abstracted_text_id: {
            'encoded_text': ep,
            'content_xml': ep.content_xml,
        }
        for ep in
        EncodedText.objects.filter(
            type__slug='transcription',
            abstracted_text_id__in=[
                et.abstracted_text.group_id for et in encoded_texts
            ],
        ).select_related('abstracted_text')
    }
    for ep in encoded_parents.values():
        ep['vregions'] = [
            vregion if vregion.clear(keep_tail=True) else vregion
            for vregion in
            ep['content_xml'].findall(vpattern)
        ]

        ep['wregions'] = list(get_regions_from_content_xml(ep['content_xml'], 'work'))

    for encoded_text in encoded_texts:
        ms_abstracted = encoded_text.abstracted_text
        member_siglum = ms_abstracted.short_name

        # get vregions from member
        vregions = []
        content = encoded_text.content_xml
        for vregion in content.findall(vpattern):
            vregions.append(get_unicode_from_xml(vregion, text_only=True))

        # get parent
        parent = encoded_parents[ms_abstracted.group_id]

        parent_siglum = parent['encoded_text'].abstracted_text.short_name

        # replace vregion in parent with text from member
        for i, vregion in enumerate(parent['vregions']):
            if i < len(vregions):
                vregion.text = vregions[i]
            else:
                print('WARNING: v-region #{} of {} not found in {}'.format(
                    i, encoded_text, parent['encoded_text'])
                )

        # get the text of all the wregions from parent
        for i, wregion in enumerate(parent['wregions']):
            wregion['text'] = get_unicode_from_xml(
                wregion['xml'], text_only=True
            ).strip()
            ms_wreading_callback(
                wregion, parent_siglum, member_siglum,
                ms_index, ms_abstracted
            )

        ms_index += 1


def get_annotations_from_archetype():
    '''
    Returns a simplified dictionary of annotations from archetype api.

    ret['principem-regem'] = {
        rects: [
            [
                [994.4017594070153,2871.1062469927056]],
                [1201.1631251142062,2825.8702290932333]
            ]
        ]
    },
    '''
    ret = {}

    annotation_path = os.path.join(
        settings.MEDIA_ROOT, 'arch-annotations.json'
    )
    with open(annotation_path, 'rt') as fh:
        api_response = json.load(fh)

    for a in api_response['results']:
        geo_json = json.loads(a['geo_json'])

        # skip 'ghost' annotations (no properties)
        if not geo_json['properties']:
            continue

        # extract bounds and text from geo_json
        key = ':'.join([
            e[1] for e in
            geo_json['properties']['elementid']
            if e[0].startswith('@')
        ])

        if key not in ret:
            ret[key] = {'rects': []}

        ret[key]['rects'].append([
            geo_json['geometry']['coordinates'][0][0],
            geo_json['geometry']['coordinates'][0][2]
        ])

    return ret


def get_text_chunk(encoded_text, view, region_type):
    if view in ['histogram']:
        ret = get_text_viz_data(encoded_text, region_type)
    else:
        ret = remove_separator_paragraphs(
            encoded_text.get_content_with_readings()
        )

    return ret


def get_text_viz_data(encoded_text, region_type):
    '''Returns a list of sentences; for each one, the number of regions
    Also called 'histogram' '''
    ret = []

    xml = get_xml_from_unicode(encoded_text.content, add_root=True, ishtml=True)
    for para in xml.findall('.//p'):
        for sentence_element in para.findall('.//span[@data-dpt="sn"]'):
            number = re.sub(r'^s-(\d+)$', r'\1',
                            sentence_element.attrib.get('data-rid', ''))
            if not number:
                continue

            regions = para.findall(
                './/span[@data-dpt-group="' + region_type + '"]')

            res = {
                'key': number,
                'value': len(regions),
            }
            ret.append(res)

    return ret


def search_text(encoded_text, query=''):
    '''Returns a list of sentences that contains the 'query' pattern.
    Each entry in the list is a tuple [sentence_id, sentence_string]
    Where 'sentence_string' is a string of the complete html for the sentence.
    'sentence_id' is the value of the data-rid attribute, e.g. s-1.1 for
    sentence 1.1.
    '''
    if not encoded_text:
        return None

    query = query.lower()

    lowercase = (
        'translate(., '
        '"ABCDEFGHIJKLMNOPQRSTUVWXYZ", '
        '"abcdefghijklmnopqrstuvwxyz")'
    )
    search_pattern = get_text_search_pattern()
    search_xpath = (
        r'.//p[re:match(normalize-space({}), "{}", "i")]'.format(
            lowercase, search_pattern.format(query))
    )

    xml = get_xml_from_unicode(
        encoded_text.content, ishtml=True, add_root=True
    )

    results = []
    for sentence in xml.xpath(
            search_xpath,
            namespaces={'re': 'http://exslt.org/regular-expressions'}
    ):
        sentence_string = get_unicode_from_xml(sentence)
        sentence_numbers = re.findall(
            r'<span\s+data-dpt="sn"\s+data-rid="([^"]+)',
            sentence_string
        )
        if sentence_numbers:
            sentence_number = sentence_numbers[0]
        else:
            sentence_number = ''
            # print(sentence_string)
        results.append([sentence_number, sentence_string])

    return results


def get_text_search_pattern():
    return r'\b{}\w*\b'


def get_plain_text(encoded_text):
    '''Returns the plain text content from an `EncodedText`.'''
    if not encoded_text:
        return None

    xml = html.fromstring(encoded_text.content)
    text = xml.text_content()

    if not text:
        return None

    return text.strip()


def get_sentence_numbers(work=None):
    '''return all sentence numbers for the given work
    work is a an AbstractedText'''
    ret = [str(n) for n in range(1, 28)]

    if work.slug == 'regiam':
        encoded = work.encoded_texts.filter(type__slug='transcription').first()
        if encoded:
            ret = re.findall(
                r'<span data-dpt="sn"[^>]*>(\d+(?:\.\d+)?)',
                encoded.content
            )

    return ret


def get_page_from_list(alist, request, per_page=None):
    '''returns a Page object from a list a 'page' param in the GET request
    if per_page is None, we use settings.ITEMS_PER_PAGE
    '''
    # &page=1 is first page
    page_number = get_int(request.GET.get('page', 1))

    from django.core.paginator import Paginator
    paginator = Paginator(alist, per_page or settings.ITEMS_PER_PAGE)
    return paginator.get_page(page_number)


def get_page_response_from_list(alist, request):
    '''returns a json api dictionary from a list of results and a request'''
    page = get_page_from_list(alist, request)

    return OrderedDict([
        ['jsonapi', '1.0'],
        ['meta', {
            'page_count': page.paginator.num_pages,
            'hit_count': page.paginator.count,
            'page': page.number,
        }],
        ['data', page.object_list],
    ])


def get_int(string, default=0):
    '''returns int from string, or default if invalid number'''
    try:
        return int(string)
    except ValueError:
        return default
