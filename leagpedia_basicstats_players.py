from googleapiclient.discovery import build
from google.oauth2 import service_account
from mwrogue.esports_client import EsportsClient
import orjson
import pandas as pd
import numpy as np
import os

"""
Script done to upload data to a Google Sheet from Leaguepedia.
This script gets basic data from a list of players.
"""

# API Google Sheets Connection
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = os.getcwd() + "\\Keys\\llaves.json" # PATH Keys for GoogleSheets API
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
SPREADSHEET_ID = '' #Spreadsheet ID

# GoogleSheet API Request
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# Create EsportsClient using mwrogue
site = EsportsClient('lol')

players = ["Player1",
           "Player2",
           "Player3",
           "Player4",
           "Player5"]
games = []

for player in players:
    # LeaguepediaQuery Example: DnDn
    # https://lol.fandom.com/wiki/Special:CargoQuery?tables=Players%3DP%2C+PlayerRedirects%3DPR%2C&fields=P.OverviewPage%2C+PR.OverviewPage%2C+PR.AllName%2C&where=P.OverviewPage%3D%27DnDn%27&join_on=P.OverviewPage%3DPR.OverviewPage&group_by=&having=&order_by%5B0%5D=&order_by_options%5B0%5D=ASC&limit=500&offset=0&format=
    # We get all usernames from a single player
    response_player_names = site.cargo_client.query(
        limit = "max",
        tables = "Players=P, PlayerRedirects=PR", # Table: https://lol.fandom.com/wiki/Special:CargoTables/PlayerRedirects
        fields = "P.OverviewPage, PR.OverviewPage, PR.AllName",
        where = "P.OverviewPage='"+ player + "'",
        join_on="P.OverviewPage=PR.OverviewPage"
    )
    player_names = orjson.loads(orjson.dumps(response_player_names))
    
    games_list = []
    
    # For every username a player has, we search for all their games
    for pname in player_names:
        # LeaguepediaQuery Example: DnDn Stats for every game
        # https://lol.fandom.com/wiki/Special:CargoQuery?tables=ScoreboardPlayers%3DSP%2C+ScoreboardGames%3DSG%2C&fields=SP.GameId%2C+SP.Link%2C+SG.Patch%2C+SG.Gamelength%2C+SG.Gamelength_Number%3DGamelengthN%2C+SP.PlayerWin%2C+SP.Team%2C+SP.TeamVs%2C+SG.Team1%2C+SG.Team2%2C+SG.Team1Players%2C+SG.Team2Players%2C+SG.Winner%2C+SP.Champion%2C+SP.Kills%2C+SP.Deaths%2C+SP.Assists%2C+SP.Gold%2C+SP.CS%2C+SP.DamageToChampions%2C+SP.TeamKills%2C+SP.TeamGold%2C&where=SP.Link%3D%27DnDn%27+AND+SP.DateTime_UTC>%272022-01-01+1%3A00%3A00+AM%27&join_on=SP.GameId%3DSG.GameId&group_by=&having=&order_by%5B0%5D=SP.DateTime_UTC&order_by_options%5B0%5D=DESC&limit=500&offset=0&format=
        response_list_of_games = site.cargo_client.query(
            limit = 10,
            tables = "ScoreboardPlayers=SP, ScoreboardGames=SG",
            fields = "SP.GameId, SP.Link, SG.Patch, SG.Gamelength, SG.Gamelength_Number=GamelengthN, SP.PlayerWin, SP.Team, SP.TeamVs, SG.Team1, SG.Team2, SG.Team1Players, SG.Team2Players, SG.Winner, SP.Champion, SP.Kills, SP.Deaths, SP.Assists, SP.Gold, SP.CS, SP.DamageToChampions, SP.TeamKills, SP.TeamGold",
            where = "SP.Link='" + pname['AllName'] + "'",
            order_by = "SP.DateTime_UTC DESC",
            join_on="SP.GameId=SG.GameId"
        )
        stat_list = []
        
        for match in response_list_of_games:
            # For every match, we get all the stats of every player. Example:
            # https://lol.fandom.com/wiki/Special:CargoQuery?tables=ScoreboardPlayers%3DSP%2C+ScoreboardGames%3DSG&fields=SP.Champion%2C+SP.Kills%2C+SP.Deaths%2C+SP.Assists%2C+SP.Gold%2C+SP.CS%2C+SP.DamageToChampions%2C+SP.TeamKills%2C+SP.TeamGold%2C+SP.Team%2C+SG.Team1%2C+SP.GameId%2C+SP.Role&where=SP.GameId%3D%27LCK%2F2023+Season%2FSummer+Season_Week+9_6_3%27&join_on=SP.GameId%3DSG.GameId&group_by=&having=&order_by%5B0%5D=SP.DateTime_UTC&order_by_options%5B0%5D=DESC&limit=500&offset=&format=
            response_game_stats = site.cargo_client.query(
                limit = "max",
                tables = "ScoreboardPlayers=SP, ScoreboardGames=SG",
                fields = "SP.Champion, SP.Kills, SP.Deaths, SP.Assists, SP.Gold, SP.CS, SP.DamageToChampions, SP.TeamKills, SP.TeamGold, SP.Team, SG.Team1, SP.GameId, SP.Role",
                where = "SP.GameId='" + match['GameId'] + "'",
                order_by = "SP.DateTime_UTC DESC",
                join_on="SP.GameId=SG.GameId"
                )
            
            # For every player in stats query, we save their stats
            for ply in response_game_stats:
                # We build a dictionary with game data followed by all the stats of the enemies
                if ply['Team'] != match['Team']:
                    # Its an Enemy
                    if ply['Role'] == 'Top':
                        match['ChampionTopVs'] = ply['Champion']
                        match['KillsTopVs'] = ply['Kills']
                        match['DeathsTopVs'] = ply['Deaths']
                        match['AssistsTopVs'] = ply['Assists']
                        match['GoldTopVs'] = ply['Gold']
                        match['CSTopVs'] = ply['CS']
                        match['DMGTopVs'] = ply['DamageToChampions']
                        match['TeamKillsTopVs'] = ply['TeamKills']
                        match['TeamGoldTopVs'] = ply['TeamGold']
                    elif ply['Role'] == 'Jungle':
                        match['ChampionJngVs'] = ply['Champion']
                        match['KillsJngVs'] = ply['Kills']
                        match['DeathsJngVs'] = ply['Deaths']
                        match['AssistsJngVs'] = ply['Assists']
                        match['GoldJngVs'] = ply['Gold']
                        match['CSJngVs'] = ply['CS']
                        match['DMGJngVs'] = ply['DamageToChampions']
                        match['TeamKillsJngVs'] = ply['TeamKills']
                        match['TeamGoldJngVs'] = ply['TeamGold']
                    elif ply['Role'] == 'Mid':
                        match['ChampionMidVs'] = ply['Champion']
                        match['KillsMidVs'] = ply['Kills']
                        match['DeathsMidVs'] = ply['Deaths']
                        match['AssistsMidVs'] = ply['Assists']
                        match['GoldMidVs'] = ply['Gold']
                        match['CSMidVs'] = ply['CS']
                        match['DMGMidVs'] = ply['DamageToChampions']
                        match['TeamKillsMidVs'] = ply['TeamKills']
                        match['TeamGoldMidVs'] = ply['TeamGold']
                    elif ply['Role'] == 'Bot':
                        match['ChampionBotVs'] = ply['Champion']
                        match['KillsBotVs'] = ply['Kills']
                        match['DeathsBotVs'] = ply['Deaths']
                        match['AssistsBotVs'] = ply['Assists']
                        match['GoldBotVs'] = ply['Gold']
                        match['CSBotVs'] = ply['CS']
                        match['DMGBotVs'] = ply['DamageToChampions']
                        match['TeamKillsBotVs'] = ply['TeamKills']
                        match['TeamGoldBotVs'] = ply['TeamGold']
                    elif ply['Role'] == 'Support':
                        match['ChampionSupVs'] = ply['Champion']
                        match['KillsSupVs'] = ply['Kills']
                        match['DeathsSupVs'] = ply['Deaths']
                        match['AssistsSupVs'] = ply['Assists']
                        match['GoldSupVs'] = ply['Gold']
                        match['CSSupVs'] = ply['CS']
                        match['DMGSupVs'] = ply['DamageToChampions']
                        match['TeamKillsSupVs'] = ply['TeamKills']
                        match['TeamGoldSupVs'] = ply['TeamGold']          
                else:
                    if ply['Role'] == 'Jungle':
                        match['DmgAllyJungle'] = ply['DamageToChampions']
                    elif ply['Role'] == 'Mid':
                        match['DmgAllyMid'] = ply['DamageToChampions']
                    elif ply['Role'] == 'Bot':
                        match['DmgAllyBot'] = ply['DamageToChampions']
                    elif ply['Role'] == 'Support':
                        match['DmgAllySupport'] = ply['DamageToChampions']
            
            print("Match Append: " + match['GameId'])
            stat_list.append(match)
        games_list.extend(stat_list)
    games.extend(games_list)

# Creating a Dataframe
df = pd.DataFrame(games)
df = df.astype({
    "GameId": str,
    "Link": str,
    "Patch": str,
    # "GameLength": ,
    "GamelengthN": np.float64,
    "PlayerWin": str,
    "Team": str,
    "TeamVs": str,
    "Team1": str,
    "Team2": str,
    "Team1Players": str,
    "Team2Players": str,
    "Winner": np.int8,
    "Champion": str,
    "Kills": np.int64,
    "Deaths": np.int64,
    "Assists": np.int64,
    "Gold": np.float64,
    "CS": np.int64,
    "DamageToChampions": np.float64,
    "TeamKills": np.int64,
    "TeamGold": np.float64,
    "DmgAllyJungle": np.float64,
    "DmgAllyMid": np.float64,
    "DmgAllyBot": np.float64,
    "DmgAllySupport": np.float64,
    
    "ChampionTopVs": str,
    "KillsTopVs": np.int64,
    "DeathsTopVs": np.int64,
    "AssistsTopVs": np.int64,
    "GoldTopVs": np.float64,
    "CSTopVs": np.int64,
    "DMGTopVs": np.float64,
    "TeamKillsTopVs": np.int64,
    "TeamGoldTopVs": np.float64,
    
    "ChampionJngVs": str,
    "KillsJngVs": np.int64,
    "DeathsJngVs": np.int64,
    "AssistsJngVs": np.int64,
    "GoldJngVs": np.float64,
    "CSJngVs": np.int64,
    "DMGJngVs": np.float64,
    "TeamKillsJngVs": np.int64,
    "TeamGoldJngVs": np.float64,
    
    "ChampionMidVs": str,
    "KillsMidVs": np.int64,
    "DeathsMidVs": np.int64,
    "AssistsMidVs": np.int64,
    "GoldMidVs": np.float64,
    "CSMidVs": np.int64,
    "DMGMidVs": np.float64,
    "TeamKillsMidVs": np.int64,
    "TeamGoldMidVs": np.float64,
    
    "ChampionBotVs": str,
    "KillsBotVs": np.int64,
    "DeathsBotVs": np.int64,
    "AssistsBotVs": np.int64,
    "GoldBotVs": np.float64,
    "CSBotVs": np.int64,
    "DMGBotVs": np.float64,
    "TeamKillsBotVs": np.int64,
    "TeamGoldBotVs": np.float64,
    
    "ChampionSupVs": str,
    "KillsSupVs": np.int64,
    "DeathsSupVs": np.int64,
    "AssistsSupVs": np.int64,
    "GoldSupVs": np.float64,
    "CSSupVs": np.int64,
    "DMGSupVs": np.float64,
    "TeamKillsSupVs": np.int64,
    "TeamGoldSupVs": np.float64
})

df['DPM'] = df['DamageToChampions'] / df['GamelengthN']
df['GPM'] = df['Gold'] / df['GamelengthN']
df['CSPM'] = df['CS'] / df['GamelengthN']
df['DMGEfficiency'] = df['DamageToChampions'] / df['Gold']
df['GShare'] = df['Gold'] / df['TeamGold']
df['KShare'] = df['Kills'] / df['TeamKills']
df['KP%'] = ( df['Kills'] + df['Assists'] ) / df['TeamKills']
df['TotalDamageToChampions'] = df['DamageToChampions'] + df['DmgAllyJungle'] + df['DmgAllyMid'] + df['DmgAllyBot'] + df['DmgAllySupport']
df['DMGShare'] = df['DamageToChampions'] / df['TotalDamageToChampions']
df['CarryGoldPerformance'] = df['Gold'] - (( df['GoldTopVs'] + df['GoldJngVs'] + df['GoldMidVs'] + df['GoldBotVs'] + df['GoldSupVs'] ) / 5 )

df_filled = df.fillna('')
df_filled_values = df_filled.values.tolist()
df_filled_header = df_filled.columns.tolist()
result_df_values = [df_filled_header] + df_filled_values

# Query To Update Data on Google Sheets
body = {'values' : result_df_values}
result = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range="Test!A1",valueInputOption="USER_ENTERED",body=body).execute() # Test!A1 is A1 Google Sheets Notation