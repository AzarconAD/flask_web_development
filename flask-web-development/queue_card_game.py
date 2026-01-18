import random

# --- DATA STRUCTURE: QUEUE ---
class Queue:
    def __init__(self):
        self.queue = []
    
    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if self.queue:
            return self.queue.pop(0)
        return None
    
    def is_empty(self):
        return len(self.queue) == 0
        
    def size(self):
        return len(self.queue)

class Banker(Queue):
    def draw(self):
        return self.dequeue()

# --- GAME LOGIC ---
class DeckOfCards:
    def __init__(self):
        self.suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        self.card_names = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
        self.values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    
    def shuffle_cards(self):
        # Generate full deck
        deck = [(suit, name, val) 
                for suit in self.suits 
                for name, val in zip(self.card_names, self.values)]
        
        random.shuffle(deck)
        
        # Player gets 1 card
        player_card = deck.pop(0)
        player_value = player_card[2]
        
        # Filter remaining deck
        higher_cards = [card for card in deck if card[2] > player_value]
        lower_cards = [card for card in deck if card[2] <= player_value]
        
        # Banker needs 5 cards
        total_banker_cards = 5
        needed_higher = int(total_banker_cards * 0.75) 
        needed_lower = total_banker_cards - needed_higher
        
        # Safety check: if not enough high cards, take what we have
        if len(higher_cards) < needed_higher:
            needed_higher = len(higher_cards)
            needed_lower = total_banker_cards - needed_higher
        
        # Safety check: if not enough low cards, fill with high
        if len(lower_cards) < needed_lower:
            needed_lower = len(lower_cards)
            needed_higher = total_banker_cards - needed_lower
        
        # Compose Banker's hand
        banker_cards = random.sample(higher_cards, needed_higher) + random.sample(lower_cards, needed_lower)
        random.shuffle(banker_cards)
        
        return player_card, banker_cards

class Player:
    def __init__(self, initial_cash=0):
        self.cash = initial_cash

class Game:
    def __init__(self):
        self.player = Player(0)
        self.banker = Banker()
        self.deck_logic = DeckOfCards()
        
        # Display States
        self.player_card_tuple = None
        self.current_banker_card_tuple = None
        
        # Initialize
        self.reset_game()

    def reset_game(self):
        """Resets the round (cards) but keeps player money."""
        self.player_card_tuple, banker_cards = self.deck_logic.shuffle_cards()
        
        # Clear old queue and fill new one
        self.banker.queue = [] 
        for card in banker_cards:
            self.banker.enqueue(card)
            
        self.current_banker_card_tuple = None

    # --- HTML HELPERS ---
    @property
    def balance(self):
        return self.player.cash

    @property
    def player_card(self):
        if self.player_card_tuple:
            return f"{self.player_card_tuple[1]} of {self.player_card_tuple[0]}"
        return "--"

    @property
    def banker_card(self):
        if self.current_banker_card_tuple:
            return f"{self.current_banker_card_tuple[1]} of {self.current_banker_card_tuple[0]}"
        return "--"

    @property
    def deck_count(self):
        return self.banker.size()

    # --- ACTIONS ---
    def deposit(self, amount):
        if amount > 0:
            self.player.cash += amount
            return True, f"Deposited ${amount}"
        return False, "Invalid amount"

    def withdraw(self, amount):
        if 0 < amount <= self.player.cash:
            self.player.cash -= amount
            return True, f"Withdrew ${amount}"
        return False, "Insufficient funds"

    def place_bet(self, amount):
        if amount < 10:
            return False, "Minimum bet is $10"
        if amount > self.player.cash:
            return False, "Insufficient funds"
        if self.banker.is_empty():
            return False, "Deck Empty! Please Reshuffle."

        # 1. Deduct Bet
        self.player.cash -= amount
        
        # 2. Banker Dequeues Card (FIFO)
        self.current_banker_card_tuple = self.banker.draw()
        
        # 3. Compare
        p_val = self.player_card_tuple[2]
        b_val = self.current_banker_card_tuple[2]
        
        msg = ""
        if p_val > b_val:
            win = amount * 2
            self.player.cash += win
            msg = f"You WON! (+${win})"
        elif p_val < b_val:
            msg = f"You LOST! (-${amount})"
        else:
            self.player.cash += amount
            msg = "It's a TIE! Bet returned."

        return True, msg