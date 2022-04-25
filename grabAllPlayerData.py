import numpy as np
import requests
from bs4 import BeautifulSoup, NavigableString
import pandas as pd
import progressbar
import string
from multiprocessing import Pool

def grabNBAData():
    playersDB = np.array([])
    count = 0
    bar = progressbar.ProgressBar(max_value=26)
    for letter in string.ascii_lowercase:
        count += 1
        # Grab URL and Parse URL Page
        allPlayersURL = "https://www.basketball-reference.com/players/"+letter
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
                        }
                        playersDB = np.append(playersDB, player_entry)
                    except (AttributeError):
                        continue
        bar.update(count)
    return playersDB

def scrapePlayerCollegeStats(playerEntry):

    college_start_year = ""
    college_end_year = ""
    draft_position = {
        'draft_pick': "Undrafted",
        'draft_team': "Undrafted",
        'draft_year': "Undrafted" 
    }

    # Send URL Request and parse HTML
    playerPageRequest = requests.get(playerEntry["url"])
    html_doc = playerPageRequest.text.replace('<!--', '').replace('-->', '')
    playerPageSoup = BeautifulSoup(html_doc, "html.parser")

    # NBA Stats
    nba_stat_table = playerPageSoup.find("table", id="per_game")
    nba_stat_headers = nba_stat_table.find("thead").find_all("th", class_="poptip center")
    nba_stat_totals = nba_stat_table.find("tfoot").find_all("td", class_="right")

    nba_player_obj = {}
    nba_stat_labels = []
    for category in nba_stat_headers:
        nba_stat_labels.append(f"{category.text}")
    for (statLabel, totals) in zip(nba_stat_labels, nba_stat_totals):
        nba_player_obj[statLabel] = totals.text

    try:
        
        try:
            # Draft Position
            nba_player_card = playerPageSoup.find("div", itemtype="https://schema.org/Person")
            nba_player_card_elements = nba_player_card.find_all("p")
            for element in nba_player_card_elements:
                if (element.find_next("strong").text.strip() == "Draft:"):
                    draft_pick_raw_string = [p for p in element if isinstance(p, NavigableString)]
                    draft_pick = draft_pick_raw_string[2].strip().strip(',').strip()
                    draft_details = element.find_all("a")
                    draft_team = draft_details[0].text
                    draft_year = draft_details[1].text
                    break
            draft_position = {
                'draft_pick': draft_pick,
                'draft_team': draft_team,
                'draft_year': draft_year
            }
        # Catching if player is undrafted bc of no "Draft" <p> tag
        except UnboundLocalError:
            pass

        # College Stats
        if (playerEntry["college"] != ""):
            college_stat_header = playerPageSoup.find("table", id = "all_college_stats").find_next("thead")
            college_table = playerPageSoup.find("table", id = "all_college_stats").find_next("tbody")
            college_headers = college_stat_header.find_next("tr").find_next_sibling("tr")
            college_rows = college_table.find_all("tr")
            college_stat_footer = playerPageSoup.find("table", id = "all_college_stats").find_next("tfoot")
            college_career_stats = college_stat_footer.find_next("tr").find_next("td").find_next_siblings("td", class_ = "right")

            player_obj = {}
            stat_labels = []
            for k in college_headers.find_all("th", class_ = "poptip center"):
                stat_labels.append(f"C-{k.text}")
            for (statLabel, totals) in zip(stat_labels, college_career_stats):
                player_obj[statLabel] = totals.text

            # Calculate First and Final Year
            college_years_played = []
            for college_year in college_rows:
                season = college_year.find("th")
                college_years_played.append(season.text)
            college_start_year = college_years_played[0]
            if (college_years_played[0] != college_years_played[-1]):
                college_end_year = college_years_played[-1]
            else:
                college_end_year = ""
        player_entry_college = {
            'name': playerEntry["name"],
            'position': playerEntry["position"],
            'active_from': playerEntry["active_from"],
            'active_to': playerEntry["active_to"],
            'college': playerEntry["college"],
            'college_start_year': college_start_year,
            'college_end_year': college_end_year,
            'url': playerEntry["url"]
        }
        if (playerEntry["college"] != ""):
            player_entry_college = player_entry_college | nba_player_obj | draft_position | player_obj
        else:
            player_entry_college = player_entry_college | nba_player_obj | draft_position | {'C-G': '', 'C-MP': '', 'C-FG': '', 'C-FGA': '', 'C-3P': '', 'C-3PA': '', 'C-FT': '', 'C-FTA': '', 'C-ORB': '', 'C-TRB': '', 'C-AST': '', 'C-STL': '', 'C-BLK': '', 'C-TOV': '', 'C-PF': '', 'C-PTS': '', 'C-FG%': '', 'C-3P%': '', 'C-FT%': '', 'C-MP': '', 'C-PTS': '', 'C-TRB': '', 'C-AST': ''}
        return player_entry_college
    except AttributeError:
        player_entry_college = {
            'name': playerEntry["name"],
            'active_from': playerEntry["active_from"],
            'active_to': playerEntry["active_to"],
            'position': playerEntry["position"],
            'college': playerEntry["college"],
            'college_start_year': college_start_year,
            'college_end_year': college_end_year,
            'url': playerEntry["url"]
        } | nba_player_obj | draft_position | {'C-G': '', 'C-MP': '', 'C-FG': '', 'C-FGA': '', 'C-3P': '', 'C-3PA': '', 'C-FT': '', 'C-FTA': '', 'C-ORB': '', 'C-TRB': '', 'C-AST': '', 'C-STL': '', 'C-BLK': '', 'C-TOV': '', 'C-PF': '', 'C-PTS': '', 'C-FG%': '', 'C-3P%': '', 'C-FT%': '', 'C-MP': '', 'C-PTS': '', 'C-TRB': '', 'C-AST': ''}
        return player_entry_college

def main():
    playersDB = grabNBAData()

    print("\n\tGrabbing NBA and College Statistics...\n")
    playersDBWithCollege = np.array([])
    p = Pool(10)  # Pool tells how many at a time
    playersDBWithCollege = np.append(playersDBWithCollege, p.map(scrapePlayerCollegeStats, playersDB))
    p.terminate()
    p.join()

    print("\n*************************************************************************************************\n")
    print("\tFinished Loading! Check out the players.csv in the collectedData folder.")
    print("\n*************************************************************************************************\n")
    df = pd.DataFrame([d for d in playersDBWithCollege])
    df.to_csv("collectedData/playerData.csv", encoding="utf-8", index_label="index")

if __name__=="__main__":
    main()
