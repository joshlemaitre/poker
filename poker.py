import random
from collections import Counter
import numpy
import pandas as pd


class Card(dict):
    """
    A dictionary extension class that represents a playing card.
    """
    def __init__(self, suit, value):
        self['suit'] = suit
        self['value'] = value
        self.suit = suit
        self.value = value
        
        
class Deck:
    """
    A class that represents a deck of cards. It assumes a standard 52-card 
    deck (no jokers).
    """
    def __init__(self):
        suits = "SHDC"
        values = ['01','02','03','04','05','06','07','08','09','10','11','12','13']
        self.cards = []
        for suit in suits:
            for value in values:
                self.cards.append(Card(suit, value))

    def shuffle(self):
        """
        Pseudo random re-ordering of the cards in the deck
        """
        random.shuffle(self.cards)
    
    def cut(self):
        """
        Pseudo random cutting of the deck based on a triangular distribution.
        """
        n = int(random.triangular(1,51))
        self.cards = self.cards[n:] + self.cards[:n]
    
    def deal(self, n=1, cards=None):
        """
        Draw a specified number of cards from the deck; or draw a specific set of 
        cards from the deck.

        Parameters
        ==========
        n:int: the number of cards to be randomly drawn from the deck
        cards:list(Card): a list of specific cards to be dealt
        """
        if cards is None:
            dealt_cards = self.cards[:n]
            self.cards = self.cards[n:]
            return dealt_cards
        else:
            for card in cards:
                self.cards.remove(card)


class Hand:
    """
    A helper class to represent all things related to a poker hand.
    """
    def __init__(self):
        self.cards = []
        self.multiples = {}
        self.flush = False
        self.straight = False
        self.straight_flush = False
        self.royal_flush = False
        self.full_house = False
        self.pair = False
        self.two_pair = False
        self.three = False
        self.four = False
        self.deck = None
        self.best = None
        
    def add_cards(self, cards=None, deck=None, shuffle=True, cut=True, n=1):
        """
        A method to add cards to a hand

        Parameters
        ==========
        cards:list(Card): a list of class:Card to be added to the hand
        deck:Deck: a class:Deck instance from which to draw the cards
        shuffle:bool: a flag indicating if the deck should be shuffled
        cut:bool: a flag indicating if the deck should be cut
        n:int: the number of cards to be drawn from the deck
        """
        if deck is None:
            self.cards = self.cards + cards
        else:
            if shuffle:
                deck.shuffle()
            if cut:
                deck.cut()
            self.cards = self.cards + deck.deal(n)
            
    def evaluate(self):
        """
        A simple method to evaluate a hand against possible hands
        """
        def set_multiples(self):
            """
            A method to determine the number of multiple instances of 
            cards with the same value (pairs, sets, four of a kind)
            """
            val_counts = Counter([card.value for card in self.cards])
            for key, value in val_counts.items():
                if value in self.multiples.keys():
                    self.multiples[value].append(key)
                else:
                    self.multiples[value] = [key]
            if 2 in self.multiples.keys():
                self.pair = True
                if len(self.multiples[2]) > 1:
                    self.two_pair = True
            if 3 in self.multiples.keys():
                self.three = True
            if 4 in self.multiples.keys():
                self.four = True
            

        def set_flush(self):
            """
            A method to determine if there is a flush in the hand (five cards of the same suit)
            """
            suit_counts = Counter([card.suit for card in self.cards])
            if max(suit_counts.values()) >= 5:
                self.flush = True

        def set_straight(self):
            """
            A method to determine if there is a straight in the hand (5-card run)
            """
            values = list(set([card.value for card in self.cards]))
            values = sorted(values)
            if '01' in values:
                values = values + ['01']
            s = ''.join(values)
            straight_string = '0102030405060708091011121301'
            substr = long_substr([s, straight_string])
            if len(substr) >= 10:
                self.straight = True

        def set_full_house(self):
            """
            A method to determine if there is a full house (a set and a pair)
            """
            if 3 in self.multiples.keys():
                if 2 in self.multiples.keys():
                    self.full_house = True
                if len(self.multiples[3]) > 1:
                    self.full_house = True
            elif 4 in self.multiples.keys():
                if 2 in self.multiples.keys():
                    self.full_house = True
                if 3 in self.multiples.keys():
                    self.full_house = True
            else:
                self.full_house = False

        def set_straight_flush(self):
            """
            A method to determine if there is a straight flush (5-card suited run)
            """
            if self.straight:
                if self.flush:
                    suit_counts = Counter([card.suit for card in self.cards])
                    flush_suit = [k for k,v in suit_counts.items() if v >= 5][0]
                    flush_cards = [card.value for card in self.cards if card.suit == flush_suit]
                    flush_cards = sorted(flush_cards)
                    if '01' in flush_cards:
                        flush_cards = flush_cards + ['01']
                    s = ''.join(flush_cards)
                    straight_string = '0102030405060708091011121301'
                    substr = long_substr([s, straight_string])
                    if substr == '1011121301':
                        self.royal_flush = True
                    else:
                        if len(substr) >= 10:
                            self.straight_flush = True
        
        set_multiples(self)
        set_flush(self)
        set_straight(self)
        set_straight_flush(self)
        set_full_house(self)

        if self.royal_flush:
            self.best = '01:royal flush'
        elif self.straight_flush:
            self.best = '02:straight flush'
        elif self.four:
            self.best = '03:four of a kind'
        elif self.full_house:
            self.best = '04:full house'
        elif self.flush:
            self.best = '05:flush'
        elif self.straight:
            self.best = '06:straight'
        elif self.three:
            self.best = '07:three of a kind'
        elif self.two_pair:
            self.best = '08:two pair'
        elif self.pair:
            self.best = '09:pair'
        else:
            self.best = '10:no pair'


class Player(dict):
    """
    A simple dictionary extension to represent a player
    """
    def __init__(self, label):
        self.label = label
        self['label'] = label
        self['deal'] = None
        self.hand = Hand()


class Holdem:
    """
    A simple simulator for texas holdem games. Community stages have been 
    kept separate assuming that betting will be added later.
    """
    def __init__(self, deck, player_list):
        self.deck = deck
        self.players = player_list
        self.hands = {}
        self.community = []
        self.flop = None
        self.turn = None
        self.river = None
    
    def get_deal(self):
        """
        A method to deal 2 cards to each of the players
        """
        for player in self.players:
            player.hand.add_cards(deck=self.deck, n=2)
            player['deal'] = player.hand.cards
            self.hands[player.label] = player.hand.cards
    
    def get_flop(self):
        """
        A method to deal three cards to the community
        """
        self.flop = self.deck.deal(n=3)
        self.community = self.flop

    def get_turn(self):
        """
        A method to deal a fourth card to the community
        """
        if len(self.community) != 3:
            raise Exception("No flop has been drawn. Use get_flop method first.")
        self.turn = self.deck.deal(n=1)
        self.community = self.community + self.turn
        
    def get_river(self):
        """
        A method to deal a fifth card to the community
        """
        if len(self.community) != 4:
            raise Exception("No turn has been drawn. Use get_flop, get_turn methods first.")
        self.river = self.deck.deal(n=1)
        self.community = self.community + self.river
        
    def evaluate(self):
        """
        A method to evaluate all hands of all players. Returns a dictionary with 
        players' hands, best evaluated hand and the community cards.
        """
        for player in self.players:
            player.hand.add_cards(self.community)
            player.hand.evaluate()
        return {'community':self.community,
               'hands':[(player.hand.best, player['deal']) \
                        for player in self.players]}


def player_list(n_players = 2):
    """
    Generate a random list of player objects.
    """
    return [Player(label=str(i).zfill(2)) for i in range(n_players)]
    

def long_substr(data):
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                if j > len(substr) and is_substr(data[0][i:i+j], data):
                    substr = data[0][i:i+j]
    return substr


def is_substr(find, data):
    if len(data) < 1 and len(find) < 1:
        return False
    for i in range(len(data)):
        if find not in data[i]:
            return False
    return True


#### DEPRACATED ####

def compareTwoStrings(str1, str2):
    """
    A utility function for easily finding straights.
    """
    answer = ""
    if len(str1) == len(str2):
        if str1==str2:
            return str1
        else:
            longer=str1
            shorter=str2
    elif (len(str1) == 0 or len(str2) == 0):
        return ""
    elif len(str1)>len(str2):
        longer=str1
        shorter=str2
    else:
        longer=str2
        shorter=str1
    matrix = numpy.zeros((len(shorter), len(longer)))
    for i in range(len(shorter)):
        for j in range(len(longer)):               
            if shorter[i]== longer[j]:
                matrix[i][j]=1
    longest=0
    start=[-1,-1]
    end=[-1,-1]    
    for i in range(len(shorter)-1, -1, -1):
        for j in range(len(longer)):
            count=0
            begin = [i,j]
            while matrix[i][j]==1:
                finish=[i,j]
                count=count+1 
                if j==len(longer)-1 or i==len(shorter)-1:
                    break
                else:
                    j=j+1
                    i=i+1
            i = i-count
            if count>longest:
                longest=count
                start=begin
                end=finish
                break
    answer=shorter[int(start[0]): int(end[0])+1]
    return answer
