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
from bs4 import BeautifulSoup, NavigableString
import pdb
from pattern.en import tag as tag_en
from pattern.es import tag as tag_es
from pattern.es import pluralize as pluralize_es
from pattern.en import pluralize as pluralize_en
from pattern.es import singularize as singularize_en
from pattern.es import singularize as singularize_es
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
    soup = BeautifulSoup(html)
    text = soup.get_text()
    words = [w.lower() for w in nltk.word_tokenize(text) if w.isalpha() and len(w) > 2]
    vocab = sorted(set(words))
    trans = {word: current_app.tmdb.translate_unit(word, 'en', 'es') for word in vocab}
    # print vocab
    for word in vocab:
        t_unit = trans[word]
        if len(t_unit) > 0:
            for m in re.finditer(ur'(?<=>)([\n\s\w]*(%s)[^<]*)' % t_unit[0]['source'], html, re.IGNORECASE | re.DOTALL):
                # group 2 contains the matched source term in the HTML. Group 1 contains the sourounding text. It can be used for analysis.

                # check if original source match is upper or lower case, and replace as such.
                if m.group(2)[0].isupper():
                    tag_processed = pos_tag_process(m.group(2).strip(), t_unit[0]['target'].title(), m.group(1).strip())
                    html = re.sub(r'\b%s(s\b|\b)(?![^<]*>)' % m.group(2), tag_processed.title(), html, flags=re.IGNORECASE)
                else:
                    tag_processed = pos_tag_process(m.group(2).strip(), t_unit[0]['target'].lower(), m.group(1).strip())
                    html = re.sub(r'\b%s(s\b|\b)(?![^<]*>)' % m.group(2), tag_processed.lower(), html, flags=re.IGNORECASE)

    return lxml.html.document_fromstring(html)


def pos_tag_process(source, target, outer):
    # lower case source word
    tagged_en = tag_en(source.lower())[0][1]
    tagged_es = tag_es(target)[0][1]
    out = target
    if tagged_en != tagged_es:
        if tagged_en in ["NN", "NNP"]:
            # this is a singular source word
            out = singularize_es(target)
        elif tagged_en in ["NNS", "NNPS"]:
            # this is a singlar target word
            out = pluralize_es(target)
        # print '%s-%s: %s : %s' % (tagged_en, tagged_es, source, out)
        # print '---'
    return out


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
