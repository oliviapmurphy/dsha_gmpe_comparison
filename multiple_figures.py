from pathlib import Path


from create_med_sig_data import create_hazard_site_type_data
from create_gm_input_file import list_site_hazard_scale_files


def find_plot_data_files(input_folder, hazard_type, scale):
    file_location = Path(input_folder)

    matching_files = [f for f in file_location.iterdir()
                      if f.is_file()
                      and scale.lower() in f.name.lower()
                      and hazard_type.lower() in f.name.lower()]

    return matching_files


def create_multi_hazard_site_type_data(plot_files, hazard_type, site, scale):
    site_b_files, site_d_files = list_site_hazard_scale_files(hazard_files=plot_files)

    site_files = site_b_files[0] if site =="B" else site_d_files[0]
    create_hazard_site_type_data(file_name=site_files,hazard_type=hazard_type, site_class=site, scale_target_type=scale)
