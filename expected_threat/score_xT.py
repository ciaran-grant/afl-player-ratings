def score_and_export_xT():
    
    from xthreat_config import xthreat_model_file_path, xthreat_chain_output_path
    from config import chain_file_path

    from processing import convert_chain_to_spadl, score_xTModel
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

if __name__ == "__main__":
    
    score_and_export_xT()