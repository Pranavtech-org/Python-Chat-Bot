import time
from typing import Dict, List


class KBCGame:
    def __init__(self):  # Fixed constructor
        self.questions = self._load_questions()
        self.current_amount = 0
        self.winner = True
        self.prize_ladder = {
            1: 1000,
            2: 2000,
            3: 3000,
            4: 4000,
            5: 5000,
            6: 6000,
            7: 7000,
            8: 8000,
            9: 9000,
            10: 10000
        }
        self.lifelines = {
            '50-50': True,
            'audience': True,
            'flip': True
        }

    def _load_questions(self) -> List[Dict]:
        return [
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

    def _print_with_delay(self, text: str, delay: float = 0.5):
        print(text)
        time.sleep(delay)

    def _show_lifelines(self):
        available = [name for name, available in self.lifelines.items() if available]
        if not available:
            return False

        self._print_with_delay("\nAvailable lifelines:")
        for i, lifeline in enumerate(available, 1):
            self._print_with_delay(f"{i}. {lifeline}")

        choice = input("\nWould you like to use a lifeline? (yes/no): ").lower()
        if choice == 'yes':
            lifeline_choice = input("Enter lifeline number: ")
            try:
                selected = available[int(lifeline_choice) - 1]
                self.lifelines[selected] = False
                return selected
            except (ValueError, IndexError):
                self._print_with_delay("Invalid choice. Continuing without lifeline.")
        return None

    def _use_50_50(self, options: List[str], correct_index: int):
        incorrect = [i for i in range(len(options)) if i != correct_index]
        remove = incorrect[:len(incorrect) // 2]
        return [opt if i not in remove else "❌" for i, opt in enumerate(options)]

    def _use_audience(self, correct_index: int):
        percentages = [0] * 4
        percentages[correct_index] = 60
        remaining = 40
        for i in range(4):
            if i != correct_index:
                val = min(remaining, 20)
                percentages[i] = val
                remaining -= val
        return percentages

    def _use_flip(self, options: List[str]):
        return options[::-1]

    def _display_question(self, question_data: Dict, q_num: int):
        self._print_with_delay(f"\nQuestion {q_num} for ₹{self.prize_ladder[q_num]:,}")
        self._print_with_delay("-" * 40)
        self._print_with_delay(question_data['question'] + "\n")

        options = question_data['options']
        correct_index = question_data['answer']

        lifeline = self._show_lifelines()
        modified_options = options.copy()

        if lifeline == '50-50':
            modified_options = self._use_50_50(options, correct_index)
        elif lifeline == 'audience':
            percentages = self._use_audience(correct_index)
            for i, (opt, perc) in enumerate(zip(options, percentages)):
                modified_options[i] = f"{opt} ({perc}%)"
        elif lifeline == 'flip':
            modified_options = self._use_flip(options)
            correct_index = len(options) - 1 - correct_index

        for i, opt in enumerate(modified_options):
            self._print_with_delay(f"{chr(97 + i)}. {opt}")

        return correct_index

    def _get_user_answer(self):
        while True:
            choice = input("\nEnter your choice (a-d) or 'quit' to exit: ").lower()
            if choice == 'quit':
                return None
            if choice in ['a', 'b', 'c', 'd']:
                return ord(choice) - ord('a')
            print("Invalid input. Please enter a, b, c, or d.")

    def play(self):
        self._print_with_delay("\nWelcome to Kaun Banega Crorepati!")
        self._print_with_delay("Hello Contestant! Get ready for an exciting game!\n")
        input("Press Enter to start the game...")

        for i, question in enumerate(self.questions, 1):
            correct_index = self._display_question(question, i)
            user_choice = self._get_user_answer()

            if user_choice is None:
                self._print_with_delay("\nYou've chosen to quit the game.")
                break

            if user_choice == correct_index:
                self.current_amount = self.prize_ladder[i]
                self._print_with_delay("\n🎉 Correct Answer! 🎉")
                self._print_with_delay(f"Congratulations! You've won ₹{self.current_amount:,}\n")

                if i < len(self.questions):
                    input("Press Enter for the next question...")
            else:
                self.winner = False
                self._print_with_delay("\n❌ Wrong Answer! ❌")
                if i > 1:
                    self.current_amount = self.prize_ladder[i - 1]
                    self._print_with_delay(f"You win ₹{self.current_amount:,}")
                break

        self._show_final_result()

    def _show_final_result(self):
        self._print_with_delay("\n" + "=" * 40)
        if self.winner and self.current_amount == self.prize_ladder[10]:
            self._print_with_delay("🏆 CONGRATULATIONS! YOU WON! 🏆")
            self._print_with_delay("Your performance was outstanding!")
        else:
            self._print_with_delay("Thank you for playing!")
        self._print_with_delay(f"Your total winning amount: ₹{self.current_amount:,}")
        self._print_with_delay("=" * 40 + "\n")


if __name__ == "__main__":  # Fixed this line
    game = KBCGame()
    game.play()
