from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import tkinter as tk
from tkinter import *
import numpy as np
import multiprocessing as mp

global GPSQueue, presQueue, tempQueue, humQueue, altQueue, cond, pres_data, temp_data, alt_data, hum_data
global gps_en, gps_out, gps_data
GPSQueue = mp.Queue()
presQueue = mp.Queue()
tempQueue = mp.Queue()
humQueue = mp.Queue()
altQueue = mp.Queue()
cond = False
pres_data = np.array([])
temp_data = np.array([])
alt_data = np.array([])
hum_data = np.array([])
gps_data = np.str_()
gps_en = False

def GUI_GO():
    
    def start_gps():
        global gps_en
        gps_en = True


    def stop_gps():
        global gps_en
        gps_en = False

    def pop_gps():
        global gps_data, gps_en, gps_out
        root1 = tk.Tk()
        root1.title("GPS Coordinates")
        root1.geometry("1300")
        gps_out = Text(root1, width=20, height=40)
        gps_out.pack(pady=10)
        teststring = "    GPS Coordinates    "
        gps_out.insert(tk.END, teststring)
        root1.mainloop()

    def plot_all():
        global cond, pres_data, alt_data, temp_data, hum_data, presQueue, tempQueue, humQueue, altQueue
        if cond:

            #Plot Pressure
            pres_float = presQueue.get()
            atm_float = pres_float / 101325
            if len(pres_data) < 100:
                pres_data = np.append(pres_data, atm_float)
            else:
                pres_data[0:99] = pres_data[1:100]
                pres_data[99] = atm_float

            lines.set_xdata(np.arange(0, len(pres_data)))
            lines.set_ydata(pres_data)

            #Plot Altitude
            alt_float = altQueue.get()
            if len(alt_data) < 100:
                alt_data = np.append(alt_data, alt_float)
            else:
                alt_data[0:99] = alt_data[1:100]
                alt_data[99] = alt_float

            lines1.set_xdata(np.arange(0, len(alt_data)))
            lines1.set_ydata(alt_data)

            #Plot Temperature
            temp_float = tempQueue.get()
            if len(temp_data) < 100:
                temp_data = np.append(temp_data, temp_float)
            else:
                temp_data[0:99] = temp_data[1:100]
                temp_data[99] = temp_float

            lines2.set_xdata(np.arange(0, len(temp_data)))
            lines2.set_ydata(temp_data)

            #Plot Humidity
            hum_float = humQueue.get()
            if len(hum_data) < 100:
                hum_data = np.append(hum_data, hum_float)
            else:
                hum_data[0:99] = hum_data[1:100]
                hum_data[99] = hum_float

            lines3.set_xdata(np.arange(0, len(hum_data)))
            lines3.set_ydata(hum_data)

            canvas.draw()

        root.after(1, plot_all)

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

    # Figure Settings  
    plt.style.use('seaborn')
    fig, ((ax,ax1),(ax2,ax3)) = plt.subplots(nrows=2,ncols=2)

    # Pressure Plot Config
    ax.set_title('Barometric Pressure')
    ax.set_xlabel('Sample')
    ax.set_ylabel('Pressure (atm)')
    ax.set_xlim(0, 100)
    ax.set_ylim(0.98, 1)
    lines = ax.plot([], [])[0]

    # Altitude Plot Config
    ax1.set_title('Altitude')
    ax1.set_xlabel('Sample')
    ax1.set_ylabel('Altitude (m)')
    ax1.set_xlim(0, 100)
    ax1.set_ylim(12, 20)
    lines1 = ax1.plot([], [])[0]

    # Temperature Plot Configuration
    ax2.set_title('Temperature')
    ax2.set_xlabel('Sample')
    ax2.set_ylabel('Temperature (C)')
    ax2.set_xlim(0, 100)
    ax2.set_ylim(15, 45)
    lines2 = ax2.plot([], [])[0]

    # Humidity Plot Configuration
    ax3.set_title('Humidity')
    ax3.set_xlabel('Sample')
    ax3.set_ylabel('Humidity (%)')
    ax3.set_xlim(0, 100)
    ax3.set_ylim(0, 100)
    lines3 = ax3.plot([], [])[0]

    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.get_tk_widget().place(x=10, y=0, width=1600, height=800)
    canvas.draw()

    # Start and Stop Buttons
    root.update()
    start = tk.Button(root, text="Begin Plotting", font=('calbiri', 12), command=lambda: start_plot())
    start.place(x=625, y=20)

    root.update()
    stop = tk.Button(root, text="Stop Plotting", font=('calbiri', 12), command=lambda: stop_plot())
    stop.place(x=start.winfo_x() + start.winfo_reqwidth() + 20, y=20)

    #GPS Button
    root.update()
    stop = tk.Button(root, text="GPS Readouts", font=('calbiri', 12), command=lambda: pop_gps())
    stop.place(x=950, y=20)

    root.after(1, plot_all)

    root.mainloop()
