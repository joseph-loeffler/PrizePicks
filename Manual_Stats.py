"""
Created on 1/24/23
@author: josephloeffler
"""
import math


def round_near_int(n, decimals=0):
    """rounds n (rounding up at 0.5) to a specified number of decimals"""
    multiplier = 10 ** decimals
    return math.floor(n * multiplier + 0.5) / multiplier


def p_over(n_over, n_under, n_even):
    """calculates probability of hitting the over"""
    a = n_over / (n_over + n_under + n_even)
    return a


def p_under(n_over, n_under, n_even):
    """calculates probability of hitting the under"""
    a = n_under / (n_over + n_under + n_even)
    return a


def p_even(n_over, n_under, n_even):
    """calculates probability of hitting the even"""
    a = n_even / (n_over + n_under + n_even)
    return a


def ou_player(p_num):
    """Prints whether to take the over or under for the "p_num"th player
    (based on inputted stats) and what the likelihood of it hitting is.
    Returns the p(green), p(red), and p(even) as a list"""

    # Determines how to refer to the "p_num"th player
    if p_num == 1:
        p = "1st"
    elif p_num == 2:
        p = "2nd"
    elif p_num == 3:
        p = "3rd"
    else:
        p = str(p_num) + "th"

    # Gets the player's stats from input
    n_over = int(input("How many times has your " + str(p) + " player hit the "
                                                             "over? "))
    n_under = int(input("How many times has your " + str(p) + " player hit "
                                                              "the under? "))
    n_even = int(input("How many times has your " + str(p) + " player been "
                                                             "even with the "
                                                             "O/U? "))
    # Calculates the players of hitting the O/U
    po = p_over(n_over, n_under, n_even)
    pu = p_under(n_over, n_under, n_even)
    e = p_even(n_over, n_under, n_even)

    # Determines the best strategy and prints it
    w = 1
    ls = 1
    if po > pu:
        print("\nYour", p, "player has a", round_near_int(po * 100, 1),
              "% chance of hitting the OVER: take it!\n")
        w = po
        ls = pu
    elif po < pu:
        print("\nYour", p, "player has a", round_near_int(pu * 100, 1),
              "% chance of hitting the UNDER: take it!\n")
        w = pu
        ls = po
    elif po == pu:
        print("\nYour", p, "player is just as likely to hit the over as the "
                           "under: it doesn't matter what you pick.\n")
        w = po
        ls = pu

    return w, e, ls


def count_wtl(univ: list, situation: int, wins: int, ties: int, losses: int):
    """counts the number of wins, ties, and losses in a given situation"""
    if (univ[situation].count('p_green') == wins) and \
            (univ[situation].count('p_white') == ties) and \
            (univ[situation].count('p_red') == losses):
        return True
    else:
        return False


def exp_profit(legs, bet_type):
    """calculates expected profit"""

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

    # assigning returned values from ou_player in a matrix
    probs_vals = []
    for i in range(legs):
        p_green, p_white, p_red = ou_player(i + 1)
        probs_vals.append([p_green, p_white, p_red])

    # making a matrix that simply list the *names* of win, tie, and lose probs
    # (no numerical data here)
    probs_names = []
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


if __name__ == '__main__':
    i_legs = int(input("How many legs? "))
    i_type = input("Power Play or Flex? ")
    br = round_near_int(exp_profit(i_legs, i_type), 2)
    print("\nYou should expect a", br, "return on your bet")
    pass
