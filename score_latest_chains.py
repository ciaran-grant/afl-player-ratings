import sys
sys.path.append("/Users/ciaran/Documents/Projects/AFL/git-repositories/afl-player-ratings/expected_threat")
sys.path.append("/Users/ciaran/Documents/Projects/AFL/git-repositories/afl-player-ratings/vaep")
sys.path.append("/Users/ciaran/Documents/Projects/AFL/git-repositories/afl-player-ratings/exp_vaep")
sys.path.append("/Users/ciaran/Documents/Projects/AFL/git-repositories/expected-score-model/")

from expected_threat.score_xT import score_and_export_xT
from vaep.score_vaep import score_and_export_vaep
from exp_vaep.score_exp_vaep import score_and_export_exp_vaep

# Expected Threat
score_and_export_xT()
# VAEP
score_and_export_vaep()
# Expected VAEP
score_and_export_exp_vaep()
# Merge Data