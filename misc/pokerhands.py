# http://en.wikipedia.org/wiki/List_of_poker_hands
# http://www.reddit.com/comments/6u4pn/what_successful_software_projects_are_oneman/

# TODO: test
# TODO: polish some more

import collections

## go()
#. (2, 14, 10, 9, 5, 4) ['Ad', '0d', '9s', '5c', '4c']
#. (2, 14, 10, 9, 5, 4) ['9s', '5c', 'Ad', '4c', '0d']
#. (2, 13, 12, 11, 8, 7) ['Jc', 'Qd', '8h', '7h', 'Kc']
#. 

## hand_eval('Ad 0d 9s 5c 4c'.split())
#. '2A0954'
## hand_eval('9s 5c Ad 4c 0d'.split())
#. '2A0954'
## hand_eval('Jc Qd 8h 7h Kc'.split())
#. '2KQJ87'
## hand_eval('Jc 0d 8h 7h 9c'.split())
#. '6J'

def go():
    check('Ad 0d 9s 5c 4c')
    check('9s 5c Ad 4c 0d')
    check('Jc Qd 8h 7h Kc')
    return
    check('')
    check('')
    check('')

def check(s):
    hand = s.split()
    print hand_rank(hand), hand

def best_hand(hands):
    return max(hands, key=hand_rank)

def hand_rank(hand):
    return tuple(map(kind_rank, hand_eval(hand)))

def hand_eval(hand):
    def rank(r, opt_subrank):
        return opt_subrank and (r + opt_subrank)
    return (   rank('0', flush(hand) and straight(hand)) # XXX settle ties by suit somehow?
            or rank('9', n_of_a_kind(4, hand))
            or rank('8', full_house(hand))
            or rank('7', flush(hand))
            or rank('6', straight(hand))
            or rank('5', n_of_a_kind(3, hand))
            or rank('4', n_pairs(2, hand))
            or rank('3', n_pairs(1, hand))
            or rank('2', high_card(hand)))


# Hands
# XXX incomplete tie-breaking

def n_of_a_kind(n, hand):
    return find(groups(n, hand))

def full_house(hand):
    return n_of_a_kind(2, hand) and n_of_a_kind(3, hand)

def flush(hand):
    return 1 == len(set(map(card_suit, hand))) and high_card(hand)

def straight(hand):
    kinds = ''.join(map(card_kind, hand))
    return (consecutive(kinds)                       # Try aces high
            or consecutive(kinds.replace('A', '1'))) # and aces low

def n_pairs(n, hand):
    paired = groups(2, hand)
    return (n == len(paired)
            and descending(paired) + descending(groups(1, hand)))

def high_card(hand):
    return descending(map(card_kind, hand))


# Cards:

# kind + suit
# 'As' ace of spades
# '0c' ten of clubs

def card_kind(card): return card[0]
def card_suit(card): return card[1]


# Kinds:
# A, K, Q, J, 10, 9, 8, 7, 6, 5, 4, 3, 2 (, A)

def kind_rank(kind):
    "Return a numeric rank, aces high."
    return 1 + '1234567890JQKA'.index(kind)


# Suits:

# h s c d
# heart spade club diamond


# Helpers

def consecutive(kinds):
    "Return the high rank if a straight, else None."
    kinds = sorted(kinds, key=kind_rank)
    return (kind_rank(kinds[-1]) - kind_rank(kinds[0]) == len(kinds) - 1
            and kinds[-1])

def descending(kinds):
    return ''.join(sorted(kinds, key=kind_rank, reverse=True))

def groups(n, hand):
    "Return those kinds in hand that appear in groups of n."
    d = collections.defaultdict(int)
    for card in hand:
        d[card_kind(card)] += 1
    return [kind for kind, count in d.items() if count == n]

def find(it):
    "Return the first non-None value, else None."
    for x in it:
        if x:
            return x
    return None


if __name__ == '__main__':
    go()
