import os
import copy
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patheffects as PathEffects

from some4demexp.conf import \
    ATTDICT, \
    CHES2019DEFAULTATTVIZ, \
    GPS2019DEFAULTATTVIZ, \
    VIZMAXDROP

plt.rc('text', usetex=True)
plt.rc('font', family='sans-serif', size=12)

fs = 12
dpi = 150

legend_mps = Line2D(
    [0],
    [0],
    label='MPs',
    marker='+',
    markersize=5,
    linewidth=0,
    markeredgecolor='black',
)
legend_parties = Line2D(
    [0],
    [0],
    label='Parties',
    marker='o',
    markersize=5,
    linewidth=0,
    markeredgecolor='black',
    markerfacecolor='white',
)
legend_followers = Line2D(
    [0],
    [0],
    label='Followers',
    marker='h',
    markersize=5,
    linewidth=0,
    markeredgecolor='deepskyblue',
    markerfacecolor="deepskyblue"
)
custom_legend = [legend_mps, legend_parties, legend_followers]

X0 = 0
X1 = 10
Y0 = 0
Y1 = 10

def get_ordinal(n):
    if n < 0 or not isinstance(n, int):
        raise ValueError(f"Input must be a strictly positive interger.")
    if n == 1:
        return "1st"
    elif n == 2:
        return "2nd"
    else:
        return f"{n}th"

def get_limits(df, dims, q0, q1):
    x0 = min(X0, df[dims['x']].quantile(q0))
    x1 = max(X1, df[dims['x']].quantile(q1))
    y0 = min(Y0, df[dims['y']].quantile(q0))
    y1 = max(Y1, df[dims['y']].quantile(q1))
    return x0, x1, y0, y1

def drop_extremes(df, dims, x0, x1, y0, y1):

    l0 = len(df)

    dfd = copy.deepcopy(df)

    dfd = dfd[dfd[dims['x']] > x0]
    dfd = dfd[dfd[dims['x']] < x1]
    dfd = dfd[dfd[dims['y']] > y0]
    dfd = dfd[dfd[dims['y']] < y1]

    diff = l0 - len(dfd)
    prop = 100 * diff / l0

    VIZMAXDROP = 1
    if prop > VIZMAXDROP:
        raise ValueError(
            f"Droping a proportion of points ({prop}%) bigger than {VIZMAXDROP}.")

    m2 = f"Dropped {diff} embeddings ({prop:.2f}%) "
    m2 += f"with atitudinal dimension {list(dims.values())} out of ranges\n"
    m2 += f"\t[{x0:.2f}, {x1:.2f}] x [{y0:.2f}, {y1:.2f}]."
    print(m2)

    return dfd

def visualize_ide(
    sources_coord_ide,
    targets_coord_ide,
    targets_parties,
    latent_dim_x,
    latent_dim_y,
    parties_to_show,
    palette,
    nudges,
    limits,
    cbar_rect,
    legend_loc,
    gridsize=100,
    output_folders=None,
    show=False
):

    # preprocessing
    colrename = {
        f'latent_dimension_{latent_dim_x}': 'x',
        f'latent_dimension_{latent_dim_y}': 'y'
    }
    sources_coord_ide = sources_coord_ide.rename(columns=colrename)
    targets_coord_ide = targets_coord_ide.rename(columns=colrename)
    nudges = {p: nudges[p] if p in nudges else [0, 0] for p in parties_to_show}

    plot_df = pd.concat([sources_coord_ide, targets_coord_ide]) \
        .reset_index() \
        .drop(columns="index")

    xlims = limits['x']
    ylims = limits['y']

    # This turned out to be 6x6 figsize
    kwargs = {
        'x': 'x',
        'y': 'y',
        'space': 0,
        'ratio': 10,
        'height': 5,
        'color': "deepskyblue",
        'gridsize': gridsize,
        'kind': 'hex',
        'data': plot_df,
    }

    # plot sources and targets ideological embeddings
    g = sns.jointplot(**kwargs)

    targets_coord_ide = targets_coord_ide.merge(
            targets_parties,
            left_on="entity",
            right_on="mp_pseudo_id",
            how="inner"
        ) \
        .drop(columns="mp_pseudo_id")

    # plot colored by parties target embeddings
    ax = g.ax_joint
    texts = []
    for party in parties_to_show:

        sample = targets_coord_ide[targets_coord_ide.party == party]

        ax.scatter(
            sample['x'],
            sample['y'],
            marker='+',
            s=20,
            alpha=0.5,
            color=palette[party],
            label=party
        )

        # plot estimated parties mean
        mean_group_estimated = sample[['x', 'y']].mean()
        ax.plot(
            mean_group_estimated['x'],
            mean_group_estimated['y'],
            marker='o',
            markeredgecolor='black',
            markeredgewidth=1.0,
            markersize=5,
            color=palette[party],
        )

        text = ax.text(
            mean_group_estimated['x']+nudges[party][0],
            mean_group_estimated['y']+nudges[party][1],
            party.replace("&", ""),
            color='white',
            bbox=dict(
                boxstyle="round",
                ec='black',
                fc=palette[party],
                alpha=1),
            fontsize=9)
        texts.append(text)

    xl = fr'{get_ordinal(latent_dim_x+1)} latent dimension '
    xl += fr'$\delta_{latent_dim_x+1}$'
    yl = fr'{get_ordinal(latent_dim_y+1)} latent dimension '
    yl += fr'$\delta_{latent_dim_y+1}$'
    ax.set_xlabel(xl, fontsize=fs)
    ax.set_ylabel(yl, fontsize=fs)

    ax.legend(handles=custom_legend, loc=legend_loc)
    ax.tick_params(axis='x', labelsize=fs)
    ax.tick_params(axis='x', labelsize=fs)

    ax.set_xlim(xlims)
    ax.set_ylim(ylims)

    cbar_ax = g.fig.add_axes(cbar_rect)
    cbar = plt.colorbar(cax=cbar_ax)

    if output_folders:
        for output_folder in output_folders:
            figname = f"latent_dims_{latent_dim_x}_vs_{latent_dim_y}.png"
            path = os.path.join(output_folder, figname)
            plt.savefig(path, dpi=dpi)
            print(f"Figure saved at {path}.")

    if show:
        plt.show()




def visualize_att(
    sources_coord_att,
    targets_coord_att,
    parties_coord_att,
    target_groups,
    dims,
    palette,
    nudges,
    limits,
    survey,
    cbar_rect,
    legend_loc,
    quantiles=None,
    paths=None,
    show=False,
    **kwargs
):

    SURVEYCOL = f'{survey.upper()}_party_acronym'

    parties_to_show = target_groups[SURVEYCOL].unique()

    nudges = {p: nudges[p] if p in nudges else [0, 0] for p in parties_to_show}

    plot_df = pd.concat([sources_coord_att, targets_coord_att]) \
        .reset_index() \
        .drop(columns="index")

    if quantiles is not None:
        x0, x1, y0, y1 = get_limits(plot_df, dims, q0=quantiles[0], q1=quantiles[1])
        plot_df = drop_extremes(plot_df, dims, x0, x1, y0, y1)
        targets_coord_att = drop_extremes(targets_coord_att, dims, x0, x1, y0, y1)

    kwargs = {
        'x': dims['x'],
        'y': dims['y'],
        'color': "deepskyblue",
        'space': 2,
        'ratio': 10,
        'height': 5,
        'kind': 'hex',
        # 'bins': 'log',  # to debug or make appear hexbins with low density
        'data': plot_df,
    }

    # plot sources and targets embeddings
    g = sns.jointplot(**kwargs)

    ax = g.ax_joint

    # plot square showing CHES limits

    lowlim_x = 0
    upperlim_x = 10
    lowlim_y = 0
    upperlim_y = 10
    A = [lowlim_x, lowlim_x, upperlim_x, upperlim_x, lowlim_x]
    B = [lowlim_y, upperlim_y, upperlim_y, lowlim_y, lowlim_y]
    ax.plot(A, B, color='white', linestyle='-')
    ax.plot(A, B, color='black', linestyle='--')
    txt = ax.text(2, 10.25, f'{survey.upper()} survey bounds', fontsize=12)
    txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='w')])

    # plot colored by parties targets attitudinal embeddings
    texts = []

    targets_coord_att_with_party = targets_coord_att.merge(
        target_groups[[SURVEYCOL, 'mp_pseudo_id']],
        left_on='entity',
        right_on='mp_pseudo_id')
    for party in parties_to_show:

        # plot colored by parties target embeddings
        mps_coord_att = targets_coord_att_with_party[
            targets_coord_att_with_party[SURVEYCOL] == party]

        ax.scatter(
            mps_coord_att[dims['x']],
            mps_coord_att[dims['y']],
            marker='+',
            s=20,
            alpha=0.5,
            color=palette[party],
            label=party
        )

        # plot parties attitudinal coordinates
        group_positions = parties_coord_att[parties_coord_att.party == party]
        if len(group_positions) > 1:
            raise ValueError("Bizarre")
        if len(group_positions) == 1:
            ax.plot(
                group_positions.iloc[0][dims['x']],
                group_positions.iloc[0][dims['y']],
                marker='o',
                markeredgecolor='black',
                markeredgewidth=1.0,
                markersize=5,
                color=palette[party],
        )

        text = ax.text(
            group_positions.iloc[0][dims['x']]+nudges[party][0],
            group_positions.iloc[0][dims['y']]+nudges[party][1],
            party.replace("&", ""),
            color='white',
            bbox=dict(
                boxstyle="round",
                ec='black',
                fc=palette[party],
                alpha=1),
            fontsize=9)
        texts.append(text)

    xl = f"{ATTDICT[survey][dims['x']]}"
    yl = f"{ATTDICT[survey][dims['y']]}"
    ax.set_xlabel(xl, fontsize=fs)
    ax.set_ylabel(yl, fontsize=fs)

    ax.legend(
        handles=custom_legend,
        loc=legend_loc,
        fontsize=fs-2,
        framealpha=0.98
    )

    ax.tick_params(axis='x', labelsize=fs)
    ax.tick_params(axis='x', labelsize=fs)

    # setting lims
    ax.set_xlim(limits)
    ax.set_ylim(limits)

    cbar_ax = g.fig.add_axes(cbar_rect)
    cbar = plt.colorbar(cax=cbar_ax)

    if paths:
        for path in paths:
            plt.savefig(path, dpi=dpi)
            print(f"Figure saved at {path}.")

    if show:
        plt.show()
    else:
        plt.close('all')