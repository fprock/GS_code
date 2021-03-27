from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
import numpy as np

# import serial as sr

# global vars
cond = False
presh_data = np.array([])
temp_data = np.array([])
alt_data = np.array([])
humdty_data = np.array([])


def GUI_GO():
    while 1:
        def plot_presh():
            # global cond

            # if cond:

            pass

        def plot_temp():
            pass

        def plot_alt():
            pass

        def plot_humty():
            pass

        def start_plot():
            global cond
            cond = True

        def stop_plot():
            global cond
            cond = False

        # -----GUI Window
        root = tk.Tk()
        root.title('FPRock Live Data')
        root.configure(background='light blue')
        root.geometry("1600x800")

        # Barometric Pressure Plot Configuration
        fig = Figure()
        ax = fig.add_subplot(111)

        # ax = plt.axes(xlim=(0,100),ylim=(0, 120)); #displaying only 100 samples
        ax.set_title('Barometric Pressure')
        ax.set_xlabel('Sample')
        ax.set_ylabel('Pressure (kPa)')
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 105)
        lines = ax.plot([], [])[0]

        canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
        canvas.get_tk_widget().place(x=10, y=0, width=500, height=400)
        canvas.draw()

        # Altitude Plot Configuration
        fig1 = Figure()
        ax = fig1.add_subplot(111)

        # ax = plt.axes(xlim=(0,100),ylim=(0, 120)); #displaying only 100 samples
        ax.set_title('Altitude')
        ax.set_xlabel('Sample')
        ax.set_ylabel('Altitude (m)')
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.5, 6)
        lines1 = ax.plot([], [])[0]

        canvas = FigureCanvasTkAgg(fig1, master=root)  # A tk.DrawingArea.
        canvas.get_tk_widget().place(x=1000, y=0, width=500, height=400)
        canvas.draw()

        # Temperature Plot Configuration
        fig2 = Figure()
        ax = fig2.add_subplot(111)

        # ax = plt.axes(xlim=(0,100),ylim=(0, 120)); #displaying only 100 samples
        ax.set_title('Temperature')
        ax.set_xlabel('Sample')
        ax.set_ylabel('Temperature (C)')
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.5, 40)
        lines2 = ax.plot([], [])[0]

        canvas = FigureCanvasTkAgg(fig2, master=root)  # A tk.DrawingArea.
        canvas.get_tk_widget().place(x=10, y=400, width=500, height=400)
        canvas.draw()
        # Humidity Plot Configuration
        fig3 = Figure()
        ax = fig3.add_subplot(111)

        # ax = plt.axes(xlim=(0,100),ylim=(0, 120)); #displaying only 100 samples
        ax.set_title('Humidity')
        ax.set_xlabel('Sample')
        ax.set_ylabel('Humidity (%)')
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        lines3 = ax.plot([], [])[0]

        canvas = FigureCanvasTkAgg(fig3, master=root)  # A tk.DrawingArea.
        canvas.get_tk_widget().place(x=1000, y=400, width=500, height=400)
        canvas.draw()

        # Start and Stop Buttons
        root.update()
        start = tk.Button(root, text="Begin Plotting", font=('calbiri', 12), command=lambda: start_plot())
        start.place(x=625, y=400)

        root.update()
        stop = tk.Button(root, text="Stop Plotting", font=('calbiri', 12), command=lambda: stop_plot())
        stop.place(x=start.winfo_x() + start.winfo_reqwidth() + 20, y=400)

        # Configure Serial Port
        # s = sr.Serial('COM8', 115200)
        # s.reset_input_buffer()

        root.after(1, plot_presh())
        root.after(1, plot_alt())
        root.after(1, plot_temp())
        root.after(1, plot_humty())
        root.mainloop()
