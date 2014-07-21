import urllib2
import lxml.html as lxml
import csv
import argparse
import json
import time

BALL_STRIKE_URL = 'http://www.fangraphs.com/statsd.aspx?playerid={}&position=P&type=4&gds=&gde=&season={}'
PITCHER_FILE = './pitcher_by_year/pitchers_{}.csv'


def balls_strikes(playerid, year):
    """Scrapes fangraphs for stats. URL takes player id and year perameter.

    Returns pitcher id, date, balls and strikes for a given year"""
    html = urllib2.urlopen(BALL_STRIKE_URL.format(playerid, year)).read()
    doc = lxml.fromstring(html)

    # A little funky cleanup is required from the xpath data
    dates = [x for x in doc.xpath('//*[@id="DailyStats1_dgSeason1"]//td[1]/a/text()') if x != 'Date']
    print dates
    balls = doc.xpath('//tbody/tr/td[13]/text()')[1:]
    strikes = doc.xpath('//tbody/tr/td[14]/text()')[1:]

    data = []
    for date, ball, strike in zip(dates, balls, strikes):
        data.append(
            dict(
                playerid=playerid,
                date=date,
                balls=ball,
                strikes=strike
            )
        )

    return data


def starting_pitchers(year):
    """Read csv file of standard pitching stats for all pitchers from a given year.

    Return a list of pitchers who started games."""
    file = PITCHER_FILE.format(year)

    data = []
    with open(file, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if num(row[6]) > 0:
                data.append(row[-1])

    return data


def num(s):
    try:
        return int(s)
    except ValueError:
        return -1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get stats of every pitchers start for a year')
    parser.add_argument('-y', '--year', required=True, help='Year that you want stats for')
    args = parser.parse_args()
    year = args.year
    pitcher_ids = starting_pitchers(year)
    for pitcher_id in pitcher_ids:
        print json.dumps(balls_strikes(pitcher_id, year))
        # Give the server a breather
        time.sleep(1)