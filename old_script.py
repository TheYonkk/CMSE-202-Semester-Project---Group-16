import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit
from datetime import datetime

##############################################################################################################
#
# PARAMETERS
#
#   How to use:
#       1. Change the input file path/name. This should point to the txt file exported by WinDarab.
#          Note: You should export the data with ONLY oil pressure and rpm. Darab puts oil pressure first,
#          so if your input file is different for whatever reason, you must swap the "unpack arrays" line
#       2. Change the rpm lower bound. The script will only take into consideration rpm values above the bound
#       3. Specify the output file name. You must include ".png" or ".jpg"
##############################################################################################################

# only run an optimization for points above this rpm
RPM_LOWER_BOUND = 2500

# path to the txt file exported by darab
good_data_path = "data/sample_good_oilp_2.txt"

# path to the bad data (if applicable)
bad_data_path = "sample_data/sample_bad_oilp_1.txt"

# if you would like to also plot bad oil pressure to see how well the function may predict failures
plot_bad_data = True

# percentage plot (the percent of the function - useful for determining safety cutoffs)
cutoff_percent = 70
plot_cutoff_percent = True

# what to save the plot as
output_image_name = "lower_cutoff.png"

# what to save the c++ styled function as (WinDarab function also included in file)
output_file_name = "oilp_prediction.cpp"


##############################################################################################################
#
# CALCULATIONS
#
##############################################################################################################

# unpack the data into numpy arrays
time, oilp, rpm = np.genfromtxt(good_data_path, skip_header=6, unpack=True)

# copy the data for graphing purposes
rpm_full = rpm
oilp_full = oilp

# use only rpm and oilp values above the lower rpm bound for calculations
oilp = oilp[rpm > RPM_LOWER_BOUND]
rpm = rpm[rpm > RPM_LOWER_BOUND]


# natural log function fits the data pretty well
def oilp_function(rpm_val, a, b, c):
    return a * np.log(rpm_val + b) + c


# use least-squares method to find optimal parameters
popt, pcov = curve_fit(oilp_function, rpm, oilp)

# unpack the parameters that were generated
A_param = popt[0]
B_param = popt[1]
C_param = popt[2]

# use the parameters to make a set of points to plot for visualization
rpm_range_points = np.arange(RPM_LOWER_BOUND, rpm.max(), 1)
curve_fit_points = oilp_function(rpm_range_points, A_param, B_param, C_param)

# plotting shenanigans...
sns.set_style("whitegrid")
sns.set_palette("Purples_r")
plt.scatter(rpm_full, oilp_full, marker='.', alpha=0.15, color="grey", label="Sample Data")

# if the user elected to plot bad data. unpack is the same as data above
if plot_bad_data:
    time_b, oilp_b, rpm_b = np.genfromtxt(bad_data_path, skip_header=6, unpack=True)
    plt.scatter(rpm_b, oilp_b, marker='.', alpha=0.15, color="tab:red", label="Failure Data")

plt.plot(rpm_range_points, curve_fit_points, linewidth=3,
         label="{:.2f} * ln(rpm + {:.2f}) + {:.2f}".format(A_param, B_param, C_param))

# cutoff plot
if plot_cutoff_percent:
    plt.plot(rpm_range_points, curve_fit_points * (cutoff_percent / 100), linewidth=3,
             label="{}% cutoff".format(cutoff_percent), color="tab:orange")

plt.xlabel("RPM")
plt.ylabel("Oil Pressure [psi]")
plt.title("RPM vs. Oil Pressure")
plt.legend()
sns.despine()
plt.savefig(output_image_name, dpi=600)
plt.show()

# output file generation
fp = open(output_file_name, "w")
now = datetime.now()
data_string = '''\
// C++ function generator for rpm-based oil pressure prediction
// Dave Yonkers, 2020
// 
// Function generated: {}\n\n
'''.format(now.strftime("%m/%d/%Y %H:%M:%S"))
fp.write(data_string)

# write WinDarab function
fp.write("// WinDarab function:\n")
fp.write("// {:.3f} * ln({{M400_rpm}} {:+.3f}) {:+.3f}\n\n".format(A_param, B_param, C_param))

# write cpp function
fp.write("// C++ function:\n")
fp.write("float oil_pressure_prediction(StateSignal &rpm){\n")
fp.write("\treturn {:.3f} * log(rpm.value() {:+.3f}) {:+.3f};\n".format(A_param, B_param, C_param))
fp.write("}\n")

fp.close()
