import orjson
import requests
import orjson

def transmute_league(name):
    # Change selected leagues names for whatever you want
    leagues_names = {    
        "MSI 2023": "MSI 2023",
        
        "LPL 2023 Summer": "LPL",
        "LPL 2023 Summer Playoffs": "LPL",
        
        "LCK 2023 Summer": "LCK",
        "LCK 2023 Summer Playoffs": "LCK",
        
        "LEC 2023 Winter Season": "LEC",
        "LEC 2023 Winter Groups": "LEC",
        "LEC 2023 Winter Playoffs": "LEC",
        
        "LEC 2023 Summer Season": "LEC",
        "LEC 2023 Summer Groups": "LEC",
        "LEC 2023 Summer Playoffs": "LEC",
        
        "LCS 2023 Summer": "LCS",
        "LCS 2023 Summer Playoffs": "LCS",
        
        "LLA 2023 Closing": "LLA",
        "LLA 2023 Closing Playoffs": "LLA",
        
        "VCS 2023 Summer": "VCS",
        "VCS 2023 Summer Playoffs": "VCS",
        
        "TCL 2023 Summer": "TCL",
        "TCL 2023 Summer Playoffs": "TCL",
        
        "PCS 2023 Summer": "PCS",
        "PCS 2023 Summer Playoffs": "PCS",
        
        "CBLOL 2023 Split 2": "CBLOL",
        "CBLOL 2023 Split 2 Playoffs": "CBLOL",
        
        "LCO 2023 Split 2": "LCO",
        "LCO 2023 Split 2 Playoffs": "LCO",
        
        "LJL 2023 Summer": "LJL",
        "LJL 2023 Summer Playoffs": "LJL",
        
        "LCK CL 2023 Summer": "LCK CL",
        "LCK CL 2023 Summer Playoffs": "LCK CL",
        
        "LVP SL 2023 Summer": "SLO",
        "LVP SL 2023 Summer Playoffs": "SLO",
        
        "LRS 2023 Closing": "LRS",
        "LRS 2023 Closing Playoffs": "LRS",
        
        "LRN 2023 Closing": "LRN",
        "LRN 2023 Closing Playoffs": "LRN"
    }
    
    if leagues_names.get(name)==None:
        return "-"
    else:
        return leagues_names.get(name)

def transmute_win(winner: int):
    if winner==1:
        return "Blue"
    else:
        return "Red"

def get_blinds_and_contest_picks_list(orderpick: list, blue_picks_list: list, red_picks_list: list):
    """
    This function returns a List that represents a draft in order, but showing the tags "Blind" and "Contest" instead of the names of the champions
    
    "orderpick" is a list that represents a draft in order, but only using picks (not bans)
    Structure:
    orderpick[0] = B1: 
    orderpick[1] = R1: 
    orderpick[2] = R2:
    orderpick[3] = B2:
    orderpick[4] = B3:
    orderpick[5] = R3:
    orderpick[6] = R4:
    orderpick[7] = B4:
    orderpick[8] = B5:
    orderpick[9] = R5:
    
    "blue_picks_list" is a list that has blue champions from top to support
    "red_picks_list" is a list that has red champions from top to support
    
    Logic:
    For every element on the list:
    A pick is blindpick:
        if: The element is the first on the list. BlindPick -> Pick == orderpick[0]
        else:
            Pick it's blindpick if the champion with the same role on the opposite team (Their counterpart) picked after it.
            Example: Pick = orderpick[2], and their counterpart doesn't appear on orderpick[0], orderpick[1]
        else:
            Pick its a contest.
            
    """

    blinds_and_contest_list= []

    # For every element on orderpick list
    for x in orderpick:
        # If its the first element, it is a Blind Pick
        if x == orderpick[0]:
            blinds_and_contest_list.append("BlindPick")
        else:
            # If its not the first element, it is a Blind Pick if
            # the pick on the same role but different team is picked after.
            # So, we check all the red team for their Counterpart
            for pick in red_picks_list:
                try:
                    # If its their counterpart
                    if isCounterpart(pick, x, blue_picks_list, red_picks_list):
                        # And it has lower index than the other pick
                        if orderpick.index(pick) > orderpick.index(x):
                            # Then its a blind pick
                            blinds_and_contest_list.append("BlindPick")
                        else:
                            # Or a Contest, if it has higher index
                            blinds_and_contest_list.append("Contest")
                    else:
                        pass
                except:
                    # If it has an error append ("-")
                    blinds_and_contest_list.append("-")
            
            # If its not the first element, it is a Blind Pick if
            # the pick on the same role but different team is picked after.
            # So, we check all the blue team too for their counterpart
            for pick in blue_picks_list:
                if isCounterpart(pick, x, blue_picks_list, red_picks_list):
                    if orderpick.index(pick) > orderpick.index(x):
                        blinds_and_contest_list.append("BlindPick")
                    else:
                        blinds_and_contest_list.append("Contest")
                else:
                    pass
                
    return blinds_and_contest_list

def isCounterpart(pick_2, pick_1, blue_picks_list, red_picks_list):
    """
    Checks wether a champion is Counterpart (Same role, different team) of another
    "pick_2" is pick2
    "pick_1" is pick1
    """
    
    if pick_1 in blue_picks_list:
        if pick_2 in blue_picks_list:
            # If they are on the same team(Blue) -> False
            return False
        else:
            # If the index of PICK1 is equal to the index of PICK2 -> They are counterparts
            if blue_picks_list.index(pick_1) == red_picks_list.index(pick_2):
                return True
            else:
                return False
    else:
        if pick_1 in red_picks_list:
            if pick_2 in red_picks_list:
                # If they are on the same team(Red) -> False
                return False
            else:
                # If the index of PICK1 is equal to the index of PICK2 -> They are counterparts
                if red_picks_list.index(pick_1) == blue_picks_list.index(pick_2):
                    return True
                else:
                    return False
        else:
            pass

def transmute_blinds_and_contest_per_role_list(blue_champions, red_champions, orderpick, blinds_and_contest_list):
    """
    This function uses the list provided by "get_blinds_and_contest_picks_list()"
    To transform a list with this structure:
    ['BlindPick',   <- B1 
    'BlindPick',    <-  R1
    'BlindPick',    <-  R2
    'BlindPick',    <- B2
    'Contest',      <- B3
    'Contest',      <-  R3
    'BlindPick',    <-  R4
    'Contest',      <- B4
    'Contest',      <- B5
    'Contest']      <-  R5
    Into this structure:
    ['Contest',     <- Blue Top
    'BlindPick',    <- Blue Jungle
    'Contest',      <- Blue Mid
    'BlindPick',    <- Blue Bot
    'Contest',      <- Blue Support
    'BlindPick',    <- Red Top
    'Contest',      <- Red Jungle
    'BlindPick',    <- Red Mid
    'Contest',      <- Red Bot
    'BlindPick']    <- Red Support
    
    """
    # Returns a List of 10 champions picked in a draft ordered from top to support
    # But using the 
    
    # Creates a new List
    new_list=[]
    # For every champion in Blue Champions List
    for x in blue_champions:
        # If the champion is in the orderpick
        if x in orderpick:
            # We append the "BlindPick" or "Contest" tag that matches the same index for that pick in particular 
            new_list.append(blinds_and_contest_list[orderpick.index(x)])
        else:
            new_list.append("-")
    # For every champion in Red Champions List        
    for x in red_champions:
        # If the champion is in the orderpick
        if x in orderpick:
            # We append the "BlindPick" or "Contest" tag that matches the same index for that pick in particular
            new_list.append(blinds_and_contest_list[orderpick.index(x)])
        else:
            new_list.append("-")
    return new_list

def transmute_name_champion(champion_name, champions_json):
    '''
    Transmutes Champions Names to Champions Name "Well" written
    Example: Tahm Kench -> TahmKench / Cho'Gath -> Chogath
    
    Use "check_last_version()" first to get the gameVersion
    then use "check_champions()" to get the champions Json from DDragon
    lastly use "transmute_name_champion" to get the Champions Names
    '''
    
    champion_name_transmuted = ''
    for champion_obj, champion_data in champions_json['data'].items():
        if champion_data['name'] == str(champion_name):
            champion_name_transmuted = champion_data['id']
    return champion_name_transmuted

def transmute_id_champion(champion_id, champions_json):
    '''
    Transmutes Champions IDs to Champions Names
    Example: 266 -> Aatrox
    
    Use "check_last_version()" first to get the gameVersion
    then use "check_champions()" to get the champions Json from DDragon
    lastly use "transmute_id_champion" to get the Champions Names
    '''
    
    champion_name_transmuted = ''
    for champion_obj, champion_data in champions_json['data'].items():
        if champion_data['key'] == str(champion_id):
            champion_name_transmuted = champion_data['id']
    return champion_name_transmuted

def get_champions(side, payload, champions_json):
    champions = []
    if side == "Blue":
        for player in payload['teamOne']['players']:
            champion_name = transmute_id_champion(player['championID'], champions_json)
            champions.append(champion_name)
            
        for player in payload['teamTwo']['players']:
            champion_name = transmute_id_champion(player['championID'], champions_json)
            champions.append(champion_name)
    else:
        for player in payload['teamTwo']['players']:
            champion_name = transmute_id_champion(player['championID'], champions_json)
            champions.append(champion_name)
            
        for player in payload['teamOne']['players']:
            champion_name = transmute_id_champion(player['championID'], champions_json)
            champions.append(champion_name)
    return champions

def check_last_version() -> str:
    '''Checks last patch of ddragon.'''
    response = requests.get('https://ddragon.leagueoflegends.com/api/versions.json')
    if response.status_code != 200:
        response.raise_for_status()
    gameVersion = response.json()[0]
    return gameVersion

def check_champions(gameVersion):
    '''    
    Use "check_last_version()" first to get the gameVersion
    then use "check_champions()" to get the champions Json from DDragon
    '''
    
    response = requests.get(f'http://ddragon.leagueoflegends.com/cdn/{gameVersion}/data/en_US/champion.json')
    
    if response.status_code != 200:
        response.raise_for_status()
    
    file = orjson.loads(response.content)
    
    return file