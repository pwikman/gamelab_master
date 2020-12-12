# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 12:03:17 2020

@author: peter
"""
import pandas as pd
import numpy as np

#### Function to load cleaned data

def get_clean_data(exp, ses, type):
    if exp!='master':
        type = f"{type}_{exp}{ses}"
    return pd.read_csv(f"../{exp}/clean_data/{type}.csv")
  
# Get info related to a player,game combination. Payoff matrix etc. 

def get_player_game_info(pid, gid, lis):
    all_choices = lis[0] 
    all_players = lis[1] 
    all_games = lis[2]
    role = all_players.role[all_players.id==pid]
    game = all_games[all_games.id==gid]
    if role.iat[0]==0:
        n_strats = game.p1.iat[0]
        opp_n_strats = game.p2.iat[0]
    else:
        n_strats = game.p2.iat[0]
        opp_n_strats = game.p1.iat[0]
       
    game_list = game.payoffs.iat[0]
    game_list = game_list.split(' ')
    game_list = np.array(list(map(float, game_list)))
    game_list1 = game_list[0::2]
    game_list2 = game_list[1::2]
    game_list1 = game_list1.reshape(all_games.p1.iat[gid-1],all_games.p2.iat[gid-1])
    game_list2 = game_list2.reshape(all_games.p1.iat[gid-1],all_games.p2.iat[gid-1])
    player_game_mat = game_list2.T
    opp_payoff_mat = game_list2.T
    if role.iat[0]==0:
        player_game_mat = game_list1
    else:
        opp_payoff_mat = game_list1
    dictout = {'role': role.iat[0], 'payoff_mat': player_game_mat, 'opp_payoff_mat': opp_payoff_mat, 'n_strats': n_strats}    
    return dictout


# Function to transform string of numers, possibly as rationals, to numbers
def string_to_list(lista):
    """ Takes a string of rationals on format 1/2 and returns a list of floats """
    splitted = lista.split()
    return [rational_to_double(x) for x in splitted]


def rational_to_double(rat):
    """ Takes a string of typ 4/4 or 4 and returns the corresponding float"""
    if pd.notnull(rat):
        tmp = rat.split("/")
    if len(tmp) > 1:
        num = float(tmp[0])
        den = float(tmp[1])
        return num/den
    else:
        return float(tmp[0])


# Function to generate player & game specific dataset 
def get_player_game_data(pid, gid, lis, role = None):
    all_payoffs = lis[0]
    all_choices = lis[1]
    all_players = lis[2]
    all_games = lis[3]
    all_pasts = lis[4]
    all_gameplays = lis[5]
    player_payoff_hist = all_payoffs.loc[(all_payoffs.gameid==gid) & (all_payoffs.playerid==pid)]
    past_plays_dist = all_pasts.loc[all_pasts.gameid==gid]
    choices = all_choices.loc[(all_choices.gameid==gid) & (all_choices.playerid==pid)]
    
    player_history = player_payoff_hist.merge(past_plays_dist[["currentsp1", "currentsp2", "round"]], left_on='round', right_on='round')
    player_history = player_history.merge(choices[["strats","round"]], left_on='round', right_on='round')
    prev_history = past_plays_dist
    prev_history.loc[:,'round'] += 1
    prev_history['prev_p1'] = past_plays_dist.currentsp1.apply(string_to_list)
    prev_history['prev_p2'] = past_plays_dist.currentsp2.apply(string_to_list)
  
    player_history = player_history.merge(prev_history[["prev_p1", "prev_p2", "round"]], left_on='round', right_on='round', how='left')
  
    # update strings to lists of reals 
    player_history.currentsp1 =player_history.currentsp1.apply(string_to_list)
    player_history.currentsp2 = player_history.currentsp2.apply(string_to_list)
    player_history.strats = player_history.strats.apply(string_to_list)
    player_history.payoff = player_history.payoff.apply(rational_to_double) 
    
  # rename pasts to self and opponent instead of p1 and p2
    if role == None:
        role = get_player_game_info(pid, gid, [all_choices, all_players, all_games])["role"]
  
    if role==0:
        player_history['self_avg_s'] = player_history.currentsp1
        player_history['opponent_avg_s'] = player_history.currentsp2
        player_history['prev_self'] = player_history.prev_p1
        player_history['prev_opp'] = player_history.prev_p2
    
    else:
        player_history['self_avg_s'] = player_history.currentsp2
        player_history['opponent_avg_s'] = player_history.currentsp1
        player_history['prev_self'] = player_history.prev_p2
        player_history['prev_opp'] = player_history.prev_p1
  
  
  # remove unwanted data 
    drops = ["id", "currentsp1", "currentsp2", "prev_p1", "prev_p2"]
    player_history = player_history.drop(drops,axis=1)
  
  
  # Sort data by round 
    player_history = player_history.sort_values('round').reset_index(drop=True)
  
    return player_history




      