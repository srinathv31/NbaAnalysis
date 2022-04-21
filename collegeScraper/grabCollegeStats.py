import requests
from bs4 import BeautifulSoup
import pandas as pd
import progressbar

def scrapePlayerCollegeStats(playersDB: list):
    bar = progressbar.ProgressBar(max_value=len(playersDB))
    count = 0
    playersDBWithCollege = []
    college_start_year = ""
    college_end_year = ""
    for i in playersDB:
        count += 1
        if (i["college"] != ""):
            playerPageRequest = requests.get(i["url"])
            html_doc = playerPageRequest.text.replace('<!--', '').replace('-->', '')
            playerPageSoup = BeautifulSoup(html_doc, "html.parser")
            college_div = playerPageSoup.find("div", id="all_all_college_stats")
            college_table = college_div.find("table")
            college_stats = college_table.find("tbody")
            college_rows = college_stats.find_all("tr")
            college_years_played = []
            for college_year in college_rows:
                season = college_year.find("th")
                college_years_played.append(season.text)
            college_start_year = college_years_played[0]
            if (college_years_played[0] != college_years_played[-1]):
                college_end_year = college_years_played[-1]
            else:
                college_end_year = ""
        print(i["name"])
        print(college_start_year)
        print(college_end_year)
        player_entry_college = {
            'name': i["name"],
            'active_from': i["active_from"],
            'active_to': i["active_to"],
            'position': i["position"],
            'college': i["college"],
            'college_start_year': college_start_year,
            'college_end_year': college_end_year,
            'url': i["url"]
        }
        playersDBWithCollege.append(player_entry_college)
        college_start_year = ""
        college_end_year = ""
        bar.update(count)