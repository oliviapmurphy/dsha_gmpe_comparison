from create_plot import create_dsha_sigma_plot

# for single plot still input information in list format ['x']
site_classes = ['B', 'D']
# Only does MCE

show_building_period =True
building_periods = [0.5, 1.85]

# change to file location on personal device (rf'{copy location}')
smf_model_location = rf'C:\Users\livyl\development\openseespy_smf_model\ground_motions\motion_suites'

create_dsha_sigma_plot(site_classes, show_building_period, building_periods, plot_gm_records=False)