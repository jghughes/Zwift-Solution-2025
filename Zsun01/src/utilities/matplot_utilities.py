from matplotlib.axes import Axes

def set_x_axis_seconds_in_minute_ticks(ax: Axes, max_seconds: int, interval_seconds: int = 300) -> None:
    """
    Sets x-axis ticks at specified intervals and labels them in minutes.

    Parameters:
        ax (matplotlib.axes.Axes): The axes object to modify.
        max_seconds (int): The maximum value on the x-axis in seconds.
        interval_seconds (int): The interval between ticks in seconds (default is 300).
    """
    tick_positions = range(0, max_seconds + 1, interval_seconds)  # Tick positions at intervals
    tick_labels = [int(pos / 60) for pos in tick_positions]  # Convert seconds to minutes for labels
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels)


def set_x_axis_units_ticks(ax: Axes, max_units: int, interval_units: int = 50) -> None:
    """
    Sets x-axis ticks at specified intervals.

    Parameters:
        ax (matplotlib.axes.Axes): The axes object to modify.
        max_units (int): The maximum value on the x-axis.
        interval_units (int): The interval between ticks (default is 50).
    """
    tick_positions = range(0, max_units + 1, interval_units)  # Tick positions at intervals
    ax.set_xticks(tick_positions)

def set_y_axis_units_ticks(ax: Axes, max_units: int, interval_units: int = 50) -> None:
    """
    Sets y-axis ticks at specified intervals.

    Parameters:
        ax (matplotlib.axes.Axes): The axes object to modify.
        max_units (int): The maximum value on the y-axis.
        interval_units (int): The interval between ticks (default is 50).
    """
    tick_positions = range(0, max_units + 1, interval_units)  # Tick positions at intervals
    ax.set_yticks(tick_positions)

