import tkinter as tk
from tkinter import Scrollbar, messagebox
import psutil
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

def update_processes():
    process_listbox.delete(0, tk.END)
    for process in psutil.process_iter(['pid', 'name']):
        process_listbox.insert(tk.END, f"PID: {process.info['pid']} - Name: {process.info['name']}")

def search_processes(event=None):
    search_term = search_entry.get().lower()
    process_listbox.delete(0, tk.END)
    for process in psutil.process_iter(['pid', 'name']):
        if search_term in process.info['name'].lower():
            process_listbox.insert(tk.END, f"PID: {process.info['pid']} - Name: {process.info['name']}")

def monitor_system_resources():
    cpu_percent = psutil.cpu_percent()
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')

    # Update the system info label
    system_info_label.config(text=f"CPU Usage: {cpu_percent}%\nMemory Usage: {memory_info.percent}%\nDisk Usage: {disk_usage.percent}%")

    # Update the system resource graphs
    cpu_line.set_data(range(len(cpu_data)), cpu_data)
    memory_line.set_data(range(len(memory_data)), memory_data)
    disk_line.set_data(range(len(disk_data)), disk_data)

    cpu_data.append(cpu_percent)
    memory_data.append(memory_info.percent)
    disk_data.append(disk_usage.percent)

    if len(cpu_data) > 50:
        cpu_data.pop(0)
        memory_data.pop(0)
        disk_data.pop(0)

    cpu_graph.set_xlim(0, len(cpu_data))
    cpu_graph.set_ylim(0, 100)
    memory_graph.set_xlim(0, len(memory_data))
    memory_graph.set_ylim(0, 100)
    disk_graph.set_xlim(0, len(disk_data))
    disk_graph.set_ylim(0, 100)

    system_resource_canvas.draw()

def terminate_process():
    selected_process = process_listbox.get(process_listbox.curselection())
    if selected_process:
        pid = int(selected_process.split()[1])
        try:
            process = psutil.Process(pid)
            if process.is_running():
                process.terminate()
                update_processes()  # Update the process list after successful termination
            else:
                messagebox.showinfo("Process Terminated", f"Process with PID {pid} has already been terminated.")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            messagebox.showerror("Termination Failed", f"Unable to terminate process with PID {pid}.")

# GUI setup
root = tk.Tk()
root.title("Process Manager")

process_label = tk.Label(root, text="Running Processes:")
process_label.pack()

search_frame = tk.Frame(root)
search_label = tk.Label(search_frame, text="Search:")
search_label.pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT)
search_entry.bind("<KeyRelease>", search_processes)
search_frame.pack()

process_listbox = tk.Listbox(root, width=50)
process_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

process_scrollbar = Scrollbar(root, command=process_listbox.yview)
process_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
process_listbox.config(yscrollcommand=process_scrollbar.set)

system_info_label = tk.Label(root, text="System Resources:")
system_info_label.pack()

# Create the system resource graphs
fig = Figure(figsize=(8, 4), dpi=100)

cpu_graph = fig.add_subplot(311)
cpu_line, = cpu_graph.plot([], [], color='red')
cpu_graph.set_title('CPU Usage')
cpu_graph.set_xlabel('Time')
cpu_graph.set_ylabel('Utilization (%)')

memory_graph = fig.add_subplot(312)
memory_line, = memory_graph.plot([], [], color='green')
memory_graph.set_title('Memory Usage')
memory_graph.set_xlabel('Time')
memory_graph.set_ylabel('Utilization (%)')

disk_graph = fig.add_subplot(313)
disk_line, = disk_graph.plot([], [], color='blue')
disk_graph.set_title('Disk Usage')
disk_graph.set_xlabel('Time')
disk_graph.set_ylabel('Utilization (%)')

system_resource_canvas = FigureCanvasTkAgg(fig, root)
system_resource_canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

terminate_button = tk.Button(root, text="Terminate Process", command=terminate_process)
terminate_button.pack()

update_processes()  # Initial update of processes

# Initialize data lists for the graphs
cpu_data = []
memory_data = []
disk_data = []

# Start the auto-refresh loop
def auto_refresh():
    monitor_system_resources()
    root.after(1000, auto_refresh)  # Refresh every 1 second (1000 milliseconds)

auto_refresh()

# Start the GUI
root.mainloop()