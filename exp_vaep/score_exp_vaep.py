import pandas as pd
import joblib

import sys
sys.path.append("/Users/ciaran/Documents/Projects/AFL/git-repositories/afl-player-ratings/exp_vaep")
sys.path.append("/Users/ciaran/Documents/Projects/AFL/git-repositories/expected-score-model/")

from exp_vaep.domain.contracts.modelling_data_contract import ModellingDataContract
from exp_vaep.domain.preprocessing.data_preprocessor import DataPreprocessor
from exp_vaep.domain.preprocessing.preprocessing import *
from exp_vaep.domain.preprocessing.formula import *

from config import chain_file_path
from exp_vaep_config import *

expected_scores_path_dict = {
    'set':{'goal':{'preprocessor':exp_goal_set_preprocessor_file_path,
                   'model':exp_goal_set_model_file_path},
           'behind':{'preprocessor':exp_behind_set_preprocessor_file_path,
                     'model':exp_behind_set_model_file_path},
           'miss':{'preprocessor':exp_miss_set_preprocessor_file_path,
                   'model':exp_miss_set_model_file_path}},
     'open':{'goal':{'preprocessor':exp_goal_open_preprocessor_file_path,
                    'model':exp_goal_open_model_file_path},
           'behind':{'preprocessor':exp_behind_open_preprocessor_file_path,
                     'model':exp_behind_open_model_file_path},
           'miss':{'preprocessor':exp_miss_open_preprocessor_file_path,
                   'model':exp_miss_open_model_file_path}}
}


# Load data
chains = pd.read_csv(chain_file_path)

# Processing
preproc = joblib.load(exp_vaep_preprocessor_file_path)
chain_features = preproc.transform(chains)

# Load model
chains = get_expected_scores(chains, expected_scores_path_dict)
schema_chains = convert_chains_to_schema(chains)
exp_score_model = joblib.load(exp_vaep_score_model_file_path)
schema_chains['exp_scores'] = np.clip(exp_score_model.predict(chain_features), 0, 6)
exp_concede_model = joblib.load(exp_vaep_concede_model_file_path)
schema_chains['exp_concedes'] = np.clip(exp_concede_model.predict(chain_features), 0, 6)

# Scoring
scored_chains = calculate_exp_vaep_values(schema_chains)

# Export data
scored_chains.to_csv(exp_vaep_chain_output_path, index=False)