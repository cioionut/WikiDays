"""Server code."""
from flask import Flask
from flask import request
from flask import Response
import json
from bson import json_util
from pymongo import MongoClient
app = Flask(__name__)


def build_results(dict_list, year, day, category):
    """Build specified list of results."""
    print(day)
    results = []
    for item in dict_list:
        result = {
                    'title': item['title'],
                    'year': year,
                    'day': day,
                    'category': category
                 }
        results.append(result)
    return results


def get_data(year, day, category):
    """Return data from database."""
    print(year, day, category)
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
                                        year,
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
                results += build_results(dict_list, year, document['Day'], cat)

    elif year is not None and category is not None:
        cursor = db.days.find(
                    {
                        category+'.year': year
                    })
        for document in cursor:
            dict_list = [x for x in document[category] if x['year'] == year]
            results += build_results(
                                        dict_list,
                                        year,
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
                results += build_results(dict_list, year, document['Day'], cat)

    elif day is not None and category is not None:
        cursor = db.days.find(
                    {
                        'Day': day
                    })
        for document in cursor:
            dict_list = document[category]
            results += build_results(
                                        dict_list,
                                        year,
                                        document['Day'],
                                        category)

    elif category is not None:
        cursor = db.days.find()
        for document in cursor:
            dict_list = document[category]
            results += build_results(
                                        dict_list,
                                        year,
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
                results += build_results(dict_list, year, document['Day'], cat)

    return results


@app.route("/", methods=['GET'])
def index():
    """Index function."""
    year = request.args.get('year')
    day = request.args.get('day')
    category = request.args.get('category')
    if day is not None:
        day = day.lower().capitalize()
    if category is not None:
        category = category.lower().capitalize()

    resDict = {'results': get_data(year, day, category)}

    js = json.dumps(
                        resDict,
                        sort_keys=True,
                        indent=4,
                        default=json_util.default)
    print(js)
    resp = Response(response=js,
                    status=200,
                    mimetype="application/json")
    return(resp)


if __name__ == "__main__":
    app.run()
