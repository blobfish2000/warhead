import random
import time
from tqdm import tqdm
from copy import deepcopy

class State:
    values = range(13)
    val_chars = ["2","3","4","5","6","7","8","9","t","j","q","k","a"]
    val_pts = [2,3,4,5,6,7,8,9,10,10,10,10,11]

    def __init__(self, decks = [[],[]], hands = [[],[]], plays = [[[],[],[]],[[],[],[]]], to_play=0, rd=0, done=[False,False]):
        self.decks = decks
        self.hands = hands
        self.plays = plays
        self.to_play = to_play
        self.rd = rd
        self.done = done

    def draw(self, n):
        decks = [random.sample(self.decks[0],len(self.decks[0])), random.sample(self.decks[1],len(self.decks[1]))]
        hands = [decks[0][:n], decks[1][:n]]
        decks = [decks[0][n:], decks[1][n:]]

        return State(
            decks,
            hands,
            self.plays,
            self.to_play,
            self.rd,
            self.done)

    def valid_moves(self, hidden = False):
        if(self.done[self.to_play]):
            return [-1]
        #cap out cards at 5 if simming hidden state with a big hand
        if(sum([len(rd) for rd in self.plays[self.to_play]]) > 4):
            return [-1]
        return [-1] + list(range(len(self.hands[self.to_play])))


    def game_over(self):
        return self.rd > 2

    def eval_round(self, rd):
        p1_round = self.plays[0][rd]
        p2_round = self.plays[1][rd]
        p1_scores = sum([State.val_pts[card] for card in p1_round])
        p2_scores = sum([State.val_pts[card] for card in p2_round])
        return 1 if p1_scores > p2_scores else (-1 if p2_scores > p1_scores else 0)

    def eval_game(self):
        return sum([self.eval_round(rd) for rd in range(self.rd)])

    def after_move(self, move):
        if move == -1:
            if self.done[[1,0][self.to_play]]:
                return State(
                    self.decks,
                    self.hands,
                    self.plays,
                    [1,0][self.to_play],
                    self.rd + 1,
                    [False, False])
            else:
                return State(
                    self.decks,
                    self.hands,
                    self.plays,
                    [1,0][self.to_play],
                    self.rd,
                    [self.done[0] or self.to_play == 0, self.done[1] or self.to_play == 1])
        else:
            plays = [[[card for card in rd] for rd in player] for player in self.plays]
            plays[self.to_play][self.rd].append(self.hands[self.to_play][move])
            hands = [[card for card in hand] for hand in self.hands]
            hands[self.to_play] = self.hands[self.to_play][:move] + self.hands[self.to_play][move+1:]

            return State(
                    self.decks,
                    hands,
                    plays,
                    [1,0][self.to_play],
                    self.rd,
                    self.done)

    def visualize(self, show_p1 = True, show_p2 = True):

        header = "player: " + str(self.to_play) + " round: " + str(self.rd)

        p2_hand = " ".join("**" for card in self.hands[1])
        if show_p2:
            p2_hand = " ".join(State.val_chars[card] for card in self.hands[1])

        p1_hand = " ".join("**" for card in self.hands[0])
        if show_p1:
            p1_hand = " ".join(State.val_chars[card] for card in self.hands[0])

        p1_board = ""
        p2_board = ""

        for rd in range(min(self.rd+1, 3)):
            max_cards = max(len(self.plays[0][rd]), len(self.plays[1][rd]))
            p1_plays = [State.val_chars[cd] for cd in self.plays[0][rd]] + (max_cards - len(self.plays[0][rd])) * [" "]
            p2_plays = [State.val_chars[cd] for cd in self.plays[1][rd]] + (max_cards - len(self.plays[1][rd])) * [" "]
            p1_board += " ".join(p1_plays)
            p2_board += " ".join(p2_plays)
            if rd < self.rd:
                p1_board += " | "
                p2_board += " | "
            else:
                if self.done[0]:
                    p1_board += " | "
                if self.done[1]:
                    p2_board += " | "


        out = "\n".join([header, p2_hand, p2_board, p1_board, p1_hand])
        return(out)

class Node:
    def __init__(self, move, parent, player):
        self.move, self.parent, self.player, self.children = move, parent, player, []
        self.wins, self.visits = 0, 0

    def expand(self, state):
        if not state.game_over():
            for move in state.valid_moves():
                node = Node(move, self, [1,0][state.to_play])
                self.children.append(node)

    def update(self, winner):
        self.visits += 1
        if winner > 0 and self.player == 0:
            self.wins += 1
        elif winner < 0 and self.player == 1:
            self.wins += 1
        elif winner == 0:
            self.wins += 0.5

def montesearch(state, t = 5, hidden_opponent = True):
    root = Node(None, None, state.to_play)
    root_state = deepcopy(state)

    if hidden_opponent:
        root_state.hands[[1,0][root.player]] += root_state.decks[[1,0][root.player]]
        root_state.decks[[1,0][root.player]] = []

    print("EVALUATING:")
    print(root_state.visualize())

    start = time.time()
    while time.time() - start < t:
        n, s = root, deepcopy(root_state)
        while not len(n.children) == 0:
            n = random.choice(n.children) #do better
            s = s.after_move(n.move)

        n.expand(s)
        if(len(n.children) == 0):
            continue
        n = random.choice(n.children)
        
        while not s.game_over():
            s = s.after_move(random.choice(s.valid_moves()))

        r = s.eval_game()
        while not n.parent == None:
            n.update(r)
            n = n.parent

    print([(node.wins, node.visits, node.move) for node in root.children])
    return list(filter(lambda n: n.wins == max([node.wins for node in root.children]), root.children))[0].move



#winrates
player1 = 0
player2 = 0
for i in tqdm(range(1,2)):
    state = State([list(range(1,8)),list(range(1,8))], [[],[]], [[[],[],[]],[[],[],[]]], 0, 0, [False, False])
    state = state.draw(5)
    while not state.game_over():
        print("-"*20)
        move = montesearch(state, 0.5)
        print("player", str(state.to_play) + " playing " + (["skip"] + [State.val_chars[card] for card in state.hands[state.to_play]])[move + 1])
        state = state.after_move(move)
        print(state.visualize())
    winner = state.eval_game()
    if winner > 0:
        player1 += 1
    if winner < 0:
        player2 += 1

    print("player1:" + str(player1/i))
    print("player2:" + str(player2/i))

