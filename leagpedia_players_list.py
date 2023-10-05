from googleapiclient.discovery import build
from google.oauth2 import service_account
from mwrogue.esports_client import EsportsClient
import orjson
from operator import itemgetter
import pandas as pd
import os
import time
import requests

"""
Script done to upload data to a Google Sheet from Leaguepedia.
This script gets a list of all the players from a single region.
It shows: LeaguepediaLink, Tag, Name, Location, Age, Role, Current Team, Last Team, 5 most played champions, total games

This script got obsolete because Leaguepedia now offers this to everyone on:
https://lol.fandom.com/wiki/Category:Players
https://lol.fandom.com/wiki/Category:Player_Residency_Categories
"""

def queryPlayers(response, site, gameVersion):
    """
    This function uses an EsportsClient(site) and a Leaguepedia Query with these fields:
    "P.OverviewPage, P.ID, P.Name, P.Country, P.Age, P.Role, P.Team, P.TeamLast"
    
    To loop over all tags of a player and get all of their games from leaguepedia
    """
    print("------------------------------------------------------------------------------------------------------------------------")
    
    # We get Champions.json from DDragon to update Champion Names
    # Ex: Cho'Gath -> Chogath / Wukong -> MonkeyKing / Tahm Kench -> TahmKench
    response_champions = requests.get(f'http://ddragon.leagueoflegends.com/cdn/{gameVersion}/data/en_US/champion.json')
    if response_champions.status_code != 200:
        response_champions.raise_for_status()
    file = orjson.loads(response_champions.content) # Change to orjson
    
    # sheet is the list of: lists of rows
    sheet=[]
    players = orjson.loads(orjson.dumps(response))
    sheetHeader=["Link", "Tag", "Name", "Location", "Age", "Role", "Current Team", "Last Team", "Games", "C1", "C2", "C3", "C4", "C5"]
    sheet.append(sheetHeader)
    
    # This K is just for a print statement
    k = 0
    for player in players:
        k=k+1
        # sheetRow is every row we are appending
        sheetRow = []
        
        dataGeneral = []
        print(player['OverviewPage'])
        print("Team: " + str(player['Team']))
        print("Games: " + str(player['Games']))
        dataGeneral = [ 'https://lol.fandom.com/wiki/' + player['OverviewPage'].replace(" ","_") , player['ID'],player['Name'].replace("&amp;nbsp;"," "),player['Country'],player['Age'],player['Role'],player['Team'],player['TeamLast']]
        sheetRow.extend(dataGeneral)
        
        # LeaguepediaQuery Example: DnDn
        # https://lol.fandom.com/wiki/Special:CargoQuery?tables=Players%3DP%2C+PlayerRedirects%3DPR%2C&fields=P.OverviewPage%2C+PR.OverviewPage%2C+PR.AllName%2C&where=P.OverviewPage%3D%27DnDn%27&join_on=P.OverviewPage%3DPR.OverviewPage&group_by=&having=&order_by%5B0%5D=&order_by_options%5B0%5D=ASC&limit=500&offset=0&format=
        # We get all usernames from a single player
        response_player_names = site.cargo_client.query(
            limit = "max",
            tables = "Players=P, PlayerRedirects=PR",
            fields = "P.OverviewPage, PR.OverviewPage, PR.AllName",
            where = "P.OverviewPage='"+ player['OverviewPage'] + "'",
            join_on="P.OverviewPage=PR.OverviewPage"
        )
        player_names = orjson.loads(orjson.dumps(response_player_names))
        championstotal=[]
        
        for pname in player_names:
            # Leaguepedia Example: DnDn
            # https://lol.fandom.com/wiki/Special:CargoQuery?tables=ScoreboardPlayers%3DSP&fields=SP.Champion%2C+COUNT%28SP.Champion%29%3DGames&where=SP.Link%3D%27DnDn%27&join_on=&group_by=SP.Champion&having=&order_by%5B0%5D=COUNT%28SP.Champion%29&order_by_options%5B0%5D=DESC&limit=500&offset=&format=
            # We get all games for every champion played by DnDn, for every name
            responseChampionsPlayer = site.cargo_client.query(
                limit = "max",
                tables = "ScoreboardPlayers=SP", # Table: https://lol.fandom.com/wiki/Special:CargoTables/ScoreboardPlayers
                fields = "SP.Champion, COUNT(SP.Champion)=Games",
                where = "SP.Link='" + pname['AllName'] + "'",
                order_by= "COUNT(SP.Champion) DESC",
                group_by= "SP.Champion"
            )
            champions = orjson.loads(orjson.dumps(responseChampionsPlayer))
            
            # We pass string to int to sum later on
            if len(champions) > 0:
                for champion in champions:
                    champion['Games'] = int(champion['Games'])
                championstotal.extend(champions)
            else:
                pass
        
        # We use pandas to group all champions from a player by Champion, and sum their games
        # Sort them by amount of games, and get the first 5 most played
        if len(championstotal) > 0:
            champions_grouped = pd.DataFrame(data=championstotal).groupby(['Champion'], as_index=False).Games.sum().to_dict('records')
            champions_grouped_and_sorted = sorted(champions_grouped, key=itemgetter('Games'), reverse=True)
            if len(champions_grouped_and_sorted) > 5:
                five_champions_grouped_and_sorted = champions_grouped_and_sorted[0:5]
            else:
                five_champions_grouped_and_sorted = champions_grouped_and_sorted
        else:
            five_champions_grouped_and_sorted = []
            pass        
        
        if len(five_champions_grouped_and_sorted) > 0:
            for champion in five_champions_grouped_and_sorted:
                
                championName = ''
                
                for champion_obj, champion_data in file['data'].items(): # Champions.json we requested before
                    if champion_data['name'] == str(champion['Champion']):
                        championName = champion_data['id']
                
                sheetRow.append(championName)
        else:
            pass
        
        # We use this if the player doesn't have 5 champions played
        while len(sheetRow) < 13:
            sheetRow.append("")        
        
        print("Row Number: " + str(k) + " added.")
        print("------------------------------------------------------------------------------------------------------------------------")
        
        # We append the Row
        sheetRow.append(player['Games'])
        sheet.append(sheetRow)
    return sheet

# Conexión API Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = os.getcwd() + "\\Keys\\llaves.json" # PATH Keys for GoogleSheets API
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
SPREADSHEET_ID = '' #Spreadsheet ID

# GoogleSheet API Request
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# Create EsportsClient using mwrogue
site = EsportsClient('lol')
queryFull=False
queryResponse=[]

# Doesn't stop until we have all players
while queryFull==False:
    queryOffset=len(queryResponse)
    print("Query Offset: " + str(queryOffset))
    
    # Leaguepedia Query to Get All Players from a single Region
    # Link of Example Query:
    # https://lol.fandom.com/wiki/Special:CargoQuery?tables=Players%3DP%2C+PlayerRedirects%3DPR%2C+ScoreboardPlayers%3DSP&fields=P.OverviewPage%2C+P.ID%2C+P.Name%2C+P.Country%2C+P.Age%2C+P.Role%2C+P.Team%2C+P.TeamLast%2C+COUNT%28SP.Link%29%3DGames&where=%28P.Residency%3D%27LAS%27+OR+P.Residency%3D%27Latin+America%27+OR+P.Residency%3D%27LAN%27%29+AND+P.IsRetired%3DFALSE+AND+P.ToWildrift%3DFALSE+AND+%28P.Role%3D%27Top%27+OR+P.Role%3D%27Jungle%27+OR+P.Role%3D%27Mid%27+OR+P.Role%3D%27Bot%27+OR+P.Role%3D%27Support%27+OR+P.Role%3D%27Substitute%27%29+AND+%28P.Name+IS+NOT+NULL%29&join_on=P.OverviewPage%3DPR.OverviewPage%2C+PR.AllName%3DSP.Link&group_by=P.OverviewPage&having=&order_by%5B0%5D=P.ID&order_by_options%5B0%5D=ASC&limit=500&offset=&format=
    response = site.cargo_client.query(
        limit = "max", # Max Limit is 500
        offset = queryOffset,
        tables = "Players=P, PlayerRedirects=PR, ScoreboardPlayers=SP", # Table: https://lol.fandom.com/wiki/Special:CargoTables/Players
        fields = "P.OverviewPage, P.ID, P.Name, P.Country, P.Age, P.Role, P.Team, P.TeamLast, COUNT(SP.Link)=Games",
        where = "(P.Residency='LAS' OR P.Residency='Latin America' OR P.Residency='LAN') AND " + # Change Residency here
                "P.IsRetired=FALSE AND P.ToWildrift=FALSE AND " +
                "(P.Role='Top' OR P.Role='Jungle' OR P.Role='Mid' OR P.Role='Bot' OR P.Role='Support' OR P.Role='Substitute') AND (P.Name IS NOT NULL)",
        join_on= "P.OverviewPage=PR.OverviewPage, PR.AllName=SP.Link",
        group_by= "P.OverviewPage",
        order_by= "P.ID ASC" # Ordered by ID
    )
    if len(response)>0:
        queryResponse.extend(response)
    else:
        queryFull=True
    time.sleep(0.1) # As a loop, I wait for API Limit


# We get Versions.json from DDragon to use it on the function
response_versions = requests.get('https://ddragon.leagueoflegends.com/api/versions.json')
if response_versions.status_code != 200:
    response_versions.raise_for_status()
versions = orjson.loads(response_versions.content) # Change to orjson

# Query To Update Data on Google Sheets
values = queryPlayers(response=queryResponse, site=site, gameVersion=versions[0]) # Change gameVersion or get last one from ddragon
body = {'values' : values}
result = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range="Test!A1",valueInputOption="USER_ENTERED",body=body).execute() # Test!A1 is A1 Google Sheets Notation