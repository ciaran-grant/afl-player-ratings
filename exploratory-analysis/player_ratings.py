import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from highlight_text import ax_text, fig_text
from viz.afl_colours import team_colourmaps, team_colours
import matplotlib.gridspec as grid_spec

def position_player_season_summary(position_data, position_stats):
 
    stats = [
        'Age',
        'Height',
        'Weight',
        'Debut_Year',
        'Draft_Position',
    ]
        
    totals = position_data.groupby(['Player', 'Team', 'Season']).sum()[position_stats + ['Percent_Played']].add_suffix('_sum')
    means = position_data.groupby(['Player', 'Team', 'Season']).mean()[stats]
    games = position_data.groupby(['Player', 'Team', 'Season']).count()['Match_ID']
    summary = pd.concat([games, means, totals], axis=1).rename(columns = {'Match_ID':'Games'})

    for col in position_stats:
        summary[col+'_pergame'] = summary[col+"_sum"] / summary['Games']
        summary[col+'_per100'] = 100*(summary[col+"_sum"] / summary['Percent_Played_sum'])
    
    return summary

def filter_position_summary(position_summary, min_percent_played = 200, min_games = 10):
    
    position_summary_filtered = position_summary[position_summary['Percent_Played_sum'] > min_percent_played]
    position_summary_filtered = position_summary[position_summary['Games'] > min_games]
    
    return position_summary_filtered

def display_histograms(summary_data, nrows, ncols, stats, bins=20, group = None):
    
    fig, axes = plt.subplots(nrows, ncols, figsize = (20,32))
    fig.dpi = 300
    axes_flat = axes.flatten()

    for i, (column, ax) in enumerate(zip(summary_data[stats], axes_flat)):
        if group is None:
            summary_data[column].plot.hist(ax=ax, bins=20, alpha=0.7, edgecolor="black")
        else:
            for level in list(summary_data[group].unique()):
                summary_data[summary_data[group] == level][column].plot.hist(ax=ax, bins=20, alpha=0.7, edgecolor="white")
        ax.set_xlabel(column)

    plt.tight_layout()
    plt.show()
    
def zscale_stats(summary_data, stats):
    
    for col in stats:
        summary_data[col+'_z'] = (summary_data[col] - summary_data[col].mean()) / np.std(summary_data[col])
    summary_data = summary_data.fillna(0)
    
    return summary_data

def player_stats_histograms(summary_data, player, team, season, stats, figsize = (8, 12), xlim = 4, xlabel="z-Score"):
    
    nrows = len(stats)
    gs = (grid_spec.GridSpec(nrows, 1))

    fig = plt.figure(figsize=figsize)
    i=0
    axes = []
    for stat in stats:
        axes.append(fig.add_subplot(gs[i:i+1, 0:]))
        
        plot = summary_data[stat].hist(bins=20, edgecolor = "white", lw=0.5, color = team_colours[team]['positive'])    
        (markers, stemlines, baseline) = axes[-1].stem(summary_data.loc[(player, team, season)][stat],20, basefmt=" ")
        plt.setp(stemlines, linestyle="-", color="w")
        plt.setp(markers, color="w", zorder=3)
    
        # Customise axes
        axes[-1].set_xlim(-xlim, xlim)
        axes[-1].set_ylim(0, 30)
        
        axes[-1].grid(False)
        axes[-1].spines['top'].set_visible(False)
        axes[-1].spines['right'].set_visible(False)
        axes[-1].spines['left'].set_visible(False)
        # axes[-1].spines['bottom'].set_visible(False)
        
        axes[-1].set_yticklabels([])
        axes[-1].set_yticks([])
        
        if i == nrows-1:
            axes[-1].set_xlabel(xlabel)
        # else:
            # axes[-1].set_xticklabels([])
            # axes[-1].set_xticks([])
        
        stat_text = stat.replace("_", " ").replace("per100 z", "").upper()    
        ax_text(-xlim, 10, 
                s=f"<{stat_text}>", fontweight="bold", font="Karla", ha="right"
        )
        
        i +=1
    
    plt.tight_layout()
            
    return fig, axes
        
def get_selected_position_rating(selected_position):
    
    return selected_position.lower().replace("-", "_") + "_rating"

def create_position_summary(player_stats, selected_position, position_role_stats):
    
    selected_position_rating = get_selected_position_rating(selected_position)

    position_roles = list(position_role_stats.keys())

    position_stats = []
    for key in position_roles:
        position_stats += position_role_stats[key]
    position_stats = list(set(position_stats))
    position_stats_per100 = [x+"_per100" for x in position_stats]

    position_role_stats_zscaled = {}
    for key in position_roles:
        position_role_stats_zscaled[key] = [x+"_per100_z" for x in position_role_stats[key]]
    
    if selected_position in list(set(player_stats['Position_Sub_Group'])):
        position = player_stats[player_stats['Position_Sub_Group'] == selected_position]
    elif selected_position in list(set(player_stats['Position_Group'])):
        position = player_stats[player_stats['Position_Group'] == selected_position]
        
    position_summary = position_player_season_summary(position, position_stats)
    position_summary = filter_position_summary(position_summary, min_percent_played = 200, min_games = 10)
    position_summary = zscale_stats(position_summary, position_stats_per100)

    for role in position_role_stats_zscaled.keys():
        position_summary[role+'_rating'] = position_summary[position_role_stats_zscaled[role]].mean(axis=1)
    position_summary[selected_position_rating] = position_summary[[x+"_rating" for x in list(position_role_stats_zscaled.keys())]].mean(axis=1)
        
    return position_summary, position_role_stats_zscaled

def create_player_rating_by_season(position_summary, selected_position, position_role_stats_zscaled):
    
    selected_position_rating = get_selected_position_rating(selected_position)

    position_player_season = position_summary[[x+"_rating" for x in list(position_role_stats_zscaled.keys())] + [selected_position_rating]].reset_index()
    players = position_player_season.pivot(index=['Player', 'Team'], columns = "Season", values=[selected_position_rating])
    players = players.fillna(0)
    players['overall_'+selected_position_rating] = 0.1*players[(selected_position_rating, 2021)] + 0.3*players[(selected_position_rating, 2022)] + 0.6*players[(selected_position_rating, 2023)]

    return players

def plot_stat_histogram(ax, summary_data, stat, player, team, season, xlim=4, ylim=30, stat_fontsize=4, stem_markersize=3, stem_colour = "w"):
    
    ax.hist(summary_data[stat], bins=20, edgecolor = "white", lw=0.5, color = team_colours[team]['positive'])    
    (markers, stemlines, baseline) = ax.stem(summary_data.loc[(player, team, season)][stat],20, basefmt=" ")
    plt.setp(stemlines, linestyle="-", color=stem_colour)
    plt.setp(markers, color=stem_colour, zorder=3, markersize=stem_markersize)

    # Customise axes
    ax.set_xlim(-xlim, xlim)
    ax.set_ylim(0, ylim)
    
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    ax.set_yticklabels([])
    ax.set_yticks([])
    
    stat_text = stat.replace("_", " ").replace("per100 z", "").upper()    
    ax_text(-xlim+2, 20, ax=ax,
            s=f"<{stat_text}>", fontweight="bold", font="Karla", ha="right", fontsize=stat_fontsize
    )
    return ax

def plot_multiple_role_histograms(summary_data, stats_list, player, team, season, xlim=4, ylim=30, figsize = (8,6), stat_fontsize=4, ticksize = 6, stem_markersize=3, stem_colour = "w"):
    
    nrows = max([len(x) for x in stats_list])
    ncols = len(stats_list)
    
    fig, axs = plt.subplots(ncols=ncols, nrows=nrows, layout="constrained", figsize=figsize)

    for row in range(nrows):
        for col in range(ncols):
            if row > len(stats_list[col])-1:
                axs[row, col].set_visible(False)
            else:
                axs[row, col] = plot_stat_histogram(ax=axs[row, col], summary_data=summary_data, stat=stats_list[col][row], 
                                                    player=player, team=team, season=season, 
                                                    xlim=xlim, ylim=ylim, stat_fontsize=stat_fontsize,
                                                    stem_markersize=stem_markersize, stem_colour = stem_colour)
                
                if row == len(stats_list[col])-1:
                    axs[row, col].set_xlabel('z-Score', size = ticksize)
                    axs[row, col].tick_params(axis='x', labelsize=ticksize)
                else:
                    axs[row, col].set_xticklabels([])
                    # axs[row, col].set_xticks([])
        
    plt.tight_layout(pad=0, w_pad=0, h_pad=0)
    return fig, axs