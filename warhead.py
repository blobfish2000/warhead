import random
import os

class Card:
    values = range(13)
    val_chars = ["2","3","4","5","6","7","8","9","t","j","q","k","a"]
    val_pts = [2,3,4,5,6,7,8,9,10,10,10,10,11]
    suits = ["h","d","c","s"]

    def random_card():
        return Card(random.choice(Card.suits), random.choice(Card.values))

    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __repr__(self):
        return(Card.val_chars[self.value] + self.suit)


class Game:

    def __init__(self, p1 = None, p2 = None, start = True):
        self.p1 = p1
        self.p2 = p2
        self.round = 0
        if p1 == None:
            self.p1 = Player(self, name = "player 1")
        if p2 == None:
            self.p2 = Player(self, name = "player 2")

        if start:
            self.play()

    def visualize(self, show_p1 = True, show_p2 = False):

        header = "turn: " + " ".join([p.name for p in filter(lambda p: p.turn, [self.p1, self.p2])]) + " round: " + str(self.round + 1)

        p2_hand = " ".join("**" for card in self.p2.hand)
        if show_p2:
            p2_hand = " ".join(repr(card) for card in self.p2.hand)

        p1_hand = " ".join("**" for card in self.p1.hand)
        if show_p1:
            p1_hand = " ".join(repr(card) for card in self.p1.hand)

        p1_board = ""
        p2_board = ""

        for rd in range(self.round+1):
            max_cards = max(len(self.p1.plays[rd]), len(self.p2.plays[rd]), 1)
            p1_plays = [repr(cd) for cd in self.p1.plays[rd]] + (max_cards - len(self.p1.plays[rd])) * ["  "]
            p2_plays = [repr(cd) for cd in self.p2.plays[rd]] + (max_cards - len(self.p2.plays[rd])) * ["  "]
            p1_board += " ".join(p1_plays)
            p2_board += " ".join(p2_plays)
            if rd < self.round:
                p1_board += " | "
                p2_board += " | "
            else:
                if self.p1.done:
                    p1_board += " | "
                if self.p2.done:
                    p2_board += " | "


        out = "\n".join([header, p2_hand, p2_board, p1_board, p1_hand])
        print(out)

    def setup_game(self):
        self.p1.shuffle(all_cards = True)
        self.p2.shuffle(all_cards = True)
        self.p1.draw(n=5)
        self.p2.draw(n=5)

    def round_eval(self, rd):
        p1_score = sum(Card.val_pts[cd.value] for cd in self.p1.plays[rd])
        p2_score = sum(Card.val_pts[cd.value] for cd in self.p2.plays[rd])
        if p1_score == p2_score:
            return 0
        return (1 if p1_score > p2_score else -1)

    def game_eval(self):
        return sum(self.round_eval(rd) for rd in range(3))
    
    def play(self, p1_auto = False, p2_auto = True, loop = True, visualize = True):
        self.setup_game()
        i = 0
        while self.round < 3:
            player = [self.p1, self.p2][i]

            player.turn = True

            if visualize:
                os.system("clear")
                self.visualize()

            if player.done:
                player.end_turn()
            else:
                if (p1_auto if i == 0 else p2_auto):
                    player.auto_play()
                else:
                    player.request_play()

            if self.p1.done and self.p2.done:
                if visualize:
                    os.system("clear")
                    self.visualize()
                self.round += 1
                self.p1.done = False
                self.p2.done = False

            i += 1
            i = i % 2
            if [self.p1, self.p2][i].done:
                i += 1
                i = i % 2
        
        if visualize:
            print(" ".join(["P1" if pt > 0 else ("P2" if pt < 0 else "Tie") for pt in [self.round_eval(rd) for rd in range(3)]]))
            if self.game_eval() > 0:
                print("Player 1 wins!")
            elif self.game_eval() < 0:
                print("Player 2 wins!")
            else:
                print("Tie!")

        return self.game_eval()

class Player:
    def __init__(self, game, name = "Player", deck=None, strategy = None):
        self.game = game
        self.deck = deck
        if deck == None:
            self.deck = [Card.random_card() for _ in range(7)]
        self.hand = []
        self.plays = [[],[],[]]
        self.done = False
        self.turn = False
        self.name = name
        self.strategy = strategy
        if strategy == None:
            self.strategy = self.random_play

    def shuffle(self, all_cards = False):
        if all_cards:
            self.deck += self.hand
            self.deck += sum(self.plays, [])
            self.hand = []
            self.plays = [[],[],[]]
        random.shuffle(self.deck)

    def draw(self, n=1):
        if n > len(self.deck):
            raise Exception("deck too small to draw")
        self.hand += self.deck[-n:]
        self.deck = self.deck[:-n]

    def end_turn(self):
        self.turn = False

    def play_card(self, card):
        if not self.turn:
            raise Exception("not turn")
        if self.done:
            raise Exception("done")

        hits = list(filter(lambda c: str(c) == card, self.hand))
        if len(hits) < 1:
            raise Exception("card not in hand")
        
        self.hand.remove(hits[0])
        self.plays[self.game.round].append(hits[0])
        self.end_turn()

    def launch(self):
        if not self.turn:
            raise Exception("not turn")
        self.done = True
        self.end_turn()

    def request_play(self):
        if(len(self.hand) == 0):
            self.launch()
            return
        print("current hand: " + " ".join([str(cd) for cd in self.hand]))
        done = False
        while not done:
            play = input("play ('l' -> launch): ").strip().lower()
            done = True
            try:
                if play == "l":
                    self.launch()
                else:
                    self.play_card(play.strip().lower())
            except Exception as e:
                done = False
                print(e)

    def auto_play(self):
        self.strategy()

    def moves(self):
        return [str(cd) for cd in self.hand] + ["l"]

    def do_move(self, move):
        if move == "l":

    def random_play(self, p = 0.5):
        current_round = self.plays[self.game.round]
        if len(current_round) < 1 and len(self.hand) > 0:
            self.play_card(str(random.choice(self.hand)))
        elif len(current_round) < 3 and random.random() < p and len(self.hand) > 0:
            self.play_card(str(random.choice(self.hand)))
        else:
            self.launch()

    def monte_carlo_tree_search(self, rollouts = 1000):
        tree = {}

game = Game()
