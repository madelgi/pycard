import pycard.model as pm

from io import StringIO



def test_string_to_card():
    assert pm.string_to_card("KS") == pm.Card('K', pm.Suit.spades)
    assert pm.string_to_card("2S") == pm.Card('2', pm.Suit.spades)
    assert pm.string_to_card("AC") == pm.Card('A', pm.Suit.clubs)


def test_deck_shuffle():
    d1 = pm.Deck()
    d2 = pm.Deck()
    d1.shuffle()
    d2.shuffle()
    assert len(d1._cards) == 52
    assert len(d2._cards) == 52


def test_deck_draw():
    d = pm.Deck()
    c = d.draw()
    assert c is not None
    assert len(d) == 51


def test_deck_deal():
    d = pm.Deck()
    l, new_deck = d.deal(7, 2)
    assert len(l) == 2
    assert len(l[0]) == 7
    assert len(new_deck) == 38


def test_player_draw():
    p = pm.Player('test', [], computer=True)
    g = pm.Game()
    g.initialize()
    assert len(p.hand) == 0
    p.draw(g)
    assert len(p.hand) == 1


def test_player_discard():
    p = pm.Player('test', [pm.Card('K', 'S')], computer=True)
    g = pm.Game()
    g.initialize()
    p.discard(g)
    assert len(p.hand) == 0
    assert g.discard.pop() == pm.Card('K', 'S')


def test_game_meld(rummy, monkeypatch):
    monkeypatch.setattr('sys.stdin', StringIO("2D 2H 2C 2S\ndiscard\n"))
    p0 = rummy.players['p0']
    assert p0.melds == []
    assert len(p0.hand) == 7
    p0.meld(rummy)
    assert len(p0.melds) == 1
    assert len(p0.melds[0][0]) == 4
    assert len(p0.hand) == 3


def test_game_draw(rummy, monkeypatch):
    monkeypatch.setattr('sys.stdin', StringIO("S\n"))
    prevstock = len(rummy.stock)
    rummy.players['p0'].draw(rummy)
    assert len(rummy.stock) + 1 == prevstock

    monkeypatch.setattr('sys.stdin', StringIO("D3\n"))
    prevdiscard = len(rummy.discard)
    rummy.players['p0'].draw(rummy)
    assert len(rummy.discard) + 3 == prevdiscard
