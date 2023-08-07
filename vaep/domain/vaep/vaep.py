import numpy as np

def get_player(vaep_data, player):
    
    return vaep_data[vaep_data['player'] == player]

def get_player_vaep(chains):
    
    players_vaep = chains.groupby(['player', 'team']).agg(
        vaep_value = ("vaep_value", "sum"),
        offensive_value = ("offensive_value", "sum"),
        defensive_value = ("defensive_value", "sum"),
        num_actions = ("action_type", "count")
        ).reset_index()
    players_vaep = players_vaep[['player', 'team', 'vaep_value', 'offensive_value', 'defensive_value', 'num_actions']]
    
    return players_vaep

def get_player_minutes(player_stats):
    
    player_minutes = player_stats.groupby("Player").agg(
        minutes_percent = ("Percent_Played", "sum"),
        games = ("Player", "count")
    ).reset_index()
    player_minutes = player_minutes.rename(columns = {"Player":"player"})
    
    return player_minutes

def convert_vaep_to_rating(player_vaep_mins, minutes_percent_threshold = 1000):
    
    player_ratings = player_vaep_mins[player_vaep_mins['minutes_percent'] > minutes_percent_threshold]
    player_ratings['vaep_rating'] = player_ratings['vaep_value'] * 100 / player_ratings['minutes_percent']
    player_ratings['offensive_rating'] = player_ratings['offensive_value'] * 100 / player_ratings['minutes_percent']
    player_ratings['defensive_rating'] = player_ratings['defensive_value'] * 100 / player_ratings['minutes_percent']
    
    return player_ratings    

def get_match(chains, match_id):
    return chains[chains['match_id'] == match_id]

def get_match_rankings(match_vaep):
    
    match_vaep['vaep_ranking'] = match_vaep['vaep_value'].rank(ascending = False)
    match_vaep['offensive_ranking'] = match_vaep['offensive_value'].rank(ascending = False)
    match_vaep['defensive_ranking'] = match_vaep['defensive_value'].rank(ascending = False)

    match_vaep['normalised_vaep_value'] = (match_vaep['vaep_value'] - match_vaep['vaep_value'].min()) / (match_vaep['vaep_value'].max() - match_vaep['vaep_value'].min())
    match_vaep['normalised_offensive_value'] = (match_vaep['offensive_value'] - match_vaep['offensive_value'].min()) / (match_vaep['offensive_value'].max() - match_vaep['offensive_value'].min())
    match_vaep['normalised_defensive_value'] = (match_vaep['defensive_value'] - match_vaep['defensive_value'].min()) / (match_vaep['defensive_value'].max() - match_vaep['defensive_value'].min())

    match_vaep['z_vaep_value'] = (match_vaep['vaep_value'] - match_vaep['vaep_value'].mean()) / np.std(match_vaep['vaep_value'])
    match_vaep['z_offensive_value'] = (match_vaep['offensive_value'] - match_vaep['offensive_value'].mean()) / np.std(match_vaep['offensive_value'])
    match_vaep['z_defensive_value'] = (match_vaep['defensive_value'] - match_vaep['defensive_value'].mean()) / np.std(match_vaep['defensive_value'])
    
    return match_vaep

def get_vaep_action_summary(vaep_data):
    
    action_vaep = vaep_data.groupby('action_type').agg(
        vaep_value = ("vaep_value", "sum"),
        offensive_value = ("offensive_value", "sum"),
        defensive_value = ("defensive_value", "sum"),
        num_actions = ("action_type", "count")
        ).reset_index()
    action_vaep['action_%'] = action_vaep['num_actions'] / action_vaep['num_actions'].sum()

    action_vaep['vaep_value_per_action'] = action_vaep['vaep_value'] / action_vaep['num_actions']
    action_vaep['off_value_per_action'] = action_vaep['offensive_value'] / action_vaep['num_actions']
    action_vaep['def_value_per_action'] = action_vaep['defensive_value'] / action_vaep['num_actions']

    action_vaep['vaep_%'] = action_vaep['vaep_value'] / action_vaep['vaep_value'].sum()
    action_vaep['offensive_%'] = action_vaep['offensive_value'] / action_vaep['offensive_value'].sum()
    action_vaep['defensive_%'] = action_vaep['defensive_value'] / action_vaep['defensive_value'].sum()
        
    return action_vaep