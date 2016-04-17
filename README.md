# WikiDays

## Setup

MongoDB - [Download & Install MongoDB](http://www.mongodb.org/downloads), and make sure it's running on the default port (27017).

Create wikidays database:
* Start mongo shell:
```bash
$ mongo
```
* In the new prompt, write:
```bash
> use wikidays
```
If your are using Ubuntu:
```bash
$ sudo apt-get install python3-pip
```
Install python requirements:
```bash
$ pip3 install -r requirements.txt
```

## Run Application

Download project on your system:
```bash
git clone https://github.com/cioionut/WikiDays.git
```

Move in application directory:
```bash
cd WikiDays
```

### Populate database with wikipedia records:
```bash
$ python3 populate_db.py
```
### Run server:
```bash
$ python3 server_app.py
```
* Use -p for specify port or use -d for enable debug mode:
* Example:
```bash
$ python3 server_app.py -p 8080 -d
```
## Project functionality:
* First script 'populate_db.py' make api calls via mwclient (a Python framework to interface with the MediaWiki API)
and go through all days of a year and store all data for all categories in database 'wikidays' in 'days' collection. And then make a call to function 'create_index_titles()' witch create a text-index for collection. For instance:
```bash
  {
      "Day": "March_13,
      "Events": [
                    {
                      "year": "1639",
                      "title": "Harvard College is named after clergyman John Harvard"
                    },
                    {...}
                  ],
      "Births":  [
                    {
                      "year": "1639",
                      "title": "Harvard College is named after clergyman John Harvard"
                    },
                    {...}
                  ],
      "Deaths":  [
                    {
                      "year": "1639",
                      "title": "Harvard College is named after clergyman John Harvard"
                    },
                    {...}
                  ],
      "Holidaysandobservances": [
                    {
                      "year": "1639",
                      "title": "Harvard College is named after clergyman John Harvard"
                    },
                    {...}
                  ],
  }
  ```

  * Server accept queries by day, year and category in many combinations like:
  * [year=1994 and category=births](http://127.0.0.1:5000/?year=1994&category=births)
  * [just day=may_1](http://127.0.0.1:5000/?day=may_1)
  * Also server support queries by a keyword, for instance word:
  * [Newton](http://127.0.0.1:5000/?keyword=Newton)
  * Response is a json document like:

  ```bash
  {
    "results": [
        {
            "category": "Events",
            "day": "March_15",
            "title": "French physicist Augustin-Jean Fresnel wins a contest at the Academie des Sciences in Paris by proving that light behaves like a wave. The Fresnel integrals, still used to calculate wave patterns, silence skeptics who had backed the particle theory of Isaac Newton.",
            "year": "1819"
        },
        {...}
        {
            "category": "Deaths",
            "day": "December_22",
            "title": "Walter Newton Read, American lawyer and second chairman of the New Jersey Casino Control Commission (b. 1918)",
            "year": "2001"
        },
    ]
  }
```

### Refresh the data from Wikipedia at 2 hours interval:

* Setup CronJob:
```bash
$ crontab -e
```
* In opened editor insert configuration:
```bash
0 */2 * * * /path-to/WikiDays/.env/bin/python3 /path-to/WikiDays/update_db.py >> /path-to/WikiDays/logs/cronlog.txt
```
