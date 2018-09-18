# Generated by Django 2.0 on 2018-09-18 12:49

import cms.models.streamfield
from django.db import migrations
import wagtail.contrib.table_block.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0007_renamed_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogindexpage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('home_page_block', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.URLBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('title', wagtail.core.blocks.CharBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('description', wagtail.core.blocks.TextBlock()), ('icon', cms.models.streamfield.IconChoiceBlock())), icon='placeholder')), ('intro', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('pullquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()), ('affiliation', wagtail.core.blocks.CharBlock(required=False)), ('style', cms.models.streamfield.PullQuoteStyleChoiceBlock())), icon='openquote')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', cms.models.streamfield.ImageFormatChoiceBlock()), ('text', wagtail.core.blocks.RichTextBlock(required=False))), icon='image', label='Aligned image and text')), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse')), ('link', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.CharBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('label', wagtail.core.blocks.CharBlock()), ('style', cms.models.streamfield.LinkStyleChoiceBlock())), icon='link')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('html', wagtail.core.blocks.StructBlock((('html', wagtail.core.blocks.RawHTMLBlock()), ('alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())), icon='code', label='Raw HTML')), ('table', wagtail.contrib.table_block.blocks.TableBlock({'autoColumnSize': False, 'colHeaders': False, 'contextMenu': True, 'editor': 'text', 'height': 108, 'language': 'en', 'minSpareRows': 0, 'renderer': 'html', 'rowHeaders': False, 'startCols': 3, 'startRows': 3, 'stretchH': 'all'})))),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('home_page_block', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.URLBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('title', wagtail.core.blocks.CharBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('description', wagtail.core.blocks.TextBlock()), ('icon', cms.models.streamfield.IconChoiceBlock())), icon='placeholder')), ('intro', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('pullquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()), ('affiliation', wagtail.core.blocks.CharBlock(required=False)), ('style', cms.models.streamfield.PullQuoteStyleChoiceBlock())), icon='openquote')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', cms.models.streamfield.ImageFormatChoiceBlock()), ('text', wagtail.core.blocks.RichTextBlock(required=False))), icon='image', label='Aligned image and text')), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse')), ('link', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.CharBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('label', wagtail.core.blocks.CharBlock()), ('style', cms.models.streamfield.LinkStyleChoiceBlock())), icon='link')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('html', wagtail.core.blocks.StructBlock((('html', wagtail.core.blocks.RawHTMLBlock()), ('alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())), icon='code', label='Raw HTML')), ('table', wagtail.contrib.table_block.blocks.TableBlock({'autoColumnSize': False, 'colHeaders': False, 'contextMenu': True, 'editor': 'text', 'height': 108, 'language': 'en', 'minSpareRows': 0, 'renderer': 'html', 'rowHeaders': False, 'startCols': 3, 'startRows': 3, 'stretchH': 'all'})))),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('home_page_block', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.URLBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('title', wagtail.core.blocks.CharBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('description', wagtail.core.blocks.TextBlock()), ('icon', cms.models.streamfield.IconChoiceBlock())), icon='placeholder')), ('intro', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('pullquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()), ('affiliation', wagtail.core.blocks.CharBlock(required=False)), ('style', cms.models.streamfield.PullQuoteStyleChoiceBlock())), icon='openquote')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', cms.models.streamfield.ImageFormatChoiceBlock()), ('text', wagtail.core.blocks.RichTextBlock(required=False))), icon='image', label='Aligned image and text')), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse')), ('link', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.CharBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('label', wagtail.core.blocks.CharBlock()), ('style', cms.models.streamfield.LinkStyleChoiceBlock())), icon='link')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('html', wagtail.core.blocks.StructBlock((('html', wagtail.core.blocks.RawHTMLBlock()), ('alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())), icon='code', label='Raw HTML')), ('table', wagtail.contrib.table_block.blocks.TableBlock({'autoColumnSize': False, 'colHeaders': False, 'contextMenu': True, 'editor': 'text', 'height': 108, 'language': 'en', 'minSpareRows': 0, 'renderer': 'html', 'rowHeaders': False, 'startCols': 3, 'startRows': 3, 'stretchH': 'all'})))),
        ),
        migrations.AlterField(
            model_name='indexpage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('home_page_block', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.URLBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('title', wagtail.core.blocks.CharBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('description', wagtail.core.blocks.TextBlock()), ('icon', cms.models.streamfield.IconChoiceBlock())), icon='placeholder')), ('intro', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('pullquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()), ('affiliation', wagtail.core.blocks.CharBlock(required=False)), ('style', cms.models.streamfield.PullQuoteStyleChoiceBlock())), icon='openquote')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', cms.models.streamfield.ImageFormatChoiceBlock()), ('text', wagtail.core.blocks.RichTextBlock(required=False))), icon='image', label='Aligned image and text')), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse')), ('link', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.CharBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('label', wagtail.core.blocks.CharBlock()), ('style', cms.models.streamfield.LinkStyleChoiceBlock())), icon='link')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('html', wagtail.core.blocks.StructBlock((('html', wagtail.core.blocks.RawHTMLBlock()), ('alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())), icon='code', label='Raw HTML')), ('table', wagtail.contrib.table_block.blocks.TableBlock({'autoColumnSize': False, 'colHeaders': False, 'contextMenu': True, 'editor': 'text', 'height': 108, 'language': 'en', 'minSpareRows': 0, 'renderer': 'html', 'rowHeaders': False, 'startCols': 3, 'startRows': 3, 'stretchH': 'all'})))),
        ),
        migrations.AlterField(
            model_name='peopleindexpage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('home_page_block', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.URLBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('title', wagtail.core.blocks.CharBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('description', wagtail.core.blocks.TextBlock()), ('icon', cms.models.streamfield.IconChoiceBlock())), icon='placeholder')), ('intro', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('pullquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()), ('affiliation', wagtail.core.blocks.CharBlock(required=False)), ('style', cms.models.streamfield.PullQuoteStyleChoiceBlock())), icon='openquote')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', cms.models.streamfield.ImageFormatChoiceBlock()), ('text', wagtail.core.blocks.RichTextBlock(required=False))), icon='image', label='Aligned image and text')), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse')), ('link', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.CharBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('label', wagtail.core.blocks.CharBlock()), ('style', cms.models.streamfield.LinkStyleChoiceBlock())), icon='link')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('html', wagtail.core.blocks.StructBlock((('html', wagtail.core.blocks.RawHTMLBlock()), ('alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())), icon='code', label='Raw HTML')), ('table', wagtail.contrib.table_block.blocks.TableBlock({'autoColumnSize': False, 'colHeaders': False, 'contextMenu': True, 'editor': 'text', 'height': 108, 'language': 'en', 'minSpareRows': 0, 'renderer': 'html', 'rowHeaders': False, 'startCols': 3, 'startRows': 3, 'stretchH': 'all'})))),
        ),
        migrations.AlterField(
            model_name='peoplepage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('home_page_block', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.URLBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('title', wagtail.core.blocks.CharBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('description', wagtail.core.blocks.TextBlock()), ('icon', cms.models.streamfield.IconChoiceBlock())), icon='placeholder')), ('intro', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('pullquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()), ('affiliation', wagtail.core.blocks.CharBlock(required=False)), ('style', cms.models.streamfield.PullQuoteStyleChoiceBlock())), icon='openquote')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', cms.models.streamfield.ImageFormatChoiceBlock()), ('text', wagtail.core.blocks.RichTextBlock(required=False))), icon='image', label='Aligned image and text')), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse')), ('link', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.CharBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('label', wagtail.core.blocks.CharBlock()), ('style', cms.models.streamfield.LinkStyleChoiceBlock())), icon='link')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('html', wagtail.core.blocks.StructBlock((('html', wagtail.core.blocks.RawHTMLBlock()), ('alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())), icon='code', label='Raw HTML')), ('table', wagtail.contrib.table_block.blocks.TableBlock({'autoColumnSize': False, 'colHeaders': False, 'contextMenu': True, 'editor': 'text', 'height': 108, 'language': 'en', 'minSpareRows': 0, 'renderer': 'html', 'rowHeaders': False, 'startCols': 3, 'startRows': 3, 'stretchH': 'all'})))),
        ),
        migrations.AlterField(
            model_name='richtextpage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('home_page_block', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.URLBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('title', wagtail.core.blocks.CharBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('description', wagtail.core.blocks.TextBlock()), ('icon', cms.models.streamfield.IconChoiceBlock())), icon='placeholder')), ('intro', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('pullquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()), ('affiliation', wagtail.core.blocks.CharBlock(required=False)), ('style', cms.models.streamfield.PullQuoteStyleChoiceBlock())), icon='openquote')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', cms.models.streamfield.ImageFormatChoiceBlock()), ('text', wagtail.core.blocks.RichTextBlock(required=False))), icon='image', label='Aligned image and text')), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse')), ('link', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.CharBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('label', wagtail.core.blocks.CharBlock()), ('style', cms.models.streamfield.LinkStyleChoiceBlock())), icon='link')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('html', wagtail.core.blocks.StructBlock((('html', wagtail.core.blocks.RawHTMLBlock()), ('alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())), icon='code', label='Raw HTML')), ('table', wagtail.contrib.table_block.blocks.TableBlock({'autoColumnSize': False, 'colHeaders': False, 'contextMenu': True, 'editor': 'text', 'height': 108, 'language': 'en', 'minSpareRows': 0, 'renderer': 'html', 'rowHeaders': False, 'startCols': 3, 'startRows': 3, 'stretchH': 'all'})))),
        ),
    ]
