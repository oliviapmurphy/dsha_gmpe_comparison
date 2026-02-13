from pathlib import Path
import csv
import re
import pandas as pd


def pull_hazard_data(scale_target_type):
    """
    Get the data for psha or dsha for a given scale target type for both site classes b and d
    :param scale_target_type: sle, dbe, or mce
    :return: the hazard and scale type files
    """
    folder = Path('data/final_scales')

    matching_files = [f for f in folder.iterdir() if f.is_file() and scale_target_type.lower() in f.name.lower()]

    return matching_files


def verify_hazard_files(matching_files, site_classes):
    """
    verify that all hazards and scale targets are created, if not error is raised
    :param matching_files: files that match the hazard and scale target
    :param site_classes: B and D
    :return: verification to proceed
    """
    results = {site: {"PSHA": None, "DSHA": None}  for site in site_classes}

    for file in matching_files:
        for site in site_classes:
            if site.lower() in file.name.lower():
                if 'psha' in file.name.lower():
                    results[site]["PSHA"] = file.name
                elif 'dsha' in file.name.lower():
                    results[site]["DSHA"] = file.name

    missing = []
    for site in site_classes:
        if not (results[site]["PSHA"] or results[site]["DSHA"]):
            missing.append(f'{site}')

    if missing:
        missing_str = ', '.join(missing)
        raise FileNotFoundError(f'Missing PSHA or DSHA files for : {missing_str}')

    print("✅ All PSHA and DSHA files found for every site and scale!")
    return True


def get_scale_level_files(matching_files, hazard_type):
    results = []
    hazard = None
    for file in matching_files:
        if 'psha' in file.name.lower():
            hazard = 'psha'
        if 'dsha' in file.name.lower():
            hazard = 'dsha'

        if hazard == hazard_type:
            results.append(file)

    return results


def combined_site_class_results(site):
    folder= Path(f'search_results/site_class_{site.lower()}')
    all_dfs = []

    for file_path in folder.glob('*.csv'):
        rows = []
        prev_blank = False
        with open(file_path, 'r', newline='') as f:
            for _ in range(32):
                next(f)

            reader = csv.reader(f)

            for row in reader:
                row = [cell.strip() for cell in row]

                # Check for blank row
                if all(cell=='' for cell in row):
                    prev_blank = True
                    continue

                # Stop if previous row was blank and first cell starts with "These"
                if prev_blank and row[0].startswith("These"):
                    break

                rows.append(row)
                prev_blank = False

        header=rows[0]
        df = pd.DataFrame(rows[1:], columns=header)

        df.columns = df.columns.str.strip()

        # Check which columns actually exist before filtering
        expected_cols = [
            'Earthquake Name', 'Year', 'Station Name', 'Magnitude','Mechanism', 'Horizontal-1 Acc. Filename', 'Horizontal-2 Acc. Filename']
        existing_cols = [c for c in expected_cols if c in df.columns]
        df = df.loc[:, existing_cols]

        all_dfs.append(df)

    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_df.to_csv(f'search_results/complete_site_class_{site.lower()}.csv', index=False)
    print(f'All site class {site.upper()} search results have been successfully combined')


def list_site_hazard_scale_files(hazard_files):
    site_b_files = []
    site_d_files = []
    for file in hazard_files:
            if '_b.' in file.name.lower():
                site_b_files.append(file)
            if '_d.' in file.name.lower():
                site_d_files.append(file)
    return site_b_files, site_d_files


def create_input_gm_model_file(scale_target_type, smf_model_location):
    site_classes = ['B', 'D']
    hazard_types = ['psha', 'dsha']

    matching_files = pull_hazard_data(scale_target_type)
    verify_hazard_files(matching_files, site_classes)

    for hazard in hazard_types:
        hazard_files = get_scale_level_files(matching_files, hazard) # look at psha or dsha
        site_b_files, site_d_files = list_site_hazard_scale_files(hazard_files)
        site_specific_dfs = []
        for site in site_classes:
            search_file = Path(f'search_results/complete_site_class_{site.lower()}.csv')
            if not search_file.exists():
                combined_site_class_results(site)

            search_results_df = pd.read_csv(search_file)

            scaled_info_file_name = site_b_files[0] if site == 'B' else site_d_files[0]
            scaled_df = pd.read_csv(scaled_info_file_name, skiprows=4, header=0, on_bad_lines='skip')
            scaled_df = scaled_df.rename(columns=lambda x: x.strip())
            scaled_df.columns = scaled_df.columns.str.strip()
            scaled_df = scaled_df.loc[:,['Name', 'Scale', 'Details']] # data frame with only the event name, scale factor, and details

            # --- Apply across all rows in scaled_df ---
            matches = scaled_df.apply(find_best_match_with_direction, axis=1, search_df=search_results_df)
            matches_df = pd.DataFrame(matches.tolist())

            # --- Combine back with scaled_df ---
            scaled_df_matched = pd.concat([scaled_df, matches_df], axis=1) # combination of the scaled results and the file it corresponds too

            site_class_df = scaled_df_matched.drop(columns=['Details', "Horizontal-1", "Horizontal-2"]) # cleaner data

            site_class_df['Site'] = site

            site_specific_dfs.append(site_class_df)

        hazard_df = pd.concat(site_specific_dfs)
        hazard_df = hazard_df.rename(columns={
            'Name': 'GM Title',
            'Scale': 'Scale Factor',
            'Chosen File': 'GM file',
            'Site': "Site Class"
        })
        hazard_df=hazard_df[['GM Title','Site Class', 'Scale Factor', 'GM file']]

        file_name = f'{hazard}_{scale_target_type}_motion_suite.csv'
        hazard_df.to_csv(file_name, index=False)
        hazard_df.to_csv(rf'{smf_model_location}\{file_name}', index=False)


def sanitize_name(s):
    return re.sub(r'[^A-Za-z0-9]', '', s).lower()


def find_best_match_with_direction(row, search_df):
    columns = row['Name'].split("\\")
    quake = sanitize_name(columns[0])
    station = sanitize_name(columns[1])
    direction = sanitize_name(columns[-1])

    # First try exact match
    matching_row = search_df[
        (search_df["Earthquake Name"].map(sanitize_name) == quake) &
        (search_df["Station Name"].map(sanitize_name) == station)
        ]

    # If no exact matches, try partial startswith match
    if matching_row.empty:
        quake_matches = search_df["Earthquake Name"].map(sanitize_name).str.startswith(quake)
        station_matches = search_df["Station Name"].map(sanitize_name).str.startswith(station)
        matching_row = search_df[quake_matches & station_matches]

    # If still no matches, raise error
    if matching_row.empty:
        raise LookupError(f"No match found for {quake} / {station}")

    horiz1 = matching_row["Horizontal-1 Acc. Filename"].values[0]
    horiz2 = matching_row["Horizontal-2 Acc. Filename"].values[0]
    chosen_file = horiz1 if sanitize_name(horiz1).endswith(f"{direction}at2") else horiz2
    return {
        "Chosen File": chosen_file,
        "Horizontal-1": horiz1,
        "Horizontal-2": horiz2
    }
