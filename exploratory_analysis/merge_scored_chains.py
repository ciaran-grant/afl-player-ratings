def merge_and_export_scored_chains():

    import pandas as pd

    from config import chain_file_path, scored_chain_file_path
    from expected_threat.xthreat_config import xthreat_chain_output_path
    from vaep.vaep_config import vaep_chain_output_path
    from exp_vaep.exp_vaep_config import exp_vaep_chain_output_path

    chains = pd.read_csv(chain_file_path)

    threat_chains = pd.read_csv(xthreat_chain_output_path)
    vaep_chains = pd.read_csv(vaep_chain_output_path)
    exp_vaep_chains = pd.read_csv(exp_vaep_chain_output_path)

    vaep_chains = vaep_chains.merge(exp_vaep_chains[['match_id', 'chain_number', 'order','xScore', 'exp_scores', 'exp_concedes', 'exp_offensive_value', 'exp_defensive_value', "exp_vaep_value"]], how = "left", on=['match_id', 'chain_number', 'order'])
    chains = chains.merge(vaep_chains[['match_id', 'chain_number', 'order', "overall_seconds", 'action_type', 'outcome_type', 'scores', 'concedes', 'offensive_value', 'defensive_value', "vaep_value", 'exp_scores', 'exp_concedes', 'exp_offensive_value', 'exp_defensive_value', "exp_vaep_value"]], how = "left", left_on = ['Match_ID', 'Chain_Number', 'Order'], right_on=['match_id', 'chain_number', 'order'])

    chains.to_csv(scored_chain_file_path, index=False)
    
if __name__ == "__main__":
    
    merge_scored_chains()