import pandas as pd
import numpy as np

chains = pd.read_csv("/Users/ciaran/Documents/Projects/AFL/data/scored_match_chains_v2.csv")
player_stats = pd.read_csv("/Users/ciaran/Documents/Projects/AFL/data/player_stats.csv")

def get_player_totals_by_match(chains):
    return chains.groupby(['Match_ID', 'Player', 'Team'])[['xScore', 'xT_created', 'xT_denied', 'vaep_value', 'offensive_value', 'defensive_value', 'exp_vaep_value', 'exp_offensive_value', 'exp_defensive_value']].sum().reset_index().sort_values(by=['Match_ID', "Player", "Team"])

player_value = get_player_totals_by_match(chains)
player_stats = player_stats.merge(player_value, how = "left", on = ['Match_ID', 'Player', 'Team'])

def get_receiver_totals_by_match(chains):
    
    return chains.groupby(['Match_ID', 'Receiver'])[['xT_created', 'xT_denied', 'vaep_value', 'offensive_value', 'defensive_value', 'exp_vaep_value', 'exp_offensive_value', 'exp_defensive_value']].sum().reset_index().sort_values(by=['Match_ID', "Receiver"])

receiver_value = get_receiver_totals_by_match(chains)
receiver_value = receiver_value.rename(columns = {
    "Receiver":"Player",
    "xT_created":"xT_received",
    "xT_denied":"xT_prevented",
    "vaep_value":"vaep_value_received",
    "exp_vaep_value":"exp_vaep_value_received"})

player_stats = player_stats.merge(receiver_value[['Match_ID', 'Player', 'xT_received', 'xT_prevented', 'vaep_value_received', 'exp_vaep_value_received']], how = "left", on = ['Match_ID', 'Player'])

player_stats.to_csv("/Users/ciaran/Documents/Projects/AFL/data/scored_player_stats_v2.csv", index=False)