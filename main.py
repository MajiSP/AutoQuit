import tkinter as tk
import tkinter.font as tkfont
import psutil
import keyboard
from threading import Event

class ProcessSearchWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Process")
        self.geometry("350x325")
        self.resizable(False, False)

        self.dark_mode = True
        self.configure_colors()

        #self.toggle_mode_button = tk.Button(self, text="Toggle Mode", command=self.toggle_mode, bg=self.button_bg, fg=self.text_color, relief="raised")
        #self.toggle_mode_button.place(x=5, y=5)

        self.search_entry = tk.Entry(self, bg=self.entry_bg, fg=self.text_color)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_processes)

        self.process_list = tk.Listbox(self, width=50, height=15, bg=self.list_bg, fg=self.text_color)
        self.process_list.pack(pady=2)

        self.submit_button = tk.Button(self, text="Submit", command=self.select_process, bg=self.button_bg, fg=self.text_color)
        self.submit_button.pack(pady=10)

        self.populate_process_list()

    def configure_colors(self):
        if self.dark_mode:
            self.bg_color = "#333333"
            self.text_color = "#FFFFFF"
            self.entry_bg = "#444444"
            self.list_bg = "#555555"
            self.button_bg = "#666666"
        else:
            self.bg_color = "#FFFFFF"
            self.text_color = "#000000"
            self.entry_bg = "#EEEEEE"
            self.list_bg = "#DDDDDD"
            self.button_bg = "#CCCCCC"

        self.configure(bg=self.bg_color)

    def toggle_mode(self):
        self.dark_mode = not self.dark_mode
        self.configure_colors()
        self.search_entry.configure(bg=self.entry_bg, fg=self.text_color)
        self.process_list.configure(bg=self.list_bg, fg=self.text_color)
        self.submit_button.configure(bg=self.button_bg, fg=self.text_color)
        self.toggle_mode_button.configure(bg=self.button_bg, fg=self.text_color)

    def populate_process_list(self):
        processes = [p.info['name'] for p in psutil.process_iter(['name'])]
        self.process_list.insert(tk.END, *sorted(processes))

    def filter_processes(self, event):
        search_term = self.search_entry.get().lower()
        self.process_list.delete(0, tk.END)
        for process in sorted([p.info['name'] for p in psutil.process_iter(['name'])]):
            if search_term in process.lower():
                self.process_list.insert(tk.END, process)

    def select_process(self):
        selected_process = self.process_list.get(self.process_list.curselection())
        if selected_process:
            self.destroy()
            text_overlay.process_name = selected_process
            text_overlay.create_window()

class TextOverlay:
    def __init__(self, font_name="Arial", font_size=16, font_color="red", outline_color="black"):
        self.font_name = font_name
        self.font_size = font_size
        self.font_color = font_color
        self.outline_color = outline_color
        self.root = None
        self.label1 = None
        self.label2 = None
        self.label3 = None
        self.show_overlay = True
        self.default_font = None
        self.running = True
        self.toggle_overlay_event = Event()
        self.close_process_and_program_event = Event()
        self.close_program_event = Event()
        self.process_name = None

    def create_window(self):
        self.root = tk.Tk()
        self.root.withdraw()

        if self.process_name is None:
            search_window = ProcessSearchWindow(self.root)
            self.root.wait_window(search_window)
            if self.process_name is None:
                self.root.destroy()
                return

        process_name = self.process_name.replace(".exe", "")

        self.root.deiconify()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.configure(bg="black")

        monitor_width = self.root.winfo_screenwidth()
        monitor_height = self.root.winfo_screenheight()

        self.default_font = tkfont.Font(family=self.font_name, size=self.font_size)
        text1_width = self.default_font.measure(f"Ctrl+Shift+T: Close {process_name}")
        text2_width = self.default_font.measure("HOME: Show/Hide UI")
        text3_width = self.default_font.measure("CTRL+C: Close Program")
        text_height = self.default_font.metrics("linespace")
        window_width = max(text1_width, text2_width, text3_width) + 20
        window_height = text_height * 3 + 10

        window_x = monitor_width - window_width - 10
        window_y = 10

        self.root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
        outline_font = tkfont.Font(family=self.font_name, size=self.font_size, weight="bold")
        self.label1 = tk.Label(self.root, text=f"Ctrl+Shift+T: Close {process_name}", font=outline_font, fg=self.font_color, bg="black")
        self.label1.place(x=0, y=0)
        self.label2 = tk.Label(self.root, text="HOME: Show/Hide UI", font=outline_font, fg=self.font_color, bg="black")
        self.label2.place(x=0, y=text_height)
        self.label3 = tk.Label(self.root, text="CTRL+C: Close Program", font=outline_font, fg=self.font_color, bg="black")
        self.label3.place(x=0, y=text_height * 2)

        keyboard.add_hotkey("home", self.schedule_toggle_overlay)
        keyboard.add_hotkey("ctrl+shift+t", self.schedule_close_process_and_program)
        keyboard.add_hotkey("ctrl+c", self.schedule_close_program)

        self.run_main_loop()

    def toggle_overlay(self):
        self.show_overlay = not self.show_overlay
        if self.show_overlay:
            self.label1.place(x=0, y=0)
            text_height = self.default_font.metrics("linespace")
            self.label2.place(x=0, y=text_height)
            self.label3.place(x=0, y=text_height * 2)
        else:
            self.label1.place_forget()
            self.label2.place_forget()
            self.label3.place_forget()

    def schedule_toggle_overlay(self):
        self.toggle_overlay_event.set()

    def close_process_and_program(self):
        print(f"Closing {self.process_name} and program...")
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == self.process_name:
                proc.terminate()
        self.running = False

    def schedule_close_process_and_program(self):
        self.close_process_and_program_event.set()

    def close_program(self):
        print("Closing program...")
        self.hide_overlay()
        self.running = False

    def schedule_close_program(self):
        self.close_program_event.set()

    def hide_overlay(self):
        self.label1.place_forget()
        self.label2.place_forget()
        self.label3.place_forget()

    def run_main_loop(self):
        while self.running:
            self.root.update_idletasks()
            self.root.update()
            if self.toggle_overlay_event.is_set():
                self.toggle_overlay()
                self.toggle_overlay_event.clear()
            if self.close_process_and_program_event.is_set():
                self.close_process_and_program()
                self.close_process_and_program_event.clear()
            if self.close_program_event.is_set():
                self.close_program()
                self.close_program_event.clear()

    def run(self):
        self.create_window()

text_overlay = TextOverlay(outline_color="black")
text_overlay.run()
