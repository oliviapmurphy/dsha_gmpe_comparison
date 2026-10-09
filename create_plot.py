import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import pandas as pd
from pathlib import Path
import os
import matplotlib.ticker as mticker

x_axis_label = 'Period (s)'

def get_color_styles():
    cmap = plt.get_cmap('cool')

    color_styles = {
        'Median': {
            'color': cmap(0.05),
            'linestyle': (0, (8, 3, 2, 3)),
        },
        '+1 sigma': {
            'color': cmap(0.25),
            'linestyle': '--',
        },
        'DSHA MCE': {
            'color': cmap(0.45),
            'linestyle': '-',
        },
        '+2 sigma': {
            'color': cmap(0.60),
            'linestyle': (0, (4, 2, 1, 2, 1, 2, 1, 2)),
        },
        '+3 sigma': {
            'color': cmap(0.72),
            'linestyle': (0, (3, 1, 1, 1, 1, 1)),
        },
        'period_range': {
            'color': '#D5D6D8',
        },
    }

    return color_styles


def plot_gm_suites(file_name, ax):
    df = pd.read_csv(f'data/{file_name}.csv')

    x_axis = df.iloc[:,0]
    gm_columns = df.columns[2:3+20]

    for gm in gm_columns:
        ax.plot(x_axis, df[gm], color='gray', linewidth=1.0, zorder=0, alpha=0.7)


def plot_setup():
    font_style = 'arial'
    plt.rcParams.update({
        "font.family": "times new roman",
        "font.size": "13",

        # Axis Labels
        'axes.edgecolor': 'black',
        "axes.labelsize": 16,
        "axes.labelweight": "bold",
        'axes.labelpad': 6,

        # Axis tick labels
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,

        # Legend
        "legend.fontsize": 13.8,
        'legend.frameon' : False,
        "legend.borderpad": 0.2,
        "legend.labelspacing": 0.2,
        "legend.handletextpad": 0.2,
        "legend.handlelength": 1.25,
        'legend.handleheight': 1.0,

        # mathtext
        'mathtext.fontset': 'custom',
        'mathtext.rm': font_style,
        'mathtext.it': f'{font_style}',
        'mathtext.bf': f'{font_style}'
    })


def input_information():
    output_folder = Path(f'figures')
    os.makedirs(output_folder, exist_ok=True)
    return output_folder


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


def plot_median_sigma(site_class, color_styles, ax):
    df = pd.read_csv(f'data/site_class_{site_class}.csv')

    cols = ["Median", "+1 sigma", "+2 sigma", "+3 sigma", "DSHA MCE"]
    linewidth = 2.0

    for col in cols:
        ax.plot(df["Periods"], df[col],
                label=col,
                color=color_styles[col]['color'],
                linestyle=color_styles[col]['linestyle'],
                linewidth=linewidth)


def create_dsha_sigma_plot(site_classes, show_building_period, building_periods, plot_gm_records):
    plot_setup()
    output_folder = input_information()
    color_styles = get_color_styles()

    fig, axes = plt.subplots(
        nrows=1,
        ncols=len(site_classes),
        figsize=(12, 6)
    )

    if plot_gm_records:
        tick_list = [0.0, 2.0, 4.0, 6.0, 8.0]
    else:
        tick_list = [0.0, 2.0, 4.0, 6.0, 8.0]

    for i, site_class in enumerate(site_classes):
        ax = axes[i]
        plot_median_sigma(site_class, color_styles, ax)

        if plot_gm_records:
            file_name = f"dsha_mce_site_class_{site_class}"
            plot_gm_suites(file_name, ax)

        if show_building_period:
            if len(building_periods) == 1:
                line = ax.axvline(building_periods[0], color='black', linestyle='--', zorder=5)
                line.set_dashes([5, 3])

                ax.text(
                    0.4,  # center horizontally
                    0.85,  # below the axis
                    '4-story period',
                    transform=ax.transAxes,
                    ha='center',
                    va='top',
                    fontsize=14
                )
            else:
                ax.axvspan(building_periods[0], building_periods[-1], alpha=0.65, facecolor=color_styles['period_range']['color'], label='Design Period Range',
                           zorder = -1)

        create_legend(ax, plot_gm_records)

        y_max = tick_list[-1]
        ax.set_ylim(0, y_max)
        ax.set_yticks(tick_list)
        if plot_gm_records:
            ax.set_xscale('log')  # log x-axis
        format_plot(ax)

    label_font = 22
    if len(site_classes) > 1:
        # --- Column Labels ---

        for i, site in enumerate(site_classes):
            axes[i].set_title(f'Site Class {site.upper()}', fontsize=label_font, fontweight='bold')

    if len(site_classes) > 1:
        plt.subplots_adjust(left=0.07, right=0.98, bottom=0.10, top=0.93, wspace=0.22, hspace=0.22)
    else:
        plt.subplots_adjust(left=0.06, right=0.98, bottom=0.13, top=0.92, wspace=0.22)

    if plot_gm_records:
        name = 'DSHA_sigma_w_GM'
    else:
        name = 'DSHA_sigma_comparison'
    plt.savefig(f'{output_folder}/{name}.png', dpi=300)
    plt.savefig(f'{output_folder}/{name}.pdf', dpi=300, format='pdf')
    plt.savefig(f'{output_folder}/{name}.svg', dpi=300, format='svg')


def create_legend(ax, plot_gm_records):
    color_styles = get_color_styles()
    line_width = 1.75
    header = Line2D([], [], linestyle='none')
    handles, labels = get_dsha_legend(color_styles, line_width, header)

    location = 'upper left' if plot_gm_records else 'upper right'

    leg = ax.legend(handles, labels,
                    ncol=1,
                    handletextpad=0.4,
                    borderpad=0.2,
                    labelspacing=0.09,
                    loc=location,
                    edgecolor='black',
                    frameon=True,
                    handlelength=3,)


def get_dsha_legend(color_styles, line_width, header):
    handles = [
        Line2D([], [], color=color_styles['Median']['color'], lw=line_width, ls=color_styles['Median']['linestyle']),
        Line2D([], [], color=color_styles['+1 sigma']['color'], lw=line_width, ls=color_styles['+1 sigma']['linestyle']),
        Line2D([], [], color=color_styles['+2 sigma']['color'], lw=1.5, ls=color_styles['+2 sigma']['linestyle']),
        Line2D([], [], color=color_styles['+3 sigma']['color'], lw=line_width, ls=color_styles['+3 sigma']['linestyle']),
        Line2D([], [], color=color_styles['DSHA MCE']['color'], lw=line_width, ls=color_styles['DSHA MCE']['linestyle']),
        Patch(facecolor=color_styles['period_range']['color'], alpha=0.65),

    ]

    labels = [
        "Median GMPE",
        "Median GMPE ± 1σ",
        "Median GMPE ± 2σ",
        "Median GMPE ± 3",
        'DSHA MCE',
        "Design Range",
    ]

    return handles, labels
