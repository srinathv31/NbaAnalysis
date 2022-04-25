import numpy as np
import requests
from bs4 import BeautifulSoup

# Only scrapes NBA Players with "A" names to quickly test scraping functions
def grabNBADataTest():
    playersDB = np.array([])
    # Grab URL and Parse URL Page
    allPlayersURL = "https://www.basketball-reference.com/players/a"
    allPlayersPageRequest = requests.get(allPlayersURL)
    page_soup = BeautifulSoup(allPlayersPageRequest.content, "html.parser")
    table = page_soup.find("table")

    if table:
        table_body = table.find("tbody")
        for row in table_body:
            table_body.find_all("tr")
            player_url = row.find("a")
            try:
                # all data for all players uniform across database
                cells = row.findAll("td")
                active_from = int(cells[0].text)
            except (AttributeError):
                continue
            if (active_from > 2009):
                try:
                    player_names = player_url.text
                    active_to = int(cells[1].text)
                    position = cells[2].text
                    college = "Pittsburgh" if cells[6].text == "Pitt" else cells[6].text
                    player_entry = {
                        'name': player_names,
                        'active_from': active_from,
                        'active_to': active_to,
                        'position': position,
                        'college': college,
                        'url': "https://www.basketball-reference.com"+player_url['href'],
                        'key': 'a'
                    }
                    playersDB = np.append(playersDB, player_entry)
                    print(playersDB[-1]["name"])
                except (AttributeError):
                    continue
    return playersDB

if __name__ == '__main__':
    grabNBADataTest()
