class Player:
    """ Class for holding information about players. """
    def __init__(self, 
                 name: str, 
                 team_name: str
                 ):
        
        self.name = name
        self.team_name = team_name
        self.rating = {"Initial":0}
        
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
