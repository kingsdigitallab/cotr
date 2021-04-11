# Research Software documentation of COTR

This page contains a high-level documentation of the research software analysed, designed and developed by [King's Digital Lab (KDL)](https://kdl.kcl.ac.uk) 
for the [The Community of the Realm in Scotland, 1249-1424: history, law and charters in a recreated kingdom (COTR)](https://cotr.ac.uk/) 
research project, [funded by the AHRC](https://gtr.ukri.org/projects?ref=AH%2FP013759%2F1).

Please refer to [the Guideline section on the COTR website](https://cotr.ac.uk/guidelines/) 
for the historical and research perspective on the project and ways to cite our work.

KDL team: Paul Caton, Ginestra Ferraro, Geoffroy Noël, Miguel Vieira, Brian Maher.

## UML Model

All UML Diagrams below were drawn with [Modelio](https://www.modelio.org/)
you can [download the complete model and diagrams in a single Modelio zip file](./uml/ctrs-modelio.zip)
or download the model in XMI format: [UML 2.1](./uml/XMI/ctrs-uml21.xmi), 
[UML 2.4](./uml/XMI/ctrs-uml24.xmi) or [UML-EMF 3.0](./uml/XMI/ctrs-emf3.xmi).
*Note that although the XMI format is standard but isn't well supported by all UML editors*.

## System Architecture

![UML Deployment Diagram](./uml/diagrams/ctrs-deployment-diagram.png)
[UML deployment](./uml/ctrs-modelio.zip)

The web application was developed using two python 3 web frameworks:
* [Django](https://www.djangoproject.com/)
* [Wagtail Content Management System](https://wagtail.io/)

We have used the [Django Cookie Cutter](https://github.com/cookiecutter/cookiecutter) 
stack, which is deployed with [Docker](https://www.docker.com/) and comes with postgresql for the relational database, 
nginx as a web server for the media assets, gunicorn to run the Python application and Traefik as a reverse proxy.

The [source code of the Django project](https://github.com/kingsdigitallab/cotr/tree/master/cotr) 
itself is open source and included in [this COTR repository](https://github.com/kingsdigitallab/cotr).

The [search page](https://cotr.ac.uk/search/) and the [text viewer](https://cotr.ac.uk/viewer?group=declaration&blocks=23:transcription;) 
on the public website are implemented by the [ctrs_text Django app](https://github.com/kingsdigitallab/cotr/tree/master/cotr/ctrs_texts).

## Data Models

Documentation of the logical data model of the ctrs_text application. 

## Web APIs

Documentation of the public [Web APIs to search and browse the editions](apis.md). 
