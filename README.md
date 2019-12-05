
# PDFTOOL

 

PDFTOOL is a web app for PDF operations.

 

## Main features

-   A light web app to deal with PDF easily, get rid of downloading softwares
    and sophisticate operations.

-   Support merge, split, add image, compress, encrypt, decrypt PDF, and convert
    images to PDF.

-   Apply [dropzone](https://www.dropzonejs.com/) as upload tool, support drag
    and drop and thumbnail preview.

 

## Example

See [PDFTOOL](http://52.205.233.142/) as a Demo.

 

## Install


Copy all contents to /path/to/pdfserver,

then install the dependence by:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pip3 install -r requirements.txt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

## Usage

For development and test, run

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
python3 /path/to/pdfserver/pdfserver.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This mode set Flask debug mode to True as default, such that Flask return html containing error information if internal error happen.
Be caution not to use this mode in production environment for security and performance resons.

For production use, instead, use

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
python3 /path/to/pdfserver/runserver.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this mode we start a WSGI server and the log will be logged into 'infolog.log'

## License

This app is under GNU GPLv3 license, because the dependence PyMuPDF is distributed under GNU GPLv3 license.
 

## Structure

-   pdfserver.py includes all routing maps, implementation of file receiver,
    implement of user authentication and Main configurations.

-   pdftool2.py includes implementation of pdftool class and pdfproc for PDF processing.

- db.py, model.py, form.py, sendemail.py, implement essential utilizations for user authentication and form submission.

-   ./template includes html templates. ./static includes static resources for html.
