"""
KBC Chatbot - Professional GUI (PySide6)

Requirements:
    pip install PySide6

Optional (sounds and custom font):
    Place sound files and a font file (e.g., 'Roboto-Regular.ttf' and 'Roboto-Bold.ttf') in the same folder.
    Update SOUND_* and FONT_* constants as needed.

Run:
    python kbc_qt.py
"""

import sys
import random
from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia

# ---------------------------
# CONFIG / ASSETS (edit here)
# ---------------------------
WINDOW_TITLE = "Kaun Banega Crorepati — Chatbot Edition"
WINDOW_SIZE = (1100, 700)

# Replace with actual file paths if you want sound and custom font
SOUND_THEME = None  # e.g. "kbc_theme.wav"
SOUND_CORRECT = None  # e.g. "correct.wav"
SOUND_WRONG = None  # e.g. "wrong.wav"

FONT_REGULAR = None # e.g. "Roboto-Regular.ttf"
FONT_BOLD = None    # e.g. "Roboto-Bold.ttf"

TYPING_SPEED_MS = 6  # lower -> faster

# ---------------------------
# QUESTIONS (you can extend)
# ---------------------------
QUESTIONS = [
    {"question": "What is the capital of India?", "options": ["UP", "New Delhi", "Haryana", "Patiyala"], "answer": 1},
    {"question": "What is the largest mammal in the world?", "options": ["Giraffe", "Black whale", "Blue whale", "Elephant"], "answer": 2},
    {"question": "What colour is the sun?", "options": ["Red", "Yellow", "Green", "Orange"], "answer": 1},
    {"question": "What is the name of Mickey Mouse's dog?", "options": ["Pluto", "Seyal", "Kashana", "Kalu"], "answer": 0},
    {"question": "How many legs does a spider have?", "options": ["8", "7", "10", "12"], "answer": 0},
    {"question": "Who invented the telephone?", "options": ["William Shakespeare", "Alex M", "Graham Bell", "Kalix"], "answer": 2},
    {"question": "What is the chemical formula for water?", "options": ["H2O", "CO2", "H2", "NO2"], "answer": 0},
    {"question": "What is the largest ocean on Earth?", "options": ["Indian Ocean", "Atlantic Ocean", "Pacific Ocean", "North Ocean"], "answer": 2},
    {"question": "What is the tallest mountain in the world?", "options": ["Himalayan Hills", "K2", "Arawali Hills", "Mount Everest"], "answer": 3},
    {"question": "Which planet is known for its rings?", "options": ["Saturn", "Jupiter", "Mercury", "Venus"], "answer": 0}
]

PRIZE_LADDER = {
    1: 1000, 2: 2000, 3: 3000, 4: 4000, 5: 5000,
    6: 6000, 7: 7000, 8: 8000, 9: 9000, 10: 10000
}


# ---------------------------
# Utility: play sound safely
# ---------------------------
def play_sound(path):
    if not path:
        return
    try:
        s = QtMultimedia.QSoundEffect()
        s.setSource(QtCore.QUrl.fromLocalFile(path))
        s.setLoopCount(1)
        s.setVolume(0.8)
        s.play()
    except Exception:
        pass


# ---------------------------
# Main Window
# ---------------------------
class KBCWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(*WINDOW_SIZE)

        self.questions = QUESTIONS.copy()
        self.current_index = 0
        self.current_amount = 0
        self.lifelines = {"50-50": True, "Audience": True, "Flip": True}
        self.disabled_options = []  # indexes disabled by 50-50
        random.shuffle(self.questions)

        # Load custom fonts if available
        if FONT_REGULAR and FONT_BOLD:
            QtGui.QFontDatabase.addApplicationFont(FONT_REGULAR)
            QtGui.QFontDatabase.addApplicationFont(FONT_BOLD)

        # central widget + layout
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        # Left: Chat + Options
        left_panel = QtWidgets.QFrame()
        left_panel.setMinimumWidth(720)
        left_panel.setStyleSheet("QFrame { border-radius: 12px; background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a2933, stop:1 #162a4d); }")
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setContentsMargins(18, 18, 18, 18)

        # Header
        header = QtWidgets.QLabel("KBC — Chat Host")
        header.setStyleSheet("QLabel { color: #e0e0e0; font-size: 20px; font-weight: 700; }")
        if FONT_BOLD:
            header.setFont(QtGui.QFont(FONT_BOLD.split('.')[0], 20))
        left_layout.addWidget(header)

        # Chat display (read-only)
        self.chat = QtWidgets.QTextBrowser()
        self.chat.setStyleSheet("""
            QTextBrowser { background: transparent; color: #e0e0e0; border: none; font-size: 15px; }
            """)
        if FONT_REGULAR:
            self.chat.setFont(QtGui.QFont(FONT_REGULAR.split('.')[0], 15))
        self.chat.setOpenLinks(False)
        left_layout.addWidget(self.chat, stretch=1)

        # Options (buttons)
        self.options_container = QtWidgets.QWidget()
        self.options_layout = QtWidgets.QGridLayout(self.options_container)
        self.options_layout.setSpacing(12)
        left_layout.addWidget(self.options_container)

        self.option_buttons = []
        for i in range(4):
            btn = QtWidgets.QPushButton("")
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn.setMinimumHeight(54)
            btn.setStyleSheet(self._option_stylesheet(normal=True))
            btn.clicked.connect(lambda checked, idx=i: self.on_option_click(idx))
            btn.installEventFilter(self)
            self.option_buttons.append(btn)
            r, c = divmod(i, 2)
            self.options_layout.addWidget(btn, r, c)

        # Input bar (for chat-like quick commands)
        bottom_row = QtWidgets.QHBoxLayout()
        self.entry = QtWidgets.QLineEdit()
        self.entry.setPlaceholderText("Type a / b / c / d — or 'quit'")
        self.entry.returnPressed.connect(self.on_entry_submit)
        bottom_row.addWidget(self.entry)
        send = QtWidgets.QPushButton("Send")
        send.setFixedWidth(90)
        send.clicked.connect(self.on_entry_submit)
        bottom_row.addWidget(send)
        left_layout.addLayout(bottom_row)

        # Right: Prize ladder + Lifelines + Animations
        right_panel = QtWidgets.QFrame()
        right_panel.setMinimumWidth(320)
        right_panel.setStyleSheet("QFrame { border-radius: 12px; background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #122841, stop:1 #0e213b); }")
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(14, 14, 14, 14)

        # Lifelines
        ll_label = QtWidgets.QLabel("Lifelines")
        ll_label.setStyleSheet("QLabel { color: #e0e0e0; font-size: 16px; font-weight: 700; }")
        right_layout.addWidget(ll_label)

        self.lifeline_buttons = {}
        for name in self.lifelines:
            b = QtWidgets.QPushButton(name)
            b.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            b.clicked.connect(lambda checked, n=name: self.use_lifeline(n))
            b.setStyleSheet(self._lifeline_stylesheet(enabled=True))
            right_layout.addWidget(b)
            self.lifeline_buttons[name] = b

        right_layout.addSpacing(12)

        # Prize ladder (list)
        ladder_label = QtWidgets.QLabel("Prize Ladder")
        ladder_label.setStyleSheet("QLabel { color: #e0e0e0; font-size: 16px; font-weight: 700; }")
        right_layout.addWidget(ladder_label)

        self.ladder_list = QtWidgets.QListWidget()
        self.ladder_list.setStyleSheet("""
            QListWidget { background: transparent; border: none; color: #CDE7FF; font-size: 14px; }
            QListWidget::item { padding: 8px; }
            """)
        self.ladder_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        right_layout.addWidget(self.ladder_list, stretch=1)

        # Confetti canvas (simple colored dots animation)
        self.confetti_canvas = QtWidgets.QLabel()
        self.confetti_canvas.setFixedHeight(120)
        right_layout.addWidget(self.confetti_canvas)

        # Add panels to main
        main_layout.addWidget(left_panel, stretch=3)
        main_layout.addWidget(right_panel, stretch=1)

        # State
        self.setup_ladder()
        self.typing_timer = QtCore.QTimer()
        self.typing_timer.timeout.connect(self._typing_tick)
        self._typing_text = ""
        self._typing_pos = 0

        # Confetti timer
        self._confetti_timer = QtCore.QTimer()
        self._confetti_timer.timeout.connect(self._confetti_tick)
        self._confetti_particles = []

        # Start theme (optional)
        if SOUND_THEME:
            play_sound(SOUND_THEME)

        # Start the chat with welcome message and first question
        QtCore.QTimer.singleShot(400, lambda: self.post_bot("🎉 Welcome to Kaun Banega Crorepati — Chatbot!"))
        QtCore.QTimer.singleShot(1400, self.next_question)

    # ---------------------------
    # Styles
    # ---------------------------
    def _option_stylesheet(self, normal=True, correct=False, wrong=False):
        base_style = """
            QPushButton {
                border: 2px solid #5a5a5a;
                color: #e0e0e0;
                font-weight: 700;
                font-size: 16px;
                border-radius: 20px;
                padding: 15px;
            }
        """
        if correct:
            return base_style + "QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4CAF50, stop:1 #2E7D32); border-color: #2E7D32; }"
        elif wrong:
            return base_style + "QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #D32F2F, stop:1 #B71C1C); border-color: #B71C1C; }"
        elif not normal: # 50-50 disabled
            return base_style + "QPushButton { background: #333; color: #777; border-color: #222; }"
        else: # Normal state
            return base_style + """
                QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0f1c30, stop:1 #1a3258); }
                QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #1a3258, stop:1 #0f1c30); border-color: #FFD700; }
                QPushButton:pressed { background: #081122; border-color: #FFD700; }
            """

    def _lifeline_stylesheet(self, enabled=True):
        if enabled:
            return "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #FFD700, stop:1 #FF8A00); color: black; font-weight:700; padding:8px; border-radius:8px; } QPushButton:disabled { opacity: 0.5; }"
        return "QPushButton { background: #444; color: #ccc; }"

    # ---------------------------
    # Ladder
    # ---------------------------
    def setup_ladder(self):
        self.ladder_list.clear()
        for i in range(10, 0, -1):
            item = QtWidgets.QListWidgetItem(f"Q{i}:  ₹{PRIZE_LADDER[i]:,}")
            item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.ladder_list.addItem(item)
        self.highlight_ladder()

    def highlight_ladder(self):
        # highlight current_index + 1
        for idx in range(self.ladder_list.count()):
            it = self.ladder_list.item(idx)
            level = 10 - idx
            if level == self.current_index + 1:
                it.setForeground(QtGui.QColor("#FFD700"))
                font = it.font(); font.setBold(True); it.setFont(font)
            else:
                it.setForeground(QtGui.QColor("#CDE7FF"))
                font = it.font(); font.setBold(False); it.setFont(font)

    # ---------------------------
    # Chat / Typing
    # ---------------------------
    def post_bot(self, text):
        """Type text with typing animation."""
        self._typing_text = text
        self._typing_pos = 0
        self.typing_timer.start(TYPING_SPEED_MS)

    def _typing_tick(self):
        if self._typing_pos >= len(self._typing_text):
            self.typing_timer.stop()
            self.chat.append("")  # new line
            return
        next_chunk = self._typing_text[self._typing_pos]
        self._typing_pos += 1
        # append character
        cursor = self.chat.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(next_chunk)
        self.chat.setTextCursor(cursor)
        self.chat.ensureCursorVisible()

    # ---------------------------
    # Game flow
    # ---------------------------
    def next_question(self):
        if self.current_index >= len(self.questions):
            self.win_game()
            return

        self.disabled_options = []
        q = self.questions[self.current_index]
        opts = q["options"]
        formatted = "\n".join([f"{chr(97+i)}. {opt}" for i, opt in enumerate(opts)])
        self.post_bot(f"\nQ{self.current_index+1} for ₹{PRIZE_LADDER[self.current_index+1]:,}\n\n{q['question']}\n\n{formatted}\n\n(Type a/b/c/d or click an option)")
        QtCore.QTimer.singleShot(400, self.reveal_options)

        # update ladder highlight
        self.highlight_ladder()

    def reveal_options(self):
        q = self.questions[self.current_index]
        for i, btn in enumerate(self.option_buttons):
            text = f"{chr(97+i)}. {q['options'][i]}"
            btn.setText(text)
            btn.setEnabled(True)
            btn.setStyleSheet(self._option_stylesheet(normal=True))
            # fade-in animation
            effect = QtWidgets.QGraphicsOpacityEffect()
            btn.setGraphicsEffect(effect)
            anim = QtCore.QPropertyAnimation(effect, b"opacity")
            anim.setDuration(350 + i*50)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def on_option_click(self, idx):
        # ignore disabled by lifeline
        if idx in self.disabled_options:
            return
        self.answer_selected(idx)

    def on_entry_submit(self):
        text = self.entry.text().strip().lower()
        self.entry.clear()
        if text == "quit":
            self.post_bot("\nYou chose to quit. Thank you for playing!")
            self.end_game()
            return
        if text not in ("a", "b", "c", "d"):
            self.post_bot("\nPlease enter a valid option (a/b/c/d) or click one of the buttons.")
            return
        idx = ord(text) - ord("a")
        if idx in self.disabled_options:
            self.post_bot("\nThat option is disabled by lifeline.")
            return
        self.answer_selected(idx)

    def answer_selected(self, idx):
        # lock options to prevent double click
        for btn in self.option_buttons:
            btn.setEnabled(False)

        q = self.questions[self.current_index]
        correct = q["answer"]

        # highlight the chosen button with a distinct color
        chosen_btn = self.option_buttons[idx]
        chosen_btn.setStyleSheet("QPushButton { background: #FFD700; color: #021822; font-weight:900; border-radius:20px; }")

        # reveal correct/wrong after small delay
        QtCore.QTimer.singleShot(700, lambda: self.reveal_answer(idx == correct, idx))

    def reveal_answer(self, is_correct, idx):
        q = self.questions[self.current_index]
        correct = q["answer"]

        if is_correct:
            self.option_buttons[idx].setStyleSheet(self._option_stylesheet(correct=True))
            play_sound(SOUND_CORRECT)
            self.post_bot("\n✅ Correct! 🎉")
            self.current_amount = PRIZE_LADDER[self.current_index+1]
            self.start_confetti()
            QtCore.QTimer.singleShot(1400, self.next_round)
        else:
            self.option_buttons[idx].setStyleSheet(self._option_stylesheet(wrong=True))
            self.option_buttons[correct].setStyleSheet(self._option_stylesheet(correct=True))
            play_sound(SOUND_WRONG)
            self.post_bot("\n❌ Wrong answer.")
            if self.current_index > 0:
                safe_amount = PRIZE_LADDER[self.current_index]
            else:
                safe_amount = 0
            self.current_amount = safe_amount
            QtCore.QTimer.singleShot(1200, self.end_game)

    def next_round(self):
        self.stop_confetti()
        self.current_index += 1
        self.disabled_options = []
        self.next_question()

    # ---------------------------
    # Lifelines
    # ---------------------------
    def use_lifeline(self, name):
        if not self.lifelines.get(name, False):
            self.post_bot(f"\nLifeline '{name}' already used.")
            return

        self.lifelines[name] = False
        btn = self.lifeline_buttons[name]
        btn.setEnabled(False)
        btn.setStyleSheet(self._lifeline_stylesheet(enabled=False))

        q = self.questions[self.current_index]
        correct = q["answer"]

        if name == "50-50":
            wrongs = [i for i in range(4) if i != correct]
            to_disable = random.sample(wrongs, 2)
            self.disabled_options = to_disable
            for i in to_disable:
                b = self.option_buttons[i]
                b.setText(f"{chr(97+i)}. ❌")
                b.setEnabled(False)
                b.setStyleSheet(self._option_stylesheet(normal=False))
            self.post_bot("\n🔍 50-50 used. Two wrong options removed.")
        elif name == "Audience":
            perc = [random.randint(5, 20) for _ in range(4)]
            perc[correct] += 50
            msg = "\n📊 Audience Poll:\n" + "\n".join([f"{chr(97+i)}: {q['options'][i]} — {perc[i]}%" for i in range(4)])
            self.post_bot(msg)
        elif name == "Flip":
            self.post_bot("\n🔄 Flip used — switching to a different question.")
            remaining = [i for i in range(len(self.questions)) if i > self.current_index]
            if remaining:
                swap_idx = random.choice(remaining)
                self.questions[self.current_index], self.questions[swap_idx] = self.questions[swap_idx], self.questions[self.current_index]
            self.reveal_options()

    # ---------------------------
    # End / Win / Quit
    # ---------------------------
    def end_game(self):
        self.post_bot(f"\n🎬 Game Over! You won ₹{self.current_amount:,}")
        QtWidgets.QMessageBox.information(self, "Game Over", f"Your total winning amount: ₹{self.current_amount:,}")
        self.close()

    def win_game(self):
        self.post_bot("\n🏆 CONGRATULATIONS! You completed all questions!")
        self.current_amount = PRIZE_LADDER[10]
        play_sound(SOUND_CORRECT)
        self.start_confetti()
        QtWidgets.QMessageBox.information(self, "Winner", f"🏆 YOU WON ₹{self.current_amount:,} 🏆")
        self.close()

    # ---------------------------
    # Confetti animation (simple)
    # ---------------------------
    def start_confetti(self):
        self._confetti_particles = []
        w = self.confetti_canvas.width() or 300
        for _ in range(50):
            p = {
                "x": random.randint(10, w - 10),
                "y": 0,
                "vx": random.uniform(-1, 1),
                "vy": random.uniform(2, 5),
                "rotation": random.uniform(0, 360),
                "rot_speed": random.uniform(5, 20),
                "color": QtGui.QColor(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)),
                "size": random.randint(6, 12)
            }
            self._confetti_particles.append(p)
        self._confetti_timer.start(30)

    def stop_confetti(self):
        self._confetti_timer.stop()
        self.confetti_canvas.clear()

    def _confetti_tick(self):
        from PySide6.QtGui import QPixmap, QPainter
        w = self.confetti_canvas.width() or 300
        h = self.confetti_canvas.height() or 120
        pix = QPixmap(w, h)
        pix.fill(QtGui.QColor(0, 0, 0, 0))
        painter = QPainter(pix)

        for p in self._confetti_particles:
            painter.save()
            painter.translate(p["x"], p["y"])
            painter.rotate(p["rotation"])
            painter.setBrush(p["color"])
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRect(-p["size"] / 2, -p["size"] / 2, p["size"], p["size"])
            painter.restore()

            p["y"] += p["vy"]
            p["x"] += p["vx"]
            p["vy"] += 0.06
            p["rotation"] += p["rot_speed"]

            # Reset particle if it falls off screen
            if p["y"] > h:
                p["y"] = -10
                p["x"] = random.randint(10, w - 10)
                p["vy"] = random.uniform(2, 5)
                p["vx"] = random.uniform(-1.5, 1.5)
                p["rot_speed"] = random.uniform(5, 20)
                p["color"] = QtGui.QColor(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

        painter.end()
        self.confetti_canvas.setPixmap(pix)

    # ---------------------------
    # Helpers
    # ---------------------------
    def eventFilter(self, obj, event):
        # hover effect: scale slightly
        if isinstance(obj, QtWidgets.QPushButton):
            if event.type() == QtCore.QEvent.Enter:
                obj.setGraphicsEffect(self._shadow_effect(18))
            elif event.type() == QtCore.QEvent.Leave:
                obj.setGraphicsEffect(None)
        return super().eventFilter(obj, event)

    def _shadow_effect(self, blur=12):
        ef = QtWidgets.QGraphicsDropShadowEffect()
        ef.setBlurRadius(blur)
        ef.setXOffset(0)
        ef.setYOffset(3)
        ef.setColor(QtGui.QColor(0, 0, 0, 160))
        return ef


# ---------------------------
# Run
# ---------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)

    # Enable high dpi icons for crispness
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app.setStyle("Fusion")

    w = KBCWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()