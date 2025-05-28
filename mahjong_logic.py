import random
from collections import Counter

def create_deck():
    """生成 1-9 萬 + 東南西北中發白 各 4 張，並隨機洗牌。"""
    tiles  = [f"{i}萬" for i in range(1, 10)] * 4
    honors = ["東", "南", "西", "北", "中", "發", "白"] * 4
    deck = tiles + honors
    random.shuffle(deck)
    return deck

def deal_tiles(deck, dealer="player"):
    """
    發牌：每人 13 張，莊家(dealer)額外補 1 張。
    回傳 (player_hand, ai_hand, deck)
    """
    player = [deck.pop() for _ in range(13)]
    ai     = [deck.pop() for _ in range(13)]
    if dealer == "player":
        player.append(deck.pop())
    else:
        ai.append(deck.pop())
    return player, ai, deck

def can_peng(hand, tile):
    """若手牌中有兩張 tile，則可碰。"""
    return hand.count(tile) >= 2

def can_gang(hand, tile, is_self_drawn=False):
    """
    判斷是否可以槓。
    - 明槓：手牌中有三張相同的牌，可以槓別人打出的牌
    - 暗槓：手牌中有四張相同的牌，可以自己槓
    """
    if is_self_drawn:
        # 暗槓 - 手牌中有四張相同的牌
        return hand.count(tile) >= 4
    else:
        # 明槓 - 手牌中有三張相同的牌
        return hand.count(tile) >= 3

def get_chi_options(hand, tile):
    """
    回傳所有可用此 tile 組成的順子三張牌列表（限萬子）。
    例如 tile="3萬"，若手牌有 "1萬","2萬"，就會回傳 ["1萬","2萬","3萬"]。
    """
    options = []
    if not tile.endswith("萬"):
        return options
    num = int(tile[0])
    for start in (num-2, num-1, num):
        if 1 <= start <= 7:
            seq = [f"{start+i}萬" for i in (0,1,2)]
            if all(hand.count(s) >= 1 for s in seq if s != tile):
                options.append(seq)
    return options

def can_chi(hand, tile):
    """只要有一組可吃的順子即回 True。"""
    return bool(get_chi_options(hand, tile))

def _can_form_melds_count(counts, needed_sets):
    """
    遞迴檢查 counts（Counter）能否湊出 needed_sets 個「刻子(3同)或順子(3連)」，
    且用完所有牌。
    """
    if needed_sets == 0:
        return not counts

    if not counts:
        return False

    tile = next(iter(counts))
    cnt  = counts[tile]

    # 刻子
    if cnt >= 3:
        newc = counts.copy()
        newc[tile] -= 3
        if newc[tile] == 0:
            del newc[tile]
        if _can_form_melds_count(newc, needed_sets - 1):
            return True

    # 順子（萬子）
    if tile.endswith("萬"):
        num = int(tile[0])
        for start in (num-2, num-1, num):
            if 1 <= start <= 7:
                seq = [f"{start+i}萬" for i in (0,1,2)]
                if all(counts.get(s,0) >= 1 for s in seq):
                    newc = counts.copy()
                    for s in seq:
                        newc[s] -= 1
                        if newc[s] == 0:
                            del newc[s]
                    if _can_form_melds_count(newc, needed_sets - 1):
                        return True

    return False

def is_hu(concealed_hand, meld_count=0):
    """
    標準胡牌判定：4 組 (刻子/順子) + 1 對眼。
    concealed_hand：除去副露後的手牌 list。
    meld_count：已副露組數（吃/碰/槓），預設 0。
    """
    counts = Counter(concealed_hand)
    needed_sets = 4 - meld_count

    # 嘗試當眼
    for tile, cnt in list(counts.items()):
        if cnt >= 2:
            newc = counts.copy()
            newc[tile] -= 2
            if newc[tile] == 0:
                del newc[tile]
            if _can_form_melds_count(newc, needed_sets):
                return True
    return False

def can_hu_with_tile(concealed_hand, meld_count, tile):
    """
    假設補上對方打出的 tile，再判斷能否胡。
    """
    return is_hu(concealed_hand + [tile], meld_count)