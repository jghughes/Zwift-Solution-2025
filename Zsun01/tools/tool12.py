import numpy as np
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
from datetime import datetime
from bestpower_for_model_training_item import BestPowerModelTrainingItem
from handy_utilities import read_dict_of_bestpowermodeltrainingItems, get_betel_IDs
import matplotlib.pyplot as plt
from matplot_utilities import set_x_axis_ticks,set_y_axis_ticks




def main():
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    BESTPOWER_DATA_FOR_MODEL_TRAINING_FILE_NAME = "bestpower_dataset_for_model_training.json"
    INPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"

    dict_of_modelTrainingItems = read_dict_of_bestpowermodeltrainingItems(BESTPOWER_DATA_FOR_MODEL_TRAINING_FILE_NAME, INPUT_DIRPATH)


if __name__ == "__main__":
    main()


