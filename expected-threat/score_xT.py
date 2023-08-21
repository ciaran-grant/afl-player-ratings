import sys
sys.path.append("/Users/ciaran/Documents/Projects/AFL/git-repositories/afl-player-ratings/expected-threat")

from xthreat_config import xthreat_model_file_path, xthreat_chain_output_path
from config import chain_file_path

from processing import *
import xthreat
import numpy as np
import pandas as pd


# Load data
chains = pd.read_csv(chain_file_path)

# Load model
xTModel = xthreat.load_model(xthreat_model_file_path)

# Scoring
scored_chains = score_xTModel(chains, xTModel)

# Export data
scored_chains.to_csv(xthreat_chain_output_path, index=False)
