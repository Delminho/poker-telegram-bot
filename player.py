class Player:
    def __init__(self, from_user):
        self.id = from_user.id
        self.username = from_user.username
        self.name = from_user.full_name
        self.cards = []
        self.balance = 0
        self.starting_balance = 0   # Amount of chips player started game with
        self.current_stage_bet = 0
        self.all_in = 0     # If player is all-in stores amount of chips he had at a start of hand

    def send_cards(self, bot):
        """Send player private message with his cards"""
        bot.send_message(self.id, f"Your cards:\n{self.cards[0]}{self.cards[1]}")

    def __eq__(self, other):
        if self.id == other.id and self.username == other.username:
            return True
        else:
            return False

