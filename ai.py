import random

class SmartOpponentAI:
    def __init__(self, opponent_type, offense_playbook, defensive_choices, matchups):
        self.opponent_type = opponent_type  # 'blitz', 'brains', or 'dynamic'
        self.offense_playbook = offense_playbook
        self.defensive_choices = defensive_choices
        self.matchups = matchups
        self.recent_user_plays = []  # Keeps last 5 plays for dynamic tracking

    def record_user_play(self, play_name):
        self.recent_user_plays.append(play_name)
        if len(self.recent_user_plays) > 5:
            self.recent_user_plays.pop(0)

    def get_ai_offense_play(self, down, ball_position, is_no_run_zone):
        valid_plays = [
            play for play, p_type in self.offense_playbook.items()
            if not (is_no_run_zone and p_type == "run")
        ]

        if self.opponent_type == "blitz":
            if down >= 3 or ball_position <= 20:
                deep_plays = ["Four Verticals", "Post-Corner", "Out & Up"]
                choices = [p for p in deep_plays if p in valid_plays]
                return random.choice(choices) if choices else random.choice(valid_plays)
            return random.choice(valid_plays)

        elif self.opponent_type in ["brains", "dynamic"]:
            # Finds defensive tendencies from user and counters them
            if self.recent_user_plays:
                most_frequent_def = max(set(self.recent_user_plays), key=self.recent_user_plays.count)
                counters = [
                    play for play, info in self.matchups.items()
                    if most_frequent_def in info.get("beats", []) and play in valid_plays
                ]
                if counters:
                    return random.choice(counters)
            return random.choice(valid_plays)

        return random.choice(valid_plays)

    def get_ai_defense_play(self, user_offense_play, ball_position, down):
        if self.opponent_type == "blitz":
            if down in [1, 2]:
                return random.choice(["Rush Blitz", "Rush Blitz", "Man Coverage"])
            else:
                return random.choice(["Cover 3", "Prevent", "Cover 2"])

        elif self.opponent_type == "brains":
            if ball_position >= 45:
                return "Goal Line Stand"
            rule = self.matchups.get(user_offense_play, {})
            counters = rule.get("counters", [])
            return random.choice(counters) if counters else random.choice(self.defensive_choices)

        elif self.opponent_type == "dynamic":
            # Dynamic AI: Checks if player spamming passes or runs
            if self.recent_user_plays:
                pass_count = sum(1 for p in self.recent_user_plays if self.offense_playbook.get(p) == "pass")
                if pass_count >= 4:
                    # Player is heavy passing; adapt to Cover 3 or Rush Blitz
                    return random.choice(["Cover 3", "Rush Blitz", "Cover 2"])
            
            # Counter specific play choice with 70% probability
            rule = self.matchups.get(user_offense_play, {})
            counters = rule.get("counters", [])
            if counters and random.random() < 0.70:
                return random.choice(counters)

            return random.choice(self.defensive_choices)

        return random.choice(self.defensive_choices)



    ## TYPE CHANGEMODEFOR AI SWITCH