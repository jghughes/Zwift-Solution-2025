import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler, StandardScaler
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

    xdata_bp_60 = [item.bp_60 for item in dict_of_modelTrainingItems.values()] # 3 min best
    xdata_bp_180 = [item.bp_180 for item in dict_of_modelTrainingItems.values()] # 3 min best
    xdata_bp_300 = [item.bp_300 for item in dict_of_modelTrainingItems.values()] # 5 min best
    xdata_bp_600 = [item.bp_600 for item in dict_of_modelTrainingItems.values()] # 10 min best
    xdata_bp_720 = [item.bp_720 for item in dict_of_modelTrainingItems.values()] # 12 min best
    xdata_bp_900 = [item.bp_900 for item in dict_of_modelTrainingItems.values()] # 12 min best
    xdata_bp_1200 = [item.bp_1200 for item in dict_of_modelTrainingItems.values()] # 20 min best
    xdata_bp_2400 = [item.bp_2400 for item in dict_of_modelTrainingItems.values()] # 40 min best
    ydata_zwift_ftp = [item.zwift_ftp for item in dict_of_modelTrainingItems.values()]
    ydata_zwiftracingapp_zpftp = [item.zwiftracingapp_zpFTP for item in dict_of_modelTrainingItems.values()]

    max_x = max(max(xdata_bp_60), max(xdata_bp_180), max(xdata_bp_300), max(xdata_bp_600), max(xdata_bp_720),max(xdata_bp_900), max(xdata_bp_1200), max(xdata_bp_2400))
    max_y = max(max(ydata_zwift_ftp), max(ydata_zwiftracingapp_zpftp))
    lim_x = max_x * 1.05
    lim_y = max_y * 1.05

    # plot 1

    plt.figure(figsize=(10, 6))
    plt.scatter(xdata_bp_60, ydata_zwift_ftp, color='brown', label='zwiftpower 90 day best - 1 minute')
    plt.scatter(xdata_bp_180, ydata_zwift_ftp, color='black', label='zwiftpower 90 day best - 3 minutes')
    plt.scatter(xdata_bp_300, ydata_zwift_ftp, color='grey', label='zwiftpower 90 day best - 5 minutes')
    plt.scatter(xdata_bp_600, ydata_zwift_ftp, color='purple', label='zwiftpower 90 day best - 10 minutes')
    plt.scatter(xdata_bp_720, ydata_zwift_ftp, color='red', label='zwiftpower 90 day best - 12 minutes')
    plt.scatter(xdata_bp_900, ydata_zwift_ftp, color='blue', label='zwiftpower 90 day best - 15 minutes')
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
    plt.scatter(xdata_bp_60, ydata_zwift_ftp, color='brown', label='zwiftpower 90 day best - 1 minute')
    plt.scatter(xdata_bp_180, ydata_zwift_ftp, color='black', label='zwiftpower 90 day best - 3 minutes')
    plt.scatter(xdata_bp_300, ydata_zwift_ftp, color='grey', label='zwiftpower 90 day best - 5 minutes')
    plt.scatter(xdata_bp_600, ydata_zwift_ftp, color='purple', label='zwiftpower 90 day best - 10 minutes')
    plt.scatter(xdata_bp_720, ydata_zwift_ftp, color='red', label='zwiftpower 90 day best - 12 minutes')
    plt.scatter(xdata_bp_900, ydata_zwift_ftp, color='blue', label='zwiftpower 90 day best - 15 minutes')
    plt.scatter(xdata_bp_1200, ydata_zwift_ftp, color='yellow', label='zwiftpower 90 day best - 20 minutes')
    plt.scatter(xdata_bp_2400, ydata_zwift_ftp, color='green', label='zwiftpower 90 day best - 40 minutes')

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


    # do modelling with linear regression

    # Prepare the data
    X = np.array([[item.bp_720, item.bp_900, item.bp_1200, item.bp_2400] for item in dict_of_modelTrainingItems.values()])
    y = np.array([item.zwiftracingapp_zpFTP for item in dict_of_modelTrainingItems.values()])

    # Normalize the features using Min-Max Scaling
    scaler = MinMaxScaler()
    X_normalized = scaler.fit_transform(X)

    # Alternatively, use Standardization (uncomment the following lines if preferred)
    # scaler = StandardScaler()
    # X_normalized = scaler.fit_transform(X)

    # Split the normalized data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.2, random_state=42)

    # Create and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    logger.info(f"R-squared: {r2}")
    logger.info(f"Mean Squared Error: {mse}")
    logger.info(f"Root Mean Squared Error: {rmse}")
   

    # Display the coefficients to analyze the influence of each factor
    coefficients = model.coef_
    features = ['bp_720', 'bp_900', 'bp_1200', 'bp_2400']
    for feature, coef in zip(features, coefficients):
        logger.info(f"Feature: {feature}, Coefficient: {coef}")

    # Predicted vs. Actual Values Plot
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, color='blue', alpha=0.6, label='Predicted vs Actual')
    plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--', label='Ideal Fit (y=x)')
    plt.xlabel('Actual Values (y_test)')
    plt.ylabel('Predicted Values (y_pred)')
    plt.title('Predicted vs Actual Values')
    plt.legend()
    plt.show()

    # Residuals Plot
    residuals = y_test - y_pred
    plt.figure(figsize=(10, 6))
    plt.scatter(y_pred, residuals, color='purple', alpha=0.6)
    plt.axhline(y=0, color='red', linestyle='--', label='Zero Residual Line')
    plt.xlabel('Predicted Values (y_pred)')
    plt.ylabel('Residuals (y_test - y_pred)')
    plt.title('Residuals Plot')
    plt.legend()
    plt.show()

    # Feature Importance (Coefficients)
    plt.figure(figsize=(10, 6))
    features = ['bp_720', 'bp_900', 'bp_1200', 'bp_2400']
    plt.bar(features, coefficients, color='green', alpha=0.7)
    plt.xlabel('Features')
    plt.ylabel('Coefficient Value')
    plt.title('Feature Importance (Regression Coefficients)')
    plt.show()

    # do modelling with linear regression without negative influence of item.bp_720 and bp_1200
    logger.info(f"\n\n\n\n\n\n\n\n\n\nSame linear regression, but this time excluding the -tve influence of 12 and 20min data")

    # Prepare the data
    X = np.array([[item.bp_900, item.bp_2400] for item in dict_of_modelTrainingItems.values()])
    y = np.array([item.zwiftracingapp_zpFTP for item in dict_of_modelTrainingItems.values()])

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)

    # Evaluate the model
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    logger.info(f"R-squared: {r2}")
    logger.info(f"Mean Squared Error: {mse}")
    logger.info(f"Root Mean Squared Error: {rmse}")
   

    # Display the coefficients to analyze the influence of each factor
    coefficients = model.coef_
    features = ['bp_900', 'bp_2400']
    for feature, coef in zip(features, coefficients):
        logger.info(f"Feature: {feature}, Coefficient: {coef}")

    # Predicted vs. Actual Values Plot
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, color='blue', alpha=0.6, label='Predicted vs Actual')
    plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--', label='Ideal Fit (y=x)')
    plt.xlabel('Actual Values (y_test)')
    plt.ylabel('Predicted Values (y_pred)')
    plt.title('Predicted vs Actual Values')
    plt.legend()
    plt.show()

    # Residuals Plot
    residuals = y_test - y_pred
    plt.figure(figsize=(10, 6))
    plt.scatter(y_pred, residuals, color='purple', alpha=0.6)
    plt.axhline(y=0, color='red', linestyle='--', label='Zero Residual Line')
    plt.xlabel('Predicted Values (y_pred)')
    plt.ylabel('Residuals (y_test - y_pred)')
    plt.title('Residuals Plot')
    plt.legend()
    plt.show()

    # Feature Importance (Coefficients)
    plt.figure(figsize=(10, 6))
    features = ['bp_900', 'bp_2400']
    plt.bar(features, coefficients, color='green', alpha=0.7)
    plt.xlabel('Features')
    plt.ylabel('Coefficient Value')
    plt.title('Feature Importance (Regression Coefficients)')
    plt.show()











































    # good. but not great.  let's try a inverse exponential decay model

    # from jgh_power_curve_fit_models import decay_model_numpy
    # from scipy.optimize import curve_fit

    #     # Prepare the data
    # X = np.array([[item.bp_720, item.bp_900, item.bp_1200, item.bp_2400] for item in dict_of_modelTrainingItems.values()])
    # y = np.array([item.zwiftracingapp_zpFTP for item in dict_of_modelTrainingItems.values()])

    # # Fit the inverse exponential model for each feature
    # fitted_params = {}
    # for i, feature_name in enumerate(['bp_720', 'bp_900', 'bp_1200', 'bp_2400']):
    #     xdata = X[:, i]  # Extract the feature column
    #     try:
    #         # Fit the decay model
    #         popt, _ = curve_fit(decay_model_numpy, xdata, y, bounds=(0, np.inf))
    #         fitted_params[feature_name] = popt  # Store the fitted parameters (a, b)
    #         logger.info(f"Fitted parameters for {feature_name}: a={popt[0]}, b={popt[1]}")
    #     except RuntimeError as e:
    #         logger.error(f"Could not fit decay model for {feature_name}: {e}")

    # # Evaluate the model
    # for feature_name, params in fitted_params.items():
    #     a, b = params
    #     xdata = X[:, ['bp_720', 'bp_900', 'bp_1200', 'bp_2400'].index(feature_name)]
    #     y_pred = decay_model_numpy(xdata, a, b)
    #     mse = mean_squared_error(y, y_pred)
    #     r2 = r2_score(y, y_pred)
    #     logger.info(f"Evaluation for {feature_name}: MSE={mse}, R-squared={r2}")


if __name__ == "__main__":
    main()


