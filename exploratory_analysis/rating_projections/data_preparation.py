import numpy as np
import pandas as pd

def load_match_summary():
    
    match_summary = pd.read_csv("/Users/ciaran/Documents/Projects/AFL/data/match_summary.csv")
    match_summary = score_col_splitter(match_summary, "Q4_Score")
    match_summary['Season'] = match_summary['Match_ID'].apply(lambda x: int(x[:4]))
    
    return match_summary
    
def load_player_stats():
    
    player_stats = pd.read_csv("/Users/ciaran/Documents/Projects/AFL/data/scored_player_stats_v2.csv")
    player_stats = create_additional_player_stats_variables(player_stats)
    player_stats = player_stats.fillna(0)
    
    return player_stats

def load_team_info():
    
    team_info = pd.read_csv("/Users/ciaran/Documents/Projects/AFL/data/team_info.csv")
    home_team_info = team_info[['Team', 'Home_Ground_1']].rename(columns = {'Team':'Home_Team', 'Home_Ground_1':'Home_Team_Ground'})
    away_team_info = team_info[['Team', 'Home_Ground_1']].rename(columns = {'Team':'Away_Team', 'Home_Ground_1':'Away_Team_Ground'})

    return team_info, home_team_info, away_team_info
    
def load_venue_info():
    
    venue_info = pd.read_csv("/Users/ciaran/Documents/Projects/AFL/data/venue_info.csv")
    away_venue_info = venue_info[['Venue', 'City']].rename(columns = {'Venue':'Away_Team_Ground', 'City':'Away_Team_City'})
    
    return venue_info, away_venue_info

def create_match_summary_stats(match_summary, match_stats, home_team_info, away_team_info, away_venue_info):
    
    match_summary_stats = match_summary.merge(match_stats, how = "left", on = "Match_ID")
    match_summary_stats = match_summary_stats.merge(home_team_info, how = 'left', left_on='Home_Team', right_on='Home_Team')
    match_summary_stats = match_summary_stats.merge(away_team_info, how = 'left', left_on='Away_Team', right_on='Away_Team')
    match_summary_stats = match_summary_stats.merge(away_venue_info, how = 'left', left_on='Away_Team_Ground', right_on='Away_Team_Ground')

    return match_summary_stats

def score_col_splitter(X, score_col):

    quarter = score_col.split("_")[0]
    
    X['Home_Score'] = X[score_col].apply(lambda x: x.split(" - ")[0].split(".")[-1]).astype(int)
    X['Home_Goals'] = X[score_col].apply(lambda x: x.split(" - ")[0].split(".")[0]).astype(int)
    X['Home_Behinds'] = X[score_col].apply(lambda x: x.split(" - ")[0].split(".")[1]).astype(int)
    X['Home_Shots'] = X['Home_Goals'] + X['Home_Behinds']
    X['Home_Conversion'] = X['Home_Goals'] / X['Home_Shots']
    
    X['Away_Score'] = X[score_col].apply(lambda x: x.split(" - ")[1].split(".")[-1]).astype(int)
    X['Away_Goals'] = X[score_col].apply(lambda x: x.split(" - ")[1].split(".")[0]).astype(int)
    X['Away_Behinds'] = X[score_col].apply(lambda x: x.split(" - ")[1].split(".")[1]).astype(int)
    X['Away_Shots'] = X['Away_Goals'] + X['Away_Behinds']
    X['Away_Conversion'] = X['Away_Goals'] / X['Away_Shots']
        
    return X

def create_additional_player_stats_variables(player_stats):
    
    player_stats['Season'] = player_stats['Match_ID'].apply(lambda x: int(x[:4]))
    player_stats['Player_Season'] = player_stats['Player'] + "_" + player_stats['Season'].astype(str)

    player_stats['Score'] = player_stats['Behinds'] + player_stats['Goals']*6
    player_stats['xScore_Diff'] = player_stats['Score'] - player_stats['xScore']

    player_stats['Home_Team'] = player_stats['Match_ID'].apply(lambda x: x.split("_")[1]).str.replace(r"([A-Z])", r" \1").str.strip()
    player_stats['Away_Team'] = player_stats['Match_ID'].apply(lambda x: x.split("_")[-1]).str.replace(r"([A-Z])", r" \1").str.strip()
    player_stats['Opponent'] = np.where(player_stats['Team'] == player_stats['Home_Team'], player_stats['Away_Team'], player_stats['Home_Team'])

    finals_round_map = {'F1':24,
                        'F2':25,
                        'F3':26,
                        'F4':27}
    
    player_stats['Round_ID'] = player_stats['Round_ID'].astype(str)
    player_stats['Round'] = (player_stats['Round_ID'].str[4:].replace(finals_round_map)).astype(int)
    player_stats['Round_str'] = player_stats['Round_ID'].str[4:].replace(finals_round_map)
    player_stats['Round_ID_num'] = (player_stats['Season'].astype(str) + player_stats['Round'].astype(str)).astype(int)
    
    return player_stats

def aggregate_player_to_match_stats(player_stats):
    
    match_stats = player_stats.groupby(['Match_ID', 'Team', 'Home_Team']).sum()[['Score', 'xScore', 'vaep_value', 'offensive_value', 'defensive_value', 'exp_vaep_value', 'exp_offensive_value', 'exp_defensive_value']].reset_index()
    match_stats['Home_Away'] = np.where(match_stats['Team'] == match_stats['Home_Team'], 'Home', 'Away')
    match_stats = match_stats.pivot(index = 'Match_ID', columns = 'Home_Away', values = ['xScore', 'vaep_value', 'offensive_value', 'defensive_value', 'exp_vaep_value', 'exp_offensive_value', 'exp_defensive_value'])
    match_stats.columns = ['_'.join((y, x)) for (x, y) in match_stats.columns]
    
    return match_stats