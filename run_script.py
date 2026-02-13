from create_med_sig_data import create_hazard_site_type_data
from create_plot import create_single_figure, create_complete_scaling_figure, plot_eq_levels
from create_gm_input_file import create_input_gm_model_file


def run_creation_process(file_name, hazard_types, site_classes, scale_target_types, show_building_period,
                         building_periods, create_input_gm_file, input_folder,
                         single_plot, create_target_spectra, gm_breakdown, smf_model_location):

    if single_plot:
        hazard_type = hazard_types[0]
        site_class = site_classes[0]
        scale_target_type = scale_target_types[0]
        create_hazard_site_type_data(file_name, hazard_type, site_class, scale_target_type)
        create_single_figure(file_name, hazard_type, site_class, show_building_period, building_periods, scale_target_type, gm_breakdown)
    else:
        create_complete_scaling_figure(hazard_types, site_classes, scale_target_types, input_folder, show_building_period, building_periods)

    if create_input_gm_file:
        for scale in scale_target_types:
            create_input_gm_model_file(scale, smf_model_location)

    if create_target_spectra:
        plot_eq_levels(hazard_types, scale_target_types, site_classes)
