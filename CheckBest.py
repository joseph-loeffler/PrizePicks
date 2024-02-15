"""
Created on 3/30/23
@author: josephloeffler
"""

from datetime import date
from urllib.request import urlopen
import certifi
import ssl
import math
import time
import requests
import pandas as pd

pp_props_url = 'https://api.prizepicks.com/projections'
headers = {
    'Connection': 'keep-alive',
    'Accept': 'application/json; charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/106.0.0.0 Safari/537.36',
    'Access-Control-Allow-Credentials': 'true',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Referer': 'https://app.prizepicks.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9'}

response = requests.get(url=pp_props_url, headers=headers).json()
df = pd.json_normalize(response, record_path=['data'])


def round_near_int(n: float, decimals=0):
    """
    rounds n (rounding up at 0.5) to a specified number of decimals
    :param n: number to be rounded
    :param decimals: number of decimals to be rounded to
    :return: rounded version of n
    """
    multiplier = 10 ** decimals
    return math.floor(n * multiplier + 0.5) / multiplier


def get_ids():

    global response

    id_dict = {}
    for player in response['included']:
        id_dict[player['id']] = player['attributes']['name'].strip()

    return id_dict


def scrape_prize_api(league_inp='all'):
    """
    gets a list of all Prize Picks lines for the day, and can be specified
    to a certain league.
    :param league_inp: string representing the specified league. All leagues
    if left blank
    :return: a list of all Prize Picks lines for the day
    e.g., [..., ['NBA', 'Stephen Curry', ['ast'], 5.5], ...]
    """

    global response

    stat_term_dict = {'Points': ['pts'],
                      'Rebounds': ['trb'],
                      'Assists': ['ast'],
                      'Pts+Rebs+Asts': ['pts', 'trb', 'ast'],
                      'Fantasy Score': ['fnt'],  # Going to be a problem to fix
                      '3-PT Made': ['fg3'],
                      'Pts+Rebs': ['pts', 'trb'],
                      'Pts+Asts': ['pts', 'ast'],
                      'Rebs+Asts': ['trb', 'ast'],
                      'Free Throws Made': ['ft'],
                      'Blks+Stls': ['blk', 'stl'],
                      'Blocked Shots': ['blk'],
                      'Steals': ['stl'],
                      'Turnovers': ['tov']
                      }

    id_dict = get_ids()

    lines = []
    for elem in response['data']:
        league_id = elem['relationships']['league']['data']['id']
        league = id_dict[league_id]

        if (league == league_inp) or (league_inp == 'all'):
            over_under = elem['attributes']['line_score']
            stat_type = elem['attributes']['stat_type']

            player_id = elem['relationships']['new_player']['data']['id']
            player = id_dict[player_id]

            line = [league, player, stat_term_dict[stat_type], over_under]

            lines.append(line)

    return sorted(lines)


def get_nba_year():
    """
    takes the current date and deduces the nba season year
    :return: string of the current season year (e.g., '2023')
    """
    today = str(date.today())
    today = today.split("-")

    if int(today[1]) < 7:
        season = today[0]
    else:
        season = str(int(today[0]) + 1)

    return season


def get_pp_html(player: str):
    """
    Returns the html string of the BasketballReference.com page of the
    desired player. A limitation is that certain players might return the
    wrong page if their names are similar.
    :param player: the desired player
    :return: the html string of the website
    """
    player = (player.lower()).split()
    season = get_nba_year()

    # getting the correct BasketballReference.com page and assigning it to
    # html as a string
    url = "https://www.basketball-reference.com/players/" + player[1][0] + \
          "/" + player[1][:5] + player[0][:2] + "01/gamelog/" + season
    page = urlopen(url, context=ssl.create_default_context(
        cafile=certifi.where()))
    html = page.read().decode("utf-8")

    return html


def scrape_stats(player: str, stats: list):
    """
    :param player: the desired player
    :param stats: list of strings of unique desired stats
    :return: a dictionary personalized to the player where the keys are the
    stat types and each value is the list of that stat total in each game.
    """

    # gets the html from the desired player site
    html = get_pp_html(player)
    # time.sleep(3)

    p_stats_dict = {}

    # scrape list of stats for each stat_type. Add them to p_stats_dict
    for stat in stats:
        # initializing variables for the loop
        stat_game_lst = []
        row = 1

        # helps w/ the mechanism to check that stats are unique
        text_start_idx = 0

        # loops over the non-DNP rows of stats and finds the desired stat
        while True:
            # gets the index of the row
            row_string = 'data-stat="ranker" csk="' + str(row) + '"'
            row_idx = html.find(row_string)

            # string is the html where the *text* starts
            string = 'data-stat="' + stat + '" >'
            string_start_idx = html.find(string, row_idx)

            # ends the loop when the loop arrives at the last game
            if (string_start_idx > html.find("</table>", row_idx)) or (
                    string_start_idx == -1):
                p_stats_dict[stat] = stat_game_lst
                break

            # helps make sure the stat is unique
            text_start_test = text_start_idx

            # gets the first index of the desired stat
            text_start_idx = string_start_idx + len(string)

            # makes sure that the stat is unique
            if text_start_idx == text_start_test:
                row += 1
                continue

            # gets the last index of the desired stat
            next_html_tag_offset = html[text_start_idx:].find('<')
            text_end_idx = text_start_idx + next_html_tag_offset

            # assigns the desired stat to clean_text (the strip is just good
            # practice I think)
            raw_text = html[text_start_idx:text_end_idx]
            clean_text = raw_text.strip(" \r\n\t")
            stat_game_lst.append(int(clean_text))

            row += 1

    return p_stats_dict


def check_best(file):
    """

    :param file:
    :return:
    """
    f = open(file, "r")
    # make a dict with each player's stat_types

    p_stat_types_dict = {}
    num = 0
    for line in f:
        if num == 0:
            num += 1
            continue
        # e.g., NBA,Brandon Ingram,0.615,UNDER,37.5,pts+trb+ast,0.0\n
        line = (line.strip()).split("\t")
        player = line[1]
        stat_type = (line[5]).split("+")
        if player not in p_stat_types_dict.keys():
            p_stat_types_dict[player] = []
        p_stat_types_dict[player].extend(stat_type)

    ps_stats_dict = {}  # eg {player: {stat_type: [game stats], ...}, ...}
    for player in p_stat_types_dict.keys():
        # make the stat types unique
        p_stat_types_dict[player] = set(p_stat_types_dict[player])

        # get the player's html *once*, and scrape all their stats, and add
        # that dictionary to the bigger overall dictionary with each player
        # as a key. Also, it makes sure to not get timed out from
        # BasketballReference.com

        start_time = time.time()
        ps_stats_dict[player] = scrape_stats(player, p_stat_types_dict[player])
        end_time = time.time()
        time_elapsed = end_time - start_time
        if (3 - time_elapsed) > 0:
            time.sleep(3 - time_elapsed)

    # for each inner list in all_pp_lines, lookup the player and the
    # desired stat in the player's nested dictionary, then calculate odds
    # based on the O/U Prize Picks gives

    ret = ["LEAGUE\tPlayer\twin%\tO/U\tline #\tstat\twin:lose\tSuccess?"]
    num = 0

    f.seek(0)

    lst = (f.readlines())[1:]
    for line in lst:  # NBA,Brandon Ingram,0.615,UNDER,37.5,pts+trb+ast,0.0
        line = (line.strip()).split("\t")
        player = line[1]
        stat_type_list = (line[5]).split("+")

        game_stats = []
        for stat_type in stat_type_list:
            if not game_stats:
                game_stats = ps_stats_dict[player][stat_type]
            else:
                game_stats = [sum(x) for x in zip(game_stats,
                                                  ps_stats_dict[player]
                                                               [stat_type])]
        line_num = line[4]
        if not (game_stats == []):
            if float(game_stats[-1]) > float(line_num):
                correct = 'OVER'
            elif float(game_stats[-1]) < float(line_num):
                correct = 'UNDER'
            else:
                correct = 'EVEN'

            over_under = line[3]
            line = "\t".join(line)

            if correct == 'EVEN':
                elem = line + "\tEVEN"
            elif correct == over_under:
                elem = line + "\tWIN"
            else:
                elem = line + "\tLOSE"

            elem = elem.split("\t")

            last = elem[-1]
            s_last = elem[-2]

            elem[-1] = s_last
            elem[-2] = last

            if elem[6] == 'WIN':
                elem.append('1')
            elif elem[6] == 'LOSE':
                elem.append('0')
            elif elem[6] == 'EVEN':
                elem.append('0.5')
            print(elem)

            elem = "\t".join(elem)

            ret.append(elem)

    return ret
    # e.g.,["NBA,Stephen Curry,win%=0.6,OVER,5.5,ast,tie%=0.1",...]


if __name__ == '__main__':

    fw = open('bestPicksChecked.txt', 'w')

    checks = check_best('bestPicks.txt')
    # print(checks)
    for elem in checks:
        fw.write(elem + '\n')

    pl = open("PreviousLines.txt", "a")
    c = 0
    for elem in checks:
        if c == 0:
            c += 1
            continue
        pl.write(elem + '\n')
    pl.close()

    fw.close()


    pass
