import numpy as np
from scipy import stats
import pandas as pd
import re

class TeamRatings:
    """ Class for holding and processing player and team ratings across rounds. """
    def __init__(self, prior_weight = 1, prior_std = 10):
        
        self.prior_weight = prior_weight
        self.prior_std = prior_std
        self.home_advantage = 0
        self.player_values = {}
        self.player_stds = {}
        self.team_values = {}
        self.team_stds = {}
        self.match_predictions = {}
        self.latest_round = 'Start'
        
    
    def calculate_home_advantage(self, match_summary_stats):
        self.home_advantage = match_summary_stats['Home_exp_vaep_value'].mean() - match_summary_stats['Away_exp_vaep_value'].mean()
    
    def get_home_advantage(self):
        return self.home_advantage
        
    def initialise_player_values(self, player_stats):
        self.player_values['Start'] = player_stats.groupby(['Player']).mean()[['exp_vaep_value']].reset_index()
        self.player_values['Start'].columns = ['Player', 'Value']
        self.player_values['Start']['Value'] = 0

    def get_player_values(self, round_id):
        return self.player_values[round_id]
    
    def initialise_player_stds(self, player_stats):
        self.player_stds['Start'] = player_stats.groupby(['Player']).std()[['exp_vaep_value']].reset_index()
        self.player_stds['Start'].columns = ['Player', 'Std']
        self.player_stds['Start']['Std'] = 10

    def get_player_stds(self, round_id):
        return self.player_stds[round_id]
    
    def initialise_team_values(self, player_stats):
        self.team_values['Start'] = create_team_summary(player_stats)[['exp_vaep_value_pergame_diff', 'exp_vaep_value_pergame_F', 'exp_vaep_value_pergame_A']].reset_index()
        self.team_values['Start'].columns = ['Team', 'Rating', 'Offensive_Value', 'Defensive_Value']
        self.team_values['Start']['Rating'] = 0
        self.team_values['Start']['Offensive_Value'] = 0
        self.team_values['Start']['Defensive_Value'] = 0
        
    def get_team_values(self, round_id):
        return self.team_values[round_id]
    
    def get_match_player_stats(self, player_stats, match_id):
        return player_stats[player_stats['Match_ID'] == match_id]
        
    def get_home_players(self, player_stats, match_id):
        match_player_stats = self.get_match_player_stats(player_stats, match_id)
        return list(match_player_stats[match_player_stats['Team'] == match_player_stats['Home_Team']]['Player'].unique())

    def get_away_players(self, player_stats, match_id):
        match_player_stats = self.get_match_player_stats(player_stats, match_id)
        return list(match_player_stats[match_player_stats['Team'] != match_player_stats['Home_Team']]['Player'].unique())
    
    def calculate_predicted_match_offensive_values(self, player_stats, round_id, match_id):
        home_players = self.get_home_players(player_stats, match_id)
        home_predicted_offensive_value = self.player_values[round_id][self.player_values[round_id]['Player'].isin(home_players)]['Value'].sum()

        away_players = self.get_away_players(player_stats, match_id)
        away_predicted_offensive_value = self.player_values[round_id][self.player_values[round_id]['Player'].isin(away_players)]['Value'].sum()
        
        return home_predicted_offensive_value, away_predicted_offensive_value
        
    def calculate_predicted_match_defensive_ratings(self, round_id, match_id):
        home_team, away_team = get_teams(match_id)
        home_predicted_defensive_rating = self.team_values[round_id][self.team_values[round_id]['Team'] == home_team]['Defensive_Value']
        away_predicted_defensive_rating = self.team_values[round_id][self.team_values[round_id]['Team'] == away_team]['Defensive_Value']
        
        return home_predicted_defensive_rating, away_predicted_defensive_rating
    
    def apply_home_advantage(self, home_rating):
        
        return home_rating + self.home_advantage        
    
    def calculate_predicted_match_ratings(self, player_stats, match_id):
        home_predicted_offensive_value, away_predicted_offensive_value = self.calculate_predicted_match_offensive_values(player_stats, match_id)
        home_predicted_defensive_rating, away_predicted_defensive_rating = self.calculate_predicted_match_defensive_ratings(player_stats, match_id)
        
        home_predicted_rating = home_predicted_offensive_value - home_predicted_defensive_rating
        away_predicted_rating = away_predicted_offensive_value - away_predicted_defensive_rating

        home_predicted_rating_ha = self.apply_home_advantage(home_predicted_rating)

        return home_predicted_rating_ha, away_predicted_rating
        
    def calculate_probabilities(self, rating_diff, std):
        
        diff = stats.norm(loc = rating_diff, scale = std)
        
        away_prob = diff.cdf(0)
        draw_prob = diff.pdf(0)
        home_prob = 1 - away_prob - draw_prob
        
        return home_prob, draw_prob, away_prob
    
    def get_actual_match_offensive_values(self, player_stats, match_id):
        
        match_player_stats = self.get_match_player_stats(player_stats, match_id)

        home_actual_player_values = match_player_stats[match_player_stats['Team'] == match_player_stats['Home_Team']][['Player', 'exp_vaep_value']]
        home_actual_offensive_value_ha = home_actual_player_values['exp_vaep_value'].sum()
        
        away_actual_player_values = match_player_stats[match_player_stats['Team'] != match_player_stats['Home_Team']][['Player', 'exp_vaep_value']]
        away_actual_offensive_value = away_actual_player_values['exp_vaep_value'].sum()
        
        return home_actual_offensive_value_ha, away_actual_offensive_value
    
    def calculate_actual_match_ratings(self, player_stats, match_id):
        
        home_actual_offensive_value_ha, away_actual_offensive_value = self.get_actual_match_offensive_values(player_stats, match_id)
                
        home_actual_rating = home_actual_offensive_value_ha - away_actual_offensive_value
        away_actual_rating = -1*home_actual_rating
        
        return home_actual_rating, away_actual_rating
    
    def calculate_posterior(self, prior_mean, actual):
            
        return (self.prior_weight*(self.prior_std**2)*prior_mean + (2-self.prior_weight)*(self.prior_std**2)*actual) / (self.prior_std**2 + self.prior_std**2)
        
    def calculate_posterior_rating(self, prior_rating, actual_rating):
                
        return self.calculate_posterior(prior_rating, actual_rating)
    
    def remove_home_advantage(self, home_rating_ha):
        
        return home_rating_ha - self.home_advantage 
    
    def calculate_posterior_offensive_value(self, prior_player_values, actual_player_values):
        
        # home_players = self.get_home_players(player_stats, match_id)
        # home_player_values = self.player_values[round_id][self.player_values[round_id]['Player'].isin(home_players)]['Value']
        
        # home_actual_player_values = match_player_stats[match_player_stats['Team'] == match_player_stats['Home_Team']][['Player', 'exp_offensive_value']]

        # team = prior_player_values.merge(actual_player_values, how = 'left', on = 'Player')
        # team.columns = ['Player', 'Team', 'prior', 'actual']
        
        data = pd.concat([actual_player_values, prior_player_values], axis=1)
        data.columns = ['actual', 'prior']
        
        return self.calculate_posterior(prior_mean=data['prior'], actual=data['actual']).sum()
        
    def calculate_posterior_defensive_value(self, posterior_rating, posterior_offensive_value):
        
        return posterior_offensive_value - posterior_rating
        
    def calculate_player_posteriors(self, actual_values, round_id):
        
        player_list = []
        posterior_list = []
        for player in list(actual_values['Player'].unique()):
            posterior_mean = self.calculate_posterior_offensive_value(player, actual_values, round_id)
            player_list.append(player)
            posterior_mean_list.append(posterior_mean)
        posteriors = pd.DataFrame(
            {'Player': player_list,
            'Posterior_Value': posterior_mean_list,
            })
        return posteriors
    
    def update_team_rating(self, player_stats, match_id, round_id):
        
        home_team, away_team = get_teams(match_id)
        
        home_prior_rating = self.team_values[round_id].loc[self.team_values[round_id]['Team'] == home_team]['Rating']
        away_prior_rating = self.team_values[round_id].loc[self.team_values[round_id]['Team'] == away_team]['Rating']
        
        home_actual_rating, away_actual_rating = self.calculate_actual_match_ratings(player_stats, match_id)
        
        home_posterior_rating = self.calculate_posterior_rating(home_prior_rating, home_actual_rating)
        self.team_values[round_id].loc[self.team_values[round_id]['Team'] == home_team, 'Rating'] = home_posterior_rating
        away_posterior_rating = self.calculate_posterior_rating(away_prior_rating, away_actual_rating)
        self.team_values[round_id].loc[self.team_values[round_id]['Team'] == away_team, 'Rating'] = away_posterior_rating       
        
    def update_team_offensive_value(self, player_stats, match_id, round_id, ):
        
        match_player_stats = self.get_match_player_stats(player_stats, match_id)
        home_team, away_team = get_teams(match_id)
        
        home_players = self.get_home_players(player_stats, match_id)
        home_player_values = self.player_values[round_id][self.player_values[round_id]['Player'].isin(home_players)]['Value'].reset_index(drop=True)
        home_actual_player_values = match_player_stats[match_player_stats['Team'] == match_player_stats['Home_Team']]['exp_vaep_value'].reset_index(drop=True)
        home_posterior_offensive_value = self.calculate_posterior_offensive_value(home_player_values, home_actual_player_values)
        self.team_values[round_id].loc[self.team_values[round_id]['Team'] == home_team, 'Offensive_Value'] = home_posterior_offensive_value

        away_players = self.get_away_players(player_stats, match_id)
        away_player_values = self.player_values[round_id][self.player_values[round_id]['Player'].isin(away_players)]['Value'].reset_index(drop=True)
        away_actual_player_values = match_player_stats[match_player_stats['Team'] != match_player_stats['Home_Team']]['exp_vaep_value'].reset_index(drop=True)    
        away_posterior_offensive_value = self.calculate_posterior_offensive_value(away_player_values, away_actual_player_values)
        self.team_values[round_id].loc[self.team_values[round_id]['Team'] == away_team, 'Offensive_Value'] = away_posterior_offensive_value 
    
    def update_team_defensive_value(self, match_id, round_id):
        
        home_team, away_team = get_teams(match_id)
        
        home_rating = self.team_values[round_id].loc[self.team_values[round_id]['Team'] == home_team, 'Rating']
        home_offensive_value = self.team_values[round_id].loc[self.team_values[round_id]['Team'] == home_team, 'Offensive_Value']
        self.team_values[round_id].loc[self.team_values[round_id]['Team'] == home_team, 'Defensive_Value'] = home_offensive_value - home_rating
        
        away_rating = self.team_values[round_id].loc[self.team_values[round_id]['Team'] == away_team, 'Rating']
        away_offensive_value = self.team_values[round_id].loc[self.team_values[round_id]['Team'] == away_team, 'Offensive_Value']
        self.team_values[round_id].loc[self.team_values[round_id]['Team'] == away_team, 'Defensive_Value'] = away_offensive_value - away_rating
    
    def update_player_values(self, player_stats, match_id, round_id):
        
        match_player_stats = self.get_match_player_stats(player_stats, match_id)
        
        home_players = self.get_home_players(player_stats, match_id)
        home_player_values = self.player_values[round_id][self.player_values[round_id]['Player'].isin(home_players)][['Player', 'Value']]
        home_actual_player_values = match_player_stats[match_player_stats['Team'] == match_player_stats['Home_Team']][['Player', 'exp_vaep_value']]

        home_team = home_player_values.merge(home_actual_player_values, how = 'left', on = 'Player')
        home_team.columns = ['Player', 'prior', 'actual']
        home_team['Posterior_Value'] = self.calculate_posterior(prior_mean=home_team['prior'], actual=home_team['actual'])
        home_posteriors = home_team[['Player', 'Posterior_Value']]
        
        away_players = self.get_away_players(player_stats, match_id)
        away_player_values = self.player_values[round_id][self.player_values[round_id]['Player'].isin(away_players)][['Player', 'Value']]
        away_actual_player_values = match_player_stats[match_player_stats['Team'] != match_player_stats['Home_Team']][['Player', 'exp_vaep_value']]

        away_team = away_player_values.merge(away_actual_player_values, how = 'left', on = 'Player')
        away_team.columns = ['Player', 'prior', 'actual']
        away_team['Posterior_Value'] = self.calculate_posterior(prior_mean=away_team['prior'], actual=away_team['actual'])
        away_posteriors = away_team[['Player', 'Posterior_Value']]
               
        posteriors = pd.concat([home_posteriors, away_posteriors], axis=0)
        for player in list(posteriors['Player'].unique()):
            self.player_values[round_id].loc[self.player_values[round_id]['Player'] == player, 'Value'] = posteriors.loc[posteriors['Player'] == player, 'Posterior_Value'].iloc[0]

    def update_match_values(self, player_stats, match_id, round_id):
        
        self.update_team_rating(player_stats, match_id, round_id)
        self.update_team_offensive_value(player_stats, match_id, round_id)
        self.update_team_defensive_value(match_id, round_id)
        self.update_player_values(player_stats, match_id, round_id)
        
    def update_round_values(self, player_stats, round_id):
        
        self.player_values[round_id] = self.player_values[self.latest_round].copy()
        self.team_values[round_id] = self.team_values[self.latest_round].copy()
        
        round_match_list = list(player_stats[player_stats['Round_ID'] == round_id]['Match_ID'].unique())
        
        for match_id in round_match_list:
            home_score = player_stats[(player_stats['Match_ID'] == match_id) & (player_stats['Team'] == player_stats['Home_Team'])]['exp_vaep_value'].sum()
            away_score = player_stats[(player_stats['Match_ID'] == match_id) & (player_stats['Team'] != player_stats['Home_Team'])]['exp_vaep_value'].sum()
            self.update_match_values(player_stats, match_id, round_id)
        
        self.latest_round = round_id
        
    def get_home_team(self, player_stats, match_id):
        match_player_stats = self.get_match_player_stats(player_stats, match_id)
        return list(match_player_stats['Home_Team'].unique())[0]

    def get_away_team(self, player_stats, match_id):
        match_player_stats = self.get_match_player_stats(player_stats, match_id)
        return list(match_player_stats['Away_Team'].unique())[0]
                
    def get_team_ratings(self, player_stats, round_id):
        player_values = self.get_player_values(round_id)
        player_stds = self.get_player_stds(round_id)
            
        if round_id != "Start":
            round_match_list = list(player_stats[player_stats['Round_ID'] == round_id]['Match_ID'].unique())    
            
            team_ratings = []
            for match_id in round_match_list:
                home_players = self.get_home_players(player_stats, match_id)
                home_team = self.get_home_team(player_stats, match_id)
                home_offensive_value = player_values[player_values['Player'].isin(home_players)]['Offensive_Value'].sum()
                home_defensive_rating = player_values[player_values['Player'].isin(home_players)]['Defensive_Value'].sum()
                home_offensive_std = player_stds[player_stds['Player'].isin(home_players)]['Offensive_Std'].sum()
                home_defensive_std = player_stds[player_stds['Player'].isin(home_players)]['Defensive_Std'].sum()
                home = pd.DataFrame.from_dict({
                    'Team':[home_team],
                    'Offensive_Value':[home_offensive_value],
                    'Defensive_Value':[home_defensive_rating],
                    'Offensive_Std':[home_offensive_std],
                    'Defensive_Std':[home_defensive_std]
                })
                home['Value'] = home['Offensive_Value'] + home['Defensive_Value'] 
                
                away_players = self.get_away_players(player_stats, match_id)
                away_team = self.get_away_team(player_stats, match_id)
                away_offensive_value = player_values[player_values['Player'].isin(away_players)]['Offensive_Value'].sum()
                away_defensive_rating = player_values[player_values['Player'].isin(away_players)]['Defensive_Value'].sum()
                away_offensive_std = player_stds[player_stds['Player'].isin(away_players)]['Offensive_Std'].sum()
                away_defensive_std = player_stds[player_stds['Player'].isin(away_players)]['Defensive_Std'].sum()
                away = pd.DataFrame.from_dict({
                    'Team':[away_team],
                    'Offensive_Value':[away_offensive_value],
                    'Defensive_Value':[away_defensive_rating],
                    'Offensive_Std':[away_offensive_std],
                    'Defensive_Std':[away_defensive_std]
                })
                away['Value'] = away['Offensive_Value'] + away['Defensive_Value'] 

                team_ratings.append(home)
                team_ratings.append(away)
            
            return pd.concat(team_ratings)
    
    def get_squad_ratings(self, player_stats, round_id):
        
        player_values = self.get_player_values(round_id)
        player_stds = self.get_player_stds(round_id)
        
        team_list = list(player_stats['Team'].unique())
        team_ratings = []
        for team in team_list:
            players = list(player_stats[player_stats['Team'] == team]['Player'].unique())
            offensive_value = player_values[player_values['Player'].isin(players)]['Offensive_Value'].sum()
            defensive_rating = player_values[player_values['Player'].isin(players)]['Defensive_Value'].sum()
            offensive_std = player_stds[player_stds['Player'].isin(players)]['Offensive_Std'].sum()
            defensive_std = player_stds[player_stds['Player'].isin(players)]['Defensive_Std'].sum()
            rating = pd.DataFrame.from_dict({
                'Team':[team],
                'Offensive_Value':[offensive_value],
                'Defensive_Value':[defensive_rating],
                'Offensive_Std':[offensive_std],
                'Defensive_Std':[defensive_std]
            })
            rating['Value'] = rating['Offensive_Value'] + rating['Defensive_Value'] 
            
            team_ratings.append(rating)
        
        return pd.concat(team_ratings).reset_index(drop=True)
        


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

def get_previous_round_id(round_id):
    
    finals_round_map = {'F1':24,
                        'F2':25,
                        'F3':26,
                        'F4':27}
    
    season = round_id[:4]
    if 'F' in round_id:
        round_num = finals_round_map[round_id[4:]]
    else:
        round_num = round_id[4:]
    
    previous_round_num = int(round_id[4:])-1
    previous_round_num = str(previous_round_num).zfill(2)
    if previous_round_num == 1:
        previous_season = int(season) - 1
    else:
        previous_season = season
    previous_round_id = str(previous_season) + str(previous_round_num)
    
    return previous_round_id

def create_team_summary(player_stats, rounds = None):
    
    player_stats_copy = player_stats.copy()
    
    if rounds is not None:
        all_rounds = sorted(list(set(player_stats_copy['Round_ID'])))
        rating_rounds = all_rounds[-rounds:]
        player_stats_copy = player_stats_copy[player_stats_copy['Round_ID'].isin(rating_rounds)]
    
    team_for = player_stats_copy.groupby(['Team']).sum()[['Score', 'xScore','vaep_value', 'vaep_value_received', 'offensive_value', 'defensive_value', 'exp_vaep_value', 'exp_vaep_value_received', 'exp_offensive_value', 'exp_defensive_value']]
    team_for.columns = [x+"_F" for x in list(team_for)]
    team_against = player_stats_copy.groupby(['Opponent']).sum()[['Score', 'xScore', 'vaep_value', 'vaep_value_received', 'offensive_value', 'defensive_value', 'exp_vaep_value', 'exp_vaep_value_received', 'exp_offensive_value', 'exp_defensive_value']]
    team_against.columns = [x+"_A" for x in list(team_against)]
    team_games = player_stats_copy.groupby(['Match_ID', 'Team']).size().reset_index().groupby(['Team']).count()[['Match_ID']]
    team_games.columns = ['Games']
    team_summary = pd.concat([team_games, team_for, team_against], axis=1)
    
    for col in [x.replace("_F", "") for x in list(team_for)]:
        team_summary[col+"_pergame_F"] = team_summary[col+"_F"] / team_summary["Games"]
        team_summary[col+"_pergame_A"] = team_summary[col+"_A"] / team_summary["Games"]

        team_summary[col+"_diff"] = team_summary[col+"_F"] - team_summary[col+"_A"]
        team_summary[col+"_pergame_diff"] = team_summary[col+"_pergame_F"] - team_summary[col+"_pergame_A"]

    return team_summary

def get_teams(match_id):
    
    home_team = re.sub(r"\B([A-Z])", r" \1", match_id.split("_")[1])
    away_team = re.sub(r"\B([A-Z])", r" \1", match_id.split("_")[-1])

    return home_team, away_team