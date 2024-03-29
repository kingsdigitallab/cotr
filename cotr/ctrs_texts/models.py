import uuid

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from . import utils
from .models_abstract import ImportedModel, NamedModel, TimestampedModel

from django.conf import settings


class EncodedTextStatus(NamedModel):
    sort_order = models.IntegerField(
        blank=False, null=False, default=0,
        help_text='The order of this status in your workflow.'
    )

    class Meta:
        verbose_name = 'Text Status'
        verbose_name_plural = 'Text Statuses'


class EncodedTextType(NamedModel):
    pass


@register_snippet
class EncodedText(index.Indexed, TimestampedModel, ImportedModel):
    '''
    An XML-encoded text.
    '''
    # e.g. draft, to-be-reviewed, live
    status = models.ForeignKey(
        'EncodedTextStatus', blank=True, null=True,
        related_name='encoded_texts',
        on_delete=models.SET_NULL
    )
    # e.g. translation or transcription
    type = models.ForeignKey(
        'EncodedTextType', blank=True, null=True,
        related_name='encoded_texts',
        on_delete=models.SET_NULL
    )
    # The XML content (as a string)
    content = models.TextField(blank=True, null=True)

    plain = models.TextField(blank=True, null=True,
                             help_text='Content in plain text')

    abstracted_text = models.ForeignKey(
        'AbstractedText', blank=False, null=False,
        related_name='encoded_texts',
        on_delete=models.CASCADE
    )

    @property
    def content_xml(self):
        '''returns the content as an ElementTree Node'''
        return utils.get_xml_from_unicode(
            self.content, ishtml=True, add_root=True
        )

    @classmethod
    def update_or_create(
        cls, imported_id, abstracted_text, type_name, content, status
    ):
        encoded_type, _ = EncodedTextType.objects.get_or_create(
            slug=slugify(type_name),
            defaults={'name': type_name}
        )

        rec, created = cls.objects.update_or_create(
            imported_id=imported_id,
            defaults={
                'content': content,
                'status': status,
                'abstracted_text': abstracted_text,
                'type': encoded_type,
            }
        )

        return rec, created

    def __str__(self):
        return '{} - {} [{}]'.format(
            self.abstracted_text, self.type, self.status
        )

    def save(self, *args, **kwargs):
        if self.content:
            self.plain = utils.get_plain_text(self)

        super().save(*args, **kwargs)

    def can_show_non_standardised(self):
        '''returns True if the non-standardised copy can be shown
        True iff there is an EncodedText with type 'non-standardised'
            AND we are in debug mode or the copy status is 'live'
        '''
        if settings.ALL_NON_STANDARDISED_TEXTS_ARE_PUBLIC:
            return True

        filters = {}
        from django.db.models.functions import Length
        if not settings.DEBUG:
            filters['status__slug'] = 'live'
        ret = EncodedText.objects.annotate(content_len=Length('plain')).filter(
            content_len__gt=settings.COTR_MIN_CONTENT_LEN,
            abstracted_text=self.abstracted_text,
            type__slug='non-standardised',
            **filters
        ).exists()

        return ret

    def get_content_with_readings(self):
        '''
        Returns XHTML content of this encoded text.
        Where each unsettled region contains the variant readings
        and associated metadata from participating members (MS or V).
        '''
        abstracted_type = self.abstracted_text.type

        if abstracted_type.slug == 'manuscript':
            return self.content

        regions, members = self.get_readings_from_members()

        parent_short_name = self.abstracted_text.short_name

        #  Get the content of the parent (i.e. self)
        xml = utils.get_xml_from_unicode(
            self.content, ishtml=True, add_root=True)
        ri = 0

        # Now inject the region content and info into each region of the parent
        selector = './/span[@data-dpt-group="' + abstracted_type.slug + '"]'
        for region in xml.findall(selector):
            if ri >= len(regions):
                break

            related_id = '{}'.format(uuid.uuid1().fields[0])
            region.attrib['data-related-id'] = related_id

            # Insert the HTML of the variants under the region
            variants = utils.append_xml_element(
                region.getparent(), 'span', None,
                class_='variants',
                id=related_id,
                # ac-112
                data_parent_rid=region.attrib['data-rid']
            )

            for mi, r in enumerate(regions[ri]):
                variant = utils.append_xml_element(
                    variants, 'span', None,
                    class_='variant',
                    data_tid=str(members[mi].id),
                )

                # small label for the type of the parent (e.g. V1, or W)
                utils.append_xml_element(
                    variant,
                    'span',
                    parent_short_name,
                    class_='label {} {}-text-id'.format(
                        abstracted_type.slug,
                        parent_short_name.lower()
                    )
                )

                # small label for the type of the reading (e.g. JH, or V1)
                # clazz = 'version' if r['parent'] == 'W' else 'manuscript'

                utils.append_xml_element(
                    variant,
                    'span',
                    members[mi].short_name,
                    class_='label {} {}-text-id'.format(
                        members[mi].type.slug,
                        members[mi].short_name.lower()
                    )
                )

                utils.append_xml_element(
                    variant, 'span', r['reading'],
                    class_='reading', data_copies=r['copies']
                )

            ri += 1

        ret = utils.get_unicode_from_xml(xml, remove_root=True)

        return ret

    def get_readings_from_members(self):
        '''
        Returns (regions, members)
        regions: a list of region in their order of appearance in this text
        region: a list of m readings, one for each member
        members: a list of m members
        member: an AbstractedText that belongs to the group formed by this text
        '''
        regions = []
        members = []
        abstracted_type = self.abstracted_text.type

        if abstracted_type.slug == 'manuscript':
            return regions, members

        ab_text = self.abstracted_text
        parent_short_name = ab_text.short_name
        members = list(ab_text.members.all().exclude(
            short_name__in=['HM1', 'HM2']
        ))

        #  Collate all the regions from all the members
        regions = []
        for mi, member in enumerate(members):
            other_content = member.encoded_texts.filter(type=self.type).first()

            if not other_content:
                continue
            for ri, region in enumerate(other_content.get_regions(
                abstracted_type.slug)
            ):
                # TODO: 'parent' key is probably ot needed at all.
                # was used in get_content_with_readings() for labels.
                if len(regions) <= ri:
                    # watch out: the SAME dictionary instance is shared by all
                    # entries by default. You modify one => all are modified!
                    regions.append([
                        {
                            'parent': parent_short_name,
                            'reading': '[absent]',
                            'id': '',
                            'copies': '0',
                        }
                    ] * len(members))

                regions[ri][mi] = region
                region['parent'] = parent_short_name

        return regions, members

    def get_regions(self, region_type):
        '''
        Returns a list of unsettled regions (of type region_type=work|version)
        with their plain text reading extracted from this text ONLY.
        '''
        ret = []

        xml = utils.get_xml_from_unicode(
            self.content, ishtml=True, add_root=True)

        # for region in xml.findall('.//span[@data-dpt-type="unsettled"]'):
        region_selector = './/span[@data-dpt-group="' + region_type + '"]'
        for region in xml.findall(region_selector):
            ret.append({
                'reading': utils.get_unicode_from_xml(region, text_only=True),
                'id': region.attrib.get('id', ''),
                'copies': region.attrib.get('data-copies', '0'),
            })

        return ret

    def get_api_url(self, request, view='transcription'):
        return self.abstracted_text.get_api_url(request, self.type.slug)

    search_fields = [
        index.RelatedFields('abstracted_text', [
            index.SearchField('slug', partial_match=True),
        ])
    ]


@register_snippet
class Repository(NamedModel, ImportedModel):
    city = models.CharField(max_length=200, null=False, blank=False)

    @classmethod
    def update_or_create(cls, imported_id, place, name):
        rec, created = cls.objects.update_or_create(
            imported_id=imported_id,
            defaults={
                'slug': slugify('{}-{}'.format(place, name)),
                'city': place, 'name': name,
            }
        )

        return rec, created

    class Meta:
        verbose_name_plural = 'Repositories'

    def __str__(self):
        ret = self.name
        if self.city:
            ret = self.city + ', ' + ret
        return ret


@register_snippet
class Manuscript(TimestampedModel, ImportedModel):
    repository = models.ForeignKey(
        'Repository', blank=True, null=True,
        related_name='manuscripts',
        on_delete=models.SET_NULL
    )
    shelfmark = models.CharField(max_length=200, null=True, blank=True)

    @classmethod
    def update_or_create(cls, imported_id, repository, shelfmark):
        rec, created = cls.objects.update_or_create(
            imported_id=imported_id,
            defaults={
                'repository': repository, 'shelfmark': shelfmark,
            }
        )

        return rec, created

    def __str__(self):
        return '{}, {}'.format(self.repository, self.shelfmark)


class AbstractedTextType(NamedModel):

    @classmethod
    def get_or_create_default_types(cls):
        return {
            slugify(t): cls.objects.get_or_create(
                name=t, slug=slugify(t)
            )[0]
            for t
            in ['Manuscript', 'Version', 'Work']
        }


@register_snippet
class AbstractedText(NamedModel, ImportedModel):
    '''
    A Text: either a MS Text, a Version Text or a Work Text
    '''
    # Optional link to a MS. Not used for Version or Work.
    manuscript = models.ForeignKey(
        'Manuscript', blank=True, null=True,
        related_name='manuscript_texts',
        on_delete=models.SET_NULL
    )
    # the folio/page range for that text in the manuscript
    locus = models.CharField(max_length=200, null=True, blank=True)

    # E.g. manuscript, version, work
    type = models.ForeignKey(
        'AbstractedTextType', blank=True, null=True,
        related_name='abstracted_texts',
        on_delete=models.SET_NULL
    )
    # Optional link to the 'parent'
    group = models.ForeignKey(
        'self', blank=True, null=True,
        related_name='members',
        on_delete=models.SET_NULL
    )

    def get_status(self):
        ret = None
        transc = self.encoded_texts.filter(
            type__slug='transcription').only('status').first()
        if transc:
            ret = transc.status
        return ret

    @classmethod
    def update_or_create(
        cls, imported_id, type, name=None, manuscript=None, locus=None
    ):
        assert manuscript or name

        if name is None:
            name = str(manuscript)
            if locus:
                name += ', ' + locus

        defaults = {
            'name': name,
            'type': type,
            'locus': locus,
            'manuscript': manuscript,
            'slug': slugify(name),
        }

        return cls.objects.update_or_create(
            imported_id=imported_id,
            defaults=defaults
        )

    def __str__(self):
        return '{} ({})'.format(self.name, self.type)

    def full_name_with_siglum(self):
        ret = format(self.name)
        ms = self.manuscript
        if ms:
            ret = ms.repository.city + ', ' + ret
        if self.short_name:
            ret = self.short_name + ': ' + ret
        return ret

    def get_api_url(self, request, view='transcription'):
        return request.build_absolute_uri(reverse(
            'view_api_text_chunk', kwargs={
                'text_slug': self.slug,
                'view': view,
                'unit': 'whole',
                'location': 'whole',
            }
        ))

    def get_top_parent(self):
        ret = self
        while ret.group:
            if ret == ret.group:
                break
            ret = ret.group
        return ret
