#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module containing functions for extracting keywords from German news website Tagesschau.de
"""

import re
import locale
import codecs
import os
import sys

import urllib
from collections import Counter
from GermanStemmer2 import GermanStemmer2
from bs4 import BeautifulSoup


try:
    locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
except locale.Error:
    print "Cannot set locale to de_DE.UTF-8"


def get_tagesschau_words(no_of_words):
    """Get most occuring nouns from articles on main site of Tagesschau.de [tag]

    Args:
        no_of_words: No. of words to get

    Returns:
        A list of strings of the nouns occurring most in the articles on the main site
        of Tagesschau.de, ordered by no. of occurrences.

    .. [tag] http://www.tagesschau.de
    """

    # import dictionary for lemmatization
    de_dictionary = codecs.open(os.path.dirname(__file__) + '/resources/de-lexicon.txt', encoding='utf-8').read()

    article_urls = []

    # get URLs of main articles on tagesschau.de
    r = urllib.urlopen('http://www.tagesschau.de/').read()
    site_text = BeautifulSoup(r, "html.parser")
    for links in site_text.find_all('a', attrs={'class': None}):
        dachzeilen = len(links.find_all('p', attrs={'class': 'dachzeile'}))
        headlines = len(links.find_all('h4', attrs={'class': 'headline'}))
        teasertexts = len(links.find_all('p', attrs={'class': 'teasertext'}))
        if dachzeilen and headlines and teasertexts:
            link_target = links['href']
            if link_target[0] == '/':
                article_urls.append('http://www.tagesschau.de' + links['href'])
    # print article_urls

    # get all text from articles
    all_sentences = []
    for article_url in article_urls:
        # print article_url
        r = urllib.urlopen(article_url).read()
        article = BeautifulSoup(r, "html.parser")
        for text_div in article.find_all('div', attrs={'class': 'mod modA modParagraph'}):
            for paragraph in text_div.find_all('p', attrs={'class': 'text small'}):
                paragraph_text = paragraph.getText()
                stripped_word = paragraph_text.strip().split()
                ignore = 0
                if len(stripped_word) > 0 \
                        and stripped_word[0] == 'Von' \
                        and ',' in paragraph_text \
                        and len(stripped_word) < 8:
                    ignore = 1
                if not ignore:
                    all_sentences.append(paragraph_text.encode('utf-8'))

    # Get all nouns or capitalized words
    all_nouns = []
    for sentence in all_sentences:
        # TODO: replace this with regex from different library in the future, such as https://pypi.python.org/pypi/regex
        nouns = re.compile('([A-Z][A-Za-z0-9\-äöüÄÖÜßèáàéôëêâîûùÿæçïœóåűúőíðþýøìõãòąćęłńśźżăşșţțğıčůďžěňřšťİ]+)',
                           re.UNICODE).findall(sentence)
        for noun in nouns:
            try:
                all_nouns.append(noun.decode('utf-8'))
            except UnicodeEncodeError:
                print 'UnicodeEncodeError detected. The following word contains an unknown letter:'
                print noun

    # filter

    # list forbidden words which are words that can be written capitalized at beginnings of sentences but are not nouns
    forbidden_words = [u'ab', u'aber', u'abseits', u'abzüglich', u'als', u'am', u'an', u'anfangs', u'angesichts',
                       u'anhand',
                       u'anlässlich', u'ans', u'anstatt', u'anstelle', u'auf', u'aufgrund', u'aufs', u'aufseiten',
                       u'aus',
                       u'ausgangs', u'ausschließlich', u'ausweislich', u'außer', u'außerhalb', u'behufs', u'bei',
                       u'beiderseits', u'beidseits', u'beim', u'betreffs', u'bevor', u'beziehungsweise', u'bezüglich',
                       u'binnen', u'bis', u'contra', u'da', u'damit', u'dank', u'das', u'dass', u'dem', u'den', u'denn',
                       u'der', u'des', u'dessen', u'desto', u'desungeachtet', u'die', u'diesseits', u'doch', u'du',
                       u'durch', u'eh', u'ehe', u'ein', u'eine', u'einem', u'einen', u'einer', u'eines', u'eingangs',
                       u'eingedenk', u'einschließlich', u'entgegen', u'entlang', u'entsprechend', u'entweder', u'er',
                       u'es',
                       u'exklusive', u'falls', u'fern', u'fernab', u'für', u'fürs', u'gegen', u'gegenüber',
                       u'gelegentlich',
                       u'gemäß', u'gen', u'geschweige', u'gleich', u'halber', u'hinsichtlich', u'hinter', u'hinterm',
                       u'hinters', u'ich', u'ihr', u'im', u'in', u'indem', u'indes', u'indessen', u'infolge',
                       u'inklusive',
                       u'inmitten', u'innerhalb', u'innert', u'ins', u'insofern', u'insoweit', u'ist', u'je', u'jedoch',
                       u'jenseits', u'kontra', u'kraft', u'lang', u'laut', u'links', u'längs', u'längsseits',
                       u'mangels',
                       u'maßen', u'minus', u'mit', u'mithilfe', u'mitsamt', u'mittels', u'nach', u'nachdem', u'nebst',
                       u'nordwestlich', u'nordöstlich', u'nördlich', u'ob', u'oberhalb', u'obgleich', u'obschon',
                       u'obwohl',
                       u'obzwar', u'oder', u'ohne', u'per', u'plus', u'pro', u'rechts', u'respektive', u'samt', u'seit',
                       u'seitens', u'seitlich', u'seitwärts', u'sie', u'so', u'sobald', u'sodass', u'sofern', u'solang',
                       u'solange', u'sondern', u'sooft', u'soviel', u'soweit', u'sowie', u'sowohl', u'statt',
                       u'südlich',
                       u'südwestlich', u'südöstlich', u'trotz', u'trotzdem', u'um', u'ums', u'umso', u'unbeschadet',
                       u'und',
                       u'unerachtet', u'unfern', u'ungeachtet', u'unter', u'unterhalb', u'unterm', u'untern', u'unters',
                       u'unweit', u'vermittels', u'vermittelst', u'vermöge', u'via', u'vom', u'von', u'vonseiten',
                       u'vor',
                       u'vorbehaltlich', u'weder', u'wegen', u'weil', u'wenn', u'wennauch', u'wenngleich', u'wennschon',
                       u'wider', u'wie', u'wiewohl', u'wir', u'wo', u'wobei', u'wofern', u'wohingegen', u'während',
                       u'währenddem', u'währenddessen', u'zeit', u'zu', u'zufolge', u'zugunsten', u'zulieb', u'zuliebe',
                       u'zum', u'zumal', u'zur', u'zuungunsten', u'zuwider', u'zuzüglich', u'zwecks', u'zwischen',
                       u'östlich', u'über', u'überm', u'übern', u'übers', u'auch']

    # filter out forbidden words
    for nx, word in enumerate(forbidden_words):
        sys.stdout.write(forbidden_words[nx].title())
        forbidden_words[nx] = forbidden_words[nx].title()

    # sort words by occurrence
    news_words = Counter([item for item in all_nouns if item not in forbidden_words])
    news_words = [item[0] for item in news_words.most_common(no_of_words)]

    # filter out known nouns
    final_words = []
    stemmer = GermanStemmer2()
    for word in news_words:
        if word not in de_dictionary:
            if word.isupper():
                # do not consider abbreviations (all uppercase)
                final_words.append(word)
            else:
                # stem word with word stemmer
                final_words.append(stemmer.stem(word.encode('iso-8859-1')).decode('iso-8859-1').title())
        else:
            final_words.append(word)

    # make words unique
    seen = set()
    final_words_no_dups = []
    for item in final_words:
        if item not in seen:
            seen.add(item)
            final_words_no_dups.append(item)

    return final_words_no_dups
