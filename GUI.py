from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import tkinter as tk
from tkinter import *
import numpy as np
import multiprocessing as mp

# global presSend, tempSend, humSend, altSend, presRec, tempRec, humRec, altRec
# presSend, presRec = mp.Pipe()
# tempSend, tempRec = mp.Pipe()
# humSend, humRec = mp.Pipe()
# altSend, altRec = mp.Pipe()

global cond, pres_data, temp_data, alt_data, hum_data, pres_file, temp_file, alt_file, hum_file
global gps_data, GPSQueue, gps_en, gps_out, msg_count
global res_width, res_height, max_alt
gps_data = np.str_([])
pres_data = np.array([])
temp_data = np.array([])
alt_data = np.array([])
hum_data = np.array([])
GPSQueue = mp.Queue()
presQueue = mp.Queue()
tempQueue = mp.Queue()
altQueue = mp.Queue()
humQueue = mp.Queue()
cond = False
gps_en = False
msg_count = 0


# -----GUI Window
def GUI_GO():
    def gui_window():
        global res_width, res_height

        def start_gps():
            global gps_en
            gps_en = True

        def stop_gps():
            global gps_en
            gps_en = False

        def pop_gps():
            global gps_en, gps_data, gps_out, GPSQueue
            root1 = tk.Tk()
            root1.title("GPS Coordinates")
            # if (int(res_height) > 900):
            # gps_height = (1 / 9) * (int(res_height))
            # else:
            # gps_height = (1/3) * (int(res_height))
            # gps_geometry = res_width + "x" + str(int(gps_height))
            # root1.geometry("3840x450") -- 4k
            # root1.geometry("1900x500") -- 1920x1080
            gps_geometry = "1600x280"
            root1.geometry(gps_geometry)
            scrollbar = tk.Scrollbar(root1)
            scrollbar.pack(side=RIGHT, fill=Y)
            gps_out = Text(root1, width=130, height=15)

            gps_out.pack(pady=10)
            teststring = "---------------------------------------------------------GPS Coordinates----------------------------------------------------------"
            gps_out.insert(tk.END, teststring)
            gps_out.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=gps_out.yview)

            root1.update()
            start_gpsbutton = tk.Button(root1, text="Get Coordinates", font=('calbiri', 12),
                                        command=lambda: start_gps())
            start_gpsbutton.place(x=1300, y=60)  # --4k
            # if (int(res_width) > 1600):
            # start_gpsbutton.place(x=int(int(res_width)/2.9), y=50)
            # else:
            # start_gpsbutton.place(x=int(int(res_width) * (5/6)), y=50)
            root1.update()
            stop_gpsbutton = tk.Button(root1, text="Pause", font=('calbiri', 12), command=lambda: stop_gps())
            stop_gpsbutton.place(x=start_gpsbutton.winfo_x() + 36, y=start_gpsbutton.winfo_y() + 40)

            def write_gps():
                global gps_en, gps_data, gps_out, GPSQueue
                if gps_en:
                    gps_in = GPSQueue.get()
                    for key, val in gps_in.items():
                        gps_key = str(key)
                        gps_val = str(val)
                        gps_out.insert(tk.END, gps_key + ":" + gps_val + "\n")

                    gps_out.insert(tk.END, "------------------------------\n")
                    gps_out.see(tk.END)

                root1.after(500, write_gps)

            root1.after(500, write_gps)
            root1.mainloop()

        def plot_all():
            global cond, pres_data, alt_data, temp_data, hum_data, pres_file, temp_file, hum_file, alt_file
            # global presQueue, tempQueue, humQueue, altQueue
            if cond:

                # Plot Pressure
                pres_float = presQueue.get()
                # pres_float = float(pres_file.readline())  # JackTrash
                atm_float = pres_float
                # print("pressure float = " + str(pres_float))
                if len(pres_data) < 1000:
                    pres_data = np.append(pres_data, atm_float)
                else:
                    pres_data[0:999] = pres_data[1:1000]
                    pres_data[999] = atm_float

                lines.set_xdata(np.arange(0, len(pres_data)))
                lines.set_ydata(pres_data)

                # Plot Altitude
                alt_float = altQueue.get()
                # alt_float = float(alt_file.readline())  # JackTrash
                if len(alt_data) < 1000:
                    alt_data = np.append(alt_data, alt_float)
                else:
                    alt_data[0:999] = alt_data[1:1000]
                    alt_data[999] = alt_float

                lines1.set_xdata(np.arange(0, len(alt_data)))
                lines1.set_ydata(alt_data)

                # Plot Temperature
                temp_float = tempQueue.get()
                # temp_float = float(temp_file.readline())  # JackTrash
                if len(temp_data) < 1000:
                    temp_data = np.append(temp_data, temp_float)
                else:
                    temp_data[0:999] = temp_data[1:1000]
                    temp_data[999] = temp_float

                lines2.set_xdata(np.arange(0, len(temp_data)))
                lines2.set_ydata(temp_data)

                # Plot Humidity
                hum_float = humQueue.get()
                # hum_float = float(hum_file.readline())  # JackTrash
                if len(hum_data) < 1000:
                    hum_data = np.append(hum_data, hum_float)
                else:
                    hum_data[0:999] = hum_data[1:1000]
                    hum_data[999] = hum_float

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
        # if (int(res_height) > 900):
        # plots_height = str(int((4 / 15) * (int(res_height))))
        # else:
        # plots_height = str(int((5 / 9) * (int(res_height))))
        # plots_geometry = res_width + "x" + plots_height
        plots_geometry = "1600x550"  # -- 1920x1080
        root.geometry(plots_geometry)
        # root.geometry("1920x800")
        # root.geometry("3840x2160")

        # Figure Settings
        plt.style.use('seaborn')
        fig, ((ax, ax1), (ax2, ax3)) = plt.subplots(nrows=2, ncols=2)

        # Pressure Plot Config
        ax.set_title('Barometric Pressure')
        ax.set_xlabel('Sample')
        ax.set_ylabel('Pressure (Pa)')
        ax.set_xlim(0, 1000)
        ax.set_ylim(80000, 110000)
        lines = ax.plot([], [])[0]

        # Altitude Plot Config
        ax1.set_title('Altitude')
        ax1.set_xlabel('Sample')
        ax1.set_ylabel('Altitude (m)')
        ax1.set_xlim(0, 1000)
        ax1.set_ylim(0, int(max_alt))
        lines1 = ax1.plot([], [])[0]

        # Temperature Plot Configuration
        ax2.set_title('Temperature')
        ax2.set_xlabel('Sample')
        ax2.set_ylabel('Temperature (C)')
        ax2.set_xlim(0, 1000)
        ax2.set_ylim(10, 30)
        lines2 = ax2.plot([], [])[0]

        # Humidity Plot Configuration
        ax3.set_title('Humidity')
        ax3.set_xlabel('Sample')
        ax3.set_ylabel('Humidity (%)')
        ax3.set_xlim(0, 1000)
        ax3.set_ylim(0, 100)
        lines3 = ax3.plot([], [])[0]

        canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
        # if (int(res_width) > 1600):
        # canvas.get_tk_widget().place(x=0, y=0, width=int(int(res_width) / 2.47), height=int(plots_height))  # --4k magic numbers : 1550, 810
        # else:
        # canvas.get_tk_widget().place(x=0, y=0, width=int(int(res_width) - 100), height=int(plots_height))
        canvas.get_tk_widget().place(x=0, y=0, width=1550, height=550)
        canvas.draw()

        plt.tight_layout()

        # Start and Stop Buttons
        root.update()
        start = tk.Button(root, text="Begin Plotting", font=('calbiri', 12), command=lambda: start_plot())
        start.place(x=650, y=0)
        # start.place(x=int(int(res_width)/6.5), y=0)

        root.update()
        stop = tk.Button(root, text="Stop Plotting", font=('calbiri', 12), command=lambda: stop_plot())
        stop.place(x=start.winfo_x() + start.winfo_reqwidth() + 20, y=0)

        # GPS Button
        root.update()
        gpsbut = tk.Button(root, text="GPS Readouts", font=('calbiri', 12), command=lambda: pop_gps())
        gpsbut.place(x=stop.winfo_x() + stop.winfo_reqwidth() + 20, y=0)

        root.after(1, plot_all)

        root.mainloop()

    def apply_settings():
        global max_alt
        msg_box.delete(0, 'end')
        max_alt = alt_box.get()
        if not max_alt.isnumeric():
            num_msg = "Please enter numeric values for all settings"
            msg_box.insert(tk.END, num_msg)
            alt_box.delete(0, 'end')
        else:
            msg_box.insert(tk.END, "Settings Applied.")
            cont_button = Button(sel_res, text="Continue", command=gui_open)
            cont_button.pack()

    def gui_open():
        sel_res.destroy()
        gui_window()

    sel_res = tk.Tk()
    sel_res.geometry("275x350")
    sel_res.title('Configure Settings')
    alt_prompt = Label(sel_res, text="Maximum Expected Altitude (Meters)")
    alt_prompt.pack()
    alt_box = Entry(sel_res, width=20)
    alt_box.pack()
    ok_button = Button(sel_res, text="Apply Settings", command=apply_settings)
    ok_button.pack(pady=15)
    msg_box = Entry(sel_res, width=40)
    msg_box.pack()
    sel_res.mainloop()

# GUI_GO()
