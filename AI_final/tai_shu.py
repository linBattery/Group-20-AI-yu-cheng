#!/usr/bin/env python3

# 定義牌的順序
tile_order = {
    "one": 0, "two": 1, "three": 2, "four": 3,
    "five": 4, "six": 5, "seven": 6, "eight": 7, "nine": 8,
    "e": 9, "s": 10, "w": 11, "n": 12,
    "m": 13, "b": 14, "f": 15
}

def recursive_find(arr, remain_num):
    """判斷剩餘牌是否可以構成合法組合（順子或刻子）"""
    if remain_num == 0:
        return True
    
    for i in range(16):
        if arr[i] >= 3:  # 嘗試取出刻子
            arr[i] -= 3
            if recursive_find(arr, remain_num - 3):
                return True
            arr[i] += 3  # 復原
        
        if i <= 7 and arr[i] >= 1 and arr[i + 1] >= 1 and arr[i + 2] >= 1:  # 嘗試取出順子
            arr[i] -= 1
            arr[i + 1] -= 1
            arr[i + 2] -= 1
            if recursive_find(arr, remain_num - 3):
                return True
            arr[i] += 1
            arr[i + 1] += 1
            arr[i + 2] += 1  # 復原
    
    return False

def divide_three(d):
    """檢測手牌中是否能分成刻子與順子"""
    n = len(d)
    arr = [0] * 16
    
    for card in d:
        idx = tile_order[card]
        arr[idx] += 1
    
    return recursive_find(arr, n)

def is_hu(d):
    """一般胡牌邏輯，判斷是否符合胡牌條件"""
    tmp_d = []  # 用於記錄去掉眼後的牌
    
    if len(d) == 2:  # 只剩兩張牌，必須是對子
        return d[0] == d[1]
    
    elif len(d) == 5:
        for i in range(4):
            if d[i] == d[i + 1]:  # 找到可能的眼
                tmp_d = []
                for j in range(5):
                    if j != i and j != (i + 1):  # 加入非眼的牌
                        tmp_d.append(d[j])
                if divide_three(tmp_d):
                    return True
        return False
    
    elif len(d) == 8:
        for i in range(7):
            if d[i] == d[i + 1]:  # 找到可能的眼
                tmp_d = []
                for j in range(8):
                    if j != i and j != (i + 1):
                        tmp_d.append(d[j])
                if divide_three(tmp_d):
                    return True
        return False
    
    elif len(d) == 11:
        for i in range(10):
            if d[i] == d[i + 1]:  # 找到可能的眼
                tmp_d = []
                for j in range(11):
                    if j != i and j != (i + 1):
                        tmp_d.append(d[j])
                if divide_three(tmp_d):
                    return True
        return False
    
    else:  # len(d) == 14
        for i in range(13):
            if d[i] == d[i + 1]:  # 找到可能的眼
                tmp_d = []
                for j in range(14):
                    if j != i and j != (i + 1):
                        tmp_d.append(d[j])
                if divide_three(tmp_d):
                    return True
        return False


#大四喜
def big_four_happy(card_in_hand, exposed_card):
    """大四喜：東、南、西、北四風刻"""
    e_cnt, w_cnt, n_cnt, s_cnt = 0, 0, 0, 0
    
    for card in card_in_hand:
        if card == "e": e_cnt += 1
        elif card == "n": n_cnt += 1
        elif card == "s": s_cnt += 1
        elif card == "w": w_cnt += 1
    
    for card in exposed_card:
        if card == "e": e_cnt += 1
        elif card == "n": n_cnt += 1
        elif card == "s": s_cnt += 1
        elif card == "w": w_cnt += 1
    
    return e_cnt == 3 and s_cnt == 3 and w_cnt == 3 and n_cnt == 3

#小四喜
def small_four_happy(card_in_hand, exposed_card):
    """小四喜：三風刻加一風雀頭"""
    e_cnt, w_cnt, n_cnt, s_cnt = 0, 0, 0, 0
    
    for card in card_in_hand:
        if card == "e": e_cnt += 1
        elif card == "n": n_cnt += 1
        elif card == "s": s_cnt += 1
        elif card == "w": w_cnt += 1
    
    for card in exposed_card:
        if card == "e": e_cnt += 1
        elif card == "n": n_cnt += 1
        elif card == "s": s_cnt += 1
        elif card == "w": w_cnt += 1
    
    return (e_cnt == 3 and s_cnt == 3 and w_cnt == 3 and n_cnt == 2) or \
           (e_cnt == 3 and s_cnt == 3 and w_cnt == 2 and n_cnt == 3) or \
           (e_cnt == 3 and s_cnt == 2 and w_cnt == 3 and n_cnt == 3) or \
           (e_cnt == 2 and s_cnt == 3 and w_cnt == 3 and n_cnt == 3)

#大三元
def big_three_happy(card_in_hand, exposed_card):
    """大三元：中、發、白三副刻子"""
    m_cnt, b_cnt, f_cnt = 0, 0, 0
    
    for card in card_in_hand:
        if card == "m": m_cnt += 1
        elif card == "b": b_cnt += 1
        elif card == "f": f_cnt += 1
    
    for card in exposed_card:
        if card == "m": m_cnt += 1
        elif card == "b": b_cnt += 1
        elif card == "f": f_cnt += 1
    
    return m_cnt == 3 and b_cnt == 3 and f_cnt == 3

#小三元
def small_three_happy(card_in_hand, exposed_card):
    """小三元：兩副箭刻一組箭對"""
    m_cnt, b_cnt, f_cnt = 0, 0, 0
    
    for card in card_in_hand:
        if card == "m": m_cnt += 1
        elif card == "b": b_cnt += 1
        elif card == "f": f_cnt += 1
    
    for card in exposed_card:
        if card == "m": m_cnt += 1
        elif card == "b": b_cnt += 1
        elif card == "f": f_cnt += 1
    
    return (m_cnt == 3 and b_cnt == 3 and f_cnt == 2) or \
           (m_cnt == 3 and b_cnt == 2 and f_cnt == 3) or \
           (m_cnt == 2 and b_cnt == 3 and f_cnt == 3)

#清一色
def clear_one_color(card_in_hand, exposed_card):
    """
    檢查手牌加副露牌後是否只包含萬子（1-9萬），
    不含任何字牌（東南西北中發白）。

    :param card_in_hand: 玩家手牌（如 ['1萬','3萬',…]）
    :param exposed_card: 副露或棄牌區牌（同樣格式）
    :return: 若 9..15 號索引 (字牌) 全部計數為 0，回傳 True，否則 False。
    """
    # 建立長度 16 的計數陣列
    counts = [0] * 16

    # 計算手牌與副露牌
    for tile in card_in_hand + exposed_card:
        idx = tile_order.get(tile)
        if idx is None:
            raise ValueError(f"未知的牌面：{tile}")
        counts[idx] += 1

    # 索引 0..8 是萬子，9..15 是字牌
    # 只要有任何字牌出現，回傳 False
    for i in range(9, 16):
        if counts[i] > 0:
            return False

    return True

#字一色
def clear_no_color(card_in_hand, exposed_card):
    """
        邏輯和清一色一樣 換成沒有大字這樣
    """
    # 建立長度 16 的計數陣列
    counts = [0] * 16

    # 計算手牌與副露牌
    for tile in card_in_hand + exposed_card:
        idx = tile_order.get(tile)
        if idx is None:
            raise ValueError(f"未知的牌面：{tile}")
        counts[idx] += 1

    # 索引 0..8 是萬子，9..15 是字牌
    # 只要有任何萬字出現，回傳 False
    for i in range(0, 8):
        if counts[i] > 0:
            return False

    return True

#平胡
def find_pin_hu(arr, n):
    if n == 0:
        return True
    
    for i in range(16):
        if i <= 7 and arr[i] >= 1 and arr[i + 1] >= 1 and arr[i + 2] >= 1:  # 嘗試取出順子
            arr[i] -= 1
            arr[i + 1] -= 1
            arr[i + 2] -= 1
            if find_pin_hu(arr, n - 3): return True
            arr[i] += 1
            arr[i + 1] += 1
            arr[i + 2] += 1  # 復原
    return False
    
def pin_hu(card_in_hand, exposed_card): # 平胡邏輯
    
    tmp_d = []  # 用於記錄去掉眼後的牌
    arr = [0] * 16
    
    if len(card_in_hand) == 2:  # 只剩兩張牌，必須是對子
        arr = [0] * 16
        
        for card in exposed_card:
            idx = tile_order[card]
            arr[idx] += 1
        if find_pin_hu(arr, len(exposed_card)) : return True
    
    elif len(card_in_hand) == 5:
        for i in range(4):
            if card_in_hand[i] == card_in_hand[i + 1]:  # 找到可能的眼
                tmp_d = []
                for j in range(5):
                    if j != i and j != (i + 1):  # 加入非眼的牌
                        tmp_d.append(card_in_hand[j])
                for card in exposed_card:
                    idx = tile_order[card]
                    arr[idx] += 1
                for card in tmp_d:
                    idx = tile_order[card]
                    arr[idx] += 1
                if find_pin_hu(arr, len(tmp_d + exposed_card)) : return True
        return False
    
    elif len(card_in_hand) == 8:
        for i in range(7):
            if card_in_hand[i] == card_in_hand[i + 1]:  # 找到可能的眼
                tmp_d = []
                for j in range(8):
                    if j != i and j != (i + 1):
                        tmp_d.append(card_in_hand[j])
                for card in exposed_card:
                    idx = tile_order[card]
                    arr[idx] += 1
                for card in tmp_d:
                    idx = tile_order[card]
                    arr[idx] += 1
                if find_pin_hu(arr, len(tmp_d + exposed_card)) : return True  # 去除眼睛後 判斷平胡
        return False
    
    elif len(card_in_hand) == 11:
        for i in range(10):
            if card_in_hand[i] == card_in_hand[i + 1]:  # 找到可能的眼
                tmp_d = []
                for j in range(11):
                    if j != i and j != (i + 1):
                        tmp_d.append(card_in_hand[j])
                for card in exposed_card:
                    idx = tile_order[card]
                    arr[idx] += 1
                for card in tmp_d:
                    idx = tile_order[card]
                    arr[idx] += 1
                if find_pin_hu(arr, len(tmp_d + exposed_card)) : return True  # 去除眼睛後 判斷平胡
        return False
    
    else:  # len(d) == 14
        for i in range(13):
            if card_in_hand[i] == card_in_hand[i + 1]:  # 找到可能的眼
                tmp_d = []
                for j in range(14):
                    if j != i and j != (i + 1):
                        tmp_d.append(card_in_hand[j])
                for card in exposed_card:
                    idx = tile_order[card]
                    arr[idx] += 1
                for card in tmp_d:
                    idx = tile_order[card]
                    arr[idx] += 1
                if find_pin_hu(arr, len(tmp_d + exposed_card)) : return True  # 去除眼睛後 判斷平胡
        return False

#碰碰胡
def find_pon_pon_hu(arr, n):
    if n == 0:
        return True
    for i in range(16):
        if arr[i] >= 3:  # 嘗試取出刻子
            arr[i] -= 3
            if recursive_find(arr, n - 3):
                return True
            arr[i] += 3  # 復原
    
    return False

def pon_pon_hu(card_in_hand, exposed_card):
    tmp_d = []  # 用於記錄去掉眼後的牌
    arr = [0] * 16
    
    if len(card_in_hand) == 2:  # 只剩兩張牌，必須是對子
        arr = [0] * 16
        
        for card in exposed_card:
            idx = tile_order[card]
            arr[idx] += 1
        if find_pon_pon_hu(arr, len(exposed_card)) : return True
    
    elif len(card_in_hand) == 5:
        for i in range(4):
            if card_in_hand[i] == card_in_hand[i + 1]:  # 找到可能的眼
                tmp_d = []
                for j in range(5):
                    if j != i and j != (i + 1):  # 加入非眼的牌
                        tmp_d.append(card_in_hand[j])
                for card in exposed_card:
                    idx = tile_order[card]
                    arr[idx] += 1
                for card in tmp_d:
                    idx = tile_order[card]
                    arr[idx] += 1
                if find_pon_pon_hu(arr, 3 + len(exposed_card)) : return True
        return False
    
    elif len(card_in_hand) == 8:
        for i in range(7):
            if card_in_hand[i] == card_in_hand[i + 1]:  # 找到可能的眼
                tmp_d = []
                for j in range(8):
                    if j != i and j != (i + 1):
                        tmp_d.append(card_in_hand[j])
                for card in exposed_card:
                    idx = tile_order[card]
                    arr[idx] += 1
                for card in tmp_d:
                    idx = tile_order[card]
                    arr[idx] += 1
                if find_pon_pon_hu(arr, 6 + len(exposed_card)) : return True  # 去除眼睛後 判斷平胡
        return False
    
    elif len(card_in_hand) == 11:
        for i in range(10):
            if card_in_hand[i] == card_in_hand[i + 1]:  # 找到可能的眼
                tmp_d = []
                for j in range(11):
                    if j != i and j != (i + 1):
                        tmp_d.append(card_in_hand[j])
                for card in exposed_card:
                    idx = tile_order[card]
                    arr[idx] += 1
                for card in tmp_d:
                    idx = tile_order[card]
                    arr[idx] += 1
                if find_pon_pon_hu(arr, 8 + len( exposed_card)) : return True  # 去除眼睛後 判斷平胡
        return False
    
    else:  # len(d) == 14
        for i in range(13):
            if card_in_hand[i] == card_in_hand[i + 1]:  # 找到可能的眼
                tmp_d = []
                for j in range(14):
                    if j != i and j != (i + 1):
                        tmp_d.append(card_in_hand[j])
                for card in exposed_card:
                    idx = tile_order[card]
                    arr[idx] += 1
                for card in tmp_d:
                    idx = tile_order[card]
                    arr[idx] += 1
                if find_pin_hu(arr, 11 + len(exposed_card)) : return True  # 去除眼睛後 判斷平胡
        return False


#四暗刻
def four_dark(card_in_hand, exposed_card):
    '''
    邏輯：四*3+一*2 
    
    (自摸 跟 胡牌判斷到時候再說)
    (暗槓 跟 明槓 也到時候再說)
    '''
    arr = [0] * 16
    for card in card_in_hand:
        idx = tile_order[card]
        arr[idx] += 1
    
    connectThree = 0
    for i in range(16):
        if arr[i] == 3:
            connectThree = connectThree + 1
    
    if connectThree == 4:
        return True
    else:
        return False

#三暗刻
def three_dark(card_in_hand, exposed_card):
    '''
    邏輯：四*3+一*2 
    
    (自摸 跟 胡牌判斷到時候再說)
    (暗槓 跟 明槓 也到時候再說)
    '''
    arr = [0] * 16
    for card in card_in_hand:
        idx = tile_order[card]
        arr[idx] += 1
    
    connectThree = 0
    for i in range(16):
        if arr[i] == 3:
            connectThree = connectThree + 1
    
    if connectThree == 3:
        return True
    else:
        return False

#七對子
def seven_pairs(card_in_hand):
    #判斷7*2
    arr = [0] * 16
    for card in card_in_hand:
        idx = tile_order[card]
        arr[idx] += 1
        
    connectThree = 0
    for i in range(16):
        if arr[i] == 2:
            connectThree = connectThree + 1
    
    if connectThree == 7:
        return True
    else:
        return False

#連七
def consecutive_seven(card_in_hand):
    #判斷7*2, 想法是(0, 8), 然後紀錄連續多少個
    
    #setup
    arr = [0] * 16
    for card in card_in_hand:
        idx = tile_order[card]
        arr[idx] += 1
    
    #implement    
    now = 0
    for i in range(16):
        if now == 7:
            return True
        
        if arr[i] == 2:
            now = now + 1
        else:
            now = 0
    
    return False

#北斗七星
def weird_seven(card_in_hand):
    #判斷7*2, 從東開始, 沒有就直接結束
    arr = [0] * 16
    for card in card_in_hand:
        idx = tile_order[card]
        arr[idx] += 1
        
    
    for i in range(9, 16, 1):
        if arr[i] != 2:
            return False
    
    return True

#九聯保燈
def damnnnn(card_in_hand): 
    '''
        111 2345678 999 (可以胡9張)
        
        判斷是想說 
        1. ([1, 9]全三 + 2~8只能有一個是二，其他全一)
        2. ([1, 9]其中一個4另一個3 + 2~8全一)
        
        case 1是如果2~8有兩個非一就return
        case 2是如果有非一就return
    '''
    arr = [0] * 16
    for card in card_in_hand:
        idx = tile_order[card]
        arr[idx] += 1

    #CASE 1
    if arr[0] == 3 and arr[8] == 3:
        non_one = 0
        for i in range(1, 8, 1):
            if arr[i] != 1:
                non_one += 1
        if non_one > 1:
            return False

        return True
    elif (arr[0] == 4 and arr[8] == 3) or (arr[0] == 3 and arr[8] == 4):
        for i in range(1, 8, 1):
            if arr[i] != 1:
                return False
        
        return True
    else:
        return False


#四槓子
def four_gong(card_in_hand, exposed_card):
    '''
        看 槓牌有沒有四個槓就好 反正手牌已經確定胡牌了
    '''
    
    arr = [0] * 16
    for card in exposed_card:
        idx = tile_order[card]
        arr[idx] += 1    
    
    connectFour = 0
    for i in range(16):
        if arr[i] == 4:
            connectFour += 1
    
    if connectFour == 4:
        return True
    
    return False

#判斷胡牌
def recognize_hu(s1, s2, is_self, deck_length):
    """識別胡牌類型並計算台數"""
    
    '''variables: 吃碰槓的牌 + 手牌 + 是否自摸 (台數，可以拿來判斷暗刻) + 剩餘牌數 (判斷天地胡等)'''
    # 處理暴露的牌（吃/碰/槓）
    exposed_card = s1.split(";") if s1 else []
    # 處理手牌
    card_in_hand = s2.split(",") if s2 else []
    
    # 按照自定義順序排序
    exposed_card.sort(key=lambda x: tile_order.get(x, float('inf')))
    card_in_hand.sort(key=lambda x: tile_order.get(x, float('inf')))
    
    result = []
    tai_shu = 0  # 台數累積
    
    if is_hu(card_in_hand):
        if is_self:
            tai_shu += 1 #自摸判斷
        if deck_length == 37 or deck_length == 36:
            tai_shu += 160 #天湖, 地胡
        if deck_length == 0:
            tai_shu += 10 #海底撈月
        if deck_length == 0:
            tai_shu += 10  # 底台數為10
        
        
        #九連
        if damnnnn(card_in_hand):
            result.append("九聯保燈")
            tai_shu += 88
        
        #四槓
        if four_gong(card_in_hand, exposed_card):
            result.append("four_gong")
            tai_shu += 88
        
        #大四
        if big_four_happy(card_in_hand, exposed_card):
            result.append("big_four_happy")
            tai_shu += 88
        
        
        #小四
        if small_four_happy(card_in_hand, exposed_card):
            result.append("small_four_happy")
            tai_shu += 64
        
        
        #大三
        if big_three_happy(card_in_hand, exposed_card):
            result.append("big_three_happy")
            tai_shu += 88
        
        
        #小三
        if small_three_happy(card_in_hand, exposed_card):
            result.append("small_three_happy")
            tai_shu += 64
        
        #清一
        if clear_one_color(card_in_hand, exposed_card):
            result.append("clear_one_color")
            tai_shu += 80
 
        #字一
        if clear_no_color(card_in_hand, exposed_card):
            result.append("clear_one_color")
            tai_shu += 320
        
        #平胡
        if pin_hu(card_in_hand, exposed_card):
            # result.append("pin hu")
            tai_shu += 10
            
        #碰碰
        if pon_pon_hu(card_in_hand, exposed_card):
            # result.append("pon_pon_hu")
            tai_shu += 40
         
        #四暗刻
        if four_dark(card_in_hand, exposed_card):
            result.append("four_dark")
            tai_shu += 160   
        
        
        #三暗刻
        if three_dark(card_in_hand, exposed_card):
            result.append("three_dark")
            tai_shu += 40     
        
        if result == []:
            result.append("pi hu") # 屁胡
        return result, tai_shu
    elif seven_pairs(card_in_hand):
        if consecutive_seven(card_in_hand):
            result.append("consecutive_seven")
            tai_shu += 88
        elif weird_seven(card_in_hand):
            result.append("weird_seven")
            tai_shu += 88
        else:
            result.append("seven_pairs")
            tai_shu += 40
        return result, tai_shu
    else:
        return [], 0  # 沒有胡牌，台數為0







def main():
    s = input()
    # 在此處按照需求處理輸入和輸出
    # 例如可以分離輸入中的暴露牌和手牌信息
    # s1 = 暴露牌信息
    # s2 = 手牌信息
    # result, tai_shu = recognize_hu(s1, s2)
    # print(result, tai_shu)

if __name__ == "__main__":
    main()