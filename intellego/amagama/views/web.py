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

from flask import Blueprint, render_template, request
import requests
import re

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


@web_ui.route('/get_page', methods=('GET',))
def get_page():
    r = requests.get(request.args['url'])
    content = r.content.decode('utf-8', 'ignore')
    pos = content.index("</title>") + 8
    base = "<base href='%s' />" % request.args.get('url')
    content = content[:pos] + base + content[pos:]
    return re.subn(r'<(script).*?</\1>(?s)', '', content)[0]
