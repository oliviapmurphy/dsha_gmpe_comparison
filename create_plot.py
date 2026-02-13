import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
import pandas as pd
from pathlib import Path
import os
import math
import matplotlib.ticker as mticker


from multiple_figures import find_plot_data_files, create_multi_hazard_site_type_data

x_axis_label = 'Period (s)'

def plot_site_class_spectra(file_name, hazard_type, spectra_type, site_class, ax):
    """
    Function to plot the target and scaled response spectra and median +/- sigma for the suites
    :param file_name:
    :param hazard_type:
    :param spectra_type:
    :param site_class:
    :param ax:
    :return:
    """
    color_styles = {
        'B_scaled': {'color': '#202c59'},
        'B_target': {'color': '#2086D5'},
        'D_scaled': {'color': '#9D1506'},
        'D_target': {'color': '#DC1826'}
    }

    line_styles = {
        'median' : {'linewidth': 1.5},
        'sigma' : {'linewidth': 1.5, 'linestyle': '--'},
    }

    zorder = 2 if site_class == 'B' else 1

    df = pd.read_csv(f'processed_data/{file_name}.csv')

    spectra_plot = 'Median Sa (g)' if spectra_type == 'scaled' else 'Sa (g)'
    ax.plot(df[x_axis_label], df[spectra_plot], label=f'Site Class {site_class} {spectra_type.capitalize()}', linewidth=line_styles['median']['linewidth'], color=color_styles[f'{site_class}_{spectra_type}']['color'], zorder=zorder)
    if hazard_type == 'psha' and spectra_type == 'target':
        pass
    else:
        plus_sigma = 'scaled_plus_sigma'  if spectra_type == 'scaled' else 'target_plus_sigma'
        minus_sigma = 'scaled_minus_sigma' if spectra_type == 'scaled' else 'target_minus_sigma'
        ax.plot(df[x_axis_label], df[plus_sigma], linewidth=line_styles['sigma']['linewidth'], linestyle=line_styles['sigma']['linestyle'],color=color_styles[f'{site_class}_{spectra_type}']['color'], zorder=zorder)
        ax.plot(df[x_axis_label], df[minus_sigma], linewidth=line_styles['sigma']['linewidth'],
                linestyle=line_styles['sigma']['linestyle'], color=color_styles[f'{site_class}_{spectra_type}']['color'], zorder=zorder)


def plot_gm_individually(file_name, ax):
    df = pd.read_csv(f'processed_data/{file_name}.csv')
    x_axis = df.iloc[:, 0]
    gm_columns = df.columns[2:22]
    colors = [
        "#EE2677",  # Chi-Chi_Taiwan-03_TCU076_N (neon pink)
        "#d3d3d3",  # --
        "#d3d3d3",  # --
        "#DF2935",  # Chi-Chi_Taiwan_TCU089_E (red)
        "#731DD8",  # Chi-Chi_Taiwan_TCU089_N (mauve)
        "#B4E33D",  # Chi-Chi_Taiwan_TCU138_W (yellow green)
        "#d3d3d3",  # --
        "#17becf",  # Chuetsu-oki_Sawa_Mizuguti_Tokamachi_EW (cyan)
        "#1F01B9",  # Hector_Mine_Hector_0 (true azure)
        "#08A045",  # Iwate_AKT019_EW (green)
        "#FF8484",  # Iwate_IWT010_EW (grapefruit pink)
        "#1EFFBC",  # Iwate_IWT010_NS (tropical mint)
        "#d3d3d3",  # --
        "#d3d3d3",  # --
        "#d3d3d3",  # --
        "#004BA8",  # Manjil_Iran_Abbar_L (cobalt blue)
        "#d3d3d3",  # --
        "#d3d3d3",  # --
        "#d3d3d3",  # --
        "#d3d3d3",  # --
    ]
    for i, gm in enumerate(gm_columns):
        gm_color = colors[i%20]
        z_order = -1 if gm_color == '#d3d3d3' else 1
        ax.plot(x_axis, df[gm], color=gm_color, label=gm, linewidth=2.0, zorder=z_order, alpha=0.9)


def plot_gm_suites(file_name, site_class, ax):
    color_styles = {
        'B' : {'color': '#A0B0C6'},
        'D' : {'color': '#F7B7B6'}
    }

    df = pd.read_csv(f'processed_data/{file_name}.csv')

    x_axis = df.iloc[:,0]
    gm_columns = df.columns[2:3+20]

    color = '#d3d3d3'

    for gm in gm_columns:
        ax.plot(x_axis, df[gm], color=color_styles[f'{site_class}']['color'], linewidth=1.0, zorder=0, alpha=0.6)


def plot_setup():
    plt.rcParams.update({
        "font.family": "times new roman",
        "font.size": "13",

        # Axis Labels
        'axes.edgecolor': 'black',
        "axes.labelsize": "14",
        "axes.labelweight": "bold",

        # Axis tick labels
        "xtick.labelsize": "11",
        "ytick.labelsize": "11",

        # Legend
        "legend.fontsize": "11",
        "legend.edgecolor": "black",
        "legend.borderpad": 0.2,
        "legend.labelspacing": 0.2,
        "legend.handletextpad": 0.5
    })


def input_information():
    output_folder = Path(f'figures')
    os.makedirs(output_folder, exist_ok=True)
    spectra_types = ['target', 'scaled']
    return output_folder, spectra_types


def format_plot(ax):
    # Make all edges around the figure black
    for spine in ax.spines.values():
        spine.set_edgecolor('black')
        spine.set_linewidth(1.5)

    ax.grid(False)
    ax.margins(x=0, y=0)

    ax.set_xlabel('Period (s)')
    ax.set_ylabel('Spectral Acceleration (g)')

    ax.set_xlim(0, 5.0)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f'))

    # Build legend
    label = r'Median $\pm \sigma$'
    handles, labels = ax.get_legend_handles_labels()
    sigma_proxy = Line2D([0], [0], color='black', linestyle='--', linewidth=1.25, label=label)
    handles.append(sigma_proxy)
    labels.append(label)

    ax.legend(handles, labels)


def create_single_figure(file_name, hazard_type, site_class, show_building_period, building_periods, scale_target_type, gm_breakdown):
    plot_setup()
    output_folder, spectra_types = input_information()
    file_name = file_name.stem

    fig_size = (8, 4.5) if gm_breakdown else (5, 3.5)
    fig, axes = plt.subplots(1, 1, figsize=fig_size, constrained_layout=True)
    fig.set_constrained_layout_pads(w_pad=.2, h_pad=.2)
    if gm_breakdown:
        plot_gm_individually(file_name, axes)
    else:
        plot_gm_suites(file_name, site_class, ax=axes)
    if gm_breakdown:
        pass
    else:
        for spectra_type in spectra_types:
            plot_site_class_spectra(file_name, hazard_type, spectra_type, site_class, ax=axes)
    # if show_building_period:
    #     for period in building_periods:
    #         axes.axvline(period, color='k', linestyle=':')

    if show_building_period:
        axes.axvspan(building_periods[0], building_periods[-1], alpha=0.55, facecolor='#FECE85',
                   label='Design Period Range',
                   zorder=-1)

    y_max = get_y_max(file_name, hazard_type)

    axes.set_yticks(np.linspace(0, y_max, 5))
    axes.set_ylim(0, y_max)
    format_plot(ax=axes)

    single_plot_folder = f'{output_folder}/{hazard_type}_{site_class}_{scale_target_type}'
    os.makedirs(single_plot_folder, exist_ok=True)

    if gm_breakdown:
        output_name = f'{single_plot_folder}/{file_name}_breakdown.png'
        axes.legend(fontsize='8')
        axes.set_xlim(0, 3)
    else:
        output_name = f'{single_plot_folder}/{file_name}.png'

    plt.savefig(output_name, dpi=300)


def create_complete_scaling_figure(hazard_types, site_classes, scale_target_types, input_folder, show_building_period, building_periods):
    plot_setup()
    output_folder, spectra_types = input_information()

    fig, axes = plt.subplots(
        nrows=len(scale_target_types),
        ncols=len(hazard_types),
        figsize=(8, 3 * len(scale_target_types)),
        constrained_layout=True)

    fig.set_constrained_layout_pads(w_pad=.15, h_pad=.125)

    mce_ticks = [0.0,1.6, 3.1, 4.7, 6.2]
    dbe_ticks = [0.0, 1.0, 2.0, 3.0, 4.0]
    sle_ticks = [0.0, 0.2, 0.4, 0.6, 0.8]

    tick_list = [sle_ticks, dbe_ticks, mce_ticks]

    for i, scale in enumerate(scale_target_types):
        y_max_list = []
        for j, hazard_type in enumerate(hazard_types):
            ax = axes[i, j] if len(scale_target_types) > 1 else axes[j]
            plot_files = find_plot_data_files(input_folder, hazard_type, scale)
            for site_class in site_classes:
                create_multi_hazard_site_type_data(plot_files, hazard_type, site_class, scale)
                file_name = f"{hazard_type}_{scale}_site_class_{site_class}"
                y_max = get_y_max(file_name, hazard_type)
                y_max_list.append(y_max)
                plot_gm_suites(file_name, site_class, ax)

                for spectra_type in spectra_types:
                    plot_site_class_spectra(file_name, hazard_type, spectra_type, site_class, ax)

            if show_building_period:
                ax.axvspan(building_periods[0], building_periods[-1], alpha=0.55, facecolor='#CCCCCC', label='Design Period Range',
                           zorder = -1)

            row_index = i % len(tick_list)
            tick = tick_list[row_index]
            y_max = tick[-1]
            ax.set_ylim(0, y_max)
            ax.set_yticks(tick)
            format_plot(ax)

    if len(scale_target_types) > 1:
        label_font = 16
        # --- Column Labels ---
        for j, hazard_type in enumerate(hazard_types):
            axes[0, j].set_title(hazard_type.upper(), fontsize=label_font, fontweight='bold')

        # --- Row Labels ---
        for i, scale in enumerate(scale_target_types):
            axes[i, 0].text(-0.3, 0.5, scale.upper(),
                            transform=axes[i, 0].transAxes,
                            fontsize=label_font,
                            fontweight='bold',
                            rotation=90,
                            va='center',
                            ha='center')

    plt.savefig(f'{output_folder}/complete_scaling_figure.png', dpi=300)


def plot_eq_levels(hazard_types, scale_target_types, site_classes):
    """
    Function to plot all EQ levels (SLE, DBE, and MCE) for PSHA and DSHA on different subfigures
    :param hazard_types:
    :param scale_target_types:
    :param site_classes:
    :return:
    """
    plot_setup()
    input_folder = f'target_response_spectra'
    output_folder, _ = input_information()

    fig, axes = plt.subplots(1, len(hazard_types), figsize=(8, 3),
                             constrained_layout=True)
    fig.set_constrained_layout_pads(w_pad=.15, h_pad=.125)

    color_styles = {
        'B': '#2086D5',
        'D': '#DC1826'
    }

    linestyle_map = {
        'mce':'-',
        'dbe':'--',
        'sle':'-.'
    }

    for j, hazard in enumerate(hazard_types):
        ax = axes[j]
        for site_class in site_classes:
            for scale in scale_target_types:

                file = f'{input_folder}/{hazard}_{site_class}_{scale}_target.csv'
                df=pd.read_csv(file)
                sa = df.iloc[:, 1]  # middle column (Sa)
                period = df.iloc[:, 0]  # first column (Period)

                ax.plot(period, sa, linestyle=linestyle_map[scale], color=color_styles[site_class])

    for j, hazard in enumerate(hazard_types):
        ax = axes[j]

        y_ticks = [0.0, 1.0, 2.0 ,3.0]

        for spine in ax.spines.values():
            spine.set_edgecolor('black')
            spine.set_linewidth(1.5)

        ax.grid(False)
        ax.margins(x=0, y=0)

        ax.set_xlabel('Period (s)')
        ax.set_ylabel('Spectral Acceleration (g)')

        ax.set_xlim(0, 5)
        ax.set_ylim(0, 3)
        ax.set_yticks(y_ticks)

        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f'))

        # Build legend
        legend_handle = []

        for name, ls in linestyle_map.items():
            handle = Line2D([0], [0], color='black', linestyle=ls, label=name.upper(), linewidth=1.5)
            legend_handle.append(handle)

        color_handles= [
            Line2D([0], [0], color=color_styles['B'], marker='s', label='Site Class B', linestyle='None'),
            Line2D([0], [0], color=color_styles['D'], marker='s', label='Site Class D', linestyle='None')
        ]

        all_handles = legend_handle + color_handles

        ax.legend(handles=all_handles, loc='upper right', handletextpad=0.75)

    figure_labels = ['(a)', '(b)']
    for ax, label in zip(axes, figure_labels):
        ax.text(0.5, -0.4, label, transform=ax.transAxes,
                ha='center', va='bottom', fontsize=18, fontweight='bold')

    plt.savefig(f'{output_folder}/target_spectra_figure.png', dpi=300)


def get_y_max(file_name, hazard_type):
    df = pd.read_csv(f'processed_data/{file_name}.csv')
    scaled_max = df['scaled_plus_sigma'].max()
    target_max = df['target_plus_sigma'].max() if hazard_type == 'dsha' else 0
    y_max = max(scaled_max, target_max) * 1.10

    return math.ceil(y_max * 4) / 4
