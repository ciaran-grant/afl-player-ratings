import re

from player import Player
from team import Team
from match import Match
from projector import Projector
from rating_calculator import TeamRatingCalculator, PlayerRatingCalculator

def create_team(team_name, player_stats):
    
    players_list = list(player_stats[player_stats['Team'] == team_name]['Player'].unique())
    player_dict = {}
    for player in players_list:
        player_dict[player] = Player(player, team_name)
    
    return Team(team_name, player_dict)

def initialise_teams_players(player_stats):
    
    team_list = list(player_stats['Team'].unique())
    team_dict = {}
    
    for team in team_list:
        team_dict[team] = create_team(team, player_stats)
    
    for team in team_dict.keys():
    
        team_dict[team].add_rating('2020F4', 0)
        team_dict[team].add_offensive_rating('2020F4', 0)
        team_dict[team].add_defensive_rating('2020F4', 0)
        
        for player in team_dict[team].players.keys():
            
            team_dict[team].players[player].add_rating('2020F4', 0)
            
    
    return team_dict

def get_round_match_ids(player_stats, round_id):
    
    round_player_stats = player_stats[player_stats['Round_ID'] == round_id]
    
    return list(round_player_stats['Match_ID'].unique())
    
def get_teams(match_id):
    
    home_team = re.sub(r"(?<=\w)([A-Z])", r" \1", match_id.split("_")[1])
    away_team = re.sub(r"(?<=\w)([A-Z])", r" \1", match_id.split("_")[-1])
    
    return home_team, away_team

def create_round_matches(player_stats, match_summary, round_dict, round_id, team_dict):
    
    round_match_id_list = get_round_match_ids(player_stats, round_id)

    round_dict[round_id] = {}
    for match_id in round_match_id_list:
        home_team, away_team = get_teams(match_id)
        
        round_dict[round_id][match_id] = Match(match_id=match_id,
                                               match_summary=match_summary,
                                               player_stats=player_stats,
                                               home_team=team_dict[home_team],
                                               away_team=team_dict[away_team]
                                               )
        
    return round_dict

def update_team_ratings(Match, team_dict):
    
    home_squad_list = Match.get_home_match_squad()
    away_squad_list = Match.get_away_match_squad()
    match_projector = Projector(Match, home_squad_list, away_squad_list)
    
    home_rating_calculator = TeamRatingCalculator(team_dict[Match.home_team.get_team_name()])
    home_rating_calculator.update_team_rating(Match, match_projector)
    
    away_rating_calculator = TeamRatingCalculator(team_dict[Match.away_team.get_team_name()])
    away_rating_calculator.update_team_rating(Match, match_projector)
    
def update_player_ratings(Match):
    
    round_id = Match.get_round_id()
    
    # Home Players Update
    home_players = Match.get_home_players()
    home_match_squad = Match.get_home_match_squad()
    home_not_match_squad = set(list(home_players.keys())) - set(home_match_squad)

    for player in home_match_squad:
        player_rating_calculator = PlayerRatingCalculator(home_players[player])
        player_rating_calculator.update_player_rating(Match)
        
    for player in home_not_match_squad:
        home_players[player].add_rating(round_id, 0)
    
    ## Away Players Update
    away_players = Match.get_away_players()
    away_match_squad = Match.get_away_match_squad()
    away_not_match_squad = set(list(away_players.keys())) - set(away_match_squad)

    for player in away_match_squad:
        player_rating_calculator = PlayerRatingCalculator(away_players[player])
        player_rating_calculator.update_player_rating(Match)
        
    for player in away_not_match_squad:
        away_players[player].add_rating(round_id, 0)

def update_missing_ratings(team_dict, round_id, Match):
    
    for team in team_dict.keys():
        if round_id not in list(team_dict[team].rating.keys()):
            previous_round_id = Match.get_previous_round_id()
            team_dict[team].add_rating(round_id, team_dict[team].rating[previous_round_id])
            for player in team_dict[team].players.keys():
                team_dict[team].players[player].add_rating(round_id, team_dict[team].players[player].rating[previous_round_id])
                
                
def save_match_projections(Match, projections_dict, match_id):
    
    home_squad_list = Match.get_home_match_squad()
    away_squad_list = Match.get_away_match_squad()
    match_projector = Projector(Match, home_squad_list, away_squad_list)
    
    round_id = Match.get_round_id()
    
    projections_dict[round_id][match_id] = match_projector.home_offensive_rating - match_projector.away_offensive_rating
    
def update_ratings(player_stats, match_summary, round_dict, round_id, team_dict, projections_dict):
    
    round_dict = create_round_matches(player_stats, match_summary, round_dict, round_id, team_dict)
    projections_dict[round_id] = {}
    
    for match_id in round_dict[round_id].keys():
        update_team_ratings(round_dict[round_id][match_id], team_dict)
        update_player_ratings(round_dict[round_id][match_id])
        update_missing_ratings(team_dict, round_id, round_dict[round_id][match_id])
        
        save_match_projections(round_dict[round_id][match_id], projections_dict, match_id)
        
def actual_vs_expected(round_dict, projections_dict):
    
    error_dict = {}
    
    for round_id in round_dict.keys():
        
        error_dict[round_id] = {}
        
        for match_id in round_dict[round_id].keys():
            
            error_dict[round_id][match_id] = {}
            
            match = round_dict[round_id][match_id]
            actual_vaep = match.get_match_stats()['Home_exp_vaep_value'].iloc[0] - match.get_match_stats()['Away_exp_vaep_value'].iloc[0]
            actual = match.get_match_stats()['Home_Score'].iloc[0] - match.get_match_stats()['Away_Score'].iloc[0]
            
            expected = projections_dict[round_id][match_id]
            
            error_dict[round_id][match_id]['actual_vaep'] = actual_vaep
            error_dict[round_id][match_id]['actual'] = actual
            error_dict[round_id][match_id]['expected'] = expected
            error_dict[round_id][match_id]['mae'] = abs(actual - expected)
            error_dict[round_id][match_id]['tip'] = 1*(actual/abs(actual) == expected/abs(expected))
        
    return error_dict
    