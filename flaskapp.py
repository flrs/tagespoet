#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tagespoet Flask Application

This application displays a website that showcases a poem. The poem is generated automatically on the basis of daily
news. The website also comprises an archive and an explanation of how the poem is generated. The language of the created
website is German.

This application uses a wide range of web technologies, such as Python, Flask, MongoDB, jQuery, Ajax, HTML, Bootstrap,
JavaScript and CSS.

The application is meant to run on OpenShift [openshift]. It is configured to serve from a North American server time to
 the German time zone (North American time lagging six hours behind German time).

.. [openshift] http://openshift.com/
"""

from __future__ import print_function  # In python 2.7
from datetime import timedelta, datetime
import sys
from flask import Flask, request, render_template, jsonify
from flask_mail import Message, Mail
from flask_wtf.csrf import CsrfProtect
import flask_pymongo
from flask_pymongo import PyMongo
from flask_debugtoolbar import DebugToolbarExtension
from forms import ContactForm
from dateutil import parser as dateparser


# app config
app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

# debug config
app.debug = False
toolbar = DebugToolbarExtension(app)

# app setup
CsrfProtect(app)
mongo = PyMongo(app)
mail = Mail()
mail.init_app(app)


def make_poem_html(poem, pid):
    """This function makes a section of HTML code for a poem.

    Args:
        poem: A poem defined as a list (rows) of lists (words in rows).
        pid: HTML <p> tag ID attribute for CSS identification.

    Returns:
        A string containing HTML code for displaying a poem, for example:

        '<p id="poemline">Day, Morning, Sun,</p><p id="poemline">Birds, Trees, Grass.</p>'
    """
    res_html = ''
    for line in poem[:-1]:
        res_html += '<p id="' + pid + '">'
        for word in line:
            res_html += word + ', '
        res_html += '</p>'
    res_html += '<p id="' + pid + '">'
    for word in poem[-1][:-1]:
        res_html += word + ', '
    res_html += poem[-1][-1] + '.</p>'
    return res_html


def make_keyword_html(keywords):
    """This function makes a section of HTML code for a list of keywords.

    Args:
        keywords: A list of strings where each string is a keyword.

    Returns:
        A string containing HTML code for displaying keywords, for example:

        '<strong>Ausgangsw&ouml;rter:</strong> Nature, Plants, Fauna'
    """
    res_html = '<strong>Ausgangsw&ouml;rter:</strong> '
    for word in keywords[:-1]:
        res_html += word + ', '
    res_html += keywords[-1]
    return res_html


@app.route("/", methods=['GET', 'POST'])
def mainsite():
    """This function renders the main website.

    The function evaluates the contact form and gets poem data for both current and archive display from a database
    when loading the site.
    """

    # define standard display
    contact_form = ContactForm()
    contact_form_success = False
    jump_to_contact = False

    if request.method == 'POST':
        if not contact_form.validate():
            # contact form validation failed
            jump_to_contact = True
        else:
            # contact form validation succeeded, send email
            msg = Message('Neue Nachricht von Tagespoet.de!', sender=app.config['MAIL_USERNAME'],
                          recipients=[app.config['MAIL_RECIPIENT']])
            msg.body = """
            Von: %s <%s>
            %s
            """ % (contact_form.name.data, contact_form.email.data, contact_form.message.data)
            mail.send(msg)
            contact_form_success = True
            jump_to_contact = True

    # get poem of the day
    cur_poem = mongo.db.poems.find_one({}, sort=[('date', flask_pymongo.DESCENDING)])
    if cur_poem is not None:
        # poem found
        cur_poem_ret = make_poem_html(cur_poem['poem'], 'poemline')
        cur_poem_render_ret = 1
    else:
        # no poem found, return empty values
        # TODO: Implement error handling (logging, sending out maintenance request email)
        cur_poem_ret = ''
        cur_poem_render_ret = 0

    # organize archive
    first_poem = mongo.db.poems.find_one({}, sort=[('date', flask_pymongo.ASCENDING)])

    now = datetime.now()
    yesterdays_date = datetime(now.year, now.month, now.day, 0, 0, 1) + timedelta(hours=6) - timedelta(days=1)
    last_poem = mongo.db.poems.find_one({'date': {'$lte': yesterdays_date}}, sort=[('date', flask_pymongo.DESCENDING)])

    todays_date = datetime.today() + timedelta(hours=6)

    return render_template('index.htm', todays_date=todays_date.strftime("%d.%m.%YYYY"),
                           cur_poem_render=cur_poem_render_ret,
                           cur_poem=cur_poem_ret,
                           first_poem_date=first_poem['date'].strftime('%d.%m.%Y'),
                           last_poem_date=last_poem['date'].strftime('%d.%m.%Y'),
                           last_poem_date_heading=last_poem['date'].strftime("%Y-%m-%dT%H:%M:%S"),
                           last_poem=make_poem_html(last_poem['poem'], 'poemarchiveline'),
                           last_keywords=make_keyword_html(last_poem['keywords']),
                           contact_form=contact_form,
                           contact_form_success=contact_form_success,
                           jump_to_contact=jump_to_contact)


@app.route('/_get_archived_poem')
def get_archived_poem():
    """This function gets an archived poem.

    This function is called by the main website whenever a day in the calendar is clicked on.
    """

    # parse input
    qry_date = request.args.get('date', 0, type=str)
    qry_date_formatted = dateparser.parse(qry_date)
    qry_date_start = datetime(qry_date_formatted.year, qry_date_formatted.month, qry_date_formatted.day, 0, 0, 1)
    qry_date_end = datetime(qry_date_formatted.year, qry_date_formatted.month, qry_date_formatted.day, 23, 59, 59)

    # get poem
    qry_poem = mongo.db.poems.find_one({'date': {'$gte': qry_date_start, '$lt': qry_date_end}})
    if qry_poem is not None:
        # poem found
        qry_poem_render_ret = 1
        qry_poem_ret = make_poem_html(qry_poem['poem'], 'poemarchiveline')
        qry_words_ret = make_keyword_html(qry_poem['keywords'])
    else:
        # no poem found, return error message
        # TODO: Deactivate days on calendar for which no poem is available.
        qry_poem_render_ret = 0
        qry_poem_ret = 'Es ist kein Gedicht für dieses Datum verfügbar.'
        qry_words_ret = ''

    return jsonify(timestamp=qry_date_start.strftime("%Y-%m-%dT%H:%M:%S"),
                   keywords=qry_words_ret,
                   poem=qry_poem_ret,
                   poem_render=qry_poem_render_ret)

if __name__ == "__main__":
    app.run()
