from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
import numpy as np
import multiprocessing as mp

global presQueue, tempQueue, humQueue, altQueue, cond, pres_data, temp_data, alt_data, hum_data
presQueue = mp.Queue()
tempQueue = mp.Queue()
humQueue = mp.Queue()
altQueue = mp.Queue()
cond = False
pres_data = np.array([])
temp_data = np.array([])
alt_data = np.array([])
hum_data = np.array([])

def GUI_GO():
    
    
    def plot_pres():
        global cond, pres_data
        if cond:
            pres_float = presQueue.get()
            #print("pressure float = " + str(pres_float))
            if len(pres_data) < 100:
                pres_data = np.append(pres_data, pres_float)
            else:
                pres_data[0:99] = pres_data[1:100]
                pres_data[99] = pres_float

            lines.set_xdata(np.arange(0, len(pres_data)))
            lines.set_ydata(pres_data)

            canvas.draw()
        

    def plot_temp():
        global cond, temp_data
        if cond:
            temp_float = tempQueue.get()
            #print("temp float = " + str(temp_float))
            if len(temp_data) < 100:
                temp_data = np.append(temp_data, temp_float)
            else:
                temp_data[0:99] = temp_data[1:100]
                temp_data[99] = temp_float

            lines2.set_xdata(np.arange(0, len(temp_data)))
            lines2.set_ydata(temp_data)

            canvas2.draw()


    def plot_alt():
        global cond, alt_data
        if cond:
            alt_float = altQueue.get()
            #print("alt float = " + str(alt_float))
            if len(alt_data) < 100:
                alt_data = np.append(alt_data, alt_float)
            else:
                alt_data[0:99] = alt_data[1:100]
                alt_data[99] = alt_float

            lines1.set_xdata(np.arange(0, len(alt_data)))
            lines1.set_ydata(alt_data)

            canvas1.draw()


    def plot_hum():
        global cond, hum_data
        if cond:
            hum_float = humQueue.get()
            #print("hum float = " + str(hum_float))
            if len(hum_data) < 100:
                hum_data = np.append(hum_data, hum_float)
            else:
                hum_data[0:99] = hum_data[1:100]
                hum_data[99] = hum_float

            lines3.set_xdata(np.arange(0, len(hum_data)))
            lines3.set_ydata(hum_data)

            canvas3.draw()


    def plot_all():
        plot_pres()
        plot_alt()
        plot_temp()
        plot_hum()
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

    # Barometric Pressure Plot Configuration
    fig = Figure()
    ax = fig.add_subplot(111)

    # ax = plt.axes(xlim=(0,100),ylim=(0, 120)); #displaying only 100 samples
    ax.set_title('Barometric Pressure')
    ax.set_xlabel('Sample')
    ax.set_ylabel('Pressure (kPa)')
    ax.set_xlim(0, 100)
    ax.set_ylim(101600, 101625)
    lines = ax.plot([], [])[0]

    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.get_tk_widget().place(x=10, y=0, width=500, height=400)
    canvas.draw()

    # Altitude Plot Configuration
    fig1 = Figure()
    ax1 = fig1.add_subplot(111)

    # ax = plt.axes(xlim=(0,100),ylim=(0, 120)); #displaying only 100 samples
    ax1.set_title('Altitude')
    ax1.set_xlabel('Sample')
    ax1.set_ylabel('Altitude (m)')
    ax1.set_xlim(0, 100)
    ax1.set_ylim(12, 14)
    lines1 = ax1.plot([], [])[0]

    canvas1 = FigureCanvasTkAgg(fig1, master=root)  # A tk.DrawingArea.
    canvas1.get_tk_widget().place(x=950, y=0, width=600, height=400)
    canvas1.draw()

    # Temperature Plot Configuration
    fig2 = Figure()
    ax2 = fig2.add_subplot(111)

    # ax = plt.axes(xlim=(0,100),ylim=(0, 120)); #displaying only 100 samples
    ax2.set_title('Temperature')
    ax2.set_xlabel('Sample')
    ax2.set_ylabel('Temperature (C)')
    ax2.set_xlim(0, 100)
    ax2.set_ylim(24, 24.2)
    lines2 = ax2.plot([], [])[0]

    canvas2 = FigureCanvasTkAgg(fig2, master=root)  # A tk.DrawingArea.
    canvas2.get_tk_widget().place(x=10, y=400, width=650, height=400)
    canvas2.draw()
    # Humidity Plot Configuration
    fig3 = Figure()
    ax3 = fig3.add_subplot(111)

    # ax = plt.axes(xlim=(0,100),ylim=(0, 120)); #displaying only 100 samples
    ax3.set_title('Humidity')
    ax3.set_xlabel('Sample')
    ax3.set_ylabel('Humidity (%)')
    ax3.set_xlim(0, 100)
    ax3.set_ylim(50, 52)
    lines3 = ax3.plot([], [])[0]

    canvas3 = FigureCanvasTkAgg(fig3, master=root)  # A tk.DrawingArea.
    canvas3.get_tk_widget().place(x=950, y=400, width=600, height=400)
    canvas3.draw()

    # Start and Stop Buttons
    root.update()
    start = tk.Button(root, text="Begin Plotting", font=('calbiri', 12), command=lambda: start_plot())
    start.place(x=625, y=350)

    root.update()
    stop = tk.Button(root, text="Stop Plotting", font=('calbiri', 12), command=lambda: stop_plot())
    stop.place(x=start.winfo_x() + start.winfo_reqwidth() + 20, y=350)

    # Configure Serial Port
    # s = sr.Serial('COM8', 115200)
    # s.reset_input_buffer()

    root.after(1, plot_all)

    root.mainloop()
