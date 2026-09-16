import os
import json
import random
import sys
import textwrap
from ai import SmartOpponentAI

class NFLFlagGame:
    def __init__(self):
        self.load_game_data()
        self.scout_history = {}
        self.score = {"You": 0, "Opponent": 0}
        self.impossible_moves_count = 0
        self.half = 1
        self.time_remaining = 720
        self.ball_position = 5
        self.down = 1
        self.crossed_midfield = False
        self.possession = "You"
        self.first_half_possession = "You"
        self.ai = SmartOpponentAI(
            opponent_type="dynamic",
            offense_playbook=self.offense_playbook,
            defensive_choices=self.defensive_choices,
            matchups=self.matchups
        )

        self.ascii_digits = {
            '0': ["┌─┐", "│ │", "└─┘"],
            '1': [" ┐ ", " │ ", "─┴─"],
            '2': ["┌─┐", "┌─┘", "└──"],
            '3': ["┌─┐", " ─┤", "└─┘"],
            '4': ["│ │", "└─┤", "  │"],
            '5': ["┌─┐", "└─┐", "──┘"],
            '6': ["┌─┐", "├─┐", "└─┘"],
            '7': ["──┐", "  │", "  │"],
            '8': ["┌─┐", "├─┤", "└─┘"],
            '9': ["┌─┐", "└─┤", "──┘"]
        }

    def load_game_data(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        playbook_path = os.path.join(base_path, "data", "playbook.json")
        hints_path = os.path.join(base_path, "data", "hints.json")
        penalties_path = os.path.join(base_path, "data", "penalties.json")

        try:
            with open(playbook_path, "r") as f:
                pb_data = json.load(f)
                self.offense_playbook = pb_data["offense_playbook"]
                self.defensive_choices = pb_data["defensive_choices"]
                self.matchups = pb_data["matchups"]
                self.play_summaries = pb_data["play_summaries"]
                self.defense_summaries = pb_data["defense_summaries"]

            with open(hints_path, "r") as f:
                hint_data = json.load(f)
                self.defensive_scout_hints = hint_data["defensive_scout_hints"]
                self.offensive_scout_hints = hint_data["offensive_scout_hints"]

            with open(penalties_path, "r") as f:
                pen_data = json.load(f)
                self.offense_penalties = pen_data["offense_penalties"]
                self.defense_penalties = pen_data["defense_penalties"]
        except Exception as e:
            print(f"Error loading JSON data files: {e}")
            sys.exit(1)

    def get_scout_hint(self, category_dict, play_name):
        if play_name not in self.scout_history:
            self.scout_history[play_name] = []

        all_hints = category_dict.get(play_name, ["SCOUT REPORT: Opponent adjusting alignment."])
        recent_history = self.scout_history[play_name]

        available = [h for h in all_hints if h not in recent_history]
        if not available:
            available = all_hints

        chosen_hint = random.choice(available)
        recent_history.append(chosen_hint)

        if len(recent_history) > 3:
            recent_history.pop(0)

        return chosen_hint

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def check_quit(self, user_input):
        if user_input.strip().lower() in ["quit", "q"]:
            print("\nThanks for playing NFL Flag Football! Exiting game...")
            sys.exit()

    def get_play_summary(self, play_name):
        return self.play_summaries.get(play_name, "No explanation available.")

    def get_defense_summary(self, def_name):
        return self.defense_summaries.get(def_name, "No explanation available.")

    def get_ascii_score_string(self, score_num):
        s_str = f"{score_num:02d}"
        d1, d2 = s_str[0], s_str[1]
        return [
            f"{self.ascii_digits[d1][0]} {self.ascii_digits[d2][0]}",
            f"{self.ascii_digits[d1][1]} {self.ascii_digits[d2][1]}",
            f"{self.ascii_digits[d1][2]} {self.ascii_digits[d2][2]}"
        ]

    def render_ascii_scoreboard(self):
        you_ascii = self.get_ascii_score_string(self.score["You"])
        opp_ascii = self.get_ascii_score_string(self.score["Opponent"])

        print("+" + "=" * 58 + "+")
        print("|" + " SCOREBOARD ".center(58) + "|")
        print("| " + "YOU:".ljust(25) + "OPPONENT:".rjust(31) + " |")
        print(f"|    {you_ascii[0]}" + " " * 17 + "VS" + " " * 17 + f"{opp_ascii[0]}    |")
        print(f"|    {you_ascii[1]}" + " " * 36 + f"{opp_ascii[1]}    |")
        print(f"|    {you_ascii[2]}" + " " * 36 + f"{opp_ascii[2]}    |")
        print("+" + "=" * 58 + "+")

    def check_penalty(self):
        """Randomly triggers penalties (10% chance per play)."""
        if random.random() < 0.05:
            if random.random() < 0.5:
                pen = random.choice(self.offense_penalties)
                return "offense", pen
            else:
                pen = random.choice(self.defense_penalties)
                return "defense", pen
        return None, None

    def print_result_box(self, off_play, def_play, desc, penalty_text=None):
        box_width = 70
        content_width = box_width - 4

        print("\n+" + "-" * (box_width - 2) + "+")
        print("|" + " PLAY RESULT ".center(box_width - 2) + "|")
        print("+" + "=" * (box_width - 2) + "+")
        
        exec_str = f"Play Executed : {off_play} vs {def_play}"
        print(f"| {exec_str:<{content_width}} |")
        
        if penalty_text:
            p_lines = textwrap.wrap(f"FLAG ON FIELD: {penalty_text}", width=content_width)
            for line in p_lines:
                print(f"| {line:<{content_width}} |")
            print("+" + "-" * (box_width - 2) + "+")

        wrapped_desc = textwrap.wrap(f"Outcome       : {desc}", width=content_width)
        for line in wrapped_desc:
            print(f"| {line:<{content_width}} |")
            
        print("+" + "-" * (box_width - 2) + "+")

    def check_command(self, user_input):
        clean_input = user_input.strip().lower()
        if clean_input in ["quit", "q"]:
            print("\nThanks for playing NFL Flag Football!")
            sys.exit()
        elif clean_input == "changemode":
            self.select_opponent()
            return True
        return False

    def select_opponent(self):
        print("\n=== SELECT YOUR OPPONENT ===")
        print("1. Coach Blitz   (Aggressive, High Pressure & Deep Bombs)")
        print("2. Coach Brains  (Tactical, Static Counter AI)")
        print("3. Dynamic AI    (Adapts Mid-Game to Your Tendencies & Calling Patterns)")
        
        opp_choice = ""
        while opp_choice not in ["1", "2", "3"]:
            opp_choice = input("\nChoose Opponent (1, 2, or 3): ").strip()
            self.check_quit(opp_choice)

        types = {"1": "blitz", "2": "brains", "3": "dynamic"}
        opp_type = types[opp_choice]

        self.ai = SmartOpponentAI(
            opponent_type=opp_type,
            offense_playbook=self.offense_playbook,
            defensive_choices=self.defensive_choices,
            matchups=self.matchups
        )
        
        names = {"1": "Coach Blitz", "2": "Coach Brains", "3": "Dynamic Adaptive AI"}
        print(f"\nYou are taking on {names[opp_choice]}! Get ready!")
        input("\nPress ENTER to continue...")

    def perform_coin_flip(self):
        self.clear_screen()
        print("=" * 60)
        print("                   NFL FLAG COIN TOSS                   ")
        print("=" * 60)
        
        user_call = ""
        while user_call not in ["heads", "tails"]:
            user_call = input("Call the coin toss (Heads or Tails): ").strip().lower()
            self.check_quit(user_call)

        toss_result = random.choice(["heads", "tails"])
        print(f"\nThe coin toss landed on: {toss_result.upper()}")

        if user_call == toss_result:
            print("You won the coin toss!")
            choice = ""
            while choice not in ["1", "2"]:
                choice = input("Do you want to (1) Receive first or (2) Defer/Defend first? ").strip()
                self.check_quit(choice)
            if choice == "1":
                self.possession = "You"
                self.first_half_possession = "You"
                self.ball_position = 5
            else:
                self.possession = "Opponent"
                self.first_half_possession = "Opponent"
                self.ball_position = 45
        else:
            print("Opponent won the coin toss!")
            opp_choice = random.choice(["receive", "defend"])
            if opp_choice == "receive":
                self.possession = "Opponent"
                self.first_half_possession = "Opponent"
                self.ball_position = 45
            else:
                self.possession = "You"
                self.first_half_possession = "You"
                self.ball_position = 5
        
        input("\nPress ENTER to continue...")

    def is_no_run_zone(self):
        if self.possession == "You":
            return (20 <= self.ball_position < 25) if not self.crossed_midfield else (45 <= self.ball_position < 50)
        else:
            return (25 < self.ball_position <= 30) if not self.crossed_midfield else (0 < self.ball_position <= 5)

    def display_touchdown_screen(self, scorer):
        """Displays a full-screen Touchdown banner."""
        self.clear_screen()
        box_w = 60
        print("+" + "=" * (box_w - 2) + "+")
        print("|" + " " * (box_w - 2) + "|")
        print("|" + "TOUCHDOWN!!!".center(box_w - 2) + "|")
        print("|" + f"*** {scorer.upper()} SCORED 6 POINTS! ***".center(box_w - 2) + "|")
        print("|" + " " * (box_w - 2) + "|")
        print("+" + "=" * (box_w - 2) + "+")
        input("\n                    -- PRESS ENTER FOR EXTRA POINT --            ")

    def handle_extra_point(self, scorer):
        """Handles 1-point (from 5yd) or 2-point (from 10yd) extra point attempts."""
        self.clear_screen()
        print("=" * 60)
        print(f"               EXTRA POINT ATTEMPT ({scorer.upper()})             ")
        print("=" * 60)

        if scorer == "You":
            print("Choose Extra Point Attempt:")
            print("1. 1-Point Try (Pass from 5-yard line)")
            print("2. 2-Point Try (Pass from 10-yard line)")
            
            choice = ""
            while choice not in ["1", "2"]:
                choice = input("\nSelect attempt (1 or 2): ").strip()
                self.check_quit(choice)
            
            pt_value = int(choice)
            def_play = random.choice(self.defensive_choices)
            print(f"\nDefense lines up in: {def_play}")
            off_play = self.pick_offense_play(def_play)
            
            # 1-pt gives 65% base success, 2-pt gives 45% base success
            success_chance = 0.65 if pt_value == 1 else 0.45
            rule = self.matchups.get(off_play, {})
            if def_play in rule.get("beats", []):
                success_chance += 0.20
            elif def_play in rule.get("counters", []):
                success_chance -= 0.25

            if random.random() < success_chance:
                print(f"\nEXTRA POINT CONVERTED! Successful {off_play}!")
                self.score["You"] += pt_value
            else:
                print(f"\nEXTRA POINT FAILED! Defended by {def_play}.")

        else:  # Opponent attempt
            pt_value = 1 if random.random() < 0.70 else 2
            print(f"Opponent attempts a {pt_value}-Point Conversion!")
            off_play = self.ai.get_ai_offense_play(1, 45, True)
            def_play = self.pick_defense(off_play)

            success_chance = 0.65 if pt_value == 1 else 0.45
            rule = self.matchups.get(off_play, {})
            if def_play in rule.get("beats", []):
                success_chance -= 0.20
            elif def_play in rule.get("counters", []):
                success_chance += 0.25

            if random.random() < success_chance:
                print(f"\nOPPONENT CONVERTED THE {pt_value}-POINT EXTRA POINT!")
                self.score["Opponent"] += pt_value
            else:
                print("\nEXTRA POINT DEFENDED! No good!")

        input("\nPress ENTER to continue to kickoff...")

    def print_field(self):
        self.render_ascii_scoreboard()

        field_length = 50
        pos_char = int((self.ball_position / 50.0) * field_length)

        field_line = list("-" * (field_length + 1))
        field_line[25] = "M"

        if 0 <= pos_char <= field_length:
            field_line[pos_char] = "X"

        field_str = "".join(field_line)

        if self.possession == "You":
            target_line = 50 if self.crossed_midfield else 25
            target_name = "End Zone (50yd)" if self.crossed_midfield else "Midfield (25yd)"
            yards_needed = target_line - self.ball_position
            dir_str = "Attacking RIGHT --->"
            mode_str = "MODE: OFFENSE - DRIVE THE BALL"
            obj_str = f"Target: {target_name} ({yards_needed}yd to go)"
        else:
            target_line = 0 if self.crossed_midfield else 25
            target_name = "Your End Zone (0yd)" if self.crossed_midfield else "Midfield (25yd)"
            yards_needed = self.ball_position - target_line
            dir_str = "<--- Opponent Attacking LEFT"
            mode_str = "MODE: DEFENSE - STOP THE OFFENSE"
            obj_str = f"Defending: Stop Opponent from reaching {target_name} ({yards_needed}yd cushion)"

        nrz_status = " [NO-RUN ZONE]" if self.is_no_run_zone() else ""

        print(f" {mode_str:<40} | HALF: {self.half} ({self.time_remaining // 60}:{self.time_remaining % 60:02d})")
        print("=" * 60)
        print(f" YOUR ENDZONE [0] |{field_str}| [50] OPP ENDZONE")
        print("                 0    10   20  MID(25)  30   40   50")
        print(f" Ball Spot: {self.ball_position} yd line | Down: {self.down} of 4 | Direction: {dir_str}")
        print(f" Possession: {self.possession} | Objective: {obj_str}{nrz_status}")
        print("=" * 60)

    def pick_offense_play(self, upcoming_defense):
        play_list = list(self.offense_playbook.keys())
        no_run = self.is_no_run_zone()

        print("\n" + "-" * 60)
        hint = self.get_scout_hint(self.defensive_scout_hints, upcoming_defense)
        print(f"[!] {hint}")
        print("-" * 60)

        while True:
            print("\n--- OFFENSIVE PLAYBOOK ---")
            for i, p in enumerate(play_list, 1):
                p_type = self.offense_playbook[p].upper()
                disabled = " [DISABLED - NO-RUN ZONE]" if (no_run and p_type == "RUN") else ""
                print(f" {i}. {p:<25} ({p_type}){disabled}")
            
            user_input = input("\nSelect play # (or '# desc' for breakdown, 'auto' for random): ").strip().lower()
            if self.check_command(user_input):
                continue

            if user_input == 'auto':
                pass_plays = [p for p in play_list if self.offense_playbook[p] == "pass"]
                return random.choice(pass_plays if no_run else play_list)

            if 'desc' in user_input or 'info' in user_input or 'help' in user_input:
                digits = [int(s) for s in user_input.split() if s.isdigit()]
                if digits and 0 <= digits[0] - 1 < len(play_list):
                    play_name = play_list[digits[0] - 1]
                    print("\n" + "- " * 30)
                    print(f"PLAY BREAKDOWN: {play_name.upper()}")
                    print(self.get_play_summary(play_name))
                    print("- " * 30)
                    continue

            if user_input.isdigit() and 0 <= int(user_input) - 1 < len(play_list):
                selected = play_list[int(user_input) - 1]
                if no_run and self.offense_playbook[selected] == "run":
                    print("Illegal Play! Running plays are prohibited in the No-Run Zone.")
                    continue
                return selected
            print("Invalid selection.")

    def pick_defense(self, upcoming_offense):
        print("\n" + "-" * 60)
        hint = self.get_scout_hint(self.offensive_scout_hints, upcoming_offense)
        print(f"[!] {hint}")
        print("-" * 60)

        while True:
            print("\n--- DEFENSIVE CALL SHEET  ---")
            for i, d in enumerate(self.defensive_choices, 1):
                print(f" {i}. {d}")
            
            choice = input("\nSelect defense # (or '# desc' for breakdown, 'auto' for random): ").strip().lower()
            self.check_quit(choice)

            if choice == 'auto':
                return random.choice(self.defensive_choices)

            if 'desc' in choice or 'info' in choice or 'help' in choice:
                digits = [int(s) for s in choice.split() if s.isdigit()]
                if digits and 0 <= digits[0] - 1 < len(self.defensive_choices):
                    def_name = self.defensive_choices[digits[0] - 1]
                    print("\n" + "- " * 30)
                    print(f"DEFENSE BREAKDOWN: {def_name.upper()}")
                    print(self.get_defense_summary(def_name))
                    print("- " * 30)
                    continue

            if choice.isdigit() and 0 <= int(choice) - 1 < len(self.defensive_choices):
                return self.defensive_choices[int(choice) - 1]
            print("Invalid selection.")

    def resolve_play(self, offense_play, defense_play):
        rule = self.matchups.get(offense_play, {"beats": [], "counters": []})
        turnover_info = None

        if self.offense_playbook[offense_play] == "pass":
            if defense_play not in rule["counters"] and random.random() < 0.12:
                drop_descs = [
                    f"DROPPED PASS! Clear separation on {offense_play}, but receiver dropped it!",
                    f"INCOMPLETE! The pass slips right through the receiver's hands on {offense_play}!"
                ]
                return 0, random.choice(drop_descs), turnover_info

        if defense_play in rule["beats"]:
            gain = random.randint(12, 22)
            desc = f"{offense_play} EXPLOITED the defense! Gain of {gain} yards!"
        elif defense_play in rule["counters"]:
            if self.offense_playbook[offense_play] == "pass" and random.random() < 0.25:
                spot = min(50, self.ball_position + random.randint(5, 12)) if self.possession == "You" else max(0, self.ball_position - random.randint(5, 12))
                turnover_info = {"type": "interception", "spot": spot}
                return 0, f"INTERCEPTED! Defense jumped the route on {offense_play}!", turnover_info
            gain = random.randint(-3, 2)
            desc = f"{offense_play} STUFFED by defense! Yardage: {gain} yards."
        else:
            gain = random.randint(4, 9)
            desc = f"{offense_play} executed for a solid gain of {gain} yards."

        return gain, desc, turnover_info

    def advance_clock(self, seconds):
        self.time_remaining -= seconds
        return self.time_remaining <= 0

    def play_drive(self):
        self.clear_screen()
        self.print_field()

        # Pick Plays with AI
        if self.possession == "You":
            def_play = self.ai.get_ai_defense_play("", self.ball_position, self.down)
            off_play = self.pick_offense_play(def_play)
            self.ai.record_user_play(off_play)
        else:
            off_play = self.ai.get_ai_offense_play(self.down, self.ball_position, self.is_no_run_zone())
            def_play = self.pick_defense(off_play)
            self.ai.record_user_play(def_play)

        # Check Penalty
        side, penalty = self.check_penalty()
        if penalty:
            p_text = penalty["text"]
            p_yards = penalty["yards"]
            
            # Apply penalty yards
            if self.possession == "You":
                self.ball_position += p_yards if side == "defense" else -p_yards
            else:
                self.ball_position -= p_yards if side == "defense" else -p_yards
            
            self.ball_position = max(1, min(49, self.ball_position))
            self.print_result_box(off_play, def_play, "Play negated by penalty.", p_text)

            if not penalty["replay_down"]:
                self.down += 1
            
            input("\nPress ENTER to continue...")
            return

        # Normal Play Execution
        gain, desc, turnover_info = self.resolve_play(off_play, def_play)
        self.print_result_box(off_play, def_play, desc)

        time_expired = self.advance_clock(random.randint(20, 30))

        if turnover_info:
            self.possession = "Opponent" if self.possession == "You" else "You"
            self.down = 1
            self.crossed_midfield = False  # Reset for turnover
            input("\nPress ENTER to continue...")
            return

        if self.possession == "You":
            self.ball_position += gain
        else:
            self.ball_position -= gain
    # Check Touchdown
        if self.possession == "You" and self.ball_position >= 50:
            self.score["You"] += 6
            self.display_touchdown_screen("You")
            self.handle_extra_point("You")
            
            # Kickoff / Change Possession
            self.possession = "Opponent"
            self.ball_position = 45
            self.down = 1
            self.crossed_midfield = False
            return

        elif self.possession == "Opponent" and self.ball_position <= 0:
            self.score["Opponent"] += 6
            self.display_touchdown_screen("Opponent")
            self.handle_extra_point("Opponent")
            
            # Kickoff / Change Possession
            self.possession = "You"
            self.ball_position = 5
            self.down = 1
            self.crossed_midfield = False
            return

        # Midfield / First Down Progress Check
        if self.possession == "You":
            # Reset flag if pushed back behind midfield
            if self.ball_position < 25 and self.crossed_midfield:
                self.crossed_midfield = False

            # Crossing midfield grants First Down
            if self.ball_position >= 25 and not self.crossed_midfield:
                print("\nFIRST DOWN! You crossed midfield!")
                self.crossed_midfield = True
                self.down = 1
            else:
                self.down += 1
        else:
            # Opponent possession logic
            if self.ball_position > 25 and self.crossed_midfield:
                self.crossed_midfield = False

            if self.ball_position <= 25 and not self.crossed_midfield:
                print("\nFIRST DOWN! Opponent crossed midfield!")
                self.crossed_midfield = True
                self.down = 1
            else:
                self.down += 1

        # Check Turnover on Downs
        if self.down > 4:
            print("\nTURNOVER ON DOWNS!")
            self.possession = "Opponent" if self.possession == "You" else "You"
            self.down = 1
            self.crossed_midfield = False  # Reset midfield status for new drive

        input("\nPress ENTER to proceed...")


    def start(self):
        self.clear_screen()
        print("\n=== NFL FLAG FOOTBALL ENGINE ===")
        self.perform_coin_flip()
        
        while self.half <= 2:
            self.play_drive()

if __name__ == '__main__':
    game = NFLFlagGame()
    game.start()