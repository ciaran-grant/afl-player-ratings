from scipy import stats
from typing import List

from match import Match
from player import Player

class Projector:
    def __init__(self,
                 Match: Match,
                 home_squad: List[str],
                 away_squad: List[str]) -> None:
        self.Match = Match
        self.home_squad = home_squad
        self.away_squad = away_squad
        
        self.calculate_home_offensive_rating()
        self.calculate_away_offensive_rating()
        self.calculate_home_advantage()
        self.calculate_margin()
        self.calculate_probabilities(self.get_margin(), std = 35)
        
    def calculate_home_offensive_rating(self):
        home_player_ratings = self.Match.home_team.get_player_ratings()
        home_squad_ratings = home_player_ratings.loc[self.home_squad, self.Match.get_previous_round_id()]
        self.home_offensive_rating = home_squad_ratings.sum()
    
    def get_home_offensive_rating(self):

        return self.home_offensive_rating

    def calculate_away_offensive_rating(self):
        away_player_ratings = self.Match.away_team.get_player_ratings()
        away_squad_ratings = away_player_ratings.loc[self.away_squad, self.Match.get_previous_round_id()]
        self.away_offensive_rating = away_squad_ratings.sum()
    
    def get_away_offensive_rating(self):

        return self.away_offensive_rating
    
    def calculate_home_advantage(self):
        
        self.home_advantage = 5.83
        
    def get_home_advantage(self):

        return self.home_advantage
    
    def calculate_margin(self):
        
        self.margin = self.home_offensive_rating - self.away_offensive_rating + self.home_advantage
        
    def get_margin(self):
        
        return self.margin
    
    def calculate_probabilities(self, rating_diff, std):
        
        diff = stats.norm(loc = rating_diff, scale = std)
        
        self.away_prob = diff.cdf(0)
        self.draw_prob = diff.pdf(0)
        self.home_prob = 1 - self.away_prob - self.draw_prob
    
    def get_home_win_prob(self):
        return self.home_prob
    
    def get_draw_prob(self):
        return self.draw_prob
    
    def get_away_win_prob(self):
        return self.away_prob