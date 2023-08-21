def score_and_export_vaep():
    
    import pandas as pd
    import joblib

    from vaep.domain.contracts.modelling_data_contract import ModellingDataContract
    from vaep.domain.preprocessing.data_preprocessor import DataPreprocessor
    from vaep.domain.preprocessing.preprocessing import convert_chains_to_schema, calculate_vaep_values
    from vaep.domain.preprocessing.formula import value, offensive_value, defensive_value

    from config import chain_file_path
    from vaep_config import vaep_preprocessor_file_path, vaep_score_model_file_path, vaep_concede_model_file_path, vaep_chain_output_path

    # Load data
    chains = pd.read_csv(chain_file_path)
    print("Chain data loaded.")
    # Processing
    preproc = joblib.load(vaep_preprocessor_file_path)
    chain_features = preproc.transform(chains)
    print("Preprocessing.. Complete.")

    # Load model
    schema_chains = convert_chains_to_schema(chains)
    score_model = joblib.load(vaep_score_model_file_path)
    schema_chains['scores'] = score_model.predict_proba(chain_features, calibrate=True)
    concede_model = joblib.load(vaep_concede_model_file_path)
    schema_chains['concedes'] = concede_model.predict_proba(chain_features, calibrate=True)
    
    # Scoring
    scored_chains = calculate_vaep_values(schema_chains)
    print("Scoring.. complete.")

    # Export data
    scored_chains.to_csv(vaep_chain_output_path, index=False)
    print("Exporting.. complete.")

if __name__ == "__main__":
    
    score_and_export_vaep()