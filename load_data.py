import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def load_windarab_log(path, column_labels, preview = False):
    """
    Loads a file exported by WinDarab's "export text" functionality.
    :param path: string - the file path to the data log
    :param column_labels: list - the labels of the columns as they appear in the txt log file. Ex: ['Time', 'RPM']
    :param preview: boolean - If true, a plot is shown displaying a preview of the dataframe
    :return: the data frame of the log file
    """

    # load the data using numpy
    data = np.genfromtxt(path, skip_header=6, unpack=False)

    # create a data frame of the data
    df = pd.DataFrame(data)

    # check to make sure the oder is correct for labels!
    df.columns = column_labels

    # change index to Time
    df.set_index('Time', inplace=True)

    # display a graph of the channels over time
    if preview:
        for col in column_labels[1:]:
            plt.plot(df.index, df[col], label=col)

        plt.xlabel('Time [s]')
        plt.legend()
        plt.show()

    return df


data_labels = ['Time', 'Engine Temp', 'Oil Temp', 'Oil Pressure', 'RPM']
print(load_windarab_log('data/ford_data_log.txt', data_labels, True))
