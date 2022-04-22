import requests
from bs4 import BeautifulSoup
import pandas as pd
import progressbar
import string

def grabNBAData():
    count = 0
    playersDB = []
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
                            'key': letter
                        }
                        playersDB.append(player_entry)
                    except (AttributeError):
                        continue
        bar.update(count)
    return playersDB

def grabCollegeData(playersDB: list, allCollegePlayersURL: string, letter: string):
    college_duration = ""
    playersDBWithCollege = []
    count = 0

    allCollegePlayersPageRequest = requests.get(allCollegePlayersURL)
    college_page_soup = BeautifulSoup(allCollegePlayersPageRequest.content, "html.parser")

    college_div = college_page_soup.find("div", id="content")
    college_list_header = college_div.find_next("h2").find_next("p")
    college_total_list = college_list_header.find_next_siblings("div")
    
    for i in list(filter(lambda d: d['key'] in letter, playersDB)):
        # if (i["key"] != letter):
        #     continue
        count += 1
        if (i["college"] != ""):
            for j in college_total_list:
                short_list = j.find_all("p")
                for x in short_list:
                    if ((x.find_next("a").text == i["name"]) and (x.find_next("small").find_next("a").text == i["college"])):
                        year = x.find_next("small")
                        # print(x.find_next("a").text) # Player Name
                        college_duration = year.find(text=True, recursive=False)
                        # print(year.find(text=True, recursive=False))
                        # print(x.find_next("small").find_next("a").text) # Player College
                        break
        player_entry_college = {
            'name': i["name"],
            'active_from': i["active_from"],
            'active_to': i["active_to"],
            'position': i["position"],
            'college': i["college"],
            'college_duration': college_duration,
            'url': i["url"]
        }
        playersDBWithCollege.append(player_entry_college)
        college_duration = ""
    return playersDBWithCollege

def generateCollegeURLs(playersDB: string):
    playersDBWithCollege = []
    count = 0
    bar = progressbar.ProgressBar(max_value=26)
    for letter in string.ascii_lowercase:
        count += 1
        playersDBWithCollege += (grabCollegeData(playersDB, "https://www.sports-reference.com/cbb/players/"+letter+"-index.html", letter))
        bar.update(count)
    return playersDBWithCollege

def main():
    playersDB = grabNBAData()
    playersDBWithCollege = generateCollegeURLs(playersDB)
    df = pd.DataFrame(playersDBWithCollege)
    df.to_csv("collectedData/playerData.csv", encoding="utf-8", index_label="index")

if __name__=="__main__":
    main()
