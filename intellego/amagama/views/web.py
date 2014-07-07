#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010-2014 Zuza Software Foundation
#
# This file is part of amaGama.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Public web query for the amaGama translation memory server"""

from flask import Blueprint, render_template, request, current_app
import requests
import re
import lxml.html
from urlparse import urlparse
import urllib
from lxml.cssselect import CSSSelector
from amagama import tmdb

web_ui = Blueprint('web_ui', __name__, static_folder='static')


@web_ui.route('/', methods=('GET', ))
def translate():
    """Serve the query web page."""
    return render_template("base.html")


@web_ui.route('/sample', methods=('GET',))
def sample():
    """Serve sample page"""
    return render_template("sample.html")


@web_ui.route('/translate_url', methods=('GET',))
def translate_url():
    """ POST method for getting URL from form and process"""
    return render_template("frame.html", url=request.args.get('url'))


def translate_document(root):
    """ Document root node translated and returned """
    # select the nodes through css selectors that may contain text
    sel = CSSSelector('div, span, a, h2, h1')
    # loop through these elements and translate the DOM inplace
    for e in sel(root):
        print e, e.text
        if e.text:
            print current_app.tmdb.translate_unit(e.text, 'en', 'es')
    return root


@web_ui.route('/get_page', methods=('GET',))
def get_page():
    # request the page
    r = requests.get(request.args['url'])
    # parse the dom into python objects
    html = lxml.html.document_fromstring(r.content)
    # prase the requested url so we can form the base href
    url = urlparse(request.args['url'])
    # create the base url dom fragment
    base_url = lxml.html.fromstring("<base href='%s://%s'>" % (url.scheme, url.hostname)).find('.//base')
    # find the head element
    head = html.find(".//head")
    # insert the base href in the last place of the head elements
    head.insert(-1, base_url)
    # rewrite urls to have absolute url
    html.resolve_base_href()
    # rewrite links to load through this proxy
    for element, attribute, link, pos in html.iterlinks():
        if element.tag == "a" and attribute == "href":
            link = "http://localhost:8888/translate_url?url=%s" % (link)
            element.set("href", link)
            element.set("target", "_parent")
    html = translate_document(html)
    # dump the html string for debugging
    with open('html_dump', 'w') as f:
        f.write(lxml.html.tostring(html))
    # a little regex to remove any script tags
    return re.subn(r'<(script).*?</\1>(?s)', '', lxml.html.tostring(html))[0]
