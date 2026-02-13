from pathlib import Path
from run_script import run_creation_process

# To get multiple targets, sites, and hazards together input False
single_plot = True

# for single plot still input information in list format ['x']
input_folder = 'data/final_scales'
hazard_types = ['psha', 'dsha']
site_classes = ['B', 'D']
scale_target_types = ['mce']

test_end = ('e-1')
file_name = Path(f'data/final_scales/{hazard_types[0]}_{scale_target_types[0]}_site_class_{site_classes[0]}.csv')
# file_name = Path(f'data/{hazard_type}_test/{hazard_types[0]}_{site_classes[0].lower()}_{scale_target_types[0]}_{test_end}.csv')

show_building_period =True
building_periods = [0.5, 1.5]

# only for single plot
gm_breakdown = False # best to alter colors of GM to specific collapse cases, needs manual updating to use

# creates a spectra with all scale_target_types color coated for site class B and D for psha and dsha without plotting the scaled GM
create_target_spectra = False

# creates the format file needed to use openseespy_smf_model
# all site classes and hazards must be finalized
create_input_gm_file = False

# change to file location on personal device
smf_model_location = rf'C:\Users\livyl\development\openseespy_smf_model\ground_motions\motion_suites'

run_creation_process(file_name=file_name,
                     hazard_types=hazard_types,
                     site_classes=site_classes,
                     scale_target_types=scale_target_types,
                     show_building_period=show_building_period,
                     building_periods=building_periods,
                     create_input_gm_file=create_input_gm_file,
                     input_folder=input_folder,
                     single_plot=single_plot,
                     create_target_spectra=create_target_spectra,
                     gm_breakdown=gm_breakdown,
                     smf_model_location=smf_model_location)