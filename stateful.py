import random

class State:
    values = range(13)
    val_chars = ["2","3","4","5","6","7","8","9","t","j","q","k","a"]
    val_pts = [2,3,4,5,6,7,8,9,10,10,10,10,11]

    def __init__(self, decks, hands, plays, to_play, rd, done):
        self.decks = decks
        self.hands = hands
        self.plays = plays
        self.to_play = to_play
        self.rd = rd
        self.done = done

    def valid_moves(self):
        if(self.done[to_play]):
            return [-1]
        return [-1] + self.hands[self.to_play]


    def is_done(self):
        return -3 in self.plays[0][2] and -3 in self.plays[1][2]

    def apply_move(self, move):
        if move == -1:
            if self.done[0] and self.done[1]:
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
                    [self.done[0] or self.to_play == 0, self.done[1] or self.to_play == 1]
                    )



        

