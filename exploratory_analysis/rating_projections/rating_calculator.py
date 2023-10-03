from player import Player
from team import Team
from projector import Projector

class RatingCalculator:
    """ Class to calculate ratings for a player or team. """

    def calculate_posterior_mean(self, 
                                 prior_mean: float, 
                                 actual_mean: float,
                                 prior_std: float = 10, 
                                 actual_std: float = 25):
        
        return ((actual_std**2 * prior_mean) + ((prior_std**2) * actual_mean)) / (prior_std**2 + actual_std**2)
    
class TeamRatingCalculator(RatingCalculator):
    """Class to calculate the ratings for a Player."""
    def __init__(self, 
                 Team: Team,
                 ):
        self.Team = Team
        
    def get_team_rating(self, round_id):
        return self.Team.get_rating(round_id)
    
    def get_projected_rating(self, Projector):
        if Projector.Match.home_team.team_name == self.Team.team_name:
            return Projector.home_offensive_rating - Projector.away_offensive_rating
        else:
            return Projector.away_offensive_rating - Projector.home_offensive_rating
        
    def get_match_rating(self, Match):
        if Match.home_team.team_name == self.Team.team_name:
            return Match.match_stats['Home_exp_vaep_value'].iloc[0] - Match.match_stats['Away_exp_vaep_value'].iloc[0]
        else:
            return Match.match_stats['Away_exp_vaep_value'].iloc[0] - Match.match_stats['Home_exp_vaep_value'].iloc[0]
        
    def calculate_new_rating(self, Match, Projector, home_advantage = 5.83, prior_std=10, actual_std=25):
        return self.calculate_posterior_mean(prior_mean = self.get_projected_rating(Projector),
                                             actual_mean = self.get_match_rating(Match) - home_advantage,
                                             prior_std = prior_std,
                                             actual_std = actual_std)

    def update_team_rating(self, Match, Projector, prior_std=10, actual_std=25):
        self.Team.add_rating(Match.round_id, self.calculate_new_rating(Match, Projector, prior_std, actual_std))
        
    def get_team_offensive_rating(self, round_id):
        return self.Team.get_offensive_rating(round_id)
    
    def get_match_offensive_rating(self, Match):
        if Match.home_team.team_name == self.Team.team_name:
            return Match.match_stats['Home_exp_vaep_value'].iloc[0]
        else:
            return Match.match_stats['Away_exp_vaep_value'].iloc[0]
        
    # def calculate_projected_offensive_rating(self, Match):
        
    #     return 

    # def update_team_offensive_rating(self, Match, prior_std=10, actual_std=25):
    #     self.Team.add_offensive_rating(Match.round_id, self.calculate_new_offensive_rating(Match, prior_std, actual_std))     
        
    # def get_team_defensive_rating(self, round_id):
    #     return self.Team.get_defensive_rating(round_id)
    
    # def get_match_defensive_rating(self, Match):
    #     if Match.home_team.team_name == self.Team.team_name:
    #         return Match.match_stats['Away_exp_vaep_value'].iloc[0]
    #     else:
    #         return Match.match_stats['Home_exp_vaep_value'].iloc[0]
    
    # def calculate_new_defensive_rating(self, Match):
    #     return None # Maybe not necessary
    
    # def update_team_defensive_rating(self, Match):
    #     self.Team.add_defensive_rating(Match.round_id, self.Team.get_offensive_rating() - self.Team.get_rating())
    
class PlayerRatingCalculator(RatingCalculator):
    """Class to calculate the ratings for a Player."""
    def __init__(self, 
                 Player: Player
                 ):
        self.Player = Player
        
    def get_player_rating(self, round_id):
        return self.Player.get_rating(round_id)
    
    def get_projected_rating(self, Projector):
        pass
            
    def get_match_rating(self, Match):
        try:
            return Match.player_stats[Match.player_stats['Player'] == self.Player.get_name()]['exp_vaep_value'].iloc[0]
        except:
            raise KeyError("Player {} not available in given match.".format(self.Player.get_name())) from None 
        
    def calculate_new_rating(self, Match, prior_std = 10, actual_std = 25):
        return self.calculate_posterior_mean(prior_mean = self.get_player_rating(Match.previous_round_id),
                                             actual_mean = self.get_match_rating(Match),
                                             prior_std = prior_std,
                                             actual_std = actual_std)

    def update_player_rating(self, Match, prior_std = 10, actual_std = 25):
        self.Player.add_rating(Match.round_id, self.calculate_new_rating(Match, prior_std, actual_std))