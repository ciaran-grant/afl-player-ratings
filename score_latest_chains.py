import warnings
warnings.filterwarnings("ignore")

import sys
sys.path.append("/Users/ciaran/Documents/Projects/AFL/git-repositories/afl-player-ratings/expected_threat")
sys.path.append("/Users/ciaran/Documents/Projects/AFL/git-repositories/afl-player-ratings/vaep")
sys.path.append("/Users/ciaran/Documents/Projects/AFL/git-repositories/afl-player-ratings/exp_vaep")
sys.path.append("/Users/ciaran/Documents/Projects/AFL/git-repositories/expected-score-model/")

from expected_threat.score_xT import score_and_export_xT
from vaep.score_vaep import score_and_export_vaep
from exp_vaep.score_exp_vaep import score_and_export_exp_vaep
from exploratory_analysis.merge_scored_chains import merge_and_export_scored_chains

# Expected Threat
print("Scoring xT..")
score_and_export_xT()
print("Scoring xT finished.")

# VAEP
print("Scoring VAEP..")
score_and_export_vaep()
print("Scoring VAEP finished.")

# Expected VAEP
print("Scoring Expected VAEP..")
score_and_export_exp_vaep()
print("Scoring Expected VAEP finished.")

# Merge Chains
print("Merging chains..")
merge_and_export_scored_chains()
print("Merging finished.")
