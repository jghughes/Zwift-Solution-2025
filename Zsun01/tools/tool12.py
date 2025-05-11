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
    dict_of_modelTrainingItems = {k: v for k, v in dict_of_candidate_modelTrainingItems.items() if v.zwiftracingapp_zpFTP > 0.0 and v.zwift_ftp > 0.0 and v.bp_900 > 0.0 and v.bp_1200 > 0.0 and v.bp_1800 > 0.0 and v.bp_2400 > 0.0}

    logger.info(f"\nLoaded : {len(dict_of_candidate_modelTrainingItems)} items")
    logger.info(f"Eliminated: {len(dict_of_candidate_modelTrainingItems) - len(dict_of_modelTrainingItems)} partially zero items")
    logger.info(f"Clean sample: {len(dict_of_modelTrainingItems)} items")

    # xdata_bp_60 = [item.bp_60 for item in dict_of_modelTrainingItems.values()] # 3 min best
    # xdata_bp_180 = [item.bp_180 for item in dict_of_modelTrainingItems.values()] # 3 min best
    # xdata_bp_300 = [item.bp_300 for item in dict_of_modelTrainingItems.values()] # 5 min best
    # xdata_bp_600 = [item.bp_600 for item in dict_of_modelTrainingItems.values()] # 10 min best
    # xdata_bp_720 = [item.bp_720 for item in dict_of_modelTrainingItems.values()] # 12 min best
    # xdata_bp_900 = [item.bp_900 for item in dict_of_modelTrainingItems.values()] # 12 min best
    # xdata_bp_1200 = [item.bp_1200 for item in dict_of_modelTrainingItems.values()] # 20 min best
    # xdata_bp_1800 = [item.bp_1800 for item in dict_of_modelTrainingItems.values()] # 30 min best
    # xdata_bp_2400 = [item.bp_2400 for item in dict_of_modelTrainingItems.values()] # 40 min best
    # xdata_zsun_curve_fit = [item.zsun_one_hour_watts for item in dict_of_modelTrainingItems.values()] # 40 min best
    # ydata_zwiftprofile_ftp = [item.zwift_ftp for item in dict_of_modelTrainingItems.values()]
    # ydata_zwiftracingapp_zpftp = [item.zwiftracingapp_zpFTP for item in dict_of_modelTrainingItems.values()]

    # max_x = max(max(xdata_bp_60), max(xdata_bp_180), max(xdata_bp_300), max(xdata_bp_600), max(xdata_bp_720),max(xdata_bp_900), max(xdata_bp_1200), max(xdata_bp_1800), max(xdata_bp_2400), max(xdata_zsun_curve_fit))
    # max_y = max(max(ydata_zwiftprofile_ftp), max(ydata_zwiftracingapp_zpftp))
    # lim_x = max_x * 1.05
    # lim_y = max_y * 1.05

    # # plot 1

    # plt.figure(figsize=(10, 6))
    # # plt.scatter(xdata_bp_60, ydata_zwiftprofile_ftp, color='brown', label='zwiftpower 90 day best - 1 minute')
    # # plt.scatter(xdata_bp_180, ydata_zwiftprofile_ftp, color='black', label='zwiftpower 90 day best - 3 minutes')
    # # plt.scatter(xdata_bp_300, ydata_zwiftprofile_ftp, color='grey', label='zwiftpower 90 day best - 5 minutes')
    # plt.scatter(xdata_bp_600, ydata_zwiftprofile_ftp, color='purple', label='zwiftpower 90 day best - 10 minutes')
    # plt.scatter(xdata_bp_720, ydata_zwiftprofile_ftp, color='red', label='zwiftpower 90 day best - 12 minutes')
    # plt.scatter(xdata_bp_900, ydata_zwiftprofile_ftp, color='blue', label='zwiftpower 90 day best - 15 minutes')
    # plt.scatter(xdata_bp_1200, ydata_zwiftprofile_ftp, color='yellow', label='zwiftpower 90 day best - 20 minutes')
    # plt.scatter(xdata_bp_1800, ydata_zwiftprofile_ftp, color='orange', label='zwiftpower 90 day best - 30 minutes')
    # plt.scatter(xdata_bp_2400, ydata_zwiftprofile_ftp, color='green', label='zwiftpower 90 day best - 40 minutes')
    # plt.scatter(xdata_zsun_curve_fit, ydata_zwiftprofile_ftp, color='indigo', label='zsun curve fit - 40 minutes')

    # plt.xlabel('ZwiftPower 90 day best (Watts)')
    # plt.ylabel('ZwiftProfile (Watts)')
    # plt.title(f'Scatter-plot of ZwiftProfile ftp versus ZwiftPower 90-best datasets')
    # plt.title(f'Scatter-plot of ZwiftPower 90-best datasets (x axis) versus ZwiftProfile ftp (y axis)')
    # plt.xlim(0, lim_x)
    # plt.ylim(0, lim_y)
    # ax = plt.gca()  # Get the current axes
    # set_x_axis_units_ticks(ax, int(max_x), 50)  # Set x-axis ticks
    # set_y_axis_units_ticks(ax, int(max_y), 50)  # Set y-axis ticks
    # plt.legend()
    # plt.show()


    # # plot 2

    # plt.figure(figsize=(10, 6))
    # # plt.scatter(xdata_bp_60, ydata_zwiftracingapp_zpftp, color='brown', label='zwiftpower 90 day best - 1 minute')
    # # plt.scatter(xdata_bp_180, ydata_zwiftracingapp_zpftp, color='black', label='zwiftpower 90 day best - 3 minutes')
    # # plt.scatter(xdata_bp_300, ydata_zwiftracingapp_zpftp, color='grey', label='zwiftpower 90 day best - 5 minutes')
    # plt.scatter(xdata_bp_600, ydata_zwiftracingapp_zpftp, color='purple', label='zwiftpower 90 day best - 10 minutes')
    # plt.scatter(xdata_bp_720, ydata_zwiftracingapp_zpftp, color='red', label='zwiftpower 90 day best - 12 minutes')
    # plt.scatter(xdata_bp_900, ydata_zwiftracingapp_zpftp, color='blue', label='zwiftpower 90 day best - 15 minutes')
    # plt.scatter(xdata_bp_1200, ydata_zwiftracingapp_zpftp, color='yellow', label='zwiftpower 90 day best - 20 minutes')
    # plt.scatter(xdata_bp_1800, ydata_zwiftracingapp_zpftp, color='orange', label='zwiftpower 90 day best - 20 minutes')
    # plt.scatter(xdata_bp_2400, ydata_zwiftracingapp_zpftp, color='green', label='zwiftpower 90 day best - 40 minutes')
    # plt.scatter(xdata_zsun_curve_fit, ydata_zwiftracingapp_zpftp, color='indigo', label='zsun curve fit - 40 minutes')
    # plt.xlabel('ZwiftPower 90 day best (Watts)')
    # plt.ylabel('ZwiftRacingApp zpFTP (Watts)')
    # plt.title(f'Scatter-plot of ZwiftPower 90-best datasets (x axis) versus ZwiftRacingApp zpFTP (y axis)')
    # plt.xlim(0, lim_x)
    # plt.ylim(0, lim_y)
    # ax = plt.gca()  # Get the current axes
    # set_x_axis_units_ticks(ax, int(max_x), 50)  # Set x-axis ticks
    # set_y_axis_units_ticks(ax, int(max_y), 50)  # Set y-axis ticks
    # plt.legend()
    # plt.show()

    # # plot 3

    # plt.figure(figsize=(10, 6))
    # plt.scatter(ydata_zwiftprofile_ftp, ydata_zwiftracingapp_zpftp, color='red', label='coordinates')
    # plt.xlabel('ZwiftProfile ftp (Watts)')
    # plt.ylabel('ZwiftRacingApp zpFTP (Watts)')
    # plt.title(f'Scatter-plot of ZwiftProfile ftp datasets (x axis) versus ZwiftRacingApp zpFTP (y axis)')
    # plt.xlim(0, lim_x)
    # plt.ylim(0, lim_y)
    # ax = plt.gca()  # Get the current axes
    # set_x_axis_units_ticks(ax, int(max_x), 50)  # Set x-axis ticks
    # set_y_axis_units_ticks(ax, int(max_y), 50)  # Set y-axis ticks
    # plt.legend()
    # plt.show()


















    # # do modelling with linear regression

    # # Prepare the data
    # X = np.array([[item.bp_600, item.bp_720, item.bp_900, item.bp_1200, item.bp_1800, item.bp_2400] for item in dict_of_modelTrainingItems.values()])
    # y = np.array([item.zwiftracingapp_zpFTP for item in dict_of_modelTrainingItems.values()])

    # # Normalize the features using Min-Max Scaling
    # # scaler = MinMaxScaler()
    # # X_normalized = scaler.fit_transform(X)

    # # Alternatively, use Standardization (uncomment the following lines if preferred)
    # scaler = StandardScaler()
    # X_normalized = scaler.fit_transform(X)

    # # Split the normalized data into training and testing sets
    # X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.6, random_state=42)

    # # Create and train the model
    # model = LinearRegression()
    # model.fit(X_train, y_train)

    # # Make predictions
    # y_pred = model.predict(X_test)

    # # Evaluate the model
    # r2 = r2_score(y_test, y_pred)
    # mse = mean_squared_error(y_test, y_pred)
    # rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # errorbarMsg = f"R-squared: {r2:.2} RMSE: {rmse:.3g}"
    # logger.info(errorbarMsg)


    # # Display the coefficients to analyze the influence of each factor
    # coefficients = model.coef_
    # features = ['bp_600', 'bp_720', 'bp_900', 'bp_1200', 'bp_1800', 'bp_2400']
    # for feature, coef in zip(features, coefficients):
    #     logger.info(f"Feature: {feature}, Coefficient: {coef}")

    # # Predicted vs. Actual Values Plot
    # plt.figure(figsize=(10, 6))
    # plt.scatter(y_test, y_pred, color='blue', alpha=0.6, label=f'Predicted vs Actual [{errorbarMsg}]')
    # plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--', label='Ideal Fit (y=x)')
    # plt.xlabel('Actual Values (y_test)')
    # plt.ylabel('Predicted Values (y_pred)')
    # plt.title('Predicted vs Actual Values')
    # plt.legend()
    # plt.show()

    # # Residuals Plot
    # residuals = y_test - y_pred
    # plt.figure(figsize=(10, 6))
    # plt.scatter(y_pred, residuals, color='purple', alpha=0.6)
    # plt.axhline(y=0, color='red', linestyle='--', label='Zero Residual Line')
    # plt.xlabel('Predicted Values (y_pred)')
    # plt.ylabel('Residuals (y_test - y_pred)')
    # plt.title('Residuals Plot')
    # plt.legend()
    # plt.show()

    # # Feature Importance (Coefficients)
    # plt.figure(figsize=(10, 6))
    # features = ['bp_600', 'bp_720', 'bp_900', 'bp_1200', 'bp_1800', 'bp_2400']
    # plt.bar(features, coefficients, color='green', alpha=0.7)
    # plt.xlabel('Features')
    # plt.ylabel('Coefficient Value')
    # plt.title('Feature Importance (Regression Coefficients)')
    # plt.show()









    # # do modelling with linear regression - this time we are modelling ourself - this should result in perfection

    # # Prepare the data
    # X = np.array([[item.zwiftracingapp_zpFTP] for item in dict_of_modelTrainingItems.values()])
    # y = np.array([item.zwiftracingapp_zpFTP for item in dict_of_modelTrainingItems.values()])

    # # Normalize the features using Min-Max Scaling
    # # scaler = MinMaxScaler()
    # # X_normalized = scaler.fit_transform(X)

    # # Alternatively, use Standardization (uncomment the following lines if preferred)
    # scaler = StandardScaler()
    # X_normalized = scaler.fit_transform(X)

    # # Split the normalized data into training and testing sets
    # X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.6, random_state=42)

    # # Create and train the model
    # model = LinearRegression()
    # model.fit(X_train, y_train)

    # # Make predictions
    # y_pred = model.predict(X_test)

    # # Evaluate the model
    # r2 = r2_score(y_test, y_pred)
    # mse = mean_squared_error(y_test, y_pred)
    # rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # errorbarMsg = f"R-squared: {r2:.2} RMSE: {rmse:.3g}"
    # logger.info(errorbarMsg)

    # # Display the coefficients to analyze the influence of each factor
    # coefficients = model.coef_
    # features = ['zwiftracingapp_zpFTP']
    # for feature, coef in zip(features, coefficients):
    #     logger.info(f"Feature: {feature}, Coefficient: {coef:.3}")

    # # Predicted vs. Actual Values Plot
    # plt.figure(figsize=(10, 6))
    # plt.scatter(y_test, y_pred, color='blue', alpha=0.6, label=f'Predicted vs Actual [{errorbarMsg}]')
    # plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--', label='Ideal Fit (y=x)')
    # plt.xlabel('Actual Values (y_test)')
    # plt.ylabel('Predicted Values (y_pred)')
    # plt.title('Predicted vs Actual Values  - self versus self')
    # plt.legend()
    # plt.show()

    # # Residuals Plot
    # residuals = y_test - y_pred
    # plt.figure(figsize=(10, 6))
    # plt.scatter(y_pred, residuals, color='purple', alpha=0.6)
    # plt.axhline(y=0, color='red', linestyle='--', label='Zero Residual Line')
    # plt.xlabel('Predicted Values (y_pred)')
    # plt.ylabel('Residuals (y_test - y_pred)')
    # plt.title('Residuals Plot - self versus self')
    # plt.legend()
    # plt.show()

    # # Feature Importance (Coefficients)
    # plt.figure(figsize=(10, 6))
    # features = ['zwiftracingapp_zpFTP']
    # plt.bar(features, coefficients, color='green', alpha=0.7)
    # plt.xlabel('Features')
    # plt.ylabel('Coefficient Value')
    # plt.title('Feature Importance (Regression Coefficients) - self versus self')
    # plt.show()




    # # # do modelling with our own decay curve via the ML model

    # # Prepare the data
    # X = np.array([[item.zsun_one_hour_watts] for item in dict_of_modelTrainingItems.values()])
    # y = np.array([item.zwiftracingapp_zpFTP for item in dict_of_modelTrainingItems.values()])

    # # Normalize the features using Min-Max Scaling
    # # scaler = MinMaxScaler()
    # # X_normalized = scaler.fit_transform(X)

    # # Alternatively, use Standardization (uncomment the following lines if preferred)
    # scaler = StandardScaler()
    # X_normalized = scaler.fit_transform(X)

    # # Split the normalized data into training and testing sets
    # X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.6, random_state=42)

    # # Create and train the model
    # model = LinearRegression()
    # model.fit(X_train, y_train)

    # # Make predictions
    # y_pred = model.predict(X_test)

    # # Evaluate the model
    # r2 = r2_score(y_test, y_pred)
    # mse = mean_squared_error(y_test, y_pred)
    # rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # errorbarMsg = f"R-squared: {r2:.2} RMSE: {rmse:.3g}"
    # logger.info(errorbarMsg)

    # # Display the coefficients to analyze the influence of each factor
    # coefficients = model.coef_
    # features = ['zsun_one_hour_watts']
    # for feature, coef in zip(features, coefficients):
    #     logger.info(f"Feature: {feature}, Coefficient: {coef:.3}")

    # # Predicted vs. Actual Values Plot
    # plt.figure(figsize=(10, 6))
    # plt.scatter(y_test, y_pred, color='blue', alpha=0.6, label=f'Predicted vs Actual [{errorbarMsg}]')
    # plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--', label='Ideal Fit (y=x)')
    # plt.xlabel('Actual Values (y_test)')
    # plt.ylabel('Predicted Values (y_pred)')
    # plt.title('Predicted vs Actual Values  - ZwiftPower zFTP versus zsun 40 minute watts')
    # plt.legend()
    # plt.show()

    # # Residuals Plot
    # residuals = y_test - y_pred
    # plt.figure(figsize=(10, 6))
    # plt.scatter(y_pred, residuals, color='purple', alpha=0.6)
    # plt.axhline(y=0, color='red', linestyle='--', label='Zero Residual Line')
    # plt.xlabel('Predicted Values (y_pred)')
    # plt.ylabel('Residuals (y_test - y_pred)')
    # plt.title('Residuals Plot - self versus self')
    # plt.legend()
    # plt.show()

    # # Feature Importance (Coefficients)
    # plt.figure(figsize=(10, 6))
    # features = ['zwiftracingapp_zpFTP']
    # plt.bar(features, coefficients, color='green', alpha=0.7)
    # plt.xlabel('Features')
    # plt.ylabel('Coefficient Value')
    # plt.title('Feature Importance (Regression Coefficients) - ZwiftPower zFTP versus zsun 40 minute watts')
    # plt.show()


    # # now finally the tour de force - use our own zsun model directlye ML model

    # Prepare the data
    X = np.array([[item.zsun_40_minute_watts] for item in dict_of_modelTrainingItems.values()])
    y = np.array([item.zwiftracingapp_zpFTP for item in dict_of_modelTrainingItems.values()])

    # Normalize the features using Min-Max Scaling
    # scaler = MinMaxScaler()
    # X_normalized = scaler.fit_transform(X)

    # # Alternatively, use Standardization (uncomment the following lines if preferred)
    # scaler = StandardScaler()
    # X_normalized = scaler.fit_transform(X)

    # Split the normalized data into training and testing sets
    # X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.6, random_state=42)

    # Create and train the model
    # model = LinearRegression()
    # model.fit(X_train, y_train)

    # Make predictions
    # y_pred = X_normalized
    y_pred = X
    y_test = y
    logger.info(f"y_test: {len(y_test)}")
    logger.info(f"y_pred: {len(y_pred)}")

    # Evaluate the model
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    errorbarMsg = f"R-squared: {r2:.2} RMSE: {rmse:.3g}"
    logger.info(errorbarMsg)

    # # Display the coefficients to analyze the influence of each factor
    # coefficients = model.coef_
    # features = ['zsun_one_hour_watts']
    # for feature, coef in zip(features, coefficients):
    #     logger.info(f"Feature: {feature}, Coefficient: {coef:.3}")

    # Predicted vs. Actual Values Plot
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, color='blue', alpha=0.6, label=f'Predicted vs Actual [{errorbarMsg}]')
    plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--', label='Ideal Fit (y=x)')
    plt.xlabel('Actual Values (y_test)')
    plt.ylabel('Predicted Values (y_pred)')
    plt.title('Predicted vs Actual Values - ZwiftPower_zFTP versus zsun_40_minute_watts')
    plt.legend()
    plt.show()

    # # Residuals Plot
    # residuals = y_test - y_pred
    # logger.info(f"residuals: {len(residuals)}")
    # plt.figure(figsize=(10, 6))
    # plt.scatter(y_pred, residuals, color='purple', alpha=0.6)
    # plt.axhline(y=0, color='red', linestyle='--', label='Zero Residual Line')
    # plt.xlabel('Predicted Values (y_pred)')
    # plt.ylabel('Residuals (y_test - y_pred)')
    # plt.title('Residuals Plot - ZwiftPower_zFTP versus zsun_40_minute_watts')
    # plt.legend()
    # plt.show()

    # # Feature Importance (Coefficients)
    # plt.figure(figsize=(10, 6))
    # features = ['zwiftracingapp_zpFTP']
    # plt.bar(features, coefficients, color='green', alpha=0.7)
    # plt.xlabel('Features')
    # plt.ylabel('Coefficient Value')
    # plt.title('Feature Importance (Regression Coefficients) - ZwiftPower zFTP versus zsun 40 minute watts')
    # plt.show()




if __name__ == "__main__":
    main()


