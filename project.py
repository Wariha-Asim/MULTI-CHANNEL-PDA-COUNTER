import json
import os
import tkinter as tk
from tkinter import messagebox
import winsound

SAVE_FILE = "channels_state.json"

# ----------------------------
# Default Empty State
# ----------------------------
def empty_state():
    return {
        "A": {"count": 0, "stack": [], "state": "q0", "last_input": "-"},
        "B": {"count": 0, "stack": [], "state": "q0", "last_input": "-"},
        "C": {"count": 0, "stack": [], "state": "q0", "last_input": "-"}
    }

# ----------------------------
# Persistence
# ----------------------------
def load_state():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return empty_state()

def save_state(state):
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f)

# ----------------------------
# PDA Channel
# ----------------------------
class ChannelCounter:
    def __init__(self, name, data, target=200000):
        self.name = name
        self.count = data["count"]
        self.stack = data["stack"]
        self.state = data["state"]
        self.last_input = data["last_input"]
        self.target = target

    def increment(self):
        self.last_input = "1"
        self.stack.append(1)
        if self.state == "q0":
            self.state = "q1"
        self.count += 1
        if self.count >= self.target:
            self.state = "qf"
            return True
        return False

    def reset(self):
        self.last_input = "R"
        self.count = 0
        self.stack.clear()
        self.state = "q0"

# ----------------------------
# PDA GUI
# ----------------------------
class PDA_GUI:
    def __init__(self, root, data):
        self.root = root
        self.root.title("PDA Multi-Channel Counter")
        self.root.geometry("780x560")
        self.root.configure(bg="#1b1b2f")

        self.channels = {ch: ChannelCounter(ch, data[ch]) for ch in ["A", "B", "C"]}

        # Title
        tk.Label(root, text="📊 Multi-Channel PDA Counter",
                 fg="#ffffff", bg="#1b1b2f",
                 font=("Helvetica", 18, "bold")).pack(pady=15)

        frame = tk.Frame(root, bg="#1b1b2f")
        frame.pack(pady=5)

        self.labels = {}
        self.state_labels = {}
        self.stack_labels = {}
        self.input_labels = {}

        # ---------------- Channel Display ----------------
        for ch in ["A", "B", "C"]:
            row = tk.Frame(frame, bg="#1b1b2f")
            row.pack(pady=8, fill="x", padx=20)

            tk.Label(row, text=f"Channel {ch}", fg="#4fc3f7",
                     bg="#1b1b2f", width=10,
                     font=("Helvetica", 12, "bold")).pack(side="left")

            c = tk.Label(row, text=self.channels[ch].count,
                         fg="#81c784", bg="#1b1b2f",
                         width=6, font=("Helvetica", 14, "bold"))
            c.pack(side="left", padx=5)
            self.labels[ch] = c

            s = tk.Label(row, text=f"State: {self.channels[ch].state}",
                         fg="#ffd54f", bg="#1b1b2f", width=12)
            s.pack(side="left", padx=5)
            self.state_labels[ch] = s

            st = tk.Label(row, text=f"Stack: {self.channels[ch].stack}",
                          fg="#90caf9", bg="#1b1b2f",
                          width=24, anchor="w")
            st.pack(side="left", padx=5)
            self.stack_labels[ch] = st

            inp = tk.Label(row, text=f"Input: {self.channels[ch].last_input}",
                           fg="#ffab91", bg="#1b1b2f", width=10)
            inp.pack(side="left", padx=5)
            self.input_labels[ch] = inp

            tk.Button(row, text="Reset", bg="#e57373",
                      fg="white", font=("Helvetica", 10, "bold"),
                      command=lambda c=ch: self.reset_channel(c)).pack(side="left", padx=5)

        # ---------------- Channel Selection ----------------
        self.selected = tk.StringVar(value="A")
        rf = tk.Frame(root, bg="#1b1b2f")
        rf.pack(pady=15)

        self.radiobuttons = {}
        for ch in ["A", "B", "C"]:
            rb = tk.Radiobutton(rf, text=ch, variable=self.selected,
                                value=ch, fg="white",
                                bg="#1b1b2f", selectcolor="#1b1b2f",
                                font=("Helvetica", 12, "bold"),
                                indicatoron=0, width=6,
                                command=self.update_radiobuttons)
            rb.pack(side="left", padx=10)
            self.radiobuttons[ch] = rb

        # Initialize selected color
        self.update_radiobuttons()

        # ---------------- Increment Button ----------------
        tk.Button(root, text="➕ Increment Selected Channel",
                  bg="#4caf50", fg="white",
                  font=("Helvetica", 12, "bold"),
                  width=30, height=2,
                  command=self.increment).pack(pady=10)

        # ---------------- Back Button ----------------
        tk.Button(root, text="⬅ Back to Menu",
                  bg="#9e9e9e", fg="black",
                  font=("Helvetica", 11, "bold"),
                  width=20, command=self.go_back).pack(pady=10)

        # ---------------- Info Panel ----------------
        info_frame = tk.Frame(root, bg="#292950", bd=2, relief="groove")
        info_frame.pack(pady=10, padx=15, fill="both")
        info_text = (
            "📌 PDA Concept & Enhancements:\n"
            "• States per channel: q0 (start), q1 (counting), qf (target reached)\n"
            "• Increment: q0→q1→q1(push)→qf(if target)\n"
            "• Reset: any→q0(clear stack)\n"
            "• Stack: simulates PDA memory (push/pop)\n"
            "• Input symbols: '1' for increment, 'R' for reset\n"
            "• Multiple independent PDAs (A, B, C channels)\n"
            "• Persistent stack & counts across sessions"
        )
        tk.Label(info_frame, text=info_text, justify="left",
                 fg="#ffffff", bg="#292950", font=("Helvetica", 10)).pack(padx=10, pady=10)

    # ---------------- Radiobutton Color Update ----------------
    def update_radiobuttons(self):
        for ch, rb in self.radiobuttons.items():
            if self.selected.get() == ch:
                rb.config(fg="red")
            else:
                rb.config(fg="white")

    # ---------------- PDA Functions ----------------
    def increment(self):
        ch = self.selected.get()
        reached = self.channels[ch].increment()
        self.update_gui(ch)
        self.save_all()
        if reached:
            messagebox.showinfo("Target Reached", f"Channel {ch} reached target!")
            winsound.Beep(1000, 400)

    def reset_channel(self, ch):
        self.channels[ch].reset()
        self.update_gui(ch)
        self.save_all()

    def update_gui(self, ch):
        c = self.channels[ch]
        self.labels[ch].config(text=c.count)
        self.state_labels[ch].config(text=f"State: {c.state}")
        self.stack_labels[ch].config(text=f"Stack: {c.stack}")
        self.input_labels[ch].config(text=f"Input: {c.last_input}")

    def save_all(self):
        save_state({
            ch: {
                "count": self.channels[ch].count,
                "stack": self.channels[ch].stack,
                "state": self.channels[ch].state,
                "last_input": self.channels[ch].last_input
            } for ch in self.channels
        })

    def go_back(self):
        self.root.destroy()
        start_screen()

# ----------------------------
# Start / Resume Screen
# ----------------------------
def start_screen():
    global start
    start = tk.Tk()
    start.title("Start or Resume")
    start.geometry("420x300")
    start.configure(bg="#1b1b2f")

    tk.Label(start, text="🚀 Choose Option", fg="white",
             bg="#1b1b2f", font=("Helvetica", 14, "bold")).pack(pady=20)

    tk.Button(start, text="▶ Start (New)", width=20,
              bg="#4caf50", fg="white", font=("Helvetica", 12, "bold"),
              command=lambda: launch(False)).pack(pady=5)

    tk.Button(start, text="🔁 Resume", width=20,
              bg="#2196f3", fg="white", font=("Helvetica", 12, "bold"),
              command=lambda: launch(True)).pack(pady=5)

    start.mainloop()

def launch(resume):
    start.destroy()
    data = load_state() if resume else empty_state()
    root = tk.Tk()
    PDA_GUI(root, data)
    root.mainloop()

# ----------------------------
# Run
# ----------------------------
start_screen()