from telebot import types
from itertools import cycle
from collections import deque

from deck import Deck
from player import Player
from combination import Combination



class Game:
    """Store all needed information for a game and start a new game"""
    games = 0
    def __init__(self, bot):
        self.is_active = False
        self.stage = 0
        self.joined_players = deque()
        self.players_in_game = []
        self.active_players_count = 0   # Players that are still in game and haven't gone all-in
        self.chat = None
        self.bot = bot
        self.current_message = None
        self.deck = Deck()
        self.community_cards = []
        self.player_to_act = None
        self.next_to_last_to_act = None     # If nobody raises until its player, stage ends
        self.current_bet_size = 0
        self.pot = 0

        self.set_stakes(1)

        self._actions_message = ''  # Message that stores what actions were taken this stage
        self._temp_messages = []    # List to store messages that should be deleted after reply
        Game.games += 1

    @property
    def str_community_cards(self):
        """Get string representation of currently available community cards"""
        if self.stage == 1:
            return ''
        elif self.stage == 2:
            return ''.join([str(card) for card in self.community_cards[:3]]) + '\n'    # str of 3 first community cards
        elif self.stage == 3:
            return ''.join([str(card) for card in self.community_cards[:4]]) + '\n'    # str of 4 first community cards
        elif self.stage == 4:
            return ''.join([str(card) for card in self.community_cards]) + '\n'    # str of all 5 community cards

    @property
    def message_text(self):
        """Get message needed for current stage"""
        if self.stage == 0:     # Setting up stage
            text = f"Created game hub\nBlinds: {self.SB_value}/{self.BB_value} \nPlayers joined:\n"
            for player in self.joined_players:
                text += player.name + f"({player.balance} chips)\n"
                text += f"Minimum buy-in is {self.min_buy_in}, add chips if you have less"
            return text

        elif 0 < self.stage < 5:     # Betting stages
            text = f"Pot:{self.pot}\n"
            text += self.str_community_cards
            text += self._actions_message
            # If player can't check it says price to call
            if self.player_to_act.current_stage_bet == self.current_bet_size:
                text += f"{self.player_to_act.name}({self.player_to_act.balance}), your move"
            else:
                text += f"{self.player_to_act.name}({self.player_to_act.balance}), {self.price_to_call()} to call"
            return text

        elif self.stage == 5:   # Game over stage
            community_cards_str = ''.join([str(card) for card in self.community_cards])
            text = self._actions_message
            text += community_cards_str + "\n"
            text +="Balances:\n"
            for player in self.joined_players:
                text += f"{player.name}: {player.balance}\n"
            text += f"Minimum buy-in is {self.min_buy_in}, add chips if you have less"
            return text

    @property
    def markup(self):
        """Get markup needed for current stage"""
        if 0 < self.stage < 5:     # Betting stages
            markup = types.InlineKeyboardMarkup()
            bet_btn = types.InlineKeyboardButton("Bet", callback_data='bet')
            check_btn = types.InlineKeyboardButton("Check", callback_data='check')
            fold_btn = types.InlineKeyboardButton("Fold", callback_data='fold')
            call_btn = types.InlineKeyboardButton(f"Call {self.price_to_call()}", callback_data='call')
            all_in_btn = types.InlineKeyboardButton(f"ALL IN", callback_data='all_in')

            if self.player_to_act.current_stage_bet >= self.current_bet_size:   # All-in or Bet or Check or Fold
                markup.add(all_in_btn, bet_btn, check_btn, fold_btn)
            elif self.player_to_act.balance == self.price_to_call():   # All-in or Fold
                markup.add(all_in_btn, fold_btn)
            # When all players went all-in or folded and last player need to call or fold
            elif self.player_to_act.balance > self.price_to_call() and self.active_players_count == 1:
                markup.add(call_btn, fold_btn)
            else:
                markup.add(all_in_btn, bet_btn, call_btn, fold_btn)     # All-in or Bet or Call or Fold
            return markup

        else:     # Setting up and Game over stages
            markup = types.InlineKeyboardMarkup(row_width=2)
            join_btn = types.InlineKeyboardButton("Join", callback_data='join_game')
            start_game_btn = types.InlineKeyboardButton("Start Game", callback_data='start_game')
            change_blinds_btn = types.InlineKeyboardButton("Change Blinds", callback_data='change_blinds')
            change_balance_btn = types.InlineKeyboardButton("Change My Balance", callback_data='change_balance')
            play_again_btn = types.InlineKeyboardButton("Play Again", callback_data='play_again')
            leave_btn = types.InlineKeyboardButton("Leave", callback_data='leave')
            # Set Up Stage
            if self.stage == 0:
                markup.add(change_balance_btn, change_blinds_btn, leave_btn, join_btn, start_game_btn)
            # Game Over Stage
            else:
                markup.add(change_balance_btn, change_blinds_btn, leave_btn, join_btn, play_again_btn)
            return markup

    def update_message(self):
        """Update current message and markup"""
        self.bot.edit_message_text(self.message_text, self.chat, self.current_message.id, reply_markup=self.markup)

    def delete_message(self, message):
        """Delete message sent by bot"""
        self.bot.delete_message(message.chat.id, message.message_id)

    def add_player(self, new_player: Player):
        """Adds player to game using message(or call) from that user"""
        new_player.balance = self.default_balance
        self.joined_players.append(new_player)

    def remove_player(self, leaver: Player):
        """Removes player from the game"""
        self.joined_players.remove(leaver)
        self._actions_message += f"{leaver.name} left with {leaver.balance} chips\n"

    def deal_cards(self):
        """Imitation of dealing cards in real life"""
        # Dealing 2 cards for each player one at the time and sending them this cards in PM
        for player in self.joined_players:
            player.cards.append(self.deck.take_card())
        for player in self.joined_players:
            player.cards.append(self.deck.take_card())
            player.send_cards(self.bot)

        self.deck.take_card()
        for i in range(3):
            self.community_cards.append(self.deck.take_card())
        self.deck.take_card()
        self.community_cards.append(self.deck.take_card())
        self.deck.take_card()
        self.community_cards.append(self.deck.take_card())

    def renew_deck(self):
        """Take back all cards from the table and take new full deck"""
        # Reset all player's cards from previous game
        for player in self.joined_players:
            player.cards = []
        # Reset all community cards from previous game
        self.community_cards = []
        # Make a new full deck
        self.deck = Deck()

    def set_stakes(self, new_SB_value: int):
        """Set blinds default balance, min buy-in"""
        self.SB_value = new_SB_value
        self.BB_value = self.SB_value * 2
        self.default_balance = self.BB_value * 100  # Amount of chips each player gets by default
        self.min_buy_in = self.BB_value * 10    # You can't join with fewer chips than that

    def prepare_game(self):
        """Setting everything up for game to start and dealing cards"""
        self.joined_players = deque([player for player in self.joined_players if player.balance >= self.min_buy_in])
        if len(self.joined_players) > 1:
            self.stage = 1
            self.pot = 0
            self.is_active = True
            self.deal_cards()
            self._actions_message = ''
            # Making each game SB position shift to the left
            self.joined_players.rotate(-1)
            self.players_in_game = list(self.joined_players)
            self.active_players_count = len(self.players_in_game)
            self.players_in_game_iter = cycle(self.players_in_game)
            self.player_to_act = next(self.players_in_game_iter)
            for player in self.players_in_game:
                player.starting_balance = player.balance
            # Putting blinds
            self.player_bet(self.SB_value)
            self.next_player()
            self.player_bet(self.BB_value)
            self.next_player()
            # Making Big blind last to act
            self.next_to_last_to_act = self.player_to_act
            self.update_message()
        else:
            self.handle_callbacks()

    def handle_callbacks(self):
        """Handles all the callbacks"""
        @self.bot.callback_query_handler(func=lambda call: True)
        def callbacks(call):
            # Player bets callback
            if call.data == 'bet':
                if self.player_to_act.id == call.from_user.id:
                    msg = self.bot.send_message(self.chat,
                                                f"@{call.from_user.username} reply with a bet size",
                                                reply_markup=types.ForceReply(selective=True),
                                                disable_notification=True)
                    self._temp_messages.append(msg)
                    self.bot.register_next_step_handler(msg, self.player_bet_callback)
                else:
                    self.handle_callbacks()

            # Player call callback
            elif call.data == 'call':
                if self.player_to_act.id == call.from_user.id:
                    self.player_bet(self.price_to_call() + self.player_to_act.current_stage_bet)
                    self.next_player()
                    self.update_message()
                    self.handle_callbacks()
                else:
                    self.handle_callbacks()

            # Player All-in callback
            elif call.data == 'all_in':
                if self.player_to_act.id == call.from_user.id:
                    self.player_all_in()
                    self.next_player()
                    self.update_message()
                    self.handle_callbacks()
                else:
                    self.handle_callbacks()

            # Player check callback
            elif call.data == 'check':
                if self.player_to_act.id == call.from_user.id:
                    self.handle_call(0)
                    self.next_player()
                    self.update_message()
                    self.handle_callbacks()
                else:
                    self.handle_callbacks()

            # Player fold callback
            elif call.data == 'fold':
                if self.player_to_act.id == call.from_user.id:
                    self.player_fold()
                    self.update_message()
                    self.handle_callbacks()
                else:
                    self.handle_callbacks()

            # Joining game callback
            elif call.data == 'join_game' and not self.is_active and len(self.joined_players) < 12:
                new_player = Player(call.from_user)
                if new_player not in self.joined_players:
                    self.add_player(new_player)
                    self.update_message()

            # Leaving game callback
            elif call.data == 'leave':
                leaver_id = call.from_user.id
                for player in self.joined_players:
                    if player.id == leaver_id:
                        self.remove_player(player)
                        break
                self.update_message()

            # Changing blinds callback
            elif call.data == 'change_blinds':
                msg = self.bot.send_message(self.chat, f"Reply with small blind value:", disable_notification=True)
                self._temp_messages.append(msg)
                self.bot.register_next_step_handler(msg, self.change_blinds_callback)

            # Player changing his balance callback
            elif call.data == 'change_balance':
                msg = self.bot.send_message(self.chat,
                                            f"@{call.from_user.username} reply with balance you want to have",
                                            reply_markup=types.ForceReply(selective=True), disable_notification=True)
                self._temp_messages.append(msg)
                self.bot.register_next_step_handler(msg, self.change_balance_callback)

            # Play Again callback
            elif call.data == 'play_again':
                self.reset_stage_information()
                self.renew_deck()
                # Reset all-ins
                for player in self.joined_players:
                    player.all_in = 0
                self.prepare_game()

            # Start game callback
            elif call.data == 'start_game':
                self.prepare_game()
                self.handle_callbacks()


    def change_blinds_callback(self, message):
        """Updating blinds based on any player's input"""
        try:
            new_SB_value = int(message.text)
            if new_SB_value < 1:
                raise ValueError
            old_default = self.default_balance
            self.set_stakes(new_SB_value)
            # Updating players balances for new stakes
            for player in self.joined_players:
                if player.balance == old_default:
                    player.balance = self.default_balance

            # Delete message saying to "Reply with small blind"
            message_replied = self._temp_messages.pop()
            self.delete_message(message_replied)

            self.update_message()
            self.handle_callbacks()
        except ValueError:
            # Wait for another reply
            self.bot.register_next_step_handler(self._temp_messages[-1], self.change_blinds_callback)

    def change_balance_callback(self, message):
        """Updating player's balance based on his input"""
        try:
            new_balance = int(message.text)
            if new_balance < self.min_buy_in:
                raise ValueError
            # Find a player who is changing balance and update his balance
            for player in self.joined_players:
                if player.id == message.from_user.id:
                    player.balance = new_balance
                    break

            # Deleting message saying to "reply with balance"
            message_replied = self._temp_messages.pop()
            self.delete_message(message_replied)

            self.update_message()
            self.handle_callbacks()
        except ValueError:
            # Wait for another reply
            self.bot.register_next_step_handler(self._temp_messages[-1], self.change_balance_callback)

    def player_bet_callback(self, message):
        """Checks if player's input is correct if so handles bet otherwise just waits for another reply"""
        try:
            if message.from_user.id == self.player_to_act.id:
                bet_value = int(message.text)
                if bet_value < self.current_bet_size:
                    raise ValueError("Bet size if less than current bet size")
                # Count how many more chips player bets
                over = bet_value - self.player_to_act.current_stage_bet
                self.player_bet(over)
                self.next_player()
                self.update_message()
                self.handle_callbacks()

                # Deleting message saying to "reply with a bet size"
                message_replied = self._temp_messages.pop()
                self.delete_message(message_replied)
            else:
                # If player replies is not player to act than just ignore this reply and wait for another(except block)
                raise ValueError

        except ValueError:
            # Wait for another reply
            self.bot.register_next_step_handler(self._temp_messages[-1], self.player_bet_callback)

    def player_bet(self, bet_size: int):
        """Handle player bets and player calls cases"""
        if self.player_to_act.balance > bet_size:
            self.player_to_act.balance -= bet_size
            self.pot += bet_size
            self.player_to_act.current_stage_bet += bet_size
            # Raise situation
            if self.player_to_act.current_stage_bet > self.current_bet_size:
                self.handle_raise()
            # Call situation
            else:
                self.handle_call(bet_size)
        else:
            self.player_all_in()

    def player_all_in(self):

        bet_size = self.player_to_act.balance

        self.player_to_act.balance = 0
        self.pot += bet_size
        self.player_to_act.current_stage_bet += bet_size
        self.player_to_act.all_in = self.player_to_act.starting_balance
        self.active_players_count -= 1

        # Raise situation
        if self.player_to_act.current_stage_bet > self.current_bet_size:
            self.handle_raise()
        # Call situation
        else:
            self.handle_call(bet_size)

    def price_to_call(self):
        """Calculate price to call for current player_to_act"""
        price = self.current_bet_size - self.player_to_act.current_stage_bet
        if self.player_to_act.balance > price:
            return price
        else:
            return self.player_to_act.balance   # If player doesn't have enough money he should go all-in

    def handle_raise(self):
        """Handle raise from player"""
        self.current_bet_size = self.player_to_act.current_stage_bet
        self._actions_message += f"{self.player_to_act.name}({self.player_to_act.balance}) " \
                                 f"raises to {self.player_to_act.current_stage_bet}\n"
        self.next_to_last_to_act = self.player_to_act

    def handle_call(self, bet_size):
        """Handle call or check from player"""
        if bet_size:
            self._actions_message += f"{self.player_to_act.name}({self.player_to_act.balance}) calls {bet_size} more\n"
        else:
            self._actions_message += f"{self.player_to_act.name}({self.player_to_act.balance}) checks\n"

    def player_fold(self):
        """Handle player folding(including jumping to next player)"""
        self._actions_message += f"{self.player_to_act.name}({self.player_to_act.balance}) folds\n"
        next_to_folded_player = next(self.players_in_game_iter)
        self.players_in_game.remove(self.player_to_act)
        self.active_players_count -= 1

        self.update_message()

        # Can't modify list while iterating so need to create new iterator and move to position where old one was
        self.update_iterator(next_to_folded_player)

    def update_iterator(self, next_to_folded_player):
        """Make new iterator if active players list changes and iterate to player who is next to act"""
        self.players_in_game_iter = cycle(self.players_in_game)
        # Iterator that will be one ahead our iterator so our iterator will point to player one before next_to_folded
        players_in_game_next_iter = cycle(self.players_in_game)
        # Finding a player with who next_player() would give us what we need
        while next(players_in_game_next_iter) != next_to_folded_player:
            self.player_to_act = next(self.players_in_game_iter)
        else:
            self.next_player()

    def next_player(self):
        """Move to next player"""
        self.player_to_act = next(self.players_in_game_iter)
        # Everyone but 1 folds => last one is winner
        if len(self.players_in_game) == 1:
            self.game_over()
        elif self.player_to_act == self.next_to_last_to_act:
            if self.active_players_count > 1:
                self.next_stage()
            else:
                # If 1 active player remains then he check through automatically
                self.game_over()
        elif self.player_to_act.all_in:        # If player is all-in skip him
            self.next_player()

    def next_stage(self):     # TODO add timeouts so before next stage players can see last move
        """Move to the next stage"""
        if self.stage < 4:
            self.stage += 1
            self.reset_stage_information()

            # Finding first player to act in next stage and making him next to last to act
            self.players_in_game_iter = cycle(self.players_in_game)
            self.player_to_act = next(self.players_in_game_iter)
            if self.player_to_act.all_in:
                self.next_player()
            self.next_to_last_to_act = self.player_to_act
        else:
            self.game_over()

    def reset_stage_information(self):
        """Reset all information related only to previous stage"""
        for player in self.joined_players:
            player.current_stage_bet = 0
        self._actions_message = ''
        self.current_bet_size = 0

    def game_over(self):
        self.stage = 5
        self._actions_message = ''
        self.is_active = False
        # Get combination of each player that left
        for player in self.players_in_game:
            player.combination = Combination(player.cards, self.community_cards)
        # Find and reward winner(s)
        self.find_winner()

    def find_winner(self):
        """Find winner and give him his reward"""
        # All folded so winner takes all
        if len(self.players_in_game) == 1:
            winner = self.players_in_game[0]
            self.reward_winner(winner, self.pot)
        else:
            # Find all the players with best(winning) hand
            winner_hand = max(self.players_in_game, key=lambda player: player.combination).combination.hand
            winners = [player for player in self.players_in_game if player.combination.hand == winner_hand]
            # Only one player with winning combination
            if len(winners) == 1:
                winner = winners[0]
                if not winner.all_in:
                    self.reward_winner(winner, self.pot)
                    return
                else:
                    winnings = 0
                    for player in self.joined_players:
                        # Else all player spent is already taken by someone
                        if player.starting_balance:
                            player_spent = player.starting_balance - player.balance
                            # Player all-in can't take from any player more than he spent
                            player_lost_to_winner = min(winner.all_in, player_spent)
                            winnings += player_lost_to_winner
                            player.starting_balance -= player_lost_to_winner

                    self.reward_winner(winner, winnings)
                    # If winner can't take whole pot find winner from other players to take the rest
                    if self.pot > 0:
                        self.players_in_game.remove(winner)
                        return self.find_winner()

            # Two or more players tied with best hand
            elif len(winners) > 1:
                winners_count = len(winners)
                # TODO winnings report for some will split into few lines (several winners some of them all-in)
                # Finding a smallest all-in value to make a main pot that will split evenly between all winners
                allins = [winner.all_in for winner in winners if winner.all_in]
                if allins:
                    max_win_for_all = min(allins)
                    # Counting main pot which should be split between all winners evenly
                    main_pot = 0
                    for player in self.joined_players:
                        # Else all player spent is already taken by someone so just move to next player
                        if player.starting_balance:
                            player_spent = player.starting_balance - player.balance
                            player_lost_to_main_pot = min(max_win_for_all, player_spent)
                            main_pot += player_lost_to_main_pot
                            player.starting_balance -= player_lost_to_main_pot

                    # Count how much each player should get
                    main_pot_winnings = main_pot // winners_count
                    remainders = main_pot - main_pot_winnings * winners_count
                    self.pot -= remainders  # so when we reward winners pot decreased exactly by main_pot value

                    # Reward winners and get rid of those who received all winnings
                    for winner in winners:
                        self.reward_winner(winner, main_pot_winnings)
                        # If winner is the one with the smallest all-in, he received all his winnings
                        if winner.all_in == max_win_for_all:
                            self.players_in_game.remove(winner)

                    # As some players already were rewarded we can now find winners among others to take the rest
                    if self.pot > 0:
                        return self.find_winner()

                else:
                    # If no winner is all-in then pot just splits evenly between players
                    winnings = self.pot // winners_count
                    for winner in winners:
                        self.reward_winner(winner, winnings)
                    return

            else:
                raise Exception("No winner(should not ever happen)")

    def reward_winner(self, winner, winnings):
        """Update winner's balance and game pot, add report to main message"""
        winner_cards_str = ''.join([str(card) for card in winner.cards])
        self._actions_message += f"{winner.name}({winner_cards_str}) wins " \
                                f"{winnings} with {winner.combination.rank_str}\n"
        winner.balance += winnings
        # To make player_spent variable in find_winner() work correctly
        winner.starting_balance += winnings
        self.pot -= winnings
