# Web APIs

The search page and the text viewer on the website 
are built on top of web APIs which are
publicly accessible. The APIs responses follow the 
[json:api](https://jsonapi.org/) specification.

The addresses below should be prefixed with the domain the live COTR website.
Currently: [https://cotr.ac.uk](https://cotr.ac.uk)

## List of texts

The following request returns a list of all the texts for a given work.

*group* is a code for the work, 'declaration' or 'regiam'.

`/api/texts/?&group=declaration`

The type of a text is either: manuscript, version or work.

## Text content

The following request returns the content of a given text.

Replace 23 with the id of the desired text as returned by the previous
web API call. Use 'transcription' for the Latin edition and 'translation'
for the English translation. /whole/whole is just a fixed convention.

`/api/texts/23/transcription/whole/whole/`

## Sentences matching a keyword

The following request returns the 2nd page of the results containing 
the sentence with keyword 'rege' from the Latin (transcription) text 
with the given IDs in the Declaration.

`/api/texts/search/text/?group=declaration&page=2&rt=text&et=transcription&q=rege&texts=44,35,37,40,38,7,4,20,6,9,36,3,1,50,21,2,8,22,23,51,12,13,10,11,14,5`

## Sentences matching a number

The following request returns the 2nd page of the results containing 
the 4th sentence from the Latin (transcription) text with the given IDs 
in the Declaration.

`/api/texts/search/sentences/?group=declaration&page=2&rt=sentences&sn=4&et=transcription&q=&texts=44,35,37,40,38,7,4,20,6,9,36,3,1,50,21,2,8,22,23,51,12,13,10,11,14,5`

## Unsettled regions

The following request returns the unsettled regions found in the texts
with the given IDs.

`/api/texts/search/regions/?group=declaration&page=1&rt=regions&sn=4&et=transcription&q=rege&texts=44,35`

Each region has one or more readings and one or two rectangles that bound the
region on the manuscript image.
