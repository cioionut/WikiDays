"""Server code."""
from flask import Flask
from flask import request
from flask import Response
import json
from bson import json_util
from pymongo import MongoClient
import sys
import optparse

app = Flask(__name__)


def build_results(dict_list, day, category):
    """Build specified list of results."""
    results = []
    for item in dict_list:
        year = None
        if 'year' in item:
            year = item['year']
        result = {
                    'title': item['title'],
                    'year': year,
                    'day': day,
                    'category': category
                 }
        results.append(result)
    return results


def get_data(year, day, category, keyword):
    """Return data from database."""
    # print(year, day, category)
    client = MongoClient()
    db = client.wikidays

    categories = ['Events', 'Births', 'Deaths', 'Holidaysandobservances']
    results = []
    if year is not None and day is not None and category is not None:
        cursor = db.days.find(
                    {
                        'Day': day,
                        category+'.year': year
                    })
        for document in cursor:
            dict_list = [x for x in document[category] if x['year'] == year]
            results += build_results(
                                        dict_list,
                                        document['Day'],
                                        category)

    elif year is not None and day is not None:
        cursor = db.days.find(
                    {
                        'Day': day,
                        '$or':
                            [
                                {categories[0]+'.year': year},
                                {categories[1]+'.year': year},
                                {categories[2]+'.year': year}
                            ]
                    })
        for document in cursor:
            for cat in categories[:3]:
                dict_list = [x for x in document[cat] if x['year'] == year]
                results += build_results(dict_list, document['Day'], cat)

    elif year is not None and category is not None:
        cursor = db.days.find(
                    {
                        category+'.year': year
                    })
        for document in cursor:
            dict_list = [x for x in document[category] if x['year'] == year]
            results += build_results(
                                        dict_list,
                                        document['Day'],
                                        category)
    elif year is not None:
        cursor = db.days.find(
                    {
                        '$or':
                            [
                                {categories[0]+'.year': year},
                                {categories[1]+'.year': year},
                                {categories[2]+'.year': year}
                            ]
                    })
        for document in cursor:
            for cat in categories[:3]:
                dict_list = [x for x in document[cat] if x['year'] == year]
                results += build_results(dict_list, document['Day'], cat)

    elif day is not None and category is not None:
        cursor = db.days.find(
                    {
                        'Day': day
                    })
        for document in cursor:
            dict_list = document[category]
            results += build_results(
                                        dict_list,
                                        document['Day'],
                                        category)

    elif category is not None:
        cursor = db.days.find()
        for document in cursor:
            dict_list = document[category]
            results += build_results(
                                        dict_list,
                                        document['Day'],
                                        category)

    elif day is not None:
        cursor = db.days.find(
                    {
                        'Day': day
                    })
        for document in cursor:
            for cat in categories:
                dict_list = document[cat]
                results += build_results(dict_list, document['Day'], cat)

    elif keyword is not None:
        cursor = db.days.find(
                    {
                        '$text':
                        {
                            '$search': keyword,
                            '$caseSensitive': True,
                            '$diacriticSensitive': True
                        }
                    })
        for document in cursor:
            for cat in categories:
                dict_list = [x for x in document[cat] if keyword in x['title']]
                results += build_results(dict_list, document['Day'], cat)

    return results


@app.route("/", methods=['GET'])
def index():
    """Index function."""
    year = request.args.get('year')
    day = request.args.get('day')
    category = request.args.get('category')
    keyword = request.args.get('keyword')
    if day is not None:
        day = day.lower().capitalize()
    if category is not None:
        category = category.lower().capitalize()

    resDict = {'results': get_data(year, day, category, keyword)}

    js = json.dumps(
                        resDict,
                        sort_keys=True,
                        indent=4,
                        default=json_util.default)
    # print(js)
    resp = Response(response=js,
                    status=200,
                    mimetype="application/json")
    return(resp)


def run(argv):
    """Parse command line options and start the server."""
    parser = optparse.OptionParser()
    parser.add_option(
        '-d', '--debug',
        help="enable debug mode",
        action="store_true", default=False)
    parser.add_option(
        '-p', '--port',
        help="which port to serve content on",
        type='int', default=5000)

    opts, args = parser.parse_args()

    if opts.debug:
        app.run(debug=True, port=opts.port)
    else:
        app.run(port=opts.port)


if __name__ == "__main__":
    run(sys.argv)
