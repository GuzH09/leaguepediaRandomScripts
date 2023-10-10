import os
import orjson
from natsort import natsorted
from datetime import datetime
import numpy as np
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap



"""
This script uses data of wards positions from Bayes Esports API to create heatmaps divided by lanes and sides
It can be used for one single game, or a collection of games that needs to be on the same folder

Example of what you can get:

Before using this script, check the code to fill the missing variables:
Paths, teams names/urns, etc.
"""

def read_data_heatmaps():
    path = "" # Put the path where your games are stored
    # path should look something similar to this: https://gyazo.com/1e1fd00e88ad4eb459ce9ede090dbd50
    # where each individual folder look like this: https://gyazo.com/6d8e50acee7b5bf6c5ae3a30711bd88f
    
    # We list all the folders on the path
    directory_list = os.listdir(path)
    # We sort them by date
    directory_list_sorted = natsorted(directory_list,key=lambda g: datetime.strptime(g[0:21],"%Y.%m.%d - %H.%M.%S"),reverse=True)
    
    for folder in directory_list_sorted:
        # We get match id from the folders name
        match_id = folder[24:]
        print("")
        print("Match ID is: " + str(match_id))
        
        # We get the file_dir_name for a single game 
        file_dir_name = f"{path}/{folder}"
        
        # We order JSONs in ASC and DESC order too
        file_list = os.listdir(file_dir_name)
        file_list_sorted_desc = natsorted(file_list,reverse=True) # DESC
        file_list_sorted_asc = natsorted(file_list) # ASC
        
        # We get the wards data and put them in lists for every side and player
        x_coords_blue, y_coords_blue, x_coords_red, y_coords_red,\
        x_blue_top, y_blue_top, x_red_top, y_red_top,\
        x_blue_jng, y_blue_jng, x_red_jng, y_red_jng,\
        x_blue_mid, y_blue_mid, x_red_mid, y_red_mid,\
        x_blue_bot, y_blue_bot, x_red_bot, y_red_bot,\
        x_blue_sup, y_blue_sup, x_red_sup, y_red_sup,\
        x_blue_m03, y_blue_m03, x_red_m03, y_red_m03 = get_wards_graphs(file_list_sorted_asc, file_list_sorted_desc, folder, path)
    
    # get colormap
    ncolors = 256
    aaa = np.linspace(start=0, stop=1, num=256)
    aab = np.linspace(start=0.2, stop=1, num=231)
    k=25
    for item in aab:
        aaa[k]=item
        k+=1
    color_array = plt.get_cmap('jet')(range(ncolors))
    color_array[:,-1] = aaa
    map_object = LinearSegmentedColormap.from_list(name='jet_alpha',colors=color_array)
    plt.register_cmap(cmap=map_object)
    
    # Plot the different graphs
    plot_graphs(x_coords_blue, y_coords_blue, x_coords_red, y_coords_red, "All")
    plot_graphs(x_blue_top, y_blue_top, x_red_top, y_red_top, "top")
    plot_graphs(x_blue_jng, y_blue_jng, x_red_jng, y_red_jng, "jng")
    plot_graphs(x_blue_mid, y_blue_mid, x_red_mid, y_red_mid, "mid")
    plot_graphs(x_blue_bot, y_blue_bot, x_red_bot, y_red_bot, "bot")
    plot_graphs(x_blue_sup, y_blue_sup, x_red_sup, y_red_sup, "sup")
    plot_graphs(x_blue_m03, y_blue_m03, x_red_m03, y_red_m03, "min03")

def get_wards_graphs(file_list_sorted_asc, file_list_sorted_desc, match_id, path_graphs):
    """
    Return two lists with coordinates X and Y about all the wards from a team in a match
    
    """
    # Teams URN's and PLAYERS URN's
    team_top_name = "R7 Bong" # Fill with Team Top Name -> Example R7 Top: R7 Bong
    team_urn = "98767991935149427" # Fill with Team URN -> Example R7 URN: 98767991935149427
    
    # Lists for wards
    x_blue, y_blue, x_red, y_red = [], [], [], []
    x_blue_top, y_blue_top, x_red_top, y_red_top = [], [], [], []
    x_blue_jng, y_blue_jng, x_red_jng, y_red_jng = [], [], [], []
    x_blue_mid, y_blue_mid, x_red_mid, y_red_mid = [], [], [], []
    x_blue_bot, y_blue_bot, x_red_bot, y_red_bot = [], [], [], []
    x_blue_sup, y_blue_sup, x_red_sup, y_red_sup = [], [], [], []
    x_blue_m03, y_blue_m03, x_red_m03, y_red_m03 = [], [], [], []
    
    # Variables
    is_blue = False
    is_red = False
    found = False
    gameTime = 0
    urn = ""
    file_number_wards = 0
    file_number_snap_match_upd = 0
    
    while found == False:
        try:
            # Open a single JSON and get data
            file = file_list_sorted_desc[file_number_snap_match_upd]
            path = f"{path_graphs}/{match_id}/{file}"
            
            with open(path, "rb") as current_file:
                read_data = current_file.read()
                data = orjson.loads(read_data)
                
                # We check the content of the message
                typee = data['payload']['payload']['type']
                subject = data['payload']['payload']['subject']
                action = data['payload']['payload']['action']
                # We get the payload
                payload = data['payload']['payload']['payload']
        except:
            break
        
        # If its a SNAPSHOT - MATCH - UPDATE:
        if typee == "SNAPSHOT":
            if subject == "MATCH":
                if action == "UPDATE":
                    # We get the EsportsTeamId for every team
                    team_urn_blue = str(payload['teamOne']['esportsTeamId'])
                    team_urn_red  = str(payload['teamTwo']['esportsTeamId'])
                    
                    # If team_urn_blue/red is 0 we are using data from a Scrim
                    if team_urn_blue == "0":
                        # So we get the names of the Top Laners to check the team we are looking for
                        top_urn_blue = str(payload['teamOne']['players'][0]['summonerName'])
                        top_urn_red  = str(payload['teamTwo']['players'][0]['summonerName'])
                        
                        # You have to take into account scrims or cases where players have different TAGs for teams
                        # Maybe you should choose Top/Jng/Mid/Bot/Adc manually if you have a lot of Scrims unordered data
                        if top_urn_blue == team_top_name: # or top_urn_blue == every player of the team
                            # Blue Side URN on scrims is team:one
                            urn = "live:lol:riot:team:one"
                            
                            # You can use this to track players manually
                            # for player in payload['teamOne']['players']:
                            #     if player['summonerName'] == "": # Top Summoner Name
                            #         top_urn = str(player['liveDataPlayerUrn'])
                            # for player in payload['teamOne']['players']:
                            #     if player['summonerName'] == "": # Jng Summoner Name
                            #         jng_urn = str(player['liveDataPlayerUrn'])
                            # for player in payload['teamOne']['players']:
                            #     if player['summonerName'] == "": # Mid Summoner Name
                            #         mid_urn = str(player['liveDataPlayerUrn'])
                            # for player in payload['teamOne']['players']:
                            #     if player['summonerName'] == "": # Bot Summoner Name
                            #         bot_urn = str(player['liveDataPlayerUrn'])
                            # for player in payload['teamOne']['players']:
                            #     if player['summonerName'] == "": # Sup Summoner Name
                            #         sup_urn = str(player['liveDataPlayerUrn'])
                            
                            # We can do this but if teams are unordered everything f's up
                            top_urn = str(payload['teamOne']['players'][0]['liveDataPlayerUrn'])
                            jng_urn = str(payload['teamOne']['players'][1]['liveDataPlayerUrn'])
                            mid_urn = str(payload['teamOne']['players'][2]['liveDataPlayerUrn'])
                            bot_urn = str(payload['teamOne']['players'][3]['liveDataPlayerUrn'])
                            sup_urn = str(payload['teamOne']['players'][4]['liveDataPlayerUrn'])
                            
                            found = True
                            is_blue = True
                        # If team_urn is 0 we are using data from a Scrim
                        # You have to take into account scrims or cases where players have different TAGs for teams
                        # Maybe you should choose Top/Jng/Mid/Bot/Adc manually if you have a lot of Scrims unordered data
                        elif top_urn_red == team_top_name: # or top_urn_blue == every player of the team
                            # Red Side URN on scrims is team:one/team:two
                            urn = "live:lol:riot:team:two"
                            
                            # You can use this to track players manually
                            #for player in payload['teamTwo']['players']:
                            #    if player['summonerName'] == "": # Top Summoner Name
                            #        top_urn = str(player['liveDataPlayerUrn'])
                            #for player in payload['teamTwo']['players']:
                            #    if player['summonerName'] == "": # Jng Summoner Name
                            #        jng_urn = str(player['liveDataPlayerUrn'])
                            #for player in payload['teamTwo']['players']:
                            #    if player['summonerName'] == "": # Mid Summoner Name
                            #        mid_urn = str(player['liveDataPlayerUrn'])
                            #for player in payload['teamTwo']['players']:
                            #    if player['summonerName'] == "": # Bot Summoner Name
                            #        bot_urn = str(player['liveDataPlayerUrn'])
                            #for player in payload['teamTwo']['players']:
                            #    if player['summonerName'] == "": # Sup Summoner Name
                            #        sup_urn = str(player['liveDataPlayerUrn'])
                            
                            # We can do this but if teams are unordered everything f's up
                            top_urn = str(payload['teamTwo']['players'][0]['liveDataPlayerUrn'])
                            jng_urn = str(payload['teamTwo']['players'][1]['liveDataPlayerUrn'])
                            mid_urn = str(payload['teamTwo']['players'][2]['liveDataPlayerUrn'])
                            bot_urn = str(payload['teamTwo']['players'][3]['liveDataPlayerUrn'])
                            sup_urn = str(payload['teamTwo']['players'][4]['liveDataPlayerUrn'])
                            
                            found = True
                            is_red = True
                    if team_urn_blue == team_urn:
                        urn = "live:lol:riot:team:" + team_urn_blue
                        
                        # You can use this to track players manually
                        #for player in payload['teamOne']['players']:
                        #    if player['summonerName'] == "": # Top Summoner Name
                        #        top_urn = str(player['liveDataPlayerUrn'])
                        #for player in payload['teamOne']['players']:
                        #    if player['summonerName'] == "": # Jng Summoner Name
                        #        jng_urn = str(player['liveDataPlayerUrn'])
                        #for player in payload['teamOne']['players']:
                        #    if player['summonerName'] == "": # Mid Summoner Name
                        #        mid_urn = str(player['liveDataPlayerUrn'])
                        #for player in payload['teamOne']['players']:
                        #    if player['summonerName'] == "": # Bot Summoner Name
                        #        bot_urn = str(player['liveDataPlayerUrn'])
                        #for player in payload['teamOne']['players']:
                        #    if player['summonerName'] == "": # Sup Summoner Name
                        #        sup_urn = str(player['liveDataPlayerUrn'])
                        
                        # We can do this but if teams are unordered everything f's up
                        top_urn = str(payload['teamOne']['players'][0]['liveDataPlayerUrn'])
                        jng_urn = str(payload['teamOne']['players'][1]['liveDataPlayerUrn'])
                        mid_urn = str(payload['teamOne']['players'][2]['liveDataPlayerUrn'])
                        bot_urn = str(payload['teamOne']['players'][3]['liveDataPlayerUrn'])
                        sup_urn = str(payload['teamOne']['players'][4]['liveDataPlayerUrn'])
                        
                        found = True
                        is_blue = True
                    elif team_urn_red == team_urn:
                        urn = "live:lol:riot:team:" + team_urn_red
                        
                        # You can use this to track players manually
                        for player in payload['teamTwo']['players']:
                            if player['summonerName'] == "": # Top Summoner Name
                                top_urn = str(player['liveDataPlayerUrn'])
                        for player in payload['teamTwo']['players']:
                            if player['summonerName'] == "": # Jng Summoner Name
                                jng_urn = str(player['liveDataPlayerUrn'])
                        for player in payload['teamTwo']['players']:
                            if player['summonerName'] == "": # Mid Summoner Name
                                mid_urn = str(player['liveDataPlayerUrn'])
                        for player in payload['teamTwo']['players']:
                            if player['summonerName'] == "": # Bot Summoner Name
                                bot_urn = str(player['liveDataPlayerUrn'])
                        for player in payload['teamTwo']['players']:
                            if player['summonerName'] == "": # Sup Summoner Name
                                sup_urn = str(player['liveDataPlayerUrn'])
                        
                        # We can do this but if teams are unordered everything f's up
                        top_urn = str(payload['teamTwo']['players'][0]['liveDataPlayerUrn'])
                        jng_urn = str(payload['teamTwo']['players'][1]['liveDataPlayerUrn'])
                        mid_urn = str(payload['teamTwo']['players'][2]['liveDataPlayerUrn'])
                        bot_urn = str(payload['teamTwo']['players'][3]['liveDataPlayerUrn'])
                        sup_urn = str(payload['teamTwo']['players'][4]['liveDataPlayerUrn'])
                        
                        found = True
                        is_red = True
                    print(urn)
                    print("-------------------------")
                    
                    if found == False:
                        print("We didn't found the team.")
        file_number_snap_match_upd += 1
    
    print("TOP: " + top_urn)
    print("JNG: " + jng_urn)
    print("MID: " + mid_urn)
    print("BOT: " + bot_urn)
    print("SUP: " + sup_urn)
    print("-------------------------")
    
    while gameTime < 960:
        try:
            # Open file and get data
            file = file_list_sorted_asc[file_number_wards]
            path = f"{path_graphs}/{match_id}/{file}"
            
            with open(path, "rb") as current_file:
                read_data = current_file.read()
                data = orjson.loads(read_data)
                
                # We check the content of the message
                typee = data['payload']['payload']['type']
                subject = data['payload']['payload']['subject']
                action = data['payload']['payload']['action']
                # We get the payload
                payload = data['payload']['payload']['payload']
        except:
            break
        
        # If its GAME_EVENT - PLAYER - PLACED_WARD
        if typee == "GAME_EVENT":
                if subject == "PLAYER":
                    if action == "PLACED_WARD":
                        # We check if the gametime is less than 15mins
                        gameTime = payload['gameTime'] / 1000
                        
                        if gameTime<960:
                            placerTeamUrn = payload['placerTeamUrn']
                            
                            if placerTeamUrn == urn: # We check if the placerTeamUrn is the same as the team we are looking for
                                if payload['wardType'] != 'unknown':
                                    # unknown WardTypes could be anything really
                                    if gameTime<180:
                                        # We get wards before 3 minutes
                                        if is_blue:
                                            position_x_m03 = payload['position'][0]
                                            position_y_m03 = payload['position'][1]
                                            
                                            x_blue_m03.append(position_x_m03)
                                            y_blue_m03.append(position_y_m03)
                                        elif is_red:
                                            position_x_m03 = payload['position'][0]
                                            position_y_m03 = payload['position'][1]
                                            
                                            x_red_m03.append(position_x_m03)
                                            y_red_m03.append(position_y_m03)
                                    # We get wards coordinates for the heatmap that includes every player
                                    if is_blue:
                                        position_x = payload['position'][0]
                                        position_y = payload['position'][1]
                                        
                                        x_blue.append(position_x)
                                        y_blue.append(position_y)
                                    elif is_red:
                                        
                                        position_x = payload['position'][0]
                                        position_y = payload['position'][1]
                                        
                                        x_red.append(position_x)
                                        y_red.append(position_y)
                                    # We get wards coordinates for the heatmap that includes only the top laner
                                    if payload['placerUrn'] == top_urn:
                                        if is_blue:
                                            position_x_top = payload['position'][0]
                                            position_y_top = payload['position'][1]
                                            
                                            x_blue_top.append(position_x_top)
                                            y_blue_top.append(position_y_top)
                                        elif is_red:
                                            position_x_top = payload['position'][0]
                                            position_y_top = payload['position'][1]
                                            
                                            x_red_top.append(position_x_top)
                                            y_red_top.append(position_y_top)
                                    # We get wards coordinates for the heatmap that includes only the jungler
                                    elif payload['placerUrn'] == jng_urn:
                                        if is_blue:
                                            position_x_jng = payload['position'][0]
                                            position_y_jng = payload['position'][1]
                                            
                                            x_blue_jng.append(position_x_jng)
                                            y_blue_jng.append(position_y_jng)
                                        elif is_red:
                                            position_x_jng = payload['position'][0]
                                            position_y_jng = payload['position'][1]
                                            
                                            x_red_jng.append(position_x_jng)
                                            y_red_jng.append(position_y_jng)
                                    # We get wards coordinates for the heatmap that includes only the mid laner
                                    elif payload['placerUrn'] == mid_urn:
                                        if is_blue:
                                            position_x_mid = payload['position'][0]
                                            position_y_mid = payload['position'][1]
                                            
                                            x_blue_mid.append(position_x_mid)
                                            y_blue_mid.append(position_y_mid)
                                        elif is_red:
                                            
                                            position_x_mid = payload['position'][0]
                                            position_y_mid = payload['position'][1]
                                            
                                            x_red_mid.append(position_x_mid)
                                            y_red_mid.append(position_y_mid)
                                    # We get wards coordinates for the heatmap that includes only the bot laner
                                    elif payload['placerUrn'] == bot_urn:
                                        if is_blue:
                                            position_x_bot = payload['position'][0]
                                            position_y_bot = payload['position'][1]
                                            
                                            x_blue_bot.append(position_x_bot)
                                            y_blue_bot.append(position_y_bot)
                                        elif is_red:
                                            position_x_bot = payload['position'][0]
                                            position_y_bot = payload['position'][1]
                                            
                                            x_red_bot.append(position_x_bot)
                                            y_red_bot.append(position_y_bot)
                                    # We get wards coordinates for the heatmap that includes only the support
                                    elif payload['placerUrn'] == sup_urn:
                                        if is_blue:
                                            position_x_sup = payload['position'][0]
                                            position_y_sup = payload['position'][1]
                                            
                                            x_blue_sup.append(position_x_sup)
                                            y_blue_sup.append(position_y_sup)
                                        elif is_red:
                                            position_x_sup = payload['position'][0]
                                            position_y_sup = payload['position'][1]
                                            
                                            x_red_sup.append(position_x_sup)
                                            y_red_sup.append(position_y_sup)
        file_number_wards += 1
    return x_blue, y_blue, x_red, y_red, \
        x_blue_top, y_blue_top, x_red_top, y_red_top, \
        x_blue_jng, y_blue_jng, x_red_jng, y_red_jng, \
        x_blue_mid, y_blue_mid, x_red_mid, y_red_mid, \
        x_blue_bot, y_blue_bot, x_red_bot, y_red_bot, \
        x_blue_sup, y_blue_sup, x_red_sup, y_red_sup, \
        x_blue_m03, y_blue_m03, x_red_m03, y_red_m03

def myplot(x, y, s):
    heatmap, xedges, yedges = np.histogram2d(x, y,bins=1000, range=[[-120, 14870], [-120, 14870]])
    heatmap = gaussian_filter(heatmap, sigma=s)

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    return heatmap.T, extent

def plot_graphs(xb,yb,xr,yr,lane):
    
    # Graph 1 - Blue Side Heatmap
    img, extent = myplot(xb,yb,16)
    img2 = plt.imread(os.getcwd() + "\\Bayes Esports\\map.png") # Summoners Rift Map
    plt.imshow(img2,extent=[-120,14870,-120,14870])
    plt.imshow(img, extent=extent, origin='lower', cmap= "jet_alpha")
    plt.xticks([])
    plt.yticks([])
    plt.savefig(os.getcwd() + f'\\Bayes Esports\\Heatmaps\\Blue Side\\{lane}_blue_heatmap.png') # Path to save the pictures
    plt.close()
    
    # Grafico 1.1 - Blue Side Scatter Map
    plt.imshow(img2,extent=[-120,14870,-120,14870])
    plt.set_cmap("binary")
    plt.scatter(xb, yb, color="DarkGreen")
    plt.ylim(-120,14870)
    plt.xlim(-120,14870)
    plt.xticks([])
    plt.yticks([])
    plt.savefig(os.getcwd() + f'\\Bayes Esports\\Scatter Plots\\Blue Side\\{lane}_blue_scatter.png') # Path to save the pictures
    plt.close()
    
    # Gráfico 1.2 - Red Side Heatmap
    img, extent = myplot(xr,yr,16)
    img2 = plt.imread(os.getcwd() + "\\Bayes Esports\\map.png") # Summoners Rift Map
    plt.imshow(img2,extent=[-120,14870,-120,14870])
    plt.imshow(img, extent=extent, origin='lower', cmap= "jet_alpha")
    plt.xticks([])
    plt.yticks([])
    plt.savefig(os.getcwd() + f'\\Bayes Esports\\Heatmaps\\Red Side\\{lane}_red_heatmap.png') # Path to save the pictures
    plt.close()
    
    # Gráfico 1.3 - Red Side Scatter Map
    plt.imshow(img2,extent=[-120,14870,-120,14870])
    plt.set_cmap("binary")
    plt.scatter(xr, yr, color="DarkGreen")
    plt.ylim(-120,14870)
    plt.xlim(-120,14870)
    plt.xticks([])
    plt.yticks([])
    plt.savefig(os.getcwd() + f'\\Bayes Esports\\Scatter Plots\\Red Side\\{lane}_red_scatter.png') # Path to save the pictures
    plt.close()