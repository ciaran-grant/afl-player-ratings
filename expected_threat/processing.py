import numpy as np
import pandas as pd
import xthreat

def convert_chain_to_spadl(chains):
    
    xthreat_data = chains.copy()

    xthreat_data = xthreat_data.dropna(subset=['Player'])
    xthreat_data = xthreat_data[~(xthreat_data['Description']=="Kick Into F50")]
    xthreat_data = xthreat_data[~(xthreat_data['Description']=="Goal")]

    xthreat_data['end_x'] = xthreat_data.groupby('Match_ID')['x'].shift(-1).fillna(0)
    xthreat_data['end_y'] = xthreat_data.groupby('Match_ID')['y'].shift(-1).fillna(0)
    
    xthreat_data['Receiver'] = xthreat_data.groupby('Match_ID')['Player'].shift(-1).fillna(0)
    xthreat_data['ReceiverTeam'] = xthreat_data.groupby('Match_ID')['Team'].shift(-1).fillna(0)

    xthreat_data['type_name'] = np.where(xthreat_data['Description'] == "Handball", "Handball",
                                        np.where((xthreat_data['Description'] == 'Kick') & (xthreat_data['Shot_At_Goal']==True), "Shot",
                                                np.where(xthreat_data['Description']=='Kick', "Kick",
                                                            "Carry")))
    xthreat_data['outcome_name'] = (xthreat_data['type_name'] == "Carry") | (xthreat_data['Disposal'] == "effective")
    xthreat_data['goal'] = (xthreat_data['type_name'] == "Shot") & (xthreat_data['Final_State'] == "goal")
    xthreat_data['shoot'] = xthreat_data['type_name'] == "Shot"
    xthreat_data['move'] = xthreat_data['type_name'] != "Shot"

    xthreat_data['Year'] = xthreat_data['Match_ID'].apply(lambda x: int(x[:4]))
    xthreat_data = xthreat_data[['Match_ID', 'Chain_Number', 'Order', 'Year', 'Team', 'Player', 'ReceiverTeam', 'Receiver', 'type_name', 'outcome_name', 'shoot', 'move', 'goal', 'x', 'y', 'end_x', 'end_y']]
    
    return xthreat_data

def score_xTModel(chains, xTModel):
    
    number_of_rows = chains.shape[0]
    
    xthreat_actions = convert_chain_to_spadl(chains)
    
    # xT Created
    move_actions = xthreat.get_successful_move_actions(xthreat_actions)
    move_actions['xT_created'] = xTModel.rate(move_actions)

    # xT Received
    move_unsuccessful_actions = xthreat.get_move_actions(xthreat_actions)
    move_unsuccessful_actions = move_unsuccessful_actions[move_unsuccessful_actions['outcome_name'] == False]
    move_unsuccessful_actions = move_unsuccessful_actions[(move_unsuccessful_actions['Team'] != move_unsuccessful_actions['ReceiverTeam'])]
    move_unsuccessful_actions['outcome_name'] = True
    move_unsuccessful_actions['xT_denied'] = xTModel.rate(move_unsuccessful_actions)
    move_unsuccessful_actions['outcome_name'] = False
    
    # Merge Back
    threat_actions = pd.concat([move_actions, move_unsuccessful_actions], axis=0).sort_values(by=['Match_ID', 'Chain_Number', "Order"])
    
    chains = chains.merge(threat_actions[['Match_ID', 'Chain_Number', 'Order', "ReceiverTeam", "Receiver", "type_name", 'outcome_name', 'shoot', 'move', 'goal', 'end_x', 'end_y', "xT_created", "xT_denied"]], how = "left", on = ['Match_ID', 'Chain_Number', 'Order'])
    assert chains.shape[0] == number_of_rows

    return chains