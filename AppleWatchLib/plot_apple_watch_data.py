'''
Visualizing Apple Watch Health Data w/ Bokeh
'''
import os
from datetime import datetime
import logging
import pandas as pd
from bokeh.io import show
from bokeh.plotting import figure, output_file, save, reset_output
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
    BasicTicker,
    PrintfTickFormatter,
    ColorBar
)
from bokeh.transform import factor_cmap
from bokeh.palettes import Category20_20
from read_apple_watch_data import *

# create logger object
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: add requirements text file for python libraries needed and respective versions
# TODO: Add start and end dates to plot (sub)titles
def save_plot(plot, title):
    """
    Saves plot in local directory as file_name

    :param plot: bokeh plot object
    :param title: file name for plot
    :return: None
    """
    output_file("apple_watch_plots/{}.html".format(title))
    save(plot)

def plot_heart_rate(apple_watch):
    """
    Superpostion multiple time series plots of heart data

    :param apple_watch: data frame of heart rate data
    :return: None
    """
    logger.info('Loading and Plotting Heart Rate Data')
    df = apple_watch.load_heart_rate_data()
    df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
    df['date'] = list(map(lambda dt: dt.strftime('%m/%d/%y'), df['start_timestamp']))
    df['time'] = list(map(lambda d: d.time(), df['start_timestamp']))

    plot = figure(
        width=800,
        height=600,
        title='Apple Watch Heart Rate Data',
        x_axis_type='datetime',
        x_axis_label="Hour",
        y_axis_label="Average Beats Per Minute",
        tools='pan,wheel_zoom,box_zoom,reset,hover',
        toolbar_location='above',
        sizing_mode='scale_both')

    # superpose time series plots for each date
    color_palette = Category20_20
    dates = df['date'].unique()
    for idx, dt in enumerate(dates):
        sub_df = df[df['date'] == dt][['date', 'time', 'heart_rate']]
        # format time column to be readable
        sub_df['timestamp'] = list(map(lambda t: t.strftime('%H:%M:%S'), sub_df['time']))
        source = ColumnDataSource(sub_df)
        plt = plot.circle(x='time',
                  y='heart_rate',
                  source=source,
                  size=10,
                  fill_color=color_palette[idx],
                  legend=dt)

        plot.select_one(HoverTool).tooltips = [
            ('date', '@date'),
            ('time', '@timestamp'),
            ('bpm', '@heart_rate')
        ]

    plot.xaxis.axis_label_text_font_size = '14pt'
    plot.xaxis.major_label_text_font_size = '12pt'
    plot.yaxis.axis_label_text_font_size = '14pt'
    plot.yaxis.major_label_text_font_size = '12pt'
    plot.title.text_font_size = '16pt'
    plot.legend.location = 'top_left'
    plot.legend.click_policy = 'hide'
    plot.legend.label_text_font_size = '12pt'

    if SHOW_PLOTS:
        show(plot, browser='chrome')
    save_plot(plot, 'heart_rate')
    # clear output mode for next plot
    reset_output()

    # save data frame
    df.to_csv('apple_watch_data/heart_rate.csv', index=False)

def plot_heart_rate_variability(apple_watch):
    """
    Generate swarm-like plots of heart rate variability measures for multiple days

    :param apple_watch: data frame of heart rate variability data
    :return: None
    """
    logger.info('Loading and Plotting Heart Rate Variability Data')
    df = apple_watch.load_heart_rate_variability_data()
    df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
    df['date'] = list(map(lambda d: d.strftime('%m/%d/%y'), df['start_timestamp']))
    df['time'] = list(map(lambda d: d.strftime('%H:%M:%S'), df['start_timestamp']))
    dates = list(df['date'].unique())

    # remove instantaneous data, bokeh doesn't not like dictionary format
    del df['instantaneous_bpm']
    source = ColumnDataSource(df)
    plot = figure(
        width=800,
        height=600,
        x_range=dates,
        x_axis_label='Date',
        y_axis_label='Time Between Heart Beats (ms)',
        title='Apple Watch Heart Rate Variability (SDNN)',
        tools='pan, wheel_zoom, box_zoom, reset, hover',
        toolbar_location='above',
        sizing_mode='scale_both')

    # add color map for dates
    dates_cmap = factor_cmap('date', palette=Category20_20, factors=dates)

    plot.circle(x='date', y='heart_rate_variability', source=source, size=12, fill_color=dates_cmap)
    plot.xaxis.axis_label_text_font_size = "14pt"
    plot.xaxis.major_label_text_font_size = "12pt"
    plot.yaxis.axis_label_text_font_size = "14pt"
    plot.yaxis.major_label_text_font_size = "12pt"
    plot.title.text_font_size = '16pt'

    # configure hover tool
    plot.select_one(HoverTool).tooltips = [
        ('date', '@date'),
        ('time', '@time'),
        ('time interval', '@heart_rate_variability')
    ]

    if SHOW_PLOTS:
        show(plot, browser='chrome')
    save_plot(plot, 'heart_rate_variability')
    # clear output mode for next plot
    reset_output()

    # save dataframe
    df.to_csv('apple_watch_data/heart_rate_variability.csv', index=False)

def plot_resting_heart_rate(apple_watch):
    """
    Generate simple time series plot of resting heart rate

    :param apple_watch: data frame of daily resting heart rate estimates
    :return: None
    """
    logger.info('Loading and Plotting Resting Heart Rate Data')
    df = apple_watch.load_resting_heart_rate_data()
    df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
    df['date'] = list(map(lambda dt: dt.strftime('%m/%d/%y'), df['start_timestamp']))

    source = ColumnDataSource(df)
    plot = figure(
        width=800,
        height=600,
        x_axis_type='datetime',
        x_axis_label='Date',
        y_axis_label='Average Beats Per Minutes',
        title='Apple Watch Resting Heart Rate',
        tools='pan, wheel_zoom, box_zoom, reset, hover',
        toolbar_location='above',
        sizing_mode='scale_both')

    plot.line(x='start_timestamp', y='resting_heart_rate', source=source)
    plot.xaxis.axis_label_text_font_size = "14pt"
    plot.yaxis.axis_label_text_font_size = "14pt"
    plot.title.text_font_size = '16pt'

    # configure hover tool
    plot.select_one(HoverTool).tooltips = [
        ('date','@date'),
        ('bpm', '@resting_heart_rate')
    ]

    if SHOW_PLOTS:
        show(plot, browser='chrome')
    save_plot(plot, 'resting_heart_rate')
    # clear output mode for next plot
    reset_output()

    # save dataframe
    df.to_csv('apple_watch_data/resting_heart_rate.csv', index=False)

def plot_walking_heart_rate(apple_watch):
    """
    Generate simple time series plot of walking heart rate

    :param apple_watch: data frame of daily walking heart rate estimates
    :return: None
    """
    logger.info('Loading and Plotting Walking/Running Data')
    df = apple_watch.load_walking_heart_rate_data()
    df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
    df['date'] = list(map(lambda dt: dt.strftime('%m/%d/%y'), df['start_timestamp']))

    source = ColumnDataSource(df)
    plot = figure(
        width=800,
        height=600,
        x_axis_type='datetime',
        x_axis_label='Date',
        y_axis_label='Average Beats Per Minutes',
        title='Apple Watch Walking Heart Rate',
        tools='pan, wheel_zoom, box_zoom, reset, hover',
        toolbar_location='above',
        sizing_mode='scale_both')

    plot.line(x='start_timestamp', y='walking_heart_rate', source=source)
    plot.xaxis.axis_label_text_font_size = '14pt'
    plot.xaxis.major_label_text_font_size = '12pt'
    plot.yaxis.axis_label_text_font_size = '14pt'
    plot.yaxis.major_label_text_font_size = '12pt'
    plot.title.text_font_size = '16pt'

    # configure hover tool
    plot.select_one(HoverTool).tooltips = [
        ('date', '@date'),
        ('bpm', '@walking_heart_rate')
    ]

    if SHOW_PLOTS:
        show(plot, browser='chrome')
    save_plot(plot, 'walking_heart_rate')
    # clear output mode for next plot
    reset_output()

    # save dataframe
    df.to_csv('apple_watch_data/walking_heart_rate.csv', index=False)

def plot_distance(apple_watch):
    """
    Generate grid heat map of miles walked or ran for a given hour and date, grouped by start timestamp.

    :param apple_watch: instance of apple watch data object
    :return: None
    """
    logger.info('Loading and Plotting Distance Walked/Ran Data')
    df = apple_watch.load_distance_data()
    df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
    df['date'] = list(map(lambda d: d.strftime('%m/%d/%y'), df['start_timestamp']))
    df['hour'] = list(map(lambda d: int(d.strftime('%H')), df['start_timestamp']))

    # group by hour and date and calculate sum of steps
    hourly_distance = df.groupby(['hour', 'date'])['distance_walk_run'].agg(['sum']).reset_index()
    hourly_distance.rename(columns={'sum': 'distance'}, inplace=True)

    # resort by date
    hourly_distance['datetime'] = pd.to_datetime(hourly_distance['date'])
    hourly_distance.sort_values(by=['datetime'], inplace=True)
    dates = hourly_distance['date'].unique()

    # create heat map of hourly sum grouped by date
    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
    colors = ["#000080", "#1874CD", "#63B8FF", "#C6E2FF", "#E6E6FA", "#dfccce", "#ddb7b1", "#cc7878", "#933b41"]
    mapper = LinearColorMapper(palette=colors,
                               low=hourly_distance.distance.min(),
                               high=hourly_distance.distance.max())

    source = ColumnDataSource(hourly_distance)
    plot = figure(title="Apple Watch Hourly Distance Walked/Ran",
                  x_range=[str(h) for h in range(24)],
                  y_range=list(dates),
                  x_axis_location="below",
                  plot_width=1000,
                  plot_height=600,
                  tools=TOOLS,
                  toolbar_location='above',
                  sizing_mode='scale_both')

    plot.rect(x='hour', y='date', width=1, height=1,
              source=source,
              fill_color={'field': 'distance', 'transform': mapper},
              line_color=None)

    plot.grid.grid_line_color = None
    plot.axis.axis_line_color = None
    plot.axis.major_tick_line_color = None
    plot.xaxis.axis_label_text_font_size = '14pt'
    plot.xaxis.major_label_text_font_size = '12pt'
    plot.yaxis.axis_label_text_font_size = '14pt'
    plot.yaxis.major_label_text_font_size = '12pt'
    plot.title.text_font_size = '16pt'

    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="10pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         formatter=PrintfTickFormatter(format="%d mi"),
                         label_standoff=9, border_line_color=None, location=(0, 0))
    plot.add_layout(color_bar, 'right')

    plot.select_one(HoverTool).tooltips = [
        ('date', '@date'),
        ('hour', '@hour'),
        ('miles', '@distance')
    ]

    if SHOW_PLOTS:
        show(plot, browser='chrome')
    save_plot(plot, 'distance_walked_ran')
    # clear output mode for next plot
    reset_output()

    # save dataframe
    df.to_csv('apple_watch_data/distance_walked_ran.csv', index=False)

def plot_basal_energy(apple_watch):
    """
    Generate grid heat map of basal Calories burned for a given hour and date, grouped by start timestamp.

    :param apple_watch: instance of apple watch data object
    :return: None
    """
    logger.info('Generating Basal Energy Plot')

    df = apple_watch.load_basal_energy_data()
    df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
    df['date'] = list(map(lambda d: d.strftime('%m/%d/%y'), df['start_timestamp']))
    df['hour'] = list(map(lambda d: int(d.strftime('%H')), df['start_timestamp']))

    # group by hour and date and calculate sum of steps
    basal_energy = df.groupby(['hour', 'date'])['energy_burned'].agg(['sum']).reset_index()
    basal_energy.rename(columns={'sum': 'energy_burned'}, inplace=True)

    # resort date
    basal_energy['datetime'] = pd.to_datetime(basal_energy['date'])
    basal_energy.sort_values(by=['datetime'], inplace=True)
    dates = basal_energy['date'].unique()

    # create heat map of hourly counts grouped by date
    # follow example from https://bokeh.pydata.org/en/latest/docs/gallery/unemployment.html
    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
    colors = ["#000080", "#1874CD", "#63B8FF", "#C6E2FF", "#E6E6FA", "#dfccce", "#ddb7b1", "#cc7878", "#933b41"]
    mapper = LinearColorMapper(palette=colors, low=basal_energy.energy_burned.min(), high=basal_energy.energy_burned.max())

    source = ColumnDataSource(basal_energy)
    plot = figure(title="Apple Watch Hourly Calories Burned",
                  x_range=[str(h) for h in range(24)],
                  y_range=list(dates),
                  x_axis_location="below",
                  plot_width=1000,
                  plot_height=600,
                  tools=TOOLS,
                  toolbar_location='above',
                  sizing_mode='scale_both')

    plot.grid.grid_line_color = None
    plot.axis.axis_line_color = None
    plot.axis.major_tick_line_color = None
    plot.xaxis.axis_label_text_font_size = '14pt'
    plot.xaxis.major_label_text_font_size = '12pt'
    plot.yaxis.axis_label_text_font_size = '14pt'
    plot.yaxis.major_label_text_font_size = '12pt'
    plot.title.text_font_size = '16pt'

    plot.rect(x='hour', y='date', width=1, height=1,
              source=source,
              fill_color={'field': 'energy_burned', 'transform': mapper},
              line_color=None)

    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="10pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         formatter=PrintfTickFormatter(format="%d Cal"),
                         label_standoff=10, border_line_color=None, location=(0, 0))
    plot.add_layout(color_bar, 'right')

    plot.select_one(HoverTool).tooltips = [
        ('date', '@date'),
        ('hour', '@hour'),
        ('Cal', '@energy_burned')
    ]

    if SHOW_PLOTS:
        show(plot, browser='chrome')
    save_plot(plot, 'basal_energy')
    # clear output mode for next plot
    reset_output()

    # save dataframe
    df.to_csv('apple_watch_data/basal_energy.csv', index=False)

def plot_stand_hour(apple_watch):
    """
    Generate grid heat map of stand hour labels for a given hour and date, grouped by start timestamp.

    :param apple_watch: instance of apple watch data object
    :return: None
    """
    logger.info('Loading and Generating Stand Hour Heat Map')

    df = apple_watch.load_stand_hour_data()
    df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
    df['date'] = list(map(lambda d: d.strftime('%m/%d/%y'), df['start_timestamp']))
    df['hour'] = list(map(lambda d: int(d.strftime('%H')), df['start_timestamp']))
    df['stand_hour'] = list(map(lambda label: 1 if label == 'Stood' else 0, df['stand_hour']))
    dates = df['date'].unique()

    # create heat map of hourly counts grouped by date
    # follow example from https://bokeh.pydata.org/en/latest/docs/gallery/unemployment.html
    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
    colors = ["grey", "green"]
    mapper = LinearColorMapper(palette=colors)

    source = ColumnDataSource(df)
    plot = figure(title="Apple Watch Stand Hour Data",
               x_range=[str(h) for h in range(24)],
               y_range=list(dates),
               x_axis_location="below",
               plot_width=1000,
               plot_height=600,
               tools=TOOLS,
               toolbar_location='above',
               sizing_mode='scale_both')

    plot.grid.grid_line_color = None
    plot.axis.axis_line_color = None
    plot.axis.major_tick_line_color = None
    plot.axis.major_tick_line_dash_offset = -1
    plot.xaxis.axis_label_text_font_size = '14pt'
    plot.xaxis.major_label_text_font_size = '12pt'
    plot.yaxis.axis_label_text_font_size = '14pt'
    plot.yaxis.major_label_text_font_size = '12pt'
    plot.title.text_font_size = '16pt'

    plot.rect(x='hour', y='date', width=1, height=1,
           source=source,
           fill_color={'field': 'stand_hour', 'transform': mapper},
           line_color=None)

    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="10pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         label_standoff=6, border_line_color=None, location=(0, 0))

    plot.add_layout(color_bar, 'right')

    plot.select_one(HoverTool).tooltips = [
        ('date', '@date'),
        ('hour', '@hour'),
        ('value', '@stand_hour')
    ]

    if SHOW_PLOTS:
        show(plot, browser='chrome')
    save_plot(plot, 'stand_hour')
    # clear output mode for next plot
    reset_output()

    # save dataframe
    df.to_csv('apple_watch_data/stand_hour.csv', index=False)

def plot_steps(apple_watch):
    """
    Generate grid heat map of step counts for a given hour and date, grouped by start timestamp.

    :param apple_watch: instance of apple watch data object
    :return: None
    """
    logger.info('Loading and Generating Steps Heat Map')
    df = apple_watch.load_step_data()
    df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
    df['date'] = list(map(lambda d: d.strftime('%m/%d/%y'), df['start_timestamp']))
    df['hour'] = list(map(lambda d: int(d.strftime('%H')), df['start_timestamp']))

    # group by hour and date and calculate sum of steps
    step_counts = df.groupby(['hour', 'date'])['steps'].agg(['sum']).reset_index()
    step_counts.rename(columns={'sum': 'steps'}, inplace=True)

    # resort by date
    step_counts['datetime'] = pd.to_datetime(step_counts['date'])
    step_counts.sort_values(by=['datetime'], inplace=True)
    dates = step_counts['date'].unique()

    # create grid heat map of hourly counts grouped by date
    # follow example from https://bokeh.pydata.org/en/latest/docs/gallery/unemployment.html
    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
    colors = ["#000080", "#1874CD", "#63B8FF", "#C6E2FF", "#E6E6FA", "#dfccce", "#ddb7b1", "#cc7878", "#933b41"]
    mapper = LinearColorMapper(palette=colors, low=step_counts.steps.min(), high=step_counts.steps.max())

    source = ColumnDataSource(step_counts)
    plot = figure(title="Apple Watch Hourly Step Counts",
                  x_range=[str(h) for h in range(24)],
                  y_range=list(dates),
                  x_axis_location="below",
                  plot_width=1000,
                  plot_height=600,
                  tools=TOOLS,
                  toolbar_location='above',
                  sizing_mode='scale_both')

    plot.grid.grid_line_color = None
    plot.axis.axis_line_color = None
    plot.axis.major_tick_line_color = None
    plot.xaxis.axis_label_text_font_size = '14pt'
    plot.xaxis.major_label_text_font_size = '12pt'
    plot.yaxis.axis_label_text_font_size = '14pt'
    plot.yaxis.major_label_text_font_size = '12pt'
    plot.title.text_font_size = '16pt'

    plot.rect(x='hour',
              y='date',
              width=1,
              height=1,
              source=source,
              fill_color={'field': 'steps', 'transform': mapper},
              line_color=None)

    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="10pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         formatter=PrintfTickFormatter(format="%d"),
                         label_standoff=6, border_line_color=None, location=(0, 0))
    plot.add_layout(color_bar, 'right')

    plot.select_one(HoverTool).tooltips = [
        ('date', '@date'),
        ('hour', '@hour'),
        ('count', '@steps')
    ]

    if SHOW_PLOTS:
        show(plot, browser='chrome')
    save_plot(plot, 'step_counts')
    # clear output mode for next plot
    reset_output()

    # save data frame
    df.to_csv('apple_watch_data/step_counts.csv', index=False)

def run(apple_watch, start_date, end_date, show_plots):
    global START_DATE, END_DATE, SHOW_PLOTS
    SHOW_PLOTS = show_plots

    try:
        START_DATE = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        END_DATE = datetime.strptime(end_date, '%Y-%m-%d %H:%M')
    except ValueError:
        START_DATE = datetime.strptime(start_date, '%m/%d/%y %H:%M')
        END_DATE = datetime.strptime(end_date, '%m/%d/%y %H:%M')
    except Exception as e:
        logger.error('Unrecognized date format...rasining ValueError.')
        raise ValueError()

    try:
        plot_heart_rate(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing heart rate data!')

    try:
        plot_heart_rate_variability(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing heart rate variability data!')

    try:
        plot_resting_heart_rate(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing resting heart rate data!')

    try:
        plot_walking_heart_rate(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing walking heart rate data!')

    try:
        plot_distance(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing distance walked data!')

    try:
        plot_basal_energy(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing basal energy data!')

    try:
        plot_stand_hour(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing stand hour data!')

    try:
        plot_steps(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing step count data!')
