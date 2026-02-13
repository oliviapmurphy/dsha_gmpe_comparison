import numpy as np
import pandas as pd
import os
from pathlib import Path

def calculate_sigma_bounds(df_raw, s_a, sig, type):
    plus_sigma = 'scaled_plus_sigma' if type == 'scaled' else 'target_plus_sigma'
    minus_sigma = 'scaled_minus_sigma' if type == 'scaled' else 'target_minus_sigma'

    df_raw[plus_sigma] = s_a * np.exp(sig)
    df_raw[minus_sigma] = s_a * np.exp(-sig)

    return df_raw


def obtain_target_spectra(hazard_type, scale_target, site_class):
    df_target = pd.read_csv(f'target_response_spectra/{hazard_type}_{site_class.lower()}_{scale_target}_target.csv')
    s_a = df_target['Sa (g)'].values
    if hazard_type == 'dsha':
        sig = df_target['Sigma Ln'].values

        df_sigma = calculate_sigma_bounds(df_target, s_a, sig, type='target')
        df_target = df_sigma.drop(columns=['Period (s)','Sigma Ln'])

    return df_target


def create_hazard_site_type_data(file_name, hazard_type, site_class, scale_target_type):
    df_raw = pd.read_csv(file_name, skiprows=26)

    s_a = df_raw['Median Sa (g)'].values
    sig = df_raw['Sigma_ln'].values

    calculate_sigma_bounds(df_raw, s_a, sig, type='scaled')

    df_target = obtain_target_spectra(hazard_type, scale_target_type, site_class)

    df_complete = pd.concat([df_raw, df_target], axis=1)

    df_complete = df_complete.drop(columns=['Sigma_ln'])

    output_folder = Path('processed_data')
    os.makedirs(output_folder, exist_ok=True)

    file_name = file_name.stem

    df_complete.to_csv(f'{output_folder}/{file_name}.csv', index=False)

    return df_complete
