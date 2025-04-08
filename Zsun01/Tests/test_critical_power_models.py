import numpy as np

from critical_power_metrics import map_zwiftridercriticalpoweritem_to_xy_lists, exponential_curve_formula



def hyperbolic_model(x: np.ndarray, w_prime: float, crit_power: float) -> np.ndarray:
    # this is the hyperbolic model used to calculate critical power and w_prime
    y = (w_prime + crit_power * x) / x
    return y

def log_linear_model(x: np.ndarray, a: float, b: float) -> np.ndarray:
    # this is the log-linear model
    y = a * np.log(x) + b
    return y


def main() -> None:
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    from sklearn.metrics import r2_score
    from handy_utilities import get_all_zwiftriders, get_all_zwiftriders_cp_data

    # Suppress matplotlib font matching logs.
    # This provides privided interesting logging messages, but suppresses a deluge of font matching messages
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

    barryb ='5490373' 
    johnh ='58160'
    lynseys ='383480'
    joshn ='2508033'
    richardm ='1193'
    markb ='5530045'

    riders = get_all_zwiftriders()
    metrics = get_all_zwiftriders_cp_data()

    # set the rider to the one you want to test
    rider_id = joshn

    xdata, ydata = map_zwiftridercriticalpoweritem_to_xy_lists(metrics[rider_id])
    # xdata, ydata = unbundle_cp_data_from_dict_of_duration_and_power(metrics[rider_id].map_to_int_float_equivalent())
    xdata = np.array(xdata)
    ydata = np.array(ydata)

    # Filter data for the duration range in a window from 180 to 300 seconds to deal out the outliers where least
    #squares fitting distorts the overall result
    mask = (xdata >= 60) & (xdata <= 2400)
    xdata_filtered = xdata[mask]
    ydata_filtered = ydata[mask]

    # Fit the exponential model to the filtered data - this is the best fit for our purposes
    popt_filtered, pcov_filtered = curve_fit(exponential_curve_formula, xdata_filtered, ydata_filtered)
    y_pred_filtered = exponential_curve_formula(xdata_filtered, *popt_filtered)
    r_squared_filtered = r2_score(ydata_filtered, y_pred_filtered)
    logger.info(f"\nExponential model (filtered): {riders[rider_id].name} popt_filtered: {popt_filtered} R squared: {r_squared_filtered}")

    # since this is our preferred model, we can use the fitted parameters to predict the power for a full data set out to 60 minutes
    xdata_full = np.arange(30, 60*60, 30)  # 30 second intervals
    ydata_full = exponential_curve_formula(xdata_full, *popt_filtered)
    #log the x=60*60 value of ydata_full
    logger.info(f"\nExponential model (full data): {riders[rider_id].name} 60min power: {ydata_full[-1]}")

    # Fit the exponential model to the full data
    popt01, pcov = curve_fit(exponential_curve_formula, xdata, ydata)  # popt01 is a tuple of the fitted parameters
    y_pred01 = exponential_curve_formula(xdata, *popt01)
    r_squared01 = r2_score(ydata, y_pred01)
    logger.info(f"\nExponential model: {riders[rider_id].name} popt01: {popt01} R squared: {r_squared01}")

    # hyperbolic_model
    popt02, pcov = curve_fit(hyperbolic_model, xdata, ydata)
    y_pred02 = hyperbolic_model(xdata, *popt02)
    r_squared02 = r2_score(ydata, y_pred02)
    logger.info(f"\nHyperbolic model: {riders[rider_id].name} popt02: {popt02} R squared: {r_squared02}")

    # log_linear_model
    popt04, pcov = curve_fit(log_linear_model, xdata, ydata)
    y_pred04 = log_linear_model(xdata, *popt04)
    r_squared04 = r2_score(ydata, y_pred04)
    logger.info(f"\nLog-linear model: {riders[rider_id].name} popt04: {popt04} R squared: {r_squared04}")

    # plot everything
    plt.figure(figsize=(10, 6))
    plt.scatter(xdata, ydata, color='blue', label='raw data')
    plt.plot(xdata, y_pred01, color='red', label=f'exponential curve (y = a * x ** b) where a: {round(popt01[0])}, b:{round(popt01[1], 4)}, R_squared: {round(r_squared01, 2)}')
    plt.plot(xdata, y_pred02, color='green', label=f'hyperbolic curve (y = (w_prime + crit_power*x)/x) where w_prime: {round(popt02[0])}, crit_power:{round(popt02[1], 4)}, R_squared: {round(r_squared02, 2)}')
    plt.plot(xdata, y_pred04, color='purple', label=f'log-linear curve (y = a * log(x) + b) where a: {round(popt04[0])}, b:{round(popt04[1], 4)}, R_squared: {round(r_squared04, 2)}')
    plt.plot(xdata_filtered, y_pred_filtered, color='orange', label=f'best fit curve for Zwift data (60 sec to 40 min)')
    plt.xlabel('Duration (s)')
    plt.ylabel('Power (W)')
    plt.title(f'{riders[rider_id].name} - Zwift metrics')
    plt.xticks(xdata)  
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
