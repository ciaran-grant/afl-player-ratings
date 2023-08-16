from dataclasses import dataclass

@dataclass
class PositionsContract:
    """ Holds details for defining player position stats in one place.
    """
    
    position_group_list = [
        'Back',
        'Midfield',
        'Forward',
        'Ruck',
        'Interchange'
    ]
    
    position_sub_group_list = [
        'Back-Pocket',
        'Half-Back',
        'Key-Back',
        'Centre',
        'Wing',
        'Forward-Pocket',
        'Half-Forward',
        'Key-Forward',
        'Ruck',
        'Interchange'
    ]
    
    position_list = [
        'Back Pocket Left',
        'Full Back',
        'Back Pocket Right',
        'Half Back Flank Left',
        'Centre Half Back',
        'Half Back Flank Right',
        'Wing Left',
        'Centre',
        'Wing Right',
        'Rover',
        'Ruck Rover',
        'Ruck',
        'Half Forward Flank Left',
        'Centre Half Forward',
        'Half Forward Flank Right',
        'Forward Pocket Left',
        'Full Forward',
        'Forward Pocket Right',
        'Interchange',
        'Substitute']
    
    back_stats = {
        'goal_preventing' : [
            'Defensive_Half_Pressure_Acts',
            'Pressure_Acts',
            'Spoils',
            'Tackles',
            'Clearances',
            'defensive_value',
            'exp_defensive_value'
        ],
        'ball_denial' : [
            'Rebound_50s',
            'Intercepts',
            'xT_prevented',
            'defensive_value',
            'exp_defensive_value'
        ],
        'contest' : [
            'Contested_Marks',
            'Contested_Possessions',
            'Defensive_Contest_Losses',
            'Defensive_One_On_One_Contests',
            'Ground_Ball_Gets',
            'Stoppage_Clearances',
            'Possessions',
            'Uncontested_Possessions'
        ]}