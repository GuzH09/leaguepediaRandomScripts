import sys
import os
import orjson
from natsort import natsorted
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as ani
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from functions import check_last_version, check_champions, get_champions


"""
This script uses data of players positions from Bayes Esports API to create animations that show the jungle pathing in the early game

Example of what you can get: 

Before using this script, check the code to fill the missing variables:
Paths, teams names/urns, etc.
"""


def read_data_pathing():
    path = "" # Put the path where your games are stored
    # path should look something similar to this: https://gyazo.com/1e1fd00e88ad4eb459ce9ede090dbd50
    # where each individual folder look like this: https://gyazo.com/6d8e50acee7b5bf6c5ae3a30711bd88f
    # We list all the folders on the path
    directory_list = os.listdir(path)
    # We sort them by date
    directory_list_sorted = natsorted(directory_list,key=lambda g: datetime.strptime(g[0:21],"%Y.%m.%d - %H.%M.%S"),reverse=True)
    gameVersion = check_last_version()
    champions_json = check_champions(gameVersion)
    
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
        x_y_coords_pos, bt, bj, bm, bb, bs, rt, rj, rm, rb, rs, cham = get_position_graphs(file_list_sorted_asc, file_list_sorted_desc, folder, path, champions_json)
        
        df = pd.DataFrame(x_y_coords_pos, columns=['X','Y'])
        
        df_top_b = pd.DataFrame(bt, columns=['X','Y'])
        df_jng_b = pd.DataFrame(bj, columns=['X','Y'])
        df_mid_b = pd.DataFrame(bm, columns=['X','Y'])
        df_bot_b = pd.DataFrame(bb, columns=['X','Y'])
        df_sup_b = pd.DataFrame(bs, columns=['X','Y'])
        
        df_top_r = pd.DataFrame(rt, columns=['X','Y'])
        df_jng_r = pd.DataFrame(rj, columns=['X','Y'])
        df_mid_r = pd.DataFrame(rm, columns=['X','Y'])
        df_bot_r = pd.DataFrame(rb, columns=['X','Y'])
        df_sup_r = pd.DataFrame(rs, columns=['X','Y'])
        
        # Using Pyplot module
        # Graph
        photos = []
        for x in cham:
            # Circle portraits downloaded from: https://raw.communitydragon.org/latest/game/assets/characters/
            photos.append(os.getcwd() + "\\Bayes Esports\\Circles\\" + str(x) + ".png") #    "C:/Python Scripts/Infinity/Python Files/Circles/" + str(x) + ".png")

        fig,ax = plt.subplots()
        
        for x in range(len(photos)):
            photos[x] = plt.imread(photos[x])
        
        im_top_b = OffsetImage(photos[0], zoom=0.18)
        im_jng_b = OffsetImage(photos[1], zoom=0.18)
        im_mid_b = OffsetImage(photos[2], zoom=0.18)
        im_bot_b = OffsetImage(photos[3], zoom=0.18)
        im_sup_b = OffsetImage(photos[4], zoom=0.18)
        
        im_top_r = OffsetImage(photos[5], zoom=0.18)
        im_jng_r = OffsetImage(photos[6], zoom=0.18)
        im_mid_r = OffsetImage(photos[7], zoom=0.18)
        im_bot_r = OffsetImage(photos[8], zoom=0.18)
        im_sup_r = OffsetImage(photos[9], zoom=0.18)
        
        def animate(i):
            ax.clear()
            ax.set_xlim([-120,14870])
            ax.set_ylim([-120,14870])
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.set_xticks([])
            ax.set_yticks([])
            img = plt.imread(os.getcwd() + "\\Bayes Esports\\map.png")
            plt.title('')
            plt.imshow(img, extent=[-120,14870,-120,14870])

            line, = ax.plot(0, 0, color='white', zorder=10)
            
            scat_top_b = ax.scatter(0, 0, c='Blue', s=600, zorder=20)
            scat_jng_b = ax.scatter(0, 0, c='Blue', s=600, zorder=20)
            scat_mid_b = ax.scatter(0, 0, c='Blue', s=600, zorder=20)
            scat_bot_b = ax.scatter(0, 0, c='Blue', s=600, zorder=20)
            scat_sup_b = ax.scatter(0, 0, c='Blue', s=600, zorder=20)
        
            scat_top_r = ax.scatter(0, 0, c='Red', s=600, zorder=20)
            scat_jng_r = ax.scatter(0, 0, c='Red', s=600, zorder=20)
            scat_mid_r = ax.scatter(0, 0, c='Red', s=600, zorder=20)
            scat_bot_r = ax.scatter(0, 0, c='Red', s=600, zorder=20)
            scat_sup_r = ax.scatter(0, 0, c='Red', s=600, zorder=20)
            
            scat_top_b.set_offsets( ( (df_top_b['X'].values.tolist()[i])  ,  (df_top_b['Y'].values.tolist()[i]) )  )
            scat_jng_b.set_offsets( ( (df_jng_b['X'].values.tolist()[i])  ,  (df_jng_b['Y'].values.tolist()[i]) )  )
            scat_mid_b.set_offsets( ( (df_mid_b['X'].values.tolist()[i])  ,  (df_mid_b['Y'].values.tolist()[i]) )  )
            scat_bot_b.set_offsets( ( (df_bot_b['X'].values.tolist()[i])  ,  (df_bot_b['Y'].values.tolist()[i]) )  )
            scat_sup_b.set_offsets( ( (df_sup_b['X'].values.tolist()[i])  ,  (df_sup_b['Y'].values.tolist()[i]) )  )
            
            scat_top_r.set_offsets( ( (df_top_r['X'].values.tolist()[i])  ,  (df_top_r['Y'].values.tolist()[i]) )  )
            scat_jng_r.set_offsets( ( (df_jng_r['X'].values.tolist()[i])  ,  (df_jng_r['Y'].values.tolist()[i]) )  )
            scat_mid_r.set_offsets( ( (df_mid_r['X'].values.tolist()[i])  ,  (df_mid_r['Y'].values.tolist()[i]) )  )
            scat_bot_r.set_offsets( ( (df_bot_r['X'].values.tolist()[i])  ,  (df_bot_r['Y'].values.tolist()[i]) )  )
            scat_sup_r.set_offsets( ( (df_sup_r['X'].values.tolist()[i])  ,  (df_sup_r['Y'].values.tolist()[i]) )  )
            
            line.set_xdata(df['X'].values.tolist()[:i])
            line.set_ydata(df['Y'].values.tolist()[:i])
            
            ab_top_b = AnnotationBbox(im_top_b, ( (df_top_b['X'].values.tolist()[i])  ,  (df_top_b['Y'].values.tolist()[i]) ), frameon=False, zorder=30)
            ab_jng_b = AnnotationBbox(im_jng_b, ( (df_jng_b['X'].values.tolist()[i])  ,  (df_jng_b['Y'].values.tolist()[i]) ), frameon=False, zorder=30)
            ab_mid_b = AnnotationBbox(im_mid_b, ( (df_mid_b['X'].values.tolist()[i])  ,  (df_mid_b['Y'].values.tolist()[i]) ), frameon=False, zorder=30)
            ab_bot_b = AnnotationBbox(im_bot_b, ( (df_bot_b['X'].values.tolist()[i])  ,  (df_bot_b['Y'].values.tolist()[i]) ), frameon=False, zorder=30)
            ab_sup_b = AnnotationBbox(im_sup_b, ( (df_sup_b['X'].values.tolist()[i])  ,  (df_sup_b['Y'].values.tolist()[i]) ), frameon=False, zorder=30)
            
            ab_top_r = AnnotationBbox(im_top_r, ( (df_top_r['X'].values.tolist()[i])  ,  (df_top_r['Y'].values.tolist()[i]) ), frameon=False, zorder=30)
            ab_jng_r = AnnotationBbox(im_jng_r, ( (df_jng_r['X'].values.tolist()[i])  ,  (df_jng_r['Y'].values.tolist()[i]) ), frameon=False, zorder=30)
            ab_mid_r = AnnotationBbox(im_mid_r, ( (df_mid_r['X'].values.tolist()[i])  ,  (df_mid_r['Y'].values.tolist()[i]) ), frameon=False, zorder=30)
            ab_bot_r = AnnotationBbox(im_bot_r, ( (df_bot_r['X'].values.tolist()[i])  ,  (df_bot_r['Y'].values.tolist()[i]) ), frameon=False, zorder=30)
            ab_sup_r = AnnotationBbox(im_sup_r, ( (df_sup_r['X'].values.tolist()[i])  ,  (df_sup_r['Y'].values.tolist()[i]) ), frameon=False, zorder=30)
            
            ax.add_artist(ab_top_b)
            ax.add_artist(ab_jng_b)
            ax.add_artist(ab_mid_b)
            ax.add_artist(ab_bot_b)
            ax.add_artist(ab_sup_b)
            
            ax.add_artist(ab_top_r)
            ax.add_artist(ab_jng_r)
            ax.add_artist(ab_mid_r)
            ax.add_artist(ab_bot_r)
            ax.add_artist(ab_sup_r)
            
            return scat_top_b,scat_jng_b,scat_mid_b,scat_bot_b,scat_sup_b,scat_top_r,scat_jng_r,scat_mid_r,scat_bot_r,scat_sup_r
        
        animator = ani.FuncAnimation(fig, animate, frames=len(df['X'].values.tolist()), interval = 50, repeat=False)
        # plt.show()
        writergif = ani.PillowWriter(fps=15)
        animator.save(f'Bayes Esports/Pathings/{match_id}_pathing.gif', writer=writergif)

def get_position_graphs(file_list_sorted_asc, file_list_sorted_desc, match_id, path_graphs, champions_json):
    """
    Return two lists with coordinates X and Y about all the player positions from a team in a match
    
    """
    
    team_top_name = "R7 Bong" # Fill Top Name
    champions = []
    is_in_base = False
    
    blue_top_x_y, blue_jng_x_y, blue_mid_x_y, blue_bot_x_y, blue_sup_x_y = [], [], [], [], []
    red_top_x_y , red_jng_x_y , red_mid_x_y , red_bot_x_y , red_sup_x_y  = [], [], [], [], []
    
    x_y = []
    is_blue = False
    is_red = False
    found = False
    gameTime = 0
    
    file_number_positions = 0
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
        
        # Si es un SNAPSHOT - MATCH - UPDATE:
        if typee == "SNAPSHOT":
            if subject == "MATCH":
                if action == "UPDATE":
                    # We get the EsportsTeamId for every team
                    team_urn_blue = str(payload['teamOne']['players'][0]['summonerName'])
                    team_urn_red  = str(payload['teamTwo']['players'][0]['summonerName'])
                    
                    champions_blue = get_champions("Blue", payload, champions_json)
                    champions.extend(champions_blue)
                    
                    if team_urn_blue == team_top_name:
                        urn = team_urn_blue
                        found = True
                        is_blue = True
                    elif team_urn_red == team_top_name:
                        urn = team_urn_red
                        found = True
                        is_red = True
    
    while not is_in_base:
        try:
            # Abrimos archivo(snapshot) y conseguimos data
            file = file_list_sorted_asc[file_number_positions]
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
        
        if typee == "SNAPSHOT":
                if subject == "PLAYER":
                    if action == "UPDATE_POSITIONS":                                           
                        gameTime = payload['gameTime'] / 1000
                        
                        print(gameTime)
                        
                        if is_blue:
                            x_y.append( (payload['positions'][1]['position'][0],payload['positions'][1]['position'][1]) )
                            
                            blue_top_x_y.append( (payload['positions'][0]['position'][0],payload['positions'][0]['position'][1]) )
                            blue_jng_x_y.append( (payload['positions'][1]['position'][0],payload['positions'][1]['position'][1]) )
                            blue_mid_x_y.append( (payload['positions'][2]['position'][0],payload['positions'][2]['position'][1]) )
                            blue_bot_x_y.append( (payload['positions'][3]['position'][0],payload['positions'][3]['position'][1]) )
                            blue_sup_x_y.append( (payload['positions'][4]['position'][0],payload['positions'][4]['position'][1]) )
                            
                            red_top_x_y.append( (payload['positions'][5]['position'][0],payload['positions'][5]['position'][1]) )
                            red_jng_x_y.append( (payload['positions'][6]['position'][0],payload['positions'][6]['position'][1]) )
                            red_mid_x_y.append( (payload['positions'][7]['position'][0],payload['positions'][7]['position'][1]) )
                            red_bot_x_y.append( (payload['positions'][8]['position'][0],payload['positions'][8]['position'][1]) )
                            red_sup_x_y.append( (payload['positions'][9]['position'][0],payload['positions'][9]['position'][1]) )
                            
                            if gameTime>90:
                                if x_y[-1][0] > -120 and x_y[-1][0] < 2000 and x_y[-1][1] > -120 and x_y[-1][1] < 2000:
                                    is_in_base = True
                        
                        elif is_red:
                            x_y.append( (payload['positions'][6]['position'][0],payload['positions'][6]['position'][1] ) )
                            
                            blue_top_x_y.append( (payload['positions'][0]['position'][0],payload['positions'][0]['position'][1]) )
                            blue_jng_x_y.append( (payload['positions'][1]['position'][0],payload['positions'][1]['position'][1]) )
                            blue_mid_x_y.append( (payload['positions'][2]['position'][0],payload['positions'][2]['position'][1]) )
                            blue_bot_x_y.append( (payload['positions'][3]['position'][0],payload['positions'][3]['position'][1]) )
                            blue_sup_x_y.append( (payload['positions'][4]['position'][0],payload['positions'][4]['position'][1]) )
                            
                            red_top_x_y.append( (payload['positions'][5]['position'][0],payload['positions'][5]['position'][1]) )
                            red_jng_x_y.append( (payload['positions'][6]['position'][0],payload['positions'][6]['position'][1]) )
                            red_mid_x_y.append( (payload['positions'][7]['position'][0],payload['positions'][7]['position'][1]) )
                            red_bot_x_y.append( (payload['positions'][8]['position'][0],payload['positions'][8]['position'][1]) )
                            red_sup_x_y.append( (payload['positions'][9]['position'][0],payload['positions'][9]['position'][1]) )
                            
                            if gameTime>90:
                                if x_y[-1][0] > 12750 and x_y[-1][0] < 14870 and x_y[-1][1] > 12750 and x_y[-1][1] < 14870:
                                    is_in_base = True                            
        file_number_positions+=1
    return x_y, blue_top_x_y, blue_jng_x_y, blue_mid_x_y, blue_bot_x_y, blue_sup_x_y, red_top_x_y, red_jng_x_y, red_mid_x_y, red_bot_x_y, red_sup_x_y, champions