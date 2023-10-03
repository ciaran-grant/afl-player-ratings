import pandas as pd
import numpy as np
from player import Player
from team import Team
from typing import List

class Match:
    """ Class to contain information about a match. """
    def __init__(self, 
                 match_id: str,
                 match_summary: pd.DataFrame,
                 player_stats: pd.DataFrame,
                 home_team: Team,
                 away_team: Team):
        
        self.match_summary = match_summary[match_summary['Match_ID'] == match_id]
        self.player_stats = player_stats[player_stats['Match_ID'] == match_id]
        self.match_stats = self.aggregate_player_to_match_stats()
        self.season = int(match_id.split("_")[0][:4])
        self.round_id = match_id.split("_")[0]
        self.previous_round_id = self.get_previous_round_id()
        self.home_team = home_team
        self.away_team = away_team
        
    def get_match_summary(self) -> pd.DataFrame:
        return self.match_summary
    
    def get_player_stats(self) -> pd.DataFrame:
        return self.player_stats
        
    def get_season(self) -> int:
        return self.season
    
    def get_round_id(self) -> str:
        return self.round_id
    
    def get_previous_round_id(self):
        
        season = int(self.round_id[:4])
        if season == 2023:
            finals_round_map = {
                'F1':25,
                'F2':26,
                'F3':27,
                'F4':28}
            reverse_finals_round_map ={
                25:'F1',
                26:'F2',
                27:'F3',
                28:'F4'
            }
            last_round = 24
        else:
            finals_round_map = {
                'F1':24,
                'F2':25,
                'F3':26,
                'F4':27}
            reverse_finals_round_map ={
                24:'F1',
                25:'F2',
                26:'F3',
                27:'F4'
            }
            last_round = 23      

        if 'F' in self.round_id:
            round_num = int(finals_round_map[self.round_id[4:]])
        else:
            round_num = int(self.round_id[4:])
        
        previous_round_num = round_num-1
        if previous_round_num > last_round:
            previous_round = reverse_finals_round_map[previous_round_num]
        else:
            previous_round = str(previous_round_num)
        previous_round = previous_round.zfill(2)

        if round_num == 1:
            previous_season = int(season) - 1
            previous_round = 'F4'
        else:
            previous_season = season
        self.previous_round_id = str(previous_season) + str(previous_round)
        
        return self.previous_round_id
    
    def get_home_team(self) -> Team:
        return self.home_team
    
    def get_away_team(self)-> Team:
        return self.away_team
    
    def get_home_players(self) -> List[Player]:
        return self.get_home_team().players
    
    def get_away_players(self) -> List[Player]:
        return self.get_away_team().players 
    
    def get_home_match_squad(self) -> List[str]:
        return list(self.player_stats[self.player_stats['Team'] == self.home_team.team_name]['Player'])
    
    def get_away_match_squad(self) -> List[str]:
        return list(self.player_stats[self.player_stats['Team'] == self.away_team.team_name]['Player'])
    
    def aggregate_player_to_match_stats(self) -> pd.DataFrame:
    
        self.match_stats = self.player_stats.groupby(['Match_ID', 'Team', 'Home_Team']).sum()[['Score', 'xScore', 'exp_vaep_value', 'exp_offensive_value', 'exp_defensive_value']].reset_index()
        self.match_stats['Home_Away'] = np.where(self.match_stats['Team'] == self.match_stats['Home_Team'], 'Home', 'Away')
        self.match_stats = self.match_stats.pivot(index = 'Match_ID', columns = 'Home_Away', values = ['Score', 'xScore', 'exp_vaep_value', 'exp_offensive_value', 'exp_defensive_value'])
        self.match_stats.columns = ['_'.join((y, x)) for (x, y) in self.match_stats.columns]
        
        return self.match_stats
    
    def get_match_stats(self) -> pd.DataFrame:
        return self.match_stats

    