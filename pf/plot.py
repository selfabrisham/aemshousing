"""
plot.py

Plotting and visualization functions.

project    : pf
version    : 0.0.0
status     : development
modifydate :
createdate :
website    : https://github.com/tmthydvnprt/pf
author     : tmthydvnprt
email      : tim@tmthydvnprt.com
maintainer : tmthydvnprt
license    : MIT
copyright  : Copyright 2016, tmthydvnprt
credits    :

"""
from __future__ import absolute_import

import io
import datetime
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.patches as mpatches

from pf.util import f2as

################################################################################################################################
# Plotting functions
################################################################################################################################
def timeseries(data, columns=None, title='', stacked=False, smooth=2, datapoints=True, close=True, current_bar=True):
    """Make nice plot for time series"""

    # User columns or use all
    columns = columns if columns else data.columns.tolist()

    # Smooth Data
    if smooth > 0:
        smoothdata = data[columns] \
            .resample('D', loffset=pd.Timedelta('-30 days')) \
            .interpolate(method='pchip', order=smooth)
    else:
        smoothdata = data[columns].copy()
    # Plot
    if stacked:
        smoothdata[smoothdata < 0] = 0
    ax = smoothdata.plot(kind='area', stacked=stacked, figsize=(16.0, 8.0))

    # Set axis limits
    matplotlib.pyplot.xlim([data.index[0] - pd.DateOffset(months=1), data.index[-1] + pd.DateOffset(months=1)])
    if stacked:
        matplotlib.pyplot.ylim([0, 1.1 * data[columns].sum(1).max()])
    else:
        matplotlib.pyplot.ylim([1.1 * data[columns].min().min(), 1.1 * data[columns].max().max()])

    # Style on bottom spine
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_position('zero')
    ax.spines['bottom'].set_color('none')

    # Turn of yaxis ticks
    ax.tick_params(
        axis='y', which='both',
        left='off', right='off',
        labelleft='off', labelright='off'
    )
    # Turn on xaxis major ticks
    ax.tick_params(
        axis='x', which='both',
        bottom='on', top='off',
        labelbottom='on', labeltop='off',
        colors=matplotlib.colors.hex2color('#2C3E50') + (0.9,)
    )
    ax.tick_params(axis='x', which='minor', bottom='off')

    # Get series colors
    colors = [l.get_color() for l in ax.get_lines()]

    # Set Text
    ax.set_title(title)
    ax.set_ylabel('')
    ax.set_xlabel('')

    step_size = 0.01 * (data[columns].max().max() - data[columns].min().min())

    # Get Datapoints
    if datapoints:
        datapoints = pd.concat([
            # Show max data points
            pd.concat([data[columns].idxmax(), data[columns].max()], axis=1),
            # Show min data points
            pd.concat([data[columns].idxmin(), data[columns].min()], axis=1),
            # Show last data points
            data[columns].iloc[[-1]].unstack().reset_index().set_index('level_0').rename(columns={0:1, 'Date':0})
        ]).reset_index().drop_duplicates().sort(0, inplace=False)

        # Set Text
        ann_bb = []

        # Loop thru datapoints
        for c, x, y in sorted(datapoints.values, key=lambda x: x[2]):
            # if True: # y != 0:
            xyloc = (x, y)

            ax.scatter(x - pd.DateOffset(months=1), y, color=colors[columns.index(c)])

            # If inside another annotation spread
            while any([bb.contains(*ax.transData.transform((ax.convert_xunits(xyloc[0]), xyloc[1]))) for bb in ann_bb]):
                xyloc = (xyloc[0], xyloc[1] + step_size)

            # Annotate the datapoint
            ann = ax.annotate(
                f2as(y),
                xy=xyloc,
                xytext=(1, -11),
                color=colors[columns.index(c)],
                textcoords='offset points',
                size=16,
                verticalalignment='middle'
            )
            # Render Text so we can get bounding box
            ax.figure.canvas.draw()
            # Growth bounding box by 2%
            bb = ann.get_window_extent()
            bb_new = matplotlib.transforms.Bbox(bb.get_points() * np.array([[0.98, 0.98], [1.02, 1.02]]))
            # Log bounding box
            ann_bb.append(bb_new)

    ax.legend(loc='upper center', ncol=3, handles=[
        mpatches.Patch(
            edgecolor=colors[columns.index(c)],
            facecolor=matplotlib.colors.hex2color(colors[columns.index(c)]) + (0.5,),
            label=c
        ) for c in columns
    ])

    if current_bar:
        ax.axvline(datetime.date.today(), color='gray', linestyle='--', alpha=0.8)

    # Close plot (and return as png)
    if close:
        # Grab figure
        fig = matplotlib.pyplot.gcf()
        # Output 'file'
        png = io.BytesIO()
        fig.savefig(png, format='png', bbox_inches='tight')
        matplotlib.pyplot.close()
        return png
    else:
        return None
