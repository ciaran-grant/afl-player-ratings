from player import Player

class Team:
    """ Class for holding information about teams. """
    def __init__(self,
                 team_name: str, 
                 players: dict[str, Player]):
        
        self.team_name = team_name
        self.players = players
        self.rating = {"Initial":0}
        self.offensive_rating = {"Initial":0}
        self.defensive_rating = {"Initial":0}
        
    def get_team_name(self):
        return self.team_name
    
    def get_rating(self, round_id):
        try:
            return self.rating[round_id]
        except:
            raise KeyError("Round {} not available.".format(round_id)) from None
        
    def add_rating(self, round_id, rating_value):
        self.rating[round_id] = rating_value 
    
    def get_offensive_rating(self, round_id):
        try:
            return self.offensive_rating[round_id]
        except:
            raise KeyError("Round {} not available.".format(round_id)) from None 

    def add_offensive_rating(self, round_id, offensive_rating_value):
        self.offensive_rating[round_id] = offensive_rating_value 

    def get_defensive_rating(self, round_id):
        try:
            return self.defensive_rating[round_id]
        except:
            raise KeyError("Round {} not available.".format(round_id)) from None 

    def add_defensive_rating(self, round_id, defensive_rating_value):
        self.defensive_rating[round_id] = defensive_rating_value 
            
    def calculate_offensive_rating(self):
        pass
    
    def calculate_defensive_rating(self):
        pass 
