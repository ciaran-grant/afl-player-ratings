import pandas as pd
from pandera.typing import DataFrame, Series

def _prev(x: pd.Series) -> pd.Series:
    prev_x = x.shift(1)
    prev_x[:1] = x.values[0]
    return prev_x

_samephase_nb = 10

def offensive_value(actions, scores, concedes) -> Series[float]:
    """ Compute the offensive value of each action. 
    
    VAEP defines the offensive value of an action as rthe change in scoring probability before
    and after the action.
    
    Parameters
    ----------
    actions : pd.DataFrame
        The actions of a game
    scores: pd.Series
        The probability of scoring from each corresponding gamestate.
    concedes: pd.Series
        The probability of conceding from each corresponding gamestate.    
    
    Returns
    -------
    pd.Series
        The offensive value of each action.
    
    """
    
    sameteam = _prev(actions['team']) == actions['team']
    prev_scores = _prev(scores) * sameteam + _prev(concedes) * (~sameteam)
    
    # # if the previous action was too long ago, the odds of scoring are now 0
    # toolong_idx = abs(actions['time_seconds'] - _prev(actions['time_seconds'])) - _samephase_nb
    
    # if the previous action was a goal, the chances of scoring are now 0
    prevgoal_idx = (_prev(actions['action_type'] == "Shot")) & (_prev(actions['outcome_type'] == "effective"))
    prev_scores[prevgoal_idx] = 0
    
    return scores - prev_scores

def defensive_value(actions, scores, concedes) -> Series[float]:
    """ Compute the defensive value of each action. 
    
    VAEP defines the defensice value of an action as the change in conceding probability before
    and after the action.
    
    Parameters
    ----------
    actions : pd.DataFrame
        The actions of a game
    scores: pd.Series
        The probability of scoring from each corresponding gamestate.
    concedes: pd.Series
        The probability of conceding from each corresponding gamestate.    
    
    Returns
    -------
    pd.Series
        The offensive value of each action.
    
    """
    
    sameteam = _prev(actions['team']) == actions['team']
    prev_concedes = _prev(concedes) * sameteam + _prev(scores) * (~sameteam)
    
    # # if the previous action was too long ago, the odds of scoring are now 0
    # toolong_idx = abs(actions['time_seconds'] - _prev(actions['time_seconds'])) - _samephase_nb
    
    # if the previous action was a goal, the chances of scoring are now 0
    prevgoal_idx = (_prev(actions['action_type'] == "Shot")) & (_prev(actions['outcome_type'] == "effective"))
    prev_concedes[prevgoal_idx] = 0
    
    return -(concedes - prev_concedes)


def value(actions, scores, concedes):
    
    """ Comptute the offensive, defensive and VAEP value of each action.
    
    The total VAEP value of an action is the difference between that actions offensive and
    defensive value.
    
    Parameters
    ----------
    actions : pd.DataFrame
        The actions of a game
    scores: pd.Series
        The probability of scoring from each corresponding gamestate.
    concedes: pd.Series
        The probability of conceding from each corresponding gamestate.    
    
    Returns
    -------
    pd.DataFrame
        The offensive value, defensive value and vaep_value of each action.
    
    """
    v = pd.DataFrame()
    v['offensive_value'] = offensive_value(actions, scores, concedes)
    v['defensive_value'] = defensive_value(actions, scores, concedes)
    v['vaep_value'] = v['offensive_value'] + v['defensive_value']
    return v