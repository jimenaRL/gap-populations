# classic
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# viz
import seaborn as sn
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as patches
from adjustText import adjust_text
import matplotlib.ticker as mtick
from matplotlib import cm
import matplotlib.patheffects as PathEffects
import matplotlib as mpl

mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['mathtext.rm'] = 'serif'
mpl.rcParams['text.latex.preamble'] = r"\usepackage{amsmath}"
plt.rc('text', usetex=True)
plt.rc('font', family='sans-serif', size=12)
mpl.rcParams['mathtext.fontset'] = 'custom'
mpl.rcParams['mathtext.rm'] = 'Bitstream Vera Sans'
mpl.rcParams['mathtext.it'] = 'Bitstream Vera Sans:italic'
mpl.rcParams['mathtext.bf'] = 'Bitstream Vera Sans:bold'
mpl.rcParams.update(mpl.rcParamsDefault)


##############################################################################
# Plot parameters
##############################################################################

"""
Dictionary with colors for parties.
The two alternative strategies discussed in the meeting:

1) Create an array of pyplot colours and just use sequentialy for a list of
parties of a given country. Take inspiration in the colours chosen in the
SNAM2022 article.

2) scrape the party color from wikipedia to use the colors with which people
associate parties.

[Jimena] Ok. Import from yaml.

"""
party_colors="""
    # uk
    Alliance: green
    Conservative: blue
    Democratic Unionist Party: purple
    Green Party: green
    Independent: black
    Labour: red
    Labour (Co-op): red
    Liberal Democrat: gold
    Plaid Cymru: orangered
    Respect: pink
    Scottish National Party: green
    "Sinn F\xE9in": tab:brown
    Social Democratic & Labour Party: magenta
    Speaker: white
    The Independent Group for Change: orangered
    UK Independence Party: magenta
    Ulster Unionist Party: purple
    # france
    EELV: tab:green
    LFI: tab:purple
    LR: tab:blue
    RE: tab:brown
    MoDem: orangered
    PCF: red
    PRG: blue
    PS: tab:pink
    RN: magenta
    DLF: gold
    # germany
    AfD: magenta
    CDU: black
    CSU: tab:blue
    GRÜNE: tab:green
    LINKE: mediumvioletred
    Die blaue Partei: navy
    FDP: gold
    Parteilos: tab:pink
    SPD: red
    # italy
    Azione: tab:blue
    CPE: orangered
    FI: cornflowerblue
    FdI: navy
    IV: mediumvioletred
    LeU: tab:pink
    Lega: tab:green
    M5S: gold
    MAIE: tab:green
    Misto: black
    PD: red
    PSI: magenta
    RI: gold
    SVP: darkgreen
    UV: tab:brown
    emeritus: black
    # spain
    CDC: tab:pink
    Cs: orangered
    ECP: purple
    "ERC-CATS\xCD ": gold
    IU: tab:red
    'NCa ': black
    PNV: tab:green
    PP: tab:blue
    PPP: tab:blue
    PSOE: red
    UP: mediumvioletred
    UPM: magenta
"""

"""
[Pedro] I used here a dictionary of acronyms, but in theory Hiroki's data,
in particular party_acronym, allows us to do this directly

[Jimena] Done with db mapping.

"""

fs = 12

"""
[Pedro] This is the object taken by the legend creator of pyplot.
Here it is with the 3 types of, elements in figures, but it can be adapted
to include only some.
"""

legend_mp = Line2D(
    [0],
    [0],
    color='black',
    marker='+',
    lw=0,
    alpha=1.0,
    label='MPs'
)
legend_parties = Line2D(
    [0],
    [0],
    color='gray',
    marker='o',
    mec='k',
    lw=0,
    alpha=1,
    label='Parties'
)
legend_followers = Line2D(
    [0],
    [0],
    color='deepskyblue',
    marker='s',
    alpha=0.8,
    linestyle='None',
    label='Followers'
)


custom_legend = [legend_mps, legend_parties, legend_followers]


##############################################################################
# Plotting Ideological Space
##############################################################################

"""
[pedro] In this version, I gave predefined limits. In our case, we should use
limits predefined by pyplot for ideological space, and something reasonable
for attitudinal spaces.
For, examples, given than attitudinal coordinates lay approximately around
[0, 10]^2, maybe something like [-5, 15]^2... to be refined depending on results.
"""

country_lims = {
    'france_own': {'x': (-4, 3), 'y': (-4, 3)},
    'germany_own': {'x': (-2, 4), 'y': (-2, 3)},
    'italy_own': {'x': (-3, 5), 'y': (-3, 6)},
    'spain': {'x': (-3, 4), 'y': (-3, 5)},
    'uk_own': {'x': (-3, 5), 'y': (-2, 2)},
}

"""
[pedro] In this version, I had to move party names a little bit.T
his was a pain. There is a nice python module that does this automatically:
adjusttext but I wasn't able to domesticate it for this version.
"""

disp = {
      # France
      'LC': (0.5, 0.5),
      'EELV': (-0.2, 0.35),
      'LFI': (-0.1, 0.4),
      'LR': (0.2, 0),
      'LREM': (-0.3, 0.4),
      'MoDem': (0.3, 0.15),
      'PCF': (0.05, -0.5),
      'PRG': (0.2, -0.4),
      'PS': (-0.4, -0.25),
      'RN': (-0.5, -0.3),
      # Germany
      'FDP': (0.4, 0.0),
      'SPD': (0.4, 0.0),
      'DIE LINKE': (0.4, 0.0),
      'AfD': (0.4, 0.0),
      'Die blaue Partei': (0.4, 0.0),
      'CDU': (0.4, -0.2),
      'DIE GRÜNEN': (0.4, 0.0),
      'CSU': (0.4, 0.1),
      'Parteilos': (0.4, 0.0),
      # Italy
      'FdI': (0.4, 0.2),
      'Misto': (0.2, 0.2),
      'M5S': (0.2, 0.4),
      'Lega': (0.3, 0.3),
      'IV': (0.2, 0.2),
      'FI': (0.4, 0.3),
      'PD': (0.4, 0.2),
      'LeU': (0.2, 0.2),
      'PSI': (0.2, 0.2),
      'SVP': (0.4, 0.1),
      'UV': (0.2, 0.2),
      'CPE': (0.2, 0.2),
      'emeritus': (0.2, 0.2),
      'RI': (-0.6, 0.2),
      'MAIE': (0.2, 0.2),
      'Azione': (0.2, 0.2),
      # Spain
      'Cs': (-0.4, 0.4),
      'ECP': (-0.6, -0.4),
      'PSOE': (0.3, 0.3),
      'UP': (-0.8, -0.3),
      'IU': (0.2, 0.2),
      'PP': (0.2, 0.4),
      'PPP': (0.2, 0.4),
      'PNV': (0.2, 0.2),
      'UPM': (-0.5, 0.3),
      'CDC': (0.2, 0.2),
      'ERC-CATSÍ ': (-1.2, -0.4),
      'NCa ': (0.2, 0.2),
      # UK
      'Labour': (0.3, -0.1),
      'Conservative': (0.25, 0.1),
      'Scottish National Party': (0.2, 0.2),
      'Liberal Democrat': (0.2, 0.2),
      'Labour (Co-op)': (0.2, 0.2),
      'Independent': (0.2, 0.2),
      'The Independent Group for Change': (0.2, 0.2),
      'Democratic Unionist Party': (0.2, 0.2),
      'Social Democratic & Labour Party': (0.2, 0.2),
      'Ulster Unionist Party': (0.2, 0.2),
      'Respect': (0.2, 0.2), 'Sinn Féin': (0.2, 0.2),
      'Speaker': (0.2, 0.2), 'Plaid Cymru': (0.2, 0.2),
      'Alliance': (0.2, 0.2), 'Green Party': (0.2, -0.5),
      'UK Independence Party': (-0.5, 0.3)

      }

colrename = {
    'latent_dimension_0': 'x',
    'latent_dimension_1': 'y'
}

for country in countries:

    # preparing df
    plot_df = ideo_source_df[country].rename(columns=colrename)
    # >>>> this is where I delete points with duplicated coordinates <<<<
    plot_df.drop_duplicates(subset=['x'], inplace=True)

    # setting lims
    pad = 0.35
    dx = plot_df['x'].max()-plot_df['x'].min()
    dy = plot_df['y'].max()-plot_df['y'].min()
    xlims = (plot_df['x'].min()-pad*dx, plot_df['x'].max()+pad*dx)
    ylims = (plot_df['y'].min()-pad*dy, plot_df['y'].max()+pad*dy)

    # This turned out to be 6x6 figsize
    kwargs = {
        'x': 'x',
        'y': 'y',
        'space': 0,
        'ratio': 10,
        'height': 5,
        'color': "deepskyblue",
        'kind': 'hex',
        'data': plot_df,
    }
    if country == 'uk_own':
        kwargs.update({'joint_kws': dict(gridsize=80)})
    g = sn.jointplot(**kwargs)
    ax = g.ax_joint
    cbar_ax = g.fig.add_axes([0.15, .4, .05, .5])
    plt.colorbar(cax=cbar_ax)

    # MPs
    for idx, row in groups[country].iterrows():
        mps_df = ideo_target_df[country][ideo_target_df[country]['k'] == row['k']]
        ax.scatter(
            mps_df['latent_dimension_0'],
            mps_df['latent_dimension_1'],
            s=20,
            marker='+',
            c=party_colors[row['party']],
            alpha=0.15)
    group_txt = []
    for idx, row in groups[country].iterrows():
        if row['party'] in pivot_parties[country]:
            x = row['latent_dimension_0']
            y = row['latent_dimension_1']
            ax.plot(
                x,
                y,
                'o',
                color=party_colors[row['party']],
                mew=1.0,
                ms=5,
                mec='k')
            group_txt.append(
                ax.text(
                    x+disp[row['party']][0],
                    y+disp[row['party']][1],
                    party_name[row['party']],
                    color='white',
                    bbox=dict(
                        boxstyle="round",
                        ec='black',
                        fc=party_colors[row['party']],
                        alpha=1),
                    fontsize=9))
    ax.legend(handles=custom_legend, loc='lower right', fontsize=fs-2)
    ax.set_xlabel(r'$\delta_1$', fontsize=fs)
    ax.set_ylabel(r'$\delta_2$', fontsize=fs)
    ax.tick_params(axis='x', labelsize=fs)
    ax.tick_params(axis='x', labelsize=fs)
    ax.set_xlim(country_lims[country]['x'])
    ax.set_ylim(country_lims[country]['y'])

    # the next lines plot the [0, 10]^2 square showing CHES limits
    ax.plot([0, 10, 10, 0, 0], [0, 0, 10, 10, 0], color='w', linestyle='-', alpha=1)
    ax.plot([0, 10, 10, 0, 0], [0, 0, 10, 10, 0], color='k', linestyle='--', alpha=1)
    ax.legend(handles=custom_legend, loc='lower right', fontsize=10)
    txt = ax.text(2, 10.25, 'CHES survey bounds', fontsize=12)
    txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='w')])

    # ax.set_aspect('equal')
    plt.tight_layout()
    plt.savefig(img_folder+'Spaces/I_%s.pdf' % country_name[country])
    plt.savefig(img_folder+'Spaces/I_%s.eps' % country_name[country])
    plt.clf()
    plt.close()
    print('ended '+country)


print('The, end...')
