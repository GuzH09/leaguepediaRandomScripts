import time
import orjson
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
from mwrogue.esports_client import EsportsClient
from functions import transmute_league, transmute_win, transmute_name_champion, get_blinds_and_contest_picks_list, transmute_blinds_and_contest_per_role_list, check_last_version, check_champions

"""
This scripts uploads data of all the drafts played at all the leagues in the worlds (by choice) to a Spreadsheet

You can use this data and Looker Studio to do something like this: https://lookerstudio.google.com/reporting/810270ea-a97a-46ae-826c-a9285378f7be
"""

def queryDraftChampions(response, site):
    """
    Function to get Draft Info from matches
    """

    gameVersion = check_last_version() # We get last version of Ddragon to get updated champions
    champions_json = check_champions(gameVersion)
    sheet = []
    games = orjson.loads(orjson.dumps(response))
    matchNumber=1
    
    sheetHeader=["Tab", "Date", "Tournament", "Patch", "Winner", "Blue", "Red", "VOD",\
                "Blue_Role_1", "Blue_Role_2", "Blue_Role_3", "Blue_Role_4", "Blue_Role_5",\
                "Red_Role_1", "Red_Role_2", "Red_Role_3", "Red_Role_4", "Red_Role_5",\
                "Blue_Ban_1","Red_Ban_1","Blue_Ban_2","Red_Ban_2","Blue_Ban_3","Red_Ban_3",\
                "Blue_Pick_1","Red_Pick_1","Red_Pick_2","Blue_Pick_2","Blue_Pick_3","Red_Pick_3",\
                "Red_Ban_4","Blue_Ban_4","Red_Ban_5","Blue_Ban_5",\
                "Red_Pick_4","Blue_Pick_4","Blue_Pick_5","Red_Pick_5",\
                "Blue_Pick_Top","Blue_Pick_Jng","Blue_Pick_Mid","Blue_Pick_Bot","Blue_Pick_Sup",\
                "Red_Pick_Top","Red_Pick_Jng","Red_Pick_Mid","Red_Pick_Bot","Red_Pick_Sup",\
                "Blue_bc_Top","Blue_bc_Jng","Blue_bc_Mid","Blue_bc_Bot","Blue_bc_Sup",\
                "Red_bc_Top","Red_bc_Jng","Red_bc_Mid","Red_bc_bot","Red_bc_Sup"]
    
    sheet.append(sheetHeader)

    # For every game of the query
    for game in games:
        
        sheetRow = []
        dataGeneral = [
            game['Tab'],
            game['DateTime UTC'],
            transmute_league(game['Tournament']),
            game['Patch'],
            transmute_win(int(game['Winner'])),
            site.cache.get("Team",game['Team1'],"short"),
            site.cache.get("Team",game['Team2'],"short"),
            game['VOD']
            ]
        sheetRow.extend(dataGeneral)
        print(sheetRow)
        
        roles = [
            game['Team1Role1'],
            game['Team1Role2'],
            game['Team1Role3'],
            game['Team1Role4'],
            game['Team1Role5'],
            game['Team2Role1'],
            game['Team2Role2'],
            game['Team2Role3'],
            game['Team2Role4'],
            game['Team2Role5']
        ]
        
        # We solve empty Role data
        counter = 0
        for role in roles:
            if role == None:
                counter += 1
            else:
                pass
        
        if counter == 10:
            roles_empty = ["-","-","-","-","-","-","-","-","-","-"]
            sheetRow.extend(roles_empty)
        else:
            sheetRow.extend(roles)
        
        # We get all the draft
        draft = [
            transmute_name_champion(game['Team1Ban1'], champions_json) if game['Team1Ban1']!="" and game['Team1Ban1']!="None" else "-",
            transmute_name_champion(game['Team2Ban1'], champions_json) if game['Team2Ban1']!="" and game['Team2Ban1']!="None" else "-",
            transmute_name_champion(game['Team1Ban2'], champions_json) if game['Team1Ban2']!="" and game['Team1Ban2']!="None" else "-",
            transmute_name_champion(game['Team2Ban2'], champions_json) if game['Team2Ban2']!="" and game['Team2Ban2']!="None" else "-",
            transmute_name_champion(game['Team1Ban3'], champions_json) if game['Team1Ban3']!="" and game['Team1Ban3']!="None" else "-",
            transmute_name_champion(game['Team2Ban3'], champions_json) if game['Team2Ban3']!="" and game['Team2Ban3']!="None" else "-",
            transmute_name_champion(game['Team1Pick1'], champions_json),
            transmute_name_champion(game['Team2Pick1'], champions_json),
            transmute_name_champion(game['Team2Pick2'], champions_json),
            transmute_name_champion(game['Team1Pick2'], champions_json),
            transmute_name_champion(game['Team1Pick3'], champions_json),
            transmute_name_champion(game['Team2Pick3'], champions_json),
            transmute_name_champion(game['Team2Ban4'], champions_json) if game['Team2Ban4']!="" and game['Team2Ban4']!="None" else "-",
            transmute_name_champion(game['Team1Ban4'], champions_json) if game['Team1Ban4']!="" and game['Team1Ban4']!="None" else "-",
            transmute_name_champion(game['Team2Ban5'], champions_json) if game['Team2Ban5']!="" and game['Team2Ban5']!="None" else "-",
            transmute_name_champion(game['Team1Ban5'], champions_json) if game['Team1Ban5']!="" and game['Team1Ban5']!="None" else "-",
            transmute_name_champion(game['Team2Pick4'], champions_json),
            transmute_name_champion(game['Team1Pick4'], champions_json),
            transmute_name_champion(game['Team1Pick5'], champions_json),
            transmute_name_champion(game['Team2Pick5'], champions_json),
        ]
        sheetRow.extend(draft)        
        
        # We get only the compositions
        championsblue = game['Team1Picks'].split(",")
        for x in championsblue:
            sheetRow.append(transmute_name_champion(x, champions_json))
        
        championsred = game['Team2Picks'].split(",")
        for j in championsred:
            sheetRow.append(transmute_name_champion(j, champions_json))
        picksblue = sheetRow[38:43]
        picksred = sheetRow[43:48]
        orderpick = [draft[6], draft[7], draft[8], draft[9], draft[10], draft[11], draft[16], draft[17], draft[18], draft[19]]
        
        blindsycontest = get_blinds_and_contest_picks_list(orderpick, picksblue, picksred)
        blindycounters_fin = transmute_blinds_and_contest_per_role_list(picksblue, picksred, orderpick, blindsycontest)
        sheetRow.extend(blindycounters_fin)
        
        print("Row number: " + str(matchNumber) + " added to the list.")
        
        matchNumber+=1
        
        # We append the Row to the full sheet
        sheet.append(sheetRow)  
    return sheet

# API Google Sheets Connection
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = os.getcwd() + "\\Keys\\llaves.json" # PATH Keys for GoogleSheets API
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
SPREADSHEET_ID = '' #Spreadsheet ID

# GoogleSheet API Request
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# Leaguepedia EsportsClient
site= EsportsClient('lol')

# Variables
queryFull=False
queryResponse=[]

# Doesn't stop until we have all matches played
while queryFull==False:
    queryOffset=len(queryResponse)
    print("Query Offset: " + str(queryOffset))

    # Leaguepedia Query
    responseChampionsTournament = site.cargo_client.query(
        limit = "max", #All Games (Leaguepedia max is 500)
        offset = queryOffset, #Offset to get games in chunks of 500
        tables = "PicksAndBansS7=PB, ScoreboardGames=SG,",
        fields = "PB.Tab, SG.DateTime_UTC, SG.OverviewPage, SG.Tournament, SG.Patch, PB.Winner, PB.Team1, PB.Team2, SG.VOD, " +
                    "PB.Team1Role1, PB.Team1Role2, PB.Team1Role3, PB.Team1Role4, PB.Team1Role5, " +
                    "PB.Team2Role1, PB.Team2Role2, PB.Team2Role3, PB.Team2Role4, PB.Team2Role5, " +
                    "PB.Team1Ban1, PB.Team2Ban1, PB.Team1Ban2, PB.Team2Ban2, PB.Team1Ban3, PB.Team2Ban3, " +
                    "PB.Team1Pick1, PB.Team2Pick1, PB.Team2Pick2, PB.Team1Pick2, PB.Team1Pick3, PB.Team2Pick3, " +
                    "PB.Team2Ban4, PB.Team1Ban4, PB.Team2Ban5, PB.Team1Ban5, " +
                    "PB.Team2Pick4, PB.Team1Pick4, PB.Team1Pick5, PB.Team2Pick5, SG.Team1Picks, SG.Team2Picks",
        # All leagues listed here
        where = "( " +
                "SG.OverviewPage='2023 Mid-Season Invitational' OR " +
                "SG.OverviewPage='LPL/2023 Season/Summer Season' OR " +
                "SG.OverviewPage='LPL/2023 Season/Summer Playoffs' OR " +
                "SG.OverviewPage='LCK/2023 Season/Summer Season' OR " +
                "SG.OverviewPage='LCK/2023 Season/Summer Playoffs' OR " +
                "SG.OverviewPage='LCS/2023 Season/Summer Season' OR " +
                "SG.OverviewPage='LCS/2023 Season/Summer Playoffs' OR " +
                "SG.OverviewPage='LLA/2023 Season/Closing Season' OR " +
                "SG.OverviewPage='LLA/2023 Season/Closing Playoffs' OR " +
                "SG.OverviewPage='VCS/2023 Season/Summer Season' OR " +
                "SG.OverviewPage='VCS/2023 Season/Summer Playoffs' OR " +
                "SG.OverviewPage='TCL/2023 Season/Summer Season' OR " +
                "SG.OverviewPage='TCL/2023 Season/Summer Playoffs' OR " +
                "SG.OverviewPage='PCS/2023 Season/Summer Season' OR " +
                "SG.OverviewPage='PCS/2023 Season/Summer Playoffs' OR " +
                "SG.OverviewPage='CBLOL/2023 Season/Split 2' OR " +
                "SG.OverviewPage='CBLOL/2023 Season/Split 2 Playoffs' OR " +
                "SG.OverviewPage='LCO/2023 Season/Split 2' OR " +
                "SG.OverviewPage='LCO/2023 Season/Split 2 Playoffs' OR " +
                "SG.OverviewPage='LJL/2023 Season/Summer Season' OR " +
                "SG.OverviewPage='LJL/2023 Season/Summer Playoffs' OR " +
                "SG.OverviewPage='LCK CL/2023 Season/Summer Season' OR " +
                "SG.OverviewPage='LCK CL/2023 Season/Summer Playoffs' OR " +
                "SG.OverviewPage='LVP SuperLiga/2023 Season/Summer Season' OR " +
                "SG.OverviewPage='LVP SuperLiga/2023 Season/Summer Playoffs' OR " +
                "SG.OverviewPage='Liga Regional Norte/2023 Season/Closing Season' OR " +
                "SG.OverviewPage='Liga Regional Norte/2023 Season/Closing Playoffs' OR " +
                "SG.OverviewPage='Liga Regional Sur/2023 Season/Closing Season' OR " +
                "SG.OverviewPage='Liga Regional Sur/2023 Season/Closing Playoffs'" +                
                ") " +
                "AND SG.Winner IS NOT NULL AND PB.Winner IS NOT NULL",
        join_on = "PB.GameId=SG.GameId",
        order_by = "SG.DateTime_UTC DESC", # Ordered by new to oldest
    )

    if len(responseChampionsTournament)>0:
        queryResponse.extend(responseChampionsTournament)
    else:
        queryFull=True        
    time.sleep(0.1) # As a loop, I wait for API Limit

# Update the Google WorkSheet
values = queryDraftChampions(response=queryResponse, site=site)
body = {'values' : values}
result = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range="Test!A1",valueInputOption="USER_ENTERED",body=body).execute()