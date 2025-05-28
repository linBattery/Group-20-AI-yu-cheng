import tkinter as tk
from tkinter import messagebox
import random
from collections import Counter
from PIL import Image, ImageTk
from tai_shu import recognize_hu

from mahjong_logic import (
    create_deck, deal_tiles,
    is_hu, can_hu_with_tile,
    can_peng, can_gang, get_chi_options
)

class MahjongGame:
    def __init__(self, root, is_auto_mode=False, opponent_type="normal"):
        self.root = root
        self.is_auto_mode = is_auto_mode
        self.opponent_type = opponent_type
        
        if is_auto_mode:
            from agent import MahjongAgent
            self.player_agent = MahjongAgent(role="player")
            
        if opponent_type == "agent":
            from agent import MahjongAgent
            self.ai_agent = MahjongAgent(role="ai")
        
        self.root.title("二人麻將 - 經典玩法")
        self.root.geometry("800x600")
        self.root.resizable(False, False)  # 禁止調整窗口大小，保持固定

        # --- Frames ---
        self.frame_top = tk.Frame(root); self.frame_top.pack(pady=5)
        self.frame_info = tk.Frame(root); self.frame_info.pack(pady=5)
        self.frame_discard = tk.Frame(root, width=780, height=100); 
        self.frame_discard.pack(pady=5, fill=tk.X, padx=10)
        self.frame_discard.pack_propagate(False)  # 固定大小
        self.frame_melds = tk.Frame(root); self.frame_melds.pack(pady=5)
        self.frame_hand = tk.Frame(root); self.frame_hand.pack(pady=5)
        self.frame_drawn = tk.Frame(root); self.frame_drawn.pack(pady=5)
        self.frame_combined_hand = tk.Frame(root)
        self.frame_combined_hand.pack(pady=5)
        
        # --- Status Label ---
        self.status_label = tk.Label(self.frame_top, text="", font=("Arial", 12))
        self.status_label.pack()

        # --- Info Labels ---
        self.deck_label = tk.Label(self.frame_info, text="剩餘牌數: 0")
        self.deck_label.pack(side=tk.LEFT, padx=10)

        self.tai_label = tk.Label(self.frame_info, text="胡牌番數: 0")
        self.tai_label.pack(side=tk.LEFT, padx=10)

        self.ai_meld_label = tk.Label(self.frame_info, text="AI 副露: 無")
        self.ai_meld_label.pack(side=tk.LEFT, padx=10)

        # --- 遊戲初始化 ---
        self.setup_new_game()
        
    def setup_new_game(self):
        """初始化新遊戲"""
        deck = create_deck()
        self.player_hand, self.ai_hand, self.deck = deal_tiles(deck, dealer="player")
        self.player_melds = []
        self.ai_melds = []
        self.player_discards = []
        self.ai_discards = []
        self.last_discard = None
        self.last_drawn = None  # 最新摸到的牌
        self.game_result = None

        # --- UI containers ---
        self.hand_buttons = []
        self.meld_labels = []
        self.discard_labels = []
        self.drawn_button = None

        # 棄牌區固定區塊
        self.frame_discard = tk.Frame(self.root, width=780, height=100)
        self.frame_discard.pack(pady=5, fill=tk.X, padx=10)
        self.frame_discard.pack_propagate(False)
        
        # 實際用來放棄牌圖示的內層 Frame
        self.discard_frame = tk.Frame(self.frame_discard)
        self.discard_frame.pack(fill=tk.X)

        self.frame_combined_hand = tk.Frame(self.root)
        self.frame_combined_hand.pack(pady=5)

        # --- 圖片顯示 ---
        self.tile_images = {}
        tiles = [f"{i}萬" for i in range(1,10)] + ["東","南","西","北","中","發","白"]
        for t in tiles:
            img = Image.open(f"tiles/{t}.png")
            resample = getattr(Image, 'Resampling', Image).LANCZOS
            img = img.resize((40,40), resample)
            self.tile_images[t] = ImageTk.PhotoImage(img)

        # --- 首次顯示 & 開始玩家回合 ---
        self.update_display()
        if self.is_auto_mode:
            self.root.after(1, self.auto_player_turn, True)
        else:
            self.player_turn(first_turn=True)

    def auto_player_turn(self, first_turn=False):
        """AI代理的玩家回合"""
        if not first_turn:
            if self.deck:
                self.last_drawn = self.deck.pop()
                self.player_hand.append(self.last_drawn)
                
                # 檢查自摸
                if is_hu(self.player_hand, len(self.player_melds)):
                    self.end_game('player_win')
                    print('zhi mou')
                    return
            else:
                self.end_game('draw')
                return

        # 讓 agent 決定要打出哪張牌
        action = self.player_agent.choose_action(
            hand=self.player_hand.copy(),
            last_discard=None
        )
        if isinstance(action, str) and action in self.player_hand:
            discard_tile = action
        else:
            discard_tile = self.player_hand[0]  # 預設選第一張

        # 從手牌中移除選中的牌
        self.player_hand.remove(discard_tile)
        self.last_discard = discard_tile
        self.player_discards.append(discard_tile)
        
        self.status_label.config(text=f"AI代理打出 {discard_tile}")
        self.update_display()
        self.root.after(3, self.ai_react_to_discard)

    def auto_player_react_to_discard(self):
        """AI代理對 AI 棄牌的反應"""
        tile = self.last_discard

        # 檢查是否可以胡牌
        if can_hu_with_tile(self.player_hand, len(self.player_melds), tile):
            # 讓 agent 決定是否要胡
            action = self.player_agent.choose_action(
                hand=self.player_hand.copy(),
                last_discard=tile
            )
            if action == 'hu':
                print('fun gun')
                self.end_game('player_win')
                return

        # 檢查是否可以槓牌
        if can_gang(self.player_hand, tile, is_self_drawn=False):
            # 讓 agent 決定是否要槓
            action = self.player_agent.choose_action(
                hand=self.player_hand.copy(),
                last_discard=tile
            )
            if action == 'gang':
                for _ in range(3):
                    self.player_hand.remove(tile)
                self.player_melds.append([tile]*4)

                if self.deck:
                    self.last_drawn = self.deck.pop()
                    self.player_hand.append(self.last_drawn)
                    if is_hu(self.player_hand, len(self.player_melds)):
                        self.end_game('player_win')
                        return
                    self.update_display()
                    self.root.after(1, self.auto_player_turn)
                    return
                else:
                    self.end_game('draw')
                    return

        # 檢查是否可以碰牌
        if can_peng(self.player_hand, tile):
            # 讓 agent 決定是否要碰
            action = self.player_agent.choose_action(
                hand=self.player_hand.copy(),
                last_discard=tile
            )
            if action == 'peng':
                self.player_hand.remove(tile)
                self.player_hand.remove(tile)
                self.player_melds.append([tile]*3)
                self.last_discard = None
                self.update_display()
                self.root.after(1, self.auto_player_turn)
                return

        # 檢查是否可以吃牌
        chi_opts = get_chi_options(self.player_hand, tile)
        if chi_opts:
            # 讓 agent 決定是否要吃
            action = self.player_agent.choose_action(
                hand=self.player_hand.copy(),
                last_discard=tile
            )
            if isinstance(action, list) and len(action) == 3:  # 吃牌動作會回傳一個包含3張牌的列表
                for t in action:
                    if t != tile and t in self.player_hand:
                        self.player_hand.remove(t)
                self.player_melds.append(action)
                self.last_discard = None
                self.update_display()
                self.root.after(1, self.auto_player_turn)
                return

        # 如果都不做，就摸牌
        self.auto_player_turn()

    def convert_to_tai_shu_format(self, tiles):
        translate = {
            '1萬': 'one',   '2萬': 'two',    '3萬': 'three',
            '4萬': 'four',  '5萬': 'five',   '6萬': 'six',
            '7萬': 'seven', '8萬': 'eight',  '9萬': 'nine',
            '東': 'e',      '南': 's',       '西': 'w',
            '北': 'n',      '中': 'm',       '發': 'f',
            '白': 'b'
        }
        return [translate[t] for t in tiles]
    
    def update_display(self):
        """重繪玩家副露、棄牌、手牌按鈕與最新摸到的牌，從左至右並排。"""
        # 更新剩餘牌數
        self.deck_label.config(text=f"剩餘牌數: {len(self.deck)}")

        # 更新 AI 副露
        ai_meld_text = "AI 副露: " + (" | ".join(["+".join(m) for m in self.ai_melds]) or "無")
        self.ai_meld_label.config(text=ai_meld_text)

        # 清除舊棄牌顯示
        for lbl in self.discard_labels:
            lbl.destroy()
        self.discard_labels = []

        # 清空舊內容
        for w in self.discard_frame.winfo_children():
            w.destroy()
            
            
        # 玩家棄牌第一行
        player_line = tk.Frame(self.discard_frame)
        player_line.pack(fill=tk.X, anchor='w', pady=(0,2))
        tk.Label(player_line, text="玩家棄牌: ").pack(side=tk.LEFT)
        for tile in self.player_discards:
            lbl = tk.Label(player_line, image=self.tile_images[tile], width=40, height=40)
            lbl.pack(side=tk.LEFT, padx=1)
            
            
            
        # AI 棄牌第二行
        ai_line = tk.Frame(self.discard_frame)
        ai_line.pack(fill=tk.X, anchor='w')
        tk.Label(ai_line, text="AI 棄牌: ").pack(side=tk.LEFT)
        for tile in self.ai_discards:
            lbl = tk.Label(ai_line, image=self.tile_images[tile], width=40, height=40)
            lbl.pack(side=tk.LEFT, padx=1)

        # 清除舊副露顯示（重新生成）
        for lbl in self.meld_labels:
            lbl.destroy()
        self.meld_labels = []

        # 清除舊手牌按鈕
        for btn in self.hand_buttons:
            btn.destroy()
        self.hand_buttons = []

        # 清除舊最新摸牌顯示
        if self.drawn_button:
            self.drawn_button.destroy()
            self.drawn_button = None

        # 🔁 清空舊整合框架
        for widget in self.frame_combined_hand.winfo_children():
            widget.destroy()

        # --- 建立並排區域 ---
        # 副露
        # --- 副露區（碰／槓）用圖片按鈕或 Label 顯示 ---
        meld_frame = tk.Frame(self.frame_combined_hand)
        meld_frame.pack(side=tk.LEFT, padx=5)
        if self.player_melds:
            for meld in self.player_melds:
                # meld 是像 ['8萬','8萬','8萬'] 或 ['發','發','發','發']
                for tile in meld:
                    lbl = tk.Label(meld_frame,
                                   image=self.tile_images[tile],
                                   width=40, height=40)
                    lbl.pack(side=tk.LEFT, padx=1)
                # 如果要在每組副露之間加一點間隔：
                spacer = tk.Label(meld_frame, width=1)
                spacer.pack(side=tk.LEFT)
        ## else:
            ##btn = tk.Button(meld_frame, text="副露: 無", state=tk.DISABLED)
            ##btn.pack()
            ##self.meld_labels.append(btn)

        # 手牌
        hand_frame = tk.Frame(self.frame_combined_hand)
        hand_frame.pack(side=tk.LEFT, padx=5)
        for tile in sorted(self.player_hand):
            btn = tk.Button(hand_frame,
                            image=self.tile_images[tile],
                            width=40, height=40,
                            command=lambda t=tile: self.player_discard(t))
            btn.pack(side=tk.LEFT, padx=2)
            self.hand_buttons.append(btn)

        # 最新摸到的牌
        drawn_frame = tk.Frame(self.frame_combined_hand)
        drawn_frame.pack(side=tk.LEFT, padx=5)
        if self.last_drawn:
            btn = tk.Button(drawn_frame,
                            image=self.tile_images[self.last_drawn],
                            width=40, height=40,
                            bg="yellow",
                            command=lambda: self.player_discard(self.last_drawn))
            btn.pack(side=tk.LEFT, padx=2)
            self.drawn_button = btn

    def end_game(self, result, message=None):
        """統一處理遊戲結束"""
        self.game_result = result
        if not self.is_auto_mode:
            if message:
                messagebox.showinfo("遊戲結束", message)
            else:
                # 根據結果顯示適當的訊息
                if result == 'player_win':
                    messagebox.showinfo("遊戲結束", "恭喜你贏了！")
                elif result == 'ai_win':
                    messagebox.showinfo("遊戲結束", "AI 贏了！")
                else:
                    messagebox.showinfo("遊戲結束", "遊戲和局！")
            
        # 在自動模式下更新 agent 的統計資料
        if self.is_auto_mode:
            self.player_agent.update_statistics(result)
            
        # 禁用所有按鈕
        self.disable_hand()
        
        # 如果是 AI 對戰模式，更新 AI agent 的統計資料
        if self.opponent_type == "agent" and self.ai_agent:
            # 對於 AI 來說，結果需要反轉
            ai_result = 'ai_win' if result == 'player_win' else 'player_win' if result == 'ai_win' else 'draw'
            self.ai_agent.update_statistics(ai_result)

    def player_turn(self, first_turn=False):
        if self.is_auto_mode:
            self.auto_player_turn(first_turn)
            return
            
        if not first_turn:
            if self.deck:
                self.last_drawn = self.deck.pop()
                
                # 檢查暗槓
                full = self.player_hand + ([self.last_drawn] if self.last_drawn else [])
                counts = Counter(full)
                gang_tiles = [t for t, c in counts.items() if c == 4]
                for t in gang_tiles:
                    if self.is_auto_mode:
                        action = self.player_agent.choose_action(full)
                        should_gang = action == 'gang'
                    else:
                        should_gang = messagebox.askyesno("暗槓機會", f"你要暗槓 {t} 嗎？")
                        
                    if should_gang:
                        rem = 4
                        while rem>0 and t in self.player_hand:
                            self.player_hand.remove(t); rem-=1
                        if rem>0 and self.last_drawn==t:
                            self.last_drawn=None; rem-=1
                        self.player_melds.append([t]*4)
                        if self.deck:
                            self.last_drawn = self.deck.pop()
                        self.update_display()
                        self.enable_hand()
                        return
                        
                full_hand = self.player_hand + ([self.last_drawn] if self.last_drawn else [])
                
                if is_hu(full_hand, len(self.player_melds)):
                    if self.is_auto_mode:
                        action = self.player_agent.choose_action(full_hand)
                        should_hu = action == 'hu'
                        if action == 'hu':
                            print('zi mou')
                    else:
                        should_hu = messagebox.askyesno("自摸機會", f"你摸到了 {self.last_drawn}，要自摸胡嗎？")
                        
                    if should_hu:
                        exposed = [t for meld in self.player_melds for t in meld]
                        s1 = ";".join(self.convert_to_tai_shu_format(exposed))
                        s2 = ",".join(self.convert_to_tai_shu_format(full_hand))
                        result, tai = recognize_hu(s1, s2, 1, len(self.deck))
                        self.tai_label.config(text=f"胡牌番數: {tai}")
                        self.end_game('player_win', f"自摸胡！\n牌型：{', '.join(result)}\n番數：{tai} 番")
                        return
            else:
                self.end_game('draw', "牌已用完，遊戲和局！")
                return
        
        self.status_label.config(text="你的回合：請打出一張牌")
        self.update_display()
        self.enable_hand()

    def disable_hand(self):
        for b in self.hand_buttons:
            b.config(state=tk.DISABLED)
        if self.drawn_button:
            self.drawn_button.config(state=tk.DISABLED)

    def enable_hand(self):
        for b in self.hand_buttons:
            b.config(state=tk.NORMAL)
        if self.drawn_button:
            self.drawn_button.config(state=tk.NORMAL)

    def player_discard(self, tile):
        """玩家打牌，進入 AI 反應流程。"""
        # 判斷是否是最新摸到的牌
        if tile == self.last_drawn:
            self.last_discard = tile
            self.player_discards.append(tile)
            self.last_drawn = None
        else:
            # 如果有最新摸到的牌，先加入手牌
            if self.last_drawn:
                self.player_hand.append(self.last_drawn)
                self.last_drawn = None
            
            # 從手牌中移除選中的牌
            self.player_hand.remove(tile)
            self.last_discard = tile
            self.player_discards.append(tile)
            
        self.status_label.config(text=f"你打出 {tile}，等待 AI 反應…")
        self.disable_hand()
        self.update_display()
        self.root.after(3, self.ai_react_to_discard)

    def ai_react_to_discard(self):
        """AI對玩家棄牌的反應"""
        tile = self.last_discard
        
        # 檢查是否可以胡牌
        if can_hu_with_tile(self.ai_hand, len(self.ai_melds), tile):
            if self.opponent_type == "agent":
                # 讓 agent 決定是否要胡
                action = self.ai_agent.choose_action(
                    hand=self.ai_hand.copy(),
                    last_discard=tile
                )
                if action == 'hu':
                    self.end_game('ai_win', "AI 胡牌了！")
                    return
            else:
                # 一般 AI 直接胡牌
                self.end_game('ai_win', "AI 胡牌了！")
                return

        # 檢查是否可以槓牌
        if can_gang(self.ai_hand, tile, is_self_drawn=False):
            if self.opponent_type == "agent":
                # 讓 agent 決定是否要槓
                action = self.ai_agent.choose_action(
                    hand=self.ai_hand.copy(),
                    last_discard=tile
                )
                if action == 'gang':
                    for _ in range(3):
                        self.ai_hand.remove(tile)
                    self.ai_melds.append([tile]*4)
                    self.last_discard = None
                    self.update_display()
                    
                    if self.deck:
                        drawn = self.deck.pop()
                        self.ai_hand.append(drawn)
                        if is_hu(self.ai_hand, len(self.ai_melds)):
                            self.end_game('ai_win')
                            return
                        self.ai_turn()
                        return
                    else:
                        self.end_game('draw')
                        return
            else:
                # 一般 AI 直接槓牌
                for _ in range(3):
                    self.ai_hand.remove(tile)
                self.ai_melds.append([tile]*4)
                self.last_discard = None
                self.update_display()
                
                if self.deck:
                    drawn = self.deck.pop()
                    self.ai_hand.append(drawn)
                    if is_hu(self.ai_hand, len(self.ai_melds)):
                        self.end_game('ai_win')
                        return
                    self.ai_turn()
                    return
                else:
                    self.end_game('draw')
                    return

        # 檢查是否可以碰牌
        if can_peng(self.ai_hand, tile):
            if self.opponent_type == "agent":
                # 讓 agent 決定是否要碰
                action = self.ai_agent.choose_action(
                    hand=self.ai_hand.copy(),
                    last_discard=tile
                )
                if action == 'peng':
                    self.ai_hand.remove(tile)
                    self.ai_hand.remove(tile)
                    self.ai_melds.append([tile]*3)
                    self.last_discard = None
                    self.update_display()
                    self.ai_turn()
                    return
            else:
                # 一般 AI 有機會就碰
                self.ai_hand.remove(tile)
                self.ai_hand.remove(tile)
                self.ai_melds.append([tile]*3)
                self.last_discard = None
                self.update_display()
                self.ai_turn()
                return

        # 檢查是否可以吃牌
        chi_opts = get_chi_options(self.ai_hand, tile)
        if chi_opts:
            if self.opponent_type == "agent":
                # 讓 agent 決定是否要吃
                action = self.ai_agent.choose_action(
                    hand=self.ai_hand.copy(),
                    last_discard=tile
                )
                if isinstance(action, list) and len(action) == 3:  # 吃牌動作會回傳一個包含3張牌的列表
                    for t in action:
                        if t != tile:
                            self.ai_hand.remove(t)
                    self.ai_melds.append(action)
                    self.last_discard = None
                    self.update_display()
                    self.ai_turn()
                    return
            else:
                # 一般 AI 隨機選擇是否吃牌
                if random.random() < 0.5:
                    chi_tiles = random.choice(chi_opts)
                    for t in chi_tiles:
                        if t != tile:
                            self.ai_hand.remove(t)
                    self.ai_melds.append(chi_tiles)
                    self.last_discard = None
                    self.update_display()
                    self.ai_turn()
                    return

        # 如果沒有特殊動作，進入 AI 的回合
        self.last_discard = None
        if self.deck:
            drawn = self.deck.pop()
            self.ai_hand.append(drawn)
            if is_hu(self.ai_hand, len(self.ai_melds)):
                self.end_game('ai_win')
                return
            self.ai_turn()
        else:
            self.end_game('draw')

    def ai_turn(self):
        """AI的回合"""
        if self.opponent_type == "agent":
            # 讓 agent 決定要打出哪張牌
            action = self.ai_agent.choose_action(
                hand=self.ai_hand.copy(),
                last_discard=None
            )
            if isinstance(action, str) and action in self.ai_hand:
                discard_tile = action
            else:
                discard_tile = self.ai_hand[0]  # 預設選第一張
        else:
            # 一般 AI 隨機打出一張牌
            discard_tile = random.choice(self.ai_hand)
            
        self.ai_hand.remove(discard_tile)
        self.last_discard = discard_tile
        self.ai_discards.append(discard_tile)
        self.status_label.config(text=f"AI 打出 {discard_tile}")
        self.update_display()
        
        if not self.is_auto_mode:
            self.player_react_to_discard()
        else:
            self.root.after(100, self.auto_player_react_to_discard)

    def player_react_to_discard(self):
        if self.is_auto_mode:
            self.auto_player_react_to_discard()
            return
            
        tile = self.last_discard

        # 玩家胡牌機會
        if can_hu_with_tile(self.player_hand, len(self.player_melds), tile):
            if self.is_auto_mode:
                action = self.player_agent.choose_action(
                    hand=self.player_hand.copy(),
                    last_discard=tile
                )
                should_hu = action == 'hu'
                if action == 'hu':
                    print('opponent guns')
            else:
                should_hu = messagebox.askyesno("胡牌機會", f"你要胡 {tile} 嗎？")
                
            if should_hu:
                exposed = [t for meld in self.player_melds for t in meld]
                full = self.player_hand + [tile]
                s1 = ";".join(self.convert_to_tai_shu_format(exposed))
                s2 = ",".join(self.convert_to_tai_shu_format(full))
                result, tai = recognize_hu(s1, s2, 0, len(self.deck))
                self.tai_label.config(text=f"胡牌番數: {tai}")
                self.end_game('player_win', f"吃胡！\n牌型：{', '.join(result)}\n番數：{tai} 番")
                return

        # 玩家槓牌機會
        if can_gang(self.player_hand, tile, is_self_drawn=False):
            if self.is_auto_mode:
                action = self.player_agent.choose_action(
                    hand=self.player_hand.copy(),
                    last_discard=tile
                )
                should_gang = action == 'gang'
            else:
                should_gang = messagebox.askyesno("槓牌機會", f"你要槓 {tile} 嗎？")
                
            if should_gang:
                # 移除手牌中的三張相同牌
                for _ in range(3):
                    self.player_hand.remove(tile)
                # 加入四張牌到副露區（包括打出的那張）
                self.player_melds.append([tile]*4)
                self.last_discard = None  # 清除打出的牌

                # 補摸一張
                if self.deck:
                    self.last_drawn = self.deck.pop()
                    self.update_display()
                    self.enable_hand()
                    return
                else:
                    self.end_game('draw', "牌已用完，遊戲和局！")
                    return

        # 玩家碰牌機會
        if can_peng(self.player_hand, tile):
            if self.is_auto_mode:
                # 讓 agent 決定是否要碰牌
                action = self.player_agent.choose_action(
                    hand=self.player_hand.copy(),
                    last_discard=tile
                )
                should_peng = action == 'peng'
                if action == 'peng':
                    print('player peng')
            else:
                should_peng = messagebox.askyesno("碰牌機會", f"你要碰 {tile} 嗎？")
                
            if should_peng:
                self.player_hand.remove(tile)
                self.player_hand.remove(tile)
                self.player_melds.append([tile]*3)
                self.last_discard = None
                self.update_display()
                return self.enable_hand()

        # 玩家吃牌機會
        chi_opts = get_chi_options(self.player_hand, tile)
        if chi_opts:
            if self.is_auto_mode:
                # 讓 agent 決定是否要吃牌
                action = self.player_agent.choose_action(
                    hand=self.player_hand.copy(),
                    last_discard=tile
                )
                should_chi = action == 'chi'
                if should_chi:
                    print('player chi')
                    seq = chi_opts[0]  # 簡單起見，選第一個可能的吃牌組合
                    for s in seq:
                        if s != tile and s in self.player_hand:
                            self.player_hand.remove(s)
                    self.player_melds.append(seq)
                    self.last_discard = None
                    self.update_display()
                    return self.enable_hand()
            else:
                seq_options = []
                for opt in chi_opts:
                    seq_options.append("+".join(opt))
                    
                if len(seq_options) == 1:
                    chi_question = f"你要吃 {tile} 組成 {seq_options[0]} 嗎？"
                else:
                    chi_question = f"你要吃 {tile} 嗎？"
                    
                if messagebox.askyesno("吃牌機會", chi_question):
                    seq = chi_opts[0]  # 預設選第一個
                    if len(chi_opts) > 1:
                        seq_choice = tk.StringVar(value=seq_options[0])
                        choice_dialog = tk.Toplevel(self.root)
                        choice_dialog.title("選擇吃牌組合")
                        choice_dialog.geometry("300x200")
                        choice_dialog.resizable(False, False)
                        
                        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (300 // 2)
                        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (200 // 2)
                        choice_dialog.geometry(f"+{x}+{y}")
                        
                        radio_frame = tk.Frame(choice_dialog)
                        radio_frame.pack(pady=10)
                        
                        for i, opt_str in enumerate(seq_options):
                            rb = tk.Radiobutton(radio_frame, text=opt_str, 
                                               variable=seq_choice, value=opt_str)
                            rb.pack(anchor=tk.W)
                        
                        def confirm_chi():
                            nonlocal seq
                            selected = seq_choice.get()
                            for i, opt_str in enumerate(seq_options):
                                if selected == opt_str:
                                    seq = chi_opts[i]
                                    break
                            choice_dialog.destroy()
                            
                            for s in seq:
                                if s != tile and s in self.player_hand:
                                    self.player_hand.remove(s)
                            self.player_melds.append(seq)
                            self.last_discard = None
                            self.update_display()
                            self.enable_hand()
                        
                        confirm_btn = tk.Button(choice_dialog, text="確定", command=confirm_chi)
                        confirm_btn.pack(pady=10)
                        
                        choice_dialog.transient(self.root)
                        choice_dialog.grab_set()
                        self.root.wait_window(choice_dialog)
                        return
                    else:
                        for s in seq:
                            if s != tile and s in self.player_hand:
                                self.player_hand.remove(s)
                        self.player_melds.append(seq)
                        self.last_discard = None
                        self.update_display()
                        return self.enable_hand()

        # 否則玩家摸牌
        self.player_turn()

    def is_game_active(self):
        """檢查遊戲是否仍在進行中"""
        return self.game_result is None

    def get_game_result(self):
        """獲取遊戲結果"""
        return self.game_result