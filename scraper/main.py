#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to make German poems out of a word cloud.

The scripts created by this poem match a meter and rhyme scheme defined in the code.
"""

import locale
import random
import re
import sys
import urllib
import os
import time
import base64

from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import timedelta, datetime

from scraper import get_tagesschau_words

try:
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
except locale.Error:
    print "Cannot set locale to de_DE.UTF-8"

# Get database from mongodb
client = MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
db = client.tagespoet

# poem scheme, 1 is stressed and 0 is unstressed syllable
poem_scheme = [[1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], [1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
               [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], [1, 0, 0, 1, 0, 0, 1, 0, 0, 1]]

# rhyme pairs, refers to end of lines from poem_scheme
rhyme_scheme = [1, 1, 2, 3, 3, 2]

# characters defining stress
stress_chars = [u'\u0331', u'\u0323']

consonants = [u'b', u'c', u'd', u'f', u'g', u'h', u'i', u'j', u'k', u'l', u'm', u'n', u'p', u'q', u'r', u's', u't',
              u'v', u'w', u'x', u'y', u'z', u'ß']


def get_synonyms(qry_string):
    """Get synonyms for a specific word in German.

    Args:
        qry_string: A string containing a word for that synnonyms should be found.

    Returns:
        A list of strings with synonyms for the qry_string.
    """
    res_list = []
    r = urllib.urlopen(
        base64.b64decode('***REMOVED***') + qry_string.lower() + '.php').read()
    site_text = BeautifulSoup(r)
    synonym_collections = site_text.find_all('h4', class_='synonymsContent')
    for synonym_collection in synonym_collections:
        synonyms = synonym_collection.find_all('a')
        for synonym in synonyms:
            if synonym.text not in res_list and synonym.text != qry_string:
                res_list.append(synonym.text)
    return res_list


def substitute_all_by_empty(qry_string, qry_subs):
    """Substitute all occurrences of specific string sequences by an empty sequence.
    
    Args:
        qry_string: A string containing sequences to be replaced.
        qry_subs: A list of strings containing sequences to be replaced.
    
    Returns:
        The qry_string where all sequences defined in qry_subs are deleted.
    """
    tmp_str = qry_string
    for sub in qry_subs:
        tmp_str = tmp_str.replace(sub, '')
    return tmp_str


def get_syllable(qry_string):
    """Get syllables for a specific German word

    Args:
        qry_string: A string containing a word for which syllables should be acquired.
        qry_subs: A list of strings containing sequences to be replaced.

    Returns:
        A tuple of single syllables and stressed syllables. For example:

        ['In', 'ter', 'ak', 'tion'], [0, 0, 0, 1]
    """
    single_syls = []
    url = urllib.quote(qry_string.encode('utf8'))
    r = urllib.urlopen(base64.b64decode('***REMOVED***') + url +
                       base64.b64decode('***REMOVED***')).read()
    site_text = BeautifulSoup(r)
    ress = site_text.find_all('div', class_='rom first')

    # if error in site or no syllables found
    if len(ress) == 0:
        return 0, 0

    # extract text from div
    t = ress[0].find_all('h2')[0].text.strip()

    # get rid of stuff in brackets
    end_pos = t.rfind('(')
    if end_pos != -1:
        t = t[:end_pos]

    # get first syllables of word
    first_syls = re.compile('([^ \-\t\n\r\f\v\·]*)[·]', re.UNICODE).findall(t)
    if len(first_syls) == 0:
        first_syls = re.compile('^(?:\S+\s){1}(\S+) ', re.UNICODE).findall(t)

    for match in first_syls:
        single_syls.append(match)

    # get last syllable of word
    last_syl = re.compile('[·]([^ \-\t\n\r\f\v\·]*)', re.UNICODE).findall(t)
    if len(last_syl) > 0:
        match = []
        for match in last_syl:
            pass
        if match:
            single_syls.append(substitute_all_by_empty(match, '1'))

    # check if found and queried word match
    tmp_res = ''.join(single_syls)
    if substitute_all_by_empty(tmp_res, stress_chars) == qry_string:
        # check for special cases where syllables and word do not match
        # case 'Lektion, Region,...'
        if len(single_syls) > 2:
            if substitute_all_by_empty(single_syls[-1], stress_chars) == 'on' \
                    and single_syls[-2][-1] == 'i' \
                    and single_syls[-2][-2] in consonants:
                single_syls[-2] = single_syls[-2] + single_syls[-1]
                del (single_syls[-1])

        stress_syls = [0] * len(single_syls)
        # check for syllables
        for idx, syl in enumerate(single_syls):
            if any(x in syl for x in stress_chars):
                stress_syls[idx] = 1
        if not any(stress_syls):
            # syllables not identifiable
            # print qry_string + ' syllables cannot be identified.'
            return 0, 0
        else:
            return single_syls, stress_syls
    else:
        # string mismatch
        # print qry_string + ' is not ' + substitute_all_by_empty(tmp_res, stress_chars)
        return 0, 0

# configure poem creation
min_no_of_words = 20
max_no_of_words = 35
cur_no_of_words = min_no_of_words
script_start_time = time.time()
log_string = 'empty'
break_loop = 0

while break_loop == 0:
    # get word cloud from German news site Tagesschau through scraper
    word_cloud = get_tagesschau_words(cur_no_of_words)
    sys.stdout.write('KW: ')
    for word in word_cloud:
        sys.stdout.write(word)

    words = []
    ctrlwords = []
    syls = []
    stresses = []
    topics = []
    uses = []
    last_syls = []

    # get synonyms and stresses
    for word in word_cloud:
        tmp_word = word.encode('utf-8')
        # check if this word is already in database
        cursor = db.synonyms.find({'word': tmp_word})
        if cursor.count() == 0:
            # word not in database
            tmp_syns = get_synonyms(tmp_word)

            # add origin word as synonym
            tmp_syns.append(unicode(tmp_word.decode('utf8')))
            db.synonyms.insert({'word': tmp_word})

            for syn in tmp_syns:
                # get syllables
                tmp_syls, tmp_stress_syls = get_syllable(syn)
                if tmp_syls != 0 and tmp_stress_syls != 0:
                    # syllables could be received
                    already_there = 0

                    # avoid duplicate synonyms
                    for cur_word in ctrlwords:
                        if substitute_all_by_empty(cur_word, stress_chars) == substitute_all_by_empty(syn,
                                                                                                      stress_chars):
                            already_there = 1
                            break

                    if already_there != 1:
                        # no duplicate synonyms exist, so add synonym to database
                        db.synonyms.update(
                            {'word': tmp_word},
                            {'$push':
                                 {'subword':
                                      {'word': syn,
                                       'syls': tmp_syls,
                                       'last_syls': substitute_all_by_empty(tmp_syls[-1], stress_chars),
                                       'stresses': tmp_stress_syls,
                                       'uses': 0}
                                  }
                             }
                        )
                        ctrlwords.append(syn)

        # add word with synonyms to data for making poem
        cursor = db.synonyms.find_one({'word': tmp_word}, {'subword': 1, '_id': 0})
        if len(cursor) > 0:
            subwords = cursor['subword']
            for subword in subwords:
                words.append(subword['word'])
                syls.append(subword['syls'])
                stresses.append(subword['stresses'])
                last_syls.append(subword['last_syls'])
                uses.append(0)

    # solve poem
    # strategy: use dumb 'brute force' method to fit words into line as process is not time-critical

    # define start variables
    syls_nx = 0
    syls_left = len(poem_scheme)
    rnd_ct = 0
    picked_rhyme_nxs = [0] * max(rhyme_scheme)
    line_nx = 0
    final_poem = []
    final_words = []
    poem_find_start_time = time.time()
    break_loop = 0

    while line_nx < len(poem_scheme) and not break_loop:
        # solve poem line by line
        line = poem_scheme[line_nx]
        syls_nx = len(line)
        syls_left = len(line)
        rnd_ct = 0
        rnd_ct_repeat = 0
        suggested_nxs = []
        suggested_words = []
        is_first_line_in_rhyme = 0
        while syls_left != 0 and not break_loop:
            rnd_ct += 1

            # get random word
            tmpNx = random.randrange(0, len(words))
            if uses[tmpNx] == 0 and tmpNx not in suggested_nxs and words[tmpNx] not in suggested_words \
                    and words[tmpNx] not in final_words:
                # word has neither been used in past lines nor in poem

                # check if word fits in line
                tmpSylCt = len(stresses[tmpNx])
                if syls_nx - tmpSylCt >= 0:
                    # some syllables left in line
                    if stresses[tmpNx] == line[syls_nx - tmpSylCt:syls_nx]:
                        # syllables of word fit into syllable scheme of line
                        ok_to_add = 0
                        if syls_left == len(line):
                            # syllables of picked word will end the line,
                            # so make sure last syllable of word matches rhyme scheme
                            if picked_rhyme_nxs[rhyme_scheme[line_nx] - 1] == 0:
                                # last syllable is first in rhyme pair
                                if last_syls.count(last_syls[tmpNx]) >= rhyme_scheme.count(rhyme_scheme[line_nx]):
                                    # enough last syllables available in poem words to make rhyme with proposed word
                                    picked_rhyme_nxs[rhyme_scheme[line_nx] - 1] = last_syls[tmpNx]
                                    is_first_line_in_rhyme = 1
                                    ok_to_add = 1
                            else:
                                # last syllable has to fit to rhyme pair
                                if last_syls[tmpNx] == picked_rhyme_nxs[rhyme_scheme[line_nx] - 1]:
                                    # last syllable fits rhyme pair
                                    ok_to_add = 1
                        else:
                            # syllables of picked word fit in line and are not the last ones in the line
                            ok_to_add = 1
                        if ok_to_add:
                            suggested_nxs.insert(0, tmpNx)
                            suggested_words.insert(0, words[tmpNx])
                            syls_nx -= tmpSylCt
                            syls_left -= tmpSylCt
                            rnd_ct = 0
            if rnd_ct >= len(words) * 3 or rnd_ct_repeat >= 100:
                # too many tries, reset solver
                rnd_ct_repeat += 1
                syls_nx = len(line)
                syls_left = len(line)
                rnd_ct = 0
                suggested_nxs = []
                suggested_words = []
                if is_first_line_in_rhyme:
                    picked_rhyme_nxs[rhyme_scheme[line_nx] - 1] = 0
                is_first_line_in_rhyme = 0
                if rnd_ct_repeat >= 100:
                    line_nx = 0
                    uses = [0] * len(uses)
                    rnd_ct_repeat = 0
                    picked_rhyme_nxs = [0] * max(rhyme_scheme)
                    final_poem = []
                    print ''
                    print 'Elapsed time: {0:.1f} s '.format(time.time() - poem_find_start_time)
                    print '+++ Poem cannot be resolved. Reset poem. +++'
                    print ''
                    if time.time() - poem_find_start_time > 60:
                        # time limit for poem solving with given number of keywords reached,
                        # restart solver with more keywords (and therefore more synonyms and words)
                        print '+++ Trying to create new poem with more keywords. +++'
                        break_loop = 1
        for tmpCtNx, nx in enumerate(suggested_nxs):
            uses[nx] += 1
            if tmpCtNx == 0:
                final_poem.append([])
            final_poem[-1].append(words[nx].title())
            final_words.append(words[nx])

        line_nx += 1

    if break_loop:
        # poem not resolved, reset solver and try with more keywords
        cur_no_of_words += 5
        break_loop = 0
        print '+++ Now working with ' + str(cur_no_of_words) + ' keywords. +++'
        if cur_no_of_words > max_no_of_words:
            print '+++ Poem generation not successful. +++'
            log_string = "{0} fail {1} {2:.1f}s\n".format(str(datetime.utcnow()), str(cur_no_of_words),
                                                          time.time() - script_start_time)
            break
    else:
        # poem resolved successfully
        db.poems.insert({
            'date': datetime.utcnow() + timedelta(hours=6),
            'keywords': word_cloud,
            'poem': final_poem
        })
        log_string = "{0} ok {1} {2:.1f}s\n".format(str(datetime.utcnow()), str(cur_no_of_words),
                                                    time.time() - script_start_time)
        break

# write scraper log
with open(os.environ['OPENSHIFT_DATA_DIR'] + "scraper_log.txt", "a") as scraper_log:
    scraper_log.write(log_string)
