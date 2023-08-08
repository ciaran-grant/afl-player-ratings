from dataclasses import dataclass

@dataclass
class ModellingDataContract:
    """ Holds details for defining modelling terms in a single place.
    """
    
    ID_COL = "match_ID"
    RESPONSE_SCORES = "exp_scores"
    RESPONSE_CONCEDES = "exp_concedes"
    TRAIN_TEST_SPLIT_COL = "ModellingFilter"

           
    # Scores
    feature_list_scores = [
        'type_Kick_a0',
        'type_Handball_a0',
        'type_Carry_a0',
        'type_Uncontested Mark_a0',
        'type_Contested Mark_a0',
        'type_Loose Ball Get_a0',
        'type_Hard Ball Get_a0',
        'type_Spoil_a0',
        'type_Gather_a0',
        'type_Free For_a0',
        'type_Knock On_a0',
        'type_Shot_a0',
        'type_Tackle_a0',
        'type_Error_a0',
        'outcome_effective_a0',
        'outcome_ineffective_a0',
        'outcome_clanger_a0',
        'type_Kick_outcome_effective_a0',
        'type_Kick_outcome_ineffective_a0',
        'type_Kick_outcome_clanger_a0',
        'type_Handball_outcome_effective_a0',
        'type_Handball_outcome_ineffective_a0',
        'type_Handball_outcome_clanger_a0',
        'type_Carry_outcome_effective_a0',
        'type_Carry_outcome_ineffective_a0',
        'type_Carry_outcome_clanger_a0',
        'type_Uncontested Mark_outcome_effective_a0',
        'type_Uncontested Mark_outcome_ineffective_a0',
        'type_Uncontested Mark_outcome_clanger_a0',
        'type_Contested Mark_outcome_effective_a0',
        'type_Contested Mark_outcome_ineffective_a0',
        'type_Contested Mark_outcome_clanger_a0',
        'type_Loose Ball Get_outcome_effective_a0',
        'type_Loose Ball Get_outcome_ineffective_a0',
        'type_Loose Ball Get_outcome_clanger_a0',
        'type_Hard Ball Get_outcome_effective_a0',
        'type_Hard Ball Get_outcome_ineffective_a0',
        'type_Hard Ball Get_outcome_clanger_a0',
        'type_Spoil_outcome_effective_a0',
        'type_Spoil_outcome_ineffective_a0',
        'type_Spoil_outcome_clanger_a0',
        'type_Gather_outcome_effective_a0',
        'type_Gather_outcome_ineffective_a0',
        'type_Gather_outcome_clanger_a0',
        'type_Free For_outcome_effective_a0',
        'type_Free For_outcome_ineffective_a0',
        'type_Free For_outcome_clanger_a0',
        'type_Knock On_outcome_effective_a0',
        'type_Knock On_outcome_ineffective_a0',
        'type_Knock On_outcome_clanger_a0',
        'type_Shot_outcome_effective_a0',
        'type_Shot_outcome_ineffective_a0',
        'type_Shot_outcome_clanger_a0',
        'type_Tackle_outcome_effective_a0',
        'type_Tackle_outcome_ineffective_a0',
        'type_Tackle_outcome_clanger_a0',
        'type_Error_outcome_effective_a0',
        'type_Error_outcome_ineffective_a0',
        'type_Error_outcome_clanger_a0',
        'quarter_a0',
        'quarter_seconds_a0',
        'overall_seconds_a0',
        'start_x_a0',
        'start_y_a0',
        'end_x_a0',
        'end_y_a0',
        'dx_a0',
        'dy_a0',
        'movement_a0',
        'type_Kick_a1',
        'type_Handball_a1',
        'type_Carry_a1',
        'type_Uncontested Mark_a1',
        'type_Contested Mark_a1',
        'type_Loose Ball Get_a1',
        'type_Hard Ball Get_a1',
        'type_Spoil_a1',
        'type_Gather_a1',
        'type_Free For_a1',
        'type_Knock On_a1',
        'type_Shot_a1',
        'type_Tackle_a1',
        'type_Error_a1',
        'outcome_effective_a1',
        'outcome_ineffective_a1',
        'outcome_clanger_a1',
        'type_Kick_outcome_effective_a1',
        'type_Kick_outcome_ineffective_a1',
        'type_Kick_outcome_clanger_a1',
        'type_Handball_outcome_effective_a1',
        'type_Handball_outcome_ineffective_a1',
        'type_Handball_outcome_clanger_a1',
        'type_Carry_outcome_effective_a1',
        'type_Carry_outcome_ineffective_a1',
        'type_Carry_outcome_clanger_a1',
        'type_Uncontested Mark_outcome_effective_a1',
        'type_Uncontested Mark_outcome_ineffective_a1',
        'type_Uncontested Mark_outcome_clanger_a1',
        'type_Contested Mark_outcome_effective_a1',
        'type_Contested Mark_outcome_ineffective_a1',
        'type_Contested Mark_outcome_clanger_a1',
        'type_Loose Ball Get_outcome_effective_a1',
        'type_Loose Ball Get_outcome_ineffective_a1',
        'type_Loose Ball Get_outcome_clanger_a1',
        'type_Hard Ball Get_outcome_effective_a1',
        'type_Hard Ball Get_outcome_ineffective_a1',
        'type_Hard Ball Get_outcome_clanger_a1',
        'type_Spoil_outcome_effective_a1',
        'type_Spoil_outcome_ineffective_a1',
        'type_Spoil_outcome_clanger_a1',
        'type_Gather_outcome_effective_a1',
        'type_Gather_outcome_ineffective_a1',
        'type_Gather_outcome_clanger_a1',
        'type_Free For_outcome_effective_a1',
        'type_Free For_outcome_ineffective_a1',
        'type_Free For_outcome_clanger_a1',
        'type_Knock On_outcome_effective_a1',
        'type_Knock On_outcome_ineffective_a1',
        'type_Knock On_outcome_clanger_a1',
        'type_Shot_outcome_effective_a1',
        'type_Shot_outcome_ineffective_a1',
        'type_Shot_outcome_clanger_a1',
        'type_Tackle_outcome_effective_a1',
        'type_Tackle_outcome_ineffective_a1',
        'type_Tackle_outcome_clanger_a1',
        'type_Error_outcome_effective_a1',
        'type_Error_outcome_ineffective_a1',
        'type_Error_outcome_clanger_a1',
        'quarter_a1',
        'quarter_seconds_a1',
        'overall_seconds_a1',
        'start_x_a1',
        'start_y_a1',
        'end_x_a1',
        'end_y_a1',
        'dx_a1',
        'dy_a1',
        'movement_a1',
        'type_Kick_a2',
        'type_Handball_a2',
        'type_Carry_a2',
        'type_Uncontested Mark_a2',
        'type_Contested Mark_a2',
        'type_Loose Ball Get_a2',
        'type_Hard Ball Get_a2',
        'type_Spoil_a2',
        'type_Gather_a2',
        'type_Free For_a2',
        'type_Knock On_a2',
        'type_Shot_a2',
        'type_Tackle_a2',
        'type_Error_a2',
        'outcome_effective_a2',
        'outcome_ineffective_a2',
        'outcome_clanger_a2',
        'type_Kick_outcome_effective_a2',
        'type_Kick_outcome_ineffective_a2',
        'type_Kick_outcome_clanger_a2',
        'type_Handball_outcome_effective_a2',
        'type_Handball_outcome_ineffective_a2',
        'type_Handball_outcome_clanger_a2',
        'type_Carry_outcome_effective_a2',
        'type_Carry_outcome_ineffective_a2',
        'type_Carry_outcome_clanger_a2',
        'type_Uncontested Mark_outcome_effective_a2',
        'type_Uncontested Mark_outcome_ineffective_a2',
        'type_Uncontested Mark_outcome_clanger_a2',
        'type_Contested Mark_outcome_effective_a2',
        'type_Contested Mark_outcome_ineffective_a2',
        'type_Contested Mark_outcome_clanger_a2',
        'type_Loose Ball Get_outcome_effective_a2',
        'type_Loose Ball Get_outcome_ineffective_a2',
        'type_Loose Ball Get_outcome_clanger_a2',
        'type_Hard Ball Get_outcome_effective_a2',
        'type_Hard Ball Get_outcome_ineffective_a2',
        'type_Hard Ball Get_outcome_clanger_a2',
        'type_Spoil_outcome_effective_a2',
        'type_Spoil_outcome_ineffective_a2',
        'type_Spoil_outcome_clanger_a2',
        'type_Gather_outcome_effective_a2',
        'type_Gather_outcome_ineffective_a2',
        'type_Gather_outcome_clanger_a2',
        'type_Free For_outcome_effective_a2',
        'type_Free For_outcome_ineffective_a2',
        'type_Free For_outcome_clanger_a2',
        'type_Knock On_outcome_effective_a2',
        'type_Knock On_outcome_ineffective_a2',
        'type_Knock On_outcome_clanger_a2',
        'type_Shot_outcome_effective_a2',
        'type_Shot_outcome_ineffective_a2',
        'type_Shot_outcome_clanger_a2',
        'type_Tackle_outcome_effective_a2',
        'type_Tackle_outcome_ineffective_a2',
        'type_Tackle_outcome_clanger_a2',
        'type_Error_outcome_effective_a2',
        'type_Error_outcome_ineffective_a2',
        'type_Error_outcome_clanger_a2',
        'quarter_a2',
        'quarter_seconds_a2',
        'overall_seconds_a2',
        'start_x_a2',
        'start_y_a2',
        'end_x_a2',
        'end_y_a2',
        'dx_a2',
        'dy_a2',
        'movement_a2',
        'team_1',
        'team_2',
        'time_delta1',
        'time_delta2',
        'dx_a01',
        'dy_a01',
        'move_a01',
        'dx_a02',
        'dy_a02',
        'move_a02',
        'goalscore_team',
        'goalscore_opponent',
        'goalscore_diff'
    ]
    monotone_constraints_scores = {}
    
    # Concedes
    feature_list_concedes = []
    monotone_constraints_concedes = {}    