from Main import FCS_Handling as fch
from Main import Pump_Mock as pm
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import matplotlib.pyplot as plt
from scipy.stats import linregress
import pandas as pd
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
pd.set_option('display.max_columns', 10)
# backend = matplotlib.get_backend()
# print(backend)
# matplotlib.use('QtAgg')
plt.style.use('ggplot')

# Stops/starts the pump initially
# pmp.start_pump()
pm.stop_pump()


class FileHandler(FileSystemEventHandler):
    def __init__(self):
        self.fig1, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, sharex='col')
        self.file_counter = 0
        self.start_time = None
        self.analysis_results = []

        self.reactor_1_result = pd.DataFrame(columns=['PI percentage', 'Mean FL1-H', 'Time(min)', 'Events'])
        self.new_data_1 = {}
        self.df_new_data_1 = None
        self.ema_reactor_1_PI = pd.DataFrame(columns=['PI percentage (ema)'])
        self.ema_reactor_1_fl1 = pd.DataFrame(columns=['Mean FL1-H (ema)'])
        self.dmg_percentage = []
        self.mean_fl1 = []
        self.events = []
        self.time_since = []
        #  self.time_since_seconds = None
        self.time_since_date = None

        self.fig1 = None
        self.ax1 = None
        self.ax2 = None
        self.ax3 = None

        self.reactor_1_last3_PI = []
        self.reactor_1_last3_fl1 = []
        self.reactor_1_last3_time = []

        self.pi_1_slope = 0
        self.fl1_1_slope = 0
        self.df_new_slopes = None
        self.new_slopes = None
        self.slopes_columns = pd.DataFrame(columns=['PI slope', 'FL1-H slope'])
        self.appended_result = None

        self.pi_last3 = None
        self.pi_last3_avg = None
        self.pump_status = None
        self.new_status = None
        self.df_new_status = None
        self.status_column = pd.DataFrame(columns=['Pump Status'])
        self.full_result = None

    def on_created(self, event):
        if self.file_counter == 0:
            self.start_time = datetime.now()

        if self.file_counter % 2 == 0:
            time.sleep(1)
            file_path = event.src_path
            self.analysis_results = fch.fcs_analysis(file_path)
            self.save_results()
            self.plot_results()
            self.get_slope()
            self.use_pump()

        self.file_counter += 1

    def save_results(self):
        self.dmg_percentage = self.analysis_results[0]
        self.mean_fl1 = self.analysis_results[1]
        self.events = self.analysis_results[2]

        if self.file_counter >= 2:
            self.time_since = 15 * self.file_counter
        elif self.file_counter == 0:
            self.time_since = 0
        # self.time_since_date = datetime.now() - self.start_time
        # self.time_since_seconds = self.time_since.total_seconds()
        # self.time_since = self.time_since_seconds/60

        self.new_data_1 = {'Time(min)': self.time_since, 'PI percentage': self.dmg_percentage,
                           'Mean FL1-H': self.mean_fl1,
                           'Events': self.events}
        self.df_new_data_1 = pd.DataFrame([self.new_data_1])
        self.reactor_1_result = pd.concat([self.reactor_1_result, self.df_new_data_1], ignore_index=True)
        self.ema_reactor_1_PI = self.reactor_1_result['PI percentage'].ewm(com=0.9).mean()
        self.ema_reactor_1_fl1 = self.reactor_1_result['Mean FL1-H'].ewm(com=0.9).mean()
        time.sleep(0.5)

    def plot_results(self):
        if self.file_counter >= 1:
            plt.close(self.fig1)
        plt.ion()
        self.fig1, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, sharex='col')
        self.fig1.set_figheight(8)
        self.fig1.set_figwidth(7)
        self.fig1.canvas.manager.window.geometry("+0+0")
        self.ax1.plot(self.reactor_1_result['Time(min)'], self.reactor_1_result['PI percentage'], label='PI Data',
                      color='purple')
        self.ax1.plot(self.reactor_1_result['Time(min)'], self.ema_reactor_1_PI, label='PI EMA', color='brown')
        self.ax1.set_ylabel('PI (%)')
        self.ax1.set_title('PI Positive Percentage')
        self.ax1.legend(loc='upper right')

        self.ax2.plot(self.reactor_1_result['Time(min)'], self.reactor_1_result['Mean FL1-H'], label='FL1-H data',
                      color='pink')
        self.ax2.plot(self.reactor_1_result['Time(min)'], self.ema_reactor_1_fl1, label='FL1-H EMA', color='blue')
        self.ax2.set_ylabel('Fluorescence')
        self.ax2.set_title('Mean FL1-H Fluorescence')
        self.ax2.legend(loc='upper right')

        self.ax3.plot(self.reactor_1_result['Time(min)'], self.reactor_1_result['Events'], label='Events',
                      color='black')
        self.ax3.set_xlabel('Time (min)')
        self.ax3.set_ylabel('Events')
        self.ax3.set_title('Events')
        self.ax3.legend(loc='upper right')

        self.fig1.canvas.draw()
        self.fig1.canvas.flush_events()

    def get_slope(self):
        if self.file_counter >= 4:
            self.reactor_1_last3_PI = self.ema_reactor_1_PI[-3:]
            self.reactor_1_last3_fl1 = self.ema_reactor_1_fl1[-3:]
            self.reactor_1_last3_time = self.reactor_1_result['Time(min)'][-3:].values.tolist()

            pi_1_linreg = linregress(self.reactor_1_last3_time, self.reactor_1_last3_PI)
            self.pi_1_slope = pi_1_linreg[0]
            fl1_1_linreg = linregress(self.reactor_1_last3_time, self.reactor_1_last3_fl1)
            self.fl1_1_slope = fl1_1_linreg[0]

            self.new_slopes = {'PI slope': self.pi_1_slope, 'FL1-H slope': self.fl1_1_slope}
            self.df_new_slopes = pd.DataFrame(self.new_slopes, index=[0])
            self.slopes_columns = pd.concat([self.slopes_columns, self.df_new_slopes],
                                            ignore_index=True)
            self.appended_result = self.reactor_1_result.join(self.slopes_columns.set_index(self.reactor_1_result.index)
                                                              , rsuffix='_status')

            print("\nSlopes of the last three points:")
            print("PI:", self.pi_1_slope, "\nFL1-H:", self.fl1_1_slope)
        else:
            self.pi_1_slope = "Premature"
            self.fl1_1_slope = "Premature"
            self.new_slopes = {'PI slope': self.pi_1_slope, 'FL1-H slope': self.fl1_1_slope}
            self.df_new_slopes = pd.DataFrame(self.new_slopes, index=[0])
            self.slopes_columns = pd.concat([self.slopes_columns, self.df_new_slopes],
                                            ignore_index=True)
            self.appended_result = self.reactor_1_result.join(
                self.slopes_columns.set_index(self.reactor_1_result.index)
                , rsuffix='_status')

    def use_pump(self):
        if self.file_counter >= 4:
            self.pi_last3 = self.reactor_1_result['PI percentage'][-3:].values.tolist()
            self.pi_last3_avg = sum(self.pi_last3) / len(self.pi_last3)

            # Stop
            if self.pi_1_slope >= 0.05 or self.pi_last3_avg >= 40:
                pm.stop_pump()
                self.pump_status = "Stopped"
                self.new_status = {'Pump Status': self.pump_status}
                self.df_new_status = pd.DataFrame([self.new_status])
                self.status_column = pd.concat([self.status_column, self.df_new_status],
                                               ignore_index=True)
                self.full_result = self.appended_result.join(self.status_column.set_index(self.appended_result.index),
                                                             rsuffix='_status')
            # Maximum, 10ml/h. This pumps the whole sample cycle more or less.
            # Higher threshold due to extremity and risk.
            elif ((self.status_column.iloc[-1] == "Maximum increased").item() and (self.fl1_1_slope <= -25) and
                  (self.pi_1_slope < 0.05)) or \
                    ((self.status_column.iloc[-1] == "Maximum").item() and (self.pi_1_slope < 0.05)):

                pm.constant_pump()
                self.pump_status = "Maximum"
                self.new_status = {'Pump Status': self.pump_status}
                self.df_new_status = pd.DataFrame([self.new_status])
                self.status_column = pd.concat([self.status_column, self.df_new_status],
                                               ignore_index=True)
                self.full_result = self.appended_result.join(self.status_column.set_index(self.appended_result.index),
                                                             rsuffix='_status')
            # Maximum increased, 5ml/h
            elif ((self.status_column.iloc[-1] == "Further increased").item() and (self.fl1_1_slope <= -10) and
                  (self.pi_1_slope < 0.05)) or \
                    ((self.status_column.iloc[-1] == "Maximum increased").item() and (self.pi_1_slope < 0.05)):

                pm.faster_pump()
                self.pump_status = "Maximum increased"
                self.new_status = {'Pump Status': self.pump_status}
                self.df_new_status = pd.DataFrame([self.new_status])
                self.status_column = pd.concat([self.status_column, self.df_new_status],
                                               ignore_index=True)
                self.full_result = self.appended_result.join(self.status_column.set_index(self.appended_result.index),
                                                             rsuffix='_status')
            # Further increased, 3ml/h
            elif ((self.status_column.iloc[-1] == "Increased").item() and (self.fl1_1_slope <= -10) and
                  (self.pi_1_slope < 0.05)) or \
                    ((self.status_column.iloc[-1] == "Further increased").item() and (self.pi_1_slope < 0.05)):

                pm.fast_pump()
                self.pump_status = "Further increased"
                self.new_status = {'Pump Status': self.pump_status}
                self.df_new_status = pd.DataFrame([self.new_status])
                self.status_column = pd.concat([self.status_column, self.df_new_status],
                                               ignore_index=True)
                self.full_result = self.appended_result.join(self.status_column.set_index(self.appended_result.index),
                                                             rsuffix='_status')
            # Increased, 1.5ml/h
            elif ((self.status_column.iloc[-1] == "Started").item() and (self.fl1_1_slope <= -10) and
                  (self.pi_1_slope < 0.05)) or \
                    ((self.status_column.iloc[-1] == "Increased").item() and (self.pi_1_slope < 0.05)):

                pm.increase_pump()
                self.pump_status = "Increased"
                self.new_status = {'Pump Status': self.pump_status}
                self.df_new_status = pd.DataFrame([self.new_status])
                self.status_column = pd.concat([self.status_column, self.df_new_status],
                                               ignore_index=True)
                self.full_result = self.appended_result.join(self.status_column.set_index(self.appended_result.index),
                                                             rsuffix='_status')
            # Start, 1ml/h
            elif (self.fl1_1_slope <= -0.8) or \
                    ((self.status_column.iloc[-1] == "Started").item() and (self.pi_1_slope < 0.05)):

                pm.schedule_pump()
                self.pump_status = "Started"
                self.new_status = {'Pump Status': self.pump_status}
                self.df_new_status = pd.DataFrame([self.new_status])
                self.status_column = pd.concat([self.status_column, self.df_new_status],
                                               ignore_index=True)
                self.full_result = self.appended_result.join(self.status_column.set_index(self.appended_result.index),
                                                             rsuffix='_status')
            # If no conditions apply (i.e turning points)
            else:
                print("\nNo action taken")
                self.pump_status = "No Action"
                self.new_status = {'Pump Status': self.pump_status}
                self.df_new_status = pd.DataFrame([self.new_status])
                self.status_column = pd.concat([self.status_column, self.df_new_status],
                                               ignore_index=True)
                self.full_result = self.appended_result.join(self.status_column.set_index(self.appended_result.index),
                                                             rsuffix='_status')

        # Before 3 data points, no slope available.
        else:
            print("\nNo action taken (premature)")
            self.pump_status = "Premature"
            self.new_status = {'Pump Status': self.pump_status}
            self.df_new_status = pd.DataFrame([self.new_status])
            self.status_column = pd.concat([self.status_column, self.df_new_status],
                                           ignore_index=True)
            self.full_result = self.appended_result.join(self.status_column.set_index(self.appended_result.index),
                                                         rsuffix='_status')

        print("\n", self.full_result)

    def save_to_folder(self):
        time_string = self.start_time.strftime("%Y-%m-%d_%H-%M-%S")
        figure_name = f"Figure_{time_string}.png"
        data_name = f"Data_{time_string}.xlsx"
        save_to = r"C:\Users\ADMIN\Desktop\Saras scripts\Data\Saved"

        folder_name = time_string
        new_path = os.path.join(save_to, folder_name)
        os.makedirs(new_path, exist_ok=False)
        plt.savefig(new_path + r'\ ' + figure_name)
        self.full_result.to_excel(new_path + r'\ ' + data_name)
        print("Data has been saved to the folder:" + time_string)


folder_path = r"C:\Users\ADMIN\Desktop\Saras scripts\Data\Goal\Trial"
event_handler = FileHandler()
observer = Observer()
observer.schedule(event_handler, path=folder_path, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
