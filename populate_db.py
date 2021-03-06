"""Populate DataBase with Wikipedia - Days of the year."""
from pymongo import MongoClient
import sys
import mwclient
import re


def get_years_titles(raw):
    """Parse a raw response from api and return a list of dicts.

    witch contains years and coresponding titles of Events, Births, Deaths
    """
    # regex witch matches one or more decimal digits
    r_digits = re.compile('\d+')
    # match words between square brackets i.e. [[Roman emperor]]
    r_word = re.compile('(\[\[[^\[\]]+\]\])')
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
    """Parse a raw response from api and return a list of dicts.

    witch contains coresponding titles Holidaysandobservances
    """
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
    # drop if collection already exist
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


def create_index_titles():
    """Create a text_index for titles."""
    client = MongoClient()
    db = client.wikidays
    categories = ['Events', 'Births', 'Deaths', 'Holidaysandobservances']
    db.days.create_index(
                            [
                                (categories[0]+'.title', 'text'),
                                (categories[1]+'.title', 'text'),
                                (categories[2]+'.title', 'text'),
                                (categories[3]+'.title', 'text'),
                            ]
                        )


def main(argv):
    """Main function of script."""
    try:
        # popolate db with wiki-records
        populate()
        # create a index-text for collection
        create_index_titles()
    except mwclient.MwClientError as e:
        print('Unexpected mwclient error occurred: ' + e.__class__.__name__)
        print(e.args)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main(sys.argv)
