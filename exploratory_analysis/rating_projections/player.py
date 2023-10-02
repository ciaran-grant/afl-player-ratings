class Player:
    """ Class for holding information about players. """
    def __init__(self, 
                 name: str, 
                 team_name: str,
                 season: int = None,
                 round_id: str = None,
                 rating: dict = {"Initial":0}):
        
        self.name = name
        self.team_name = team_name
        self.season = season
        self.round_id = round_id
        self.rating = rating
        
    def get_name(self):
        return self.name
    
    def get_team(self):
        return self.team_name
    
    def get_rating(self, round_id):
        try:
            return self.rating[round_id]
        except:
            raise KeyError("Round {} not available.".format(round_id)) from None
            
    def add_rating(self, round_id, rating_value):
        self.rating[round_id] = rating_value 
