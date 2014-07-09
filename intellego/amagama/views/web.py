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
from cssselect import HTMLTranslator
from amagama import tmdb
import nltk
import re
from bs4 import BeautifulSoup,NavigableString
import pdb
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

def translate_dom_string(root, html):
    raw = nltk.clean_html(html)
    words = [w.lower() for w in nltk.word_tokenize(raw) if w.isalpha() and len(w) > 2]
    vocab = sorted(set(words))
    soup = BeautifulSoup(html)
    elements = soup.find_all(True)
    trans = {word: current_app.tmdb.translate_unit(word, 'en', 'es') for word in vocab}
    for el in elements:
        # print el.string
        for word in vocab:
            t_unit = trans[word]
            # print "%s: %s" % (word,t_unit)
            # if el.text.find("basics of using bookmarks") > -1 and word == "bookmarks":
            #     debugger;
            if len(t_unit) > 0 and (el.text.lower().find(t_unit[0]['source'].lower()) > -1):
                if el.string:
                    el.string.replace_with(el.text.replace(t_unit[0]['source'].lower(), t_unit[0]['target'].lower()))
    print vocab
    return lxml.html.document_fromstring(str(soup))

def translate_html(root, html):
    words = [w.lower() for w in nltk.word_tokenize(root.text_content()) if w.isalpha() and len(w) > 2]
    vocab = sorted(set(words))
    trans = {word: current_app.tmdb.translate_unit(word, 'en', 'es') for word in vocab}
    print vocab
    for word in vocab:
        t_unit = trans[word]
        if len(t_unit) > 0:
            for m in re.finditer(ur'(?<=>)([\n\s\w]*(%s)[^<]*)' % t_unit[0]['source'], html, re.IGNORECASE):
                # group 2 contains the matched source term in the HTML. Group 1 contains the sourounding text. It can be used for analysis.
                try:
                    print '%02d-%02d: %s : %s : %s' % (m.start(), m.end(), m.group(2).strip(), t_unit[0]['target'], m.group(1).strip())
                except:
                    pass
                # check if original source match is upper or lower case, and replace as such.
                if m.group(2)[0].isupper():
                    html = re.sub(r'\b%s(s\b|\b)(?![^<]*>)' % m.group(2), t_unit[0]['target'].title(), html, count=1, flags=re.IGNORECASE)
                else:
                    html = re.sub(r'\b%s(s\b|\b)(?![^<]*>)' % m.group(2), t_unit[0]['target'].lower(), html, count=1, flags=re.IGNORECASE)
                print '---' 
    return lxml.html.document_fromstring(html)

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
    # translate through DOM Traversal
    # html = translate_dom_string(html, lxml.html.tostring(html))
    # translate through HTML regex string replacement
    html = translate_html(html, lxml.html.tostring(html))
    # dump the html string for debugging
    # with open('html_dump', 'w') as f:
    #     f.write(lxml.html.tostring(html))
    # a little regex to remove any script tags
    return re.subn(r'<(script).*?</\1>(?s)', '', lxml.html.tostring(html))[0]
