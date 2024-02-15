"""
Created on 4/7/23
@author: josephloeffler
"""

from urllib.request import urlopen
import certifi
import ssl
import time


def nba_urldict():

    start_time = time.time()
    url = "https://www.basketball-reference.com/contracts/players.html"
    page = urlopen(url, context=ssl.create_default_context(
        cafile=certifi.where()))
    html = page.read().decode("utf-8")
    print(html)
    plyr_end_idx = html.find('<table class="sortable stats_table" '
                             'id="player-contracts" data-cols-to-freeze=",2">')
    while True:

        plyr_start_idx = html.find('><a href="', plyr_end_idx) + len('><a href="')
        plyr_end_idx = html.find('"><a', plyr_start_idx)
        plyr_html = html[plyr_start_idx:plyr_end_idx]

        # print(plyr_html)
        if plyr_end_idx > html.find("</table>"):
            break
        plyr_url_start = plyr_html.find('"') + 1
        plyr_url_end = plyr_html.find('"', plyr_url_start + 1)
        plyr_url = plyr_html[plyr_url_start:plyr_url_end]

        plyr_name_start = plyr_html.find(">") + 1
        plyr_name_end = plyr_html.find("</a>")
        plyr_name = plyr_html[plyr_name_start:plyr_name_end]
        # print((plyr_name, plyr_url))

    end_time = time.time()
    time_taken = end_time - start_time
    if 3 - time_taken > 0:
        print(3 - time_taken)
        time.sleep(3-time_taken)


if __name__ == '__main__':

    nba_urldict()

    pass
