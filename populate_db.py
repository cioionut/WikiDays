"""Populate DataBase with Wikipedia - Days of the year."""
from pymongo import MongoClient
import sys
# import wikipedia
import mwclient
import json
import re
from bson import json_util
# from bson.objectid import ObjectId


def get_years_titles(raw):
    """Return a dict witch contains years and coresponding events or births."""
    # regex witch matches one or more decimal digits
    r_digits = re.compile('\d+')
    # match words between square brackets i.e. [[Roman emperor]]
    # r_sbrackets = re.compile('(\[\[[\w ]+\]\])')
    r_word = re.compile('[^(\[\[)$(\]\])]+')
    results = []
    for ye_row in raw.split('\n')[1:]:
        if len(ye_row.split('&ndash;')) == 2:
            year, title = ye_row.split('&ndash;')
            if r_digits.search(year):
                year = r_digits.search(year).group()
            matched_words = re.findall(r'(\[\[[^\[\]]+\]\])', title)
            for sword in matched_words:
                word = r_word.search(sword).group()
                title = title.replace(sword, word).strip()
            item = {'year': year, 'title': title}
            results.append(item)
    return results


def get_holi_obs(raw):
    """Return a list with holidays and observances."""
    r_word = re.compile('[^(\[\[)$(\]\])]+')
    results = []
    for o_row in raw.split('\n')[1:]:
        matched_words = re.findall(r'(\[\[[^\[\]]+\]\])', o_row)
        for sword in matched_words:
            word = r_word.search(sword).group()
            o_row = o_row.replace(sword, word).strip('*').strip(' ')
        item = {'title': o_row}
        results.append(item)
    return results


def populate():
    """Populate Database with wikipedia records."""
    client = MongoClient()
    db = client.wikidays
    wiki_web = 'en.wikipedia.org'
    site = mwclient.Site(('https', wiki_web), path='/w/')
    category = site.Pages['Category:Days of the year']

    Events = 1
    Births = 2
    Deaths = 3
    Holidaysandobservances = 4
    # drop if colection already exist
    db.days.drop()
    for page in category:
        day = page.name.replace(' ', '_')
        events = get_years_titles(page.text(section=Events))
        births = get_years_titles(page.text(section=Births))
        deaths = get_years_titles(page.text(section=Deaths))
        holi_obs = get_holi_obs(page.text(section=Holidaysandobservances))

        r = db.days.insert_one(
            {
                'Day': day,
                'Events': events,
                'Births': births,
                'Deaths': deaths,
                'Holidaysandobservances': holi_obs
            })
        print("Day: {0:<12} == complete == document id: {1}".format(page.name, r.inserted_id,))


def main(argv):
    """Main function of script."""
    try:
        populate()
    except mwclient.MwClientErrorc as e:
        print('Unexpected mwclient error occurred: ' + e.__class__.__name__)
        print(e.args)

if __name__ == "__main__":
    main(sys.argv)
