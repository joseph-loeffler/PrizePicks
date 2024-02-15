"""
Created on 2/21/23
@author: josephloeffler
"""
from datetime import date
from urllib.request import urlopen
import certifi
import ssl
import math
import time


def scrape_stat(player, stat):
    """
    :param player: the desired player
    :param stat: the desired stat
    :return: a list of the player's stat totals from every game so far in the
    season, not including DNPs
    """

    # takes the current date and deduces the nba season year
    today = str(date.today())
    today = today.split("-")

    if int(today[1]) < 7:
        season = today[0]
    else:
        season = str(int(today[0])+1)

    player = (player.lower()).split()

    # getting the correct BasketballReference.com page and assigning it to
    # html as a string
    url = "https://www.basketball-reference.com/players/" + player[1][0] + \
        "/" + player[1][:5] + player[0][:2] + "01/gamelog/" + season
    # print(url)
    page = urlopen(url, context=ssl.create_default_context(
        cafile=certifi.where()))
    html = page.read().decode("utf-8")
    # print(html)

    # wait 3 seconds to prevent error 429
    time.sleep(2)

    # initializing variables for the loop
    ret = []
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

        # ends the loop (and function) when the loop arrives at the last game
        if (string_start_idx > html.find("</table>", row_idx)) or (
                string_start_idx == -1):
            return ret

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
        ret.append(int(clean_text))

        row += 1


def round_near_int(n: float, decimals=0):
    """
    rounds n (rounding up at 0.5) to a specified number of decimals
    :param n: number to be rounded
    :param decimals: number of decimals to be rounded to
    :return: rounded version of n
    """
    multiplier = 10 ** decimals
    return math.floor(n * multiplier + 0.5) / multiplier


def probs(player: str, stat: str, ou: float):
    """
    returns the probability of hitting the OVER, UNDER, and EVEN
    :param stat: desired stat
    :param player: name of the desired player
    :param ou: the given Over/Under line
    :return: probabilities as a tuple: (OVER, UNDER, EVEN)
    """
    stats = scrape_stat(player, stat)

    n_over = len([i for i in stats if i > ou])
    n_under = len([i for i in stats if i < ou])
    n_even = len([i for i in stats if i == ou])

    if n_over == 0 and n_under == 0 and n_even == 0:
        return "pass"
    else:
        p_over = n_over / (n_over + n_under + n_even)
        p_under = n_under / (n_over + n_under + n_even)
        p_even = n_even / (n_over + n_under + n_even)

    return p_over, p_under, p_even


def ou_player(player: str,  stat: str, ou: float):
    """
    Prints whether to take the over or under for the player (based on
    web-scraped stats and the inputted ou) and what the likelihood of it
    hitting is.
    :param player:
    :param stat:
    :param ou:
    :return: p(green), p(red), and p(even) as a list
    """

    if probs(player, stat, ou) == "pass":
        return "pass"

    # Calculates the player's chance of hitting the O/U
    po, pu, e = probs(player, stat, ou)

    # adding best values to a csv file
    spreadsheet = open("bestPicks.txt", 'a')

    # Determines the best strategy and prints it
    w = 1
    ls = 1
    if po > pu:
        print("\n", player, "has a", round_near_int(po * 100, 1),
              "% chance of hitting the OVER: take it!")
        spreadsheet.write(player + "," + stat + ",over," + str(po) + "\n")
        w = po
        ls = pu
    elif po < pu:
        print("\n", player, "has a", round_near_int(pu * 100, 1),
              "% chance of hitting the UNDER: take it!")
        spreadsheet.write(player + "," + stat + ",under," + str(pu) + "\n")
        w = pu
        ls = po
    elif po == pu:
        print("\n", player, "is just as likely to hit the over as the "
                            "under: it doesn't matter what you pick.")
        spreadsheet.write(player + "," + stat + ",either,0.5" + "\n")
        w = po
        ls = pu

    spreadsheet.close()

    return w, e, ls


def count_wtl(univ: list, situation: int, wins: int, ties: int, losses: int):
    """
    counts the number of wins, ties, and losses in a given situation and
    returns True if those numbers are the same as the inputted numbers for w, t,
    and loses
    :param univ: universe of possible outcomes
    :param situation: the particular comb. of w, t, and l you want to check
    :param wins: number of wins you want to check for
    :param ties: number of ties you want to check for
    :param losses: number of losses you want to check for
    :return: True or False
    """
    if (univ[situation].count('p_green') == wins) and \
            (univ[situation].count('p_white') == ties) and \
            (univ[situation].count('p_red') == losses):
        return True
    else:
        return False


def exp_profit(info: list, bet_type: str):
    """
    Calculates and prints the probability of the players hitting the most
    likely option between the over an under.
    :param info: list of tuples: (player, stat, ou)
    :param bet_type: flex or power play (pp)
    :return: expected profit
    """

    legs = len(info)

    # prints bet_type to avoid incorrect arguments
    if bet_type.lower() == "flex":
        print("You chose Flex")
        # checks whether legs and bet_type are compatible
        if legs < 3 or legs > 6:
            print("Flex plays do not support", legs, "legs")
            return "Error"
    elif bet_type.lower() == "pp" or bet_type == "power play":
        print("You chose Power Play")
        if legs < 2 or legs > 4:
            print("Power Plays do not support", legs, "legs")
            return "Error"
    else:
        print('''You must choose either "Power Play" or "Flex"''')
        return "error"

    # assigning returned values from ou_player in a neste list
    probs_vals = []
    error_players = 0
    for player, stat, ou in info:

        ou_player_vals = ou_player(player, stat, ou)

        if ou_player_vals == "pass":
            error_players += 1
            print("\nCouldn't find " + player + "'s BasketballReference page")
            continue
        else:
            p_green, p_white, p_red = ou_player_vals
            probs_vals.append([p_green, p_white, p_red])

    # making a nested list that simply list the *names* of win, tie, and lose
    # probs (no numerical data here)
    probs_names = []
    legs += -error_players
    for i in range(legs):
        probs_names.append(["p_green", "p_white", "p_red"])

    # creating the universe of possible outcomes w/ each outcome being the
    # *probabilities* along a branch of the probability tree
    univ_vals = []
    for branch in range(3 ** legs):
        outcome = []
        for plyr_num in range(legs):
            nth_player = probs_vals[plyr_num][math.floor((branch / 3 ** (
                    legs - plyr_num - 1)) % 3)]
            outcome.append(nth_player)
        univ_vals.append(outcome)

    # creating the universe of possible outcomes w/ each outcome being the
    # *win(s), tie(s), and/or loss(es)* along a branch of the probability tree
    univ_names = []
    for branch in range(3 ** legs):
        outcome = []
        for plyr_num in range(legs):
            nth_player = probs_names[plyr_num][math.floor((branch / 3 ** (
                    legs - plyr_num - 1)) % 3)]
            outcome.append(nth_player)
        univ_names.append(outcome)

    exp_prof = 0
    if bet_type.lower() == "flex":
        if legs == 3:
            for sit in range(len(univ_names)):
                if count_wtl(univ_names, sit, 3, 0, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 2.25 * sit_prob
                elif count_wtl(univ_names, sit, 2, 0, 1):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.25 * sit_prob
                # if tie
                elif count_wtl(univ_names, sit, 2, 1, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 3 * sit_prob
                elif count_wtl(univ_names, sit, 1, 2, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.5 * sit_prob
        elif legs == 4:
            for sit in range(len(univ_names)):
                if count_wtl(univ_names, sit, 4, 0, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 5 * sit_prob
                elif count_wtl(univ_names, sit, 3, 0, 1):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.5 * sit_prob
                # if ties
                elif count_wtl(univ_names, sit, 3, 1, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 2.25 * sit_prob
                elif count_wtl(univ_names, sit, 2, 1, 1):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.25 * sit_prob
                elif count_wtl(univ_names, sit, 2, 2, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 3 * sit_prob
                elif count_wtl(univ_names, sit, 1, 3, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.5 * sit_prob
        elif legs == 5:
            for sit in range(len(univ_names)):
                if count_wtl(univ_names, sit, 5, 0, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 10 * sit_prob
                elif count_wtl(univ_names, sit, 4, 0, 1):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 2 * sit_prob
                elif count_wtl(univ_names, sit, 3, 0, 2):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 0.4 * sit_prob
                # if ties
                elif count_wtl(univ_names, sit, 4, 1, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 5 * sit_prob
                elif count_wtl(univ_names, sit, 3, 1, 1):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.5 * sit_prob
                elif count_wtl(univ_names, sit, 3, 2, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 2.25 * sit_prob
                elif count_wtl(univ_names, sit, 2, 2, 1):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.25 * sit_prob
                elif count_wtl(univ_names, sit, 2, 3, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 3 * sit_prob
                elif count_wtl(univ_names, sit, 1, 4, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.5 * sit_prob
        elif legs == 6:
            for sit in range(len(univ_names)):
                if count_wtl(univ_names, sit, 6, 0, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 25 * sit_prob
                elif count_wtl(univ_names, sit, 5, 0, 1):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 2 * sit_prob
                elif count_wtl(univ_names, sit, 4, 0, 2):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 0.4 * sit_prob
                # if ties
                elif count_wtl(univ_names, sit, 5, 1, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 10 * sit_prob
                elif count_wtl(univ_names, sit, 4, 1, 1):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 2 * sit_prob
                elif count_wtl(univ_names, sit, 3, 1, 2):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 0.4 * sit_prob
                elif count_wtl(univ_names, sit, 4, 2, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 5 * sit_prob
                elif count_wtl(univ_names, sit, 3, 2, 1):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.5 * sit_prob
                elif count_wtl(univ_names, sit, 3, 3, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 2.25 * sit_prob
                elif count_wtl(univ_names, sit, 2, 3, 1):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.25 * sit_prob
                elif count_wtl(univ_names, sit, 2, 4, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 3 * sit_prob
                elif count_wtl(univ_names, sit, 1, 5, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.5 * sit_prob
    elif bet_type.lower() == "pp" or bet_type == "power play":
        if legs == 2:
            for sit in range(len(univ_names)):
                if count_wtl(univ_names, sit, 2, 0, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 3 * sit_prob
                elif count_wtl(univ_names, sit, 1, 1, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.5 * sit_prob
        elif legs == 3:
            for sit in range(len(univ_names)):
                if count_wtl(univ_names, sit, 3, 0, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 5 * sit_prob
                elif count_wtl(univ_names, sit, 2, 1, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 3 * sit_prob
                elif count_wtl(univ_names, sit, 1, 2, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.5 * sit_prob
        elif legs == 4:
            for sit in range(len(univ_names)):
                if count_wtl(univ_names, sit, 4, 0, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 10 * sit_prob
                elif count_wtl(univ_names, sit, 3, 1, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 5 * sit_prob
                elif count_wtl(univ_names, sit, 2, 2, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 3 * sit_prob
                elif count_wtl(univ_names, sit, 1, 3, 0):
                    sit_prob = 1
                    for i in range(legs):
                        sit_prob *= univ_vals[sit][i]
                    exp_prof += 1.5 * sit_prob
        else:
            print("Power plays do not support", legs, "legs")
            return "Error"

    return exp_prof


def get_bets(file):
    """"""

    ret = []
    count = 0
    for line in file:
        line = line.strip()
        lst = line.split(",")
        ret.append((lst[1], lst[2], float(lst[3])))
        count += 1

        if count == 6:
            return ret
    return ret


if __name__ == '__main__':
    f = open("BetInfo.txt", 'r')

    nlines = len(f.readlines())
    f.close()

    f = open("BetInfo.txt", 'r')

    counter = 0

    if nlines % 6 == 0:
        for _ in range(nlines//6):
            bets = get_bets(f)

            # bet_type = input("bet type (flex or pp): ")
            br = round_near_int(exp_profit(bets, "flex"), 2)
            print("\nYou should expect a", br, "return on your bet")

            counter += 1
    else:
        for _ in range(((nlines // 6) + (nlines % 6))-2):
            start_time = time.time()
            bets = get_bets(f)

            # bet_type = input("bet type (flex or pp): ")
            br = round_near_int(exp_profit(bets, "flex"), 2)
            print("\nYou should expect a", br, "return on your bet")
            print("My program took", time.time() - start_time, "to run")

            counter += 1
