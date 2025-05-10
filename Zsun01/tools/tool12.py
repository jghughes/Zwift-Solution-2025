import numpy as np
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
from datetime import datetime
from bestpower_for_model_training_item import BestPowerModelTrainingItem
from handy_utilities import read_dict_of_bestpowermodeltrainingItems
import matplotlib.pyplot as plt
from matplot_utilities import set_x_axis_units_ticks,set_y_axis_units_ticks




def main():
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    BESTPOWER_DATA_FOR_MODEL_TRAINING_FILE_NAME = "bestpower_dataset_for_model_training.json"
    INPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"

    dict_of_candidate_modelTrainingItems = read_dict_of_bestpowermodeltrainingItems(BESTPOWER_DATA_FOR_MODEL_TRAINING_FILE_NAME, INPUT_DIRPATH)


    # filter out all items with item.zwift_ftp == 0.0 or item.zwiftracingapp_zpFTP == 0.0 or item.item.bp_720 == 0.0 or item.item.bp_1200 == 0.0 or item.item.bp_2400 == 0.0. make a new dict
    dict_of_modelTrainingItems = {k: v for k, v in dict_of_candidate_modelTrainingItems.items() if v.zwiftracingapp_zpFTP > 0.0 and v.zwift_ftp > 0.0 and v.bp_720 > 0.0 and v.bp_1200 > 0.0 and v.bp_2400 > 0.0}

    logger.info(f"\nLoaded : {len(dict_of_candidate_modelTrainingItems)} items")
    logger.info(f"Eliminated: {len(dict_of_candidate_modelTrainingItems) - len(dict_of_modelTrainingItems)} partially zero items")
    logger.info(f"Clean sample: {len(dict_of_modelTrainingItems)} items")

    xdata_bp_720 = [item.bp_720 for item in dict_of_modelTrainingItems.values()] # 12 min best
    xdata_bp_1200 = [item.bp_1200 for item in dict_of_modelTrainingItems.values()] # 20 min best
    xdata_bp_2400 = [item.bp_2400 for item in dict_of_modelTrainingItems.values()] # 40 min best
    ydata_zwift_ftp = [item.zwift_ftp for item in dict_of_modelTrainingItems.values()]
    ydata_zwiftracingapp_zpftp = [item.zwiftracingapp_zpFTP for item in dict_of_modelTrainingItems.values()]

    max_x = max(max(xdata_bp_720), max(xdata_bp_1200), max(xdata_bp_2400))
    max_y = max(max(ydata_zwift_ftp), max(ydata_zwiftracingapp_zpftp))
    lim_x = max_x * 1.05
    lim_y = max_y * 1.05

    # plot 1

    plt.figure(figsize=(10, 6))
    plt.scatter(xdata_bp_720, ydata_zwift_ftp, color='red', label='zwiftpower 90 day best - 12 minutes')
    plt.scatter(xdata_bp_1200, ydata_zwift_ftp, color='yellow', label='zwiftpower 90 day best - 20 minutes')
    plt.scatter(xdata_bp_2400, ydata_zwift_ftp, color='green', label='zwiftpower 90 day best - 40 minutes')

    plt.xlabel('ZwiftPower 90 day best (Watts)')
    plt.ylabel('ZwiftProfile (Watts)')
    plt.title(f'Scatter-plot of ZwiftProfile ftp versus ZwiftPower 90-best datasets')
    plt.title(f'Scatter-plot of ZwiftPower 90-best datasets (x axis) versus ZwiftProfile ftp (y axis)')
    plt.xlim(0, lim_x)
    plt.ylim(0, lim_y)
    ax = plt.gca()  # Get the current axes
    set_x_axis_units_ticks(ax, int(max_x), 50)  # Set x-axis ticks
    set_y_axis_units_ticks(ax, int(max_y), 50)  # Set y-axis ticks
    plt.legend()
    plt.show()


    # plot 2

    plt.figure(figsize=(10, 6))
    plt.scatter(xdata_bp_720, ydata_zwiftracingapp_zpftp, color='red', label='zwiftpower 90 day best - 12 minutes')
    plt.scatter(xdata_bp_1200, ydata_zwiftracingapp_zpftp, color='yellow', label='zwiftpower 90 day best - 20 minutes')
    plt.scatter(xdata_bp_2400, ydata_zwiftracingapp_zpftp, color='green', label='zwiftpower 90 day best - 40 minutes')

    plt.xlabel('ZwiftPower 90 day best (Watts)')
    plt.ylabel('ZwiftRacingApp zpFTP (Watts)')
    plt.title(f'Scatter-plot of ZwiftPower 90-best datasets (x axis) versus ZwiftRacingApp zpFTP (y axis)')
    plt.xlim(0, lim_x)
    plt.ylim(0, lim_y)
    ax = plt.gca()  # Get the current axes
    set_x_axis_units_ticks(ax, int(max_x), 50)  # Set x-axis ticks
    set_y_axis_units_ticks(ax, int(max_y), 50)  # Set y-axis ticks
    plt.legend()
    plt.show()

    # plot 3

    plt.figure(figsize=(10, 6))
    plt.scatter(ydata_zwift_ftp, ydata_zwiftracingapp_zpftp, color='red', label='coordinates')
    plt.xlabel('ZwiftProfile ftp (Watts)')
    plt.ylabel('ZwiftRacingApp zpFTP (Watts)')
    plt.title(f'Scatter-plot of ZwiftProfile ftp datasets (x axis) versus ZwiftRacingApp zpFTP (y axis)')
    plt.xlim(0, lim_x)
    plt.ylim(0, lim_y)
    ax = plt.gca()  # Get the current axes
    set_x_axis_units_ticks(ax, int(max_x), 50)  # Set x-axis ticks
    set_y_axis_units_ticks(ax, int(max_y), 50)  # Set y-axis ticks
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()


