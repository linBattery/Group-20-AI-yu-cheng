import random
import pickle
import os
import copy
from collections import defaultdict, Counter
from mahjong_logic import is_hu, can_hu_with_tile, can_peng, can_gang, get_chi_options

class MahjongAgent:
    def __init__(self, role="player"):
        """初始化 MahjongAgent
        role: 'player' 或 'ai'，用於區分不同角色的 agent
        """
        print(f"初始化 MahjongAgent (role: {role})")
        self.role = role
        
        # 初始化基本變數
        self.exploration_interval = 100  # 每100場嘗試探索
        self.exploration_rate = 0.90 # 90%的機率進行探索
        self.improvement_threshold = 0.025  # 2.5%的提升閾值
        
        # 初始化統計數據
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.total_games = 0
        self.games_since_last_exploration = 0
        self.best_win_rate = 0.0
        self.has_baseline = False
        
        # 當前測試回合的統計
        self.current_session_wins = 0
        self.current_session_losses = 0
        self.current_session_draws = 0
        self.current_session_games = 0
        
        # 嘗試載入已保存的模型，如果失敗則初始化新模型
        if not self.load_model():
            self.initialize_model()
        else:
            # 重置探索計數器
            self.games_since_last_exploration = 0
            self.save_model()
            
    def initialize_model(self):
        """初始化模型參數"""
        # 初始化統計數據
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.total_games = 0
        self.games_since_last_exploration = 0
        self.best_win_rate = 0.0
        self.has_baseline = False
        
        # 初始化權重
        self.weights = {
            # 基本牌型權重
            'pair': 2.0,          # 對子價值
            'triple': 3.0,        # 刻子價值
            'sequence': 2.5,      # 順子價值
            'almost_ready': 6.0,  # 聽牌價值
            'ready_high_score': 8.0,  # 高分聽牌價值（可能胡大牌）
            
            # 位置和數字權重
            'terminal': -1.0,     # 邊張價值（1和9）
            'middle': 1.5,        # 中張價值（456）
            'near_middle': 1.0,   # 近中張價值（34567）
            
            # 特殊牌權重
            'honor': 2.0,         # 字牌價值
            'honor_pair': 3.0,    # 字牌對子價值
            'honor_triple': 4.0,  # 字牌刻子價值
            
            # 進展程度權重
            'one_away': 3.0,      # 差一張完成面子
            'two_away': 1.5,      # 差兩張完成面子
            'flexible': 2.0,      # 牌型靈活度（可以形成多種組合）
            
            # 防禦權重
            'safe_tile': 2.0,     # 安全牌價值
            'risky_tile': -2.0,   # 危險牌價值
            
            # 其他權重
            'single': -1.5,       # 單張價值
            'isolated': -2.0,     # 孤立牌價值（無法形成順子）
        }
        self.best_weights = copy.deepcopy(self.weights)
        print("模型已初始化")
        
    def explore_weights(self):
        """探索新的權重組合"""
        new_weights = copy.deepcopy(self.weights)
        # 隨機選擇60%的權重進行調整
        keys_to_modify = random.sample(list(new_weights.keys()), k=int(len(new_weights) * 0.6))
        for key in keys_to_modify:
            # 在原始值的50%到150%範圍內隨機調整
            current_value = new_weights[key]
            new_value = current_value * random.uniform(0.5, 1.5)
            new_weights[key] = new_value
        return new_weights
        
    def evaluate_hand(self, hand):
        """評估手牌價值"""
        if not hand:
            return -10.0
            
        value = 0.0
        counts = Counter(hand)
        
        # 計算基本牌型價值
        value += self._evaluate_basic_patterns(hand, counts)
        
        # 計算位置和數字價值
        value += self._evaluate_positions(hand)
        
        # 計算進展程度
        value += self._evaluate_progress(hand)
        
        # 計算防禦價值
        value += self._evaluate_defense(hand)
        
        # 檢查聽牌和高分可能
        if self.is_waiting(hand):
            value += self.weights['almost_ready']
            if self._has_potential_high_score(hand):
                value += self.weights['ready_high_score']
                
        return value
        
    def _evaluate_basic_patterns(self, hand, counts):
        """評估基本牌型"""
        value = 0.0
        
        # 計算對子和刻子
        for tile, count in counts.items():
            if count == 2:
                if tile in ["東", "南", "西", "北", "中", "發", "白"]:
                    value += self.weights['honor_pair']
                else:
                    value += self.weights['pair']
            elif count == 3:
                if tile in ["東", "南", "西", "北", "中", "發", "白"]:
                    value += self.weights['honor_triple']
                else:
                    value += self.weights['triple']
            elif count == 1:
                value += self.weights['single']
                
        # 計算順子
        value += self._evaluate_sequences(hand)
        
        return value
        
    def _evaluate_sequences(self, hand):
        """評估順子和準順子"""
        value = 0.0
        numbers = defaultdict(list)
        
        # 整理數字牌
        for tile in hand:
            if tile.endswith('萬'):
                num = int(tile[0])
                numbers[num].append(tile)
                
        # 檢查順子
        for i in range(1, 8):
            if all(numbers[i+j] for j in range(3)):
                value += self.weights['sequence']
            elif len([j for j in range(3) if numbers[i+j]]) == 2:
                value += self.weights['one_away']
            elif len([j for j in range(3) if numbers[i+j]]) == 1:
                value += self.weights['two_away']
                
        return value
        
    def _evaluate_positions(self, hand):
        """評估牌的位置價值"""
        value = 0.0
        for tile in hand:
            if tile.endswith('萬'):
                num = int(tile[0])
                if num in [1, 9]:
                    value += self.weights['terminal']
                elif num in [4, 5, 6]:
                    value += self.weights['middle']
                elif num in [3, 7]:
                    value += self.weights['near_middle']
            else:  # 字牌
                value += self.weights['honor']
                
        return value
        
    def _evaluate_progress(self, hand):
        """評估手牌進展程度"""
        value = 0.0
        numbers = defaultdict(int)
        
        # 計算數字牌的靈活度
        for tile in hand:
            if tile.endswith('萬'):
                num = int(tile[0])
                numbers[num] += 1
                
                # 檢查相鄰數字
                if numbers[num-1] > 0 or numbers[num+1] > 0:
                    value += self.weights['flexible']
                else:
                    value += self.weights['isolated']
                    
        return value
        
    def _evaluate_defense(self, hand):
        """評估防禦價值"""
        value = 0.0
        
        # 簡單的防禦評估：字牌和19較安全
        for tile in hand:
            if tile in ["東", "南", "西", "北", "中", "發", "白"]:
                value += self.weights['safe_tile']
            elif tile.endswith('萬'):
                num = int(tile[0])
                if num in [1, 9]:
                    value += self.weights['safe_tile']
                elif num in [4, 5, 6]:
                    value += self.weights['risky_tile']
                    
        return value
        
    def is_waiting(self, hand):
        """檢查是否聽牌"""
        all_tiles = [f"{i}萬" for i in range(1, 10)] * 4 + \
                   ["東", "南", "西", "北", "中", "發", "白"] * 4
                   
        for tile in set(all_tiles):
            test_hand = hand + [tile]
            if is_hu(test_hand):
                return True
        return False
        
    def _has_potential_high_score(self, hand):
        """評估是否有可能胡大牌"""
        # 檢查是否有字牌刻子可能
        counts = Counter(hand)
        honor_pairs = sum(1 for t, c in counts.items() 
                         if t in ["東", "南", "西", "北", "中", "發", "白"] and c >= 2)
                         
        # 檢查是否有清一色可能
        all_numbers = all(t.endswith('萬') for t in hand)
        
        return honor_pairs >= 2 or all_numbers
        
    def choose_action(self, hand, last_discard=None):
        """選擇行動（胡、槓、碰、吃、打牌）"""
        if not hand:
            return None

        # 如果可以胡牌，就胡牌
        if last_discard and can_hu_with_tile(hand, 0, last_discard):
            print(f"{self.role} decides to hu")
            return 'hu'
            
        # 如果可以槓牌，評估是否要槓
        if last_discard and can_gang(hand, last_discard, is_self_drawn=False):
            # 評估槓後的手牌價值
            test_hand = hand.copy()
            for _ in range(3):
                test_hand.remove(last_discard)
            # 計算槓後的手牌價值（包括槓的獎勵）
            gang_value = self.evaluate_hand(test_hand) + self.weights['triple'] * 1.5
            if gang_value > self.evaluate_hand(hand):
                print(f"{self.role} decides to gang")
                return 'gang'
            
        # 如果可以碰牌，評估是否要碰
        if last_discard and can_peng(hand, last_discard):
            # 評估碰後的手牌價值
            test_hand = hand.copy()
            test_hand.remove(last_discard)
            test_hand.remove(last_discard)
            # 計算碰後的手牌價值（包括刻子獎勵）
            peng_value = self.evaluate_hand(test_hand) + self.weights['triple']
            if peng_value > self.evaluate_hand(hand):
                print(f"{self.role} decides to peng")
                return 'peng'
            
        # 如果可以吃牌，評估最佳吃牌方式
        if last_discard:
            chi_options = get_chi_options(hand, last_discard)
            if chi_options:
                best_value = float('-inf')
                best_option = None
                current_value = self.evaluate_hand(hand)
                
                for option in chi_options:
                    test_hand = hand.copy()
                    # 移除需要的牌
                    for tile in option:
                        if tile != last_discard and tile in test_hand:
                            test_hand.remove(tile)
                    # 計算吃後的手牌價值（包括順子獎勵）
                    chi_value = self.evaluate_hand(test_hand) + self.weights['sequence']
                    
                    if chi_value > best_value:
                        best_value = chi_value
                        best_option = option
                        
                if best_value > current_value and best_option:
                    print(f"{self.role} decides to chi {best_option}")
                    return best_option  # 返回具體的吃牌組合
        
        # 選擇要打出的牌
        best_discard = None
        best_value = float('-inf')
        
        for tile in hand:
            test_hand = hand.copy()
            test_hand.remove(tile)
            value = self.evaluate_hand(test_hand)
            
            # 如果這張牌是安全牌，提高其價值
            if tile in ["東", "南", "西", "北", "中", "發", "白"] or \
               (tile.endswith('萬') and tile[0] in ['1', '9']):
                value += self.weights['safe_tile']
                
            if value > best_value:
                best_value = value
                best_discard = tile
                
        print(f"{self.role} decides to discard {best_discard}")
        return best_discard
        
    def update_statistics(self, result):
        """更新統計資料並可能進行權重探索"""
        # 更新總體統計
        self.total_games += 1
        if result == 'player_win':
            self.wins += 1
            self.current_session_wins += 1
        elif result == 'ai_win':
            self.losses += 1
            self.current_session_losses += 1
        else:
            self.draws += 1
            self.current_session_draws += 1
            
        self.current_session_games += 1
            
        self.games_since_last_exploration = self.games_since_last_exploration + 1
        
        # 每隔固定場數考慮是否進行探索
        if self.games_since_last_exploration >= self.exploration_interval:
            # print(f"達到探索間隔 ({self.exploration_interval} 場)，重置計數器")
            self.games_since_last_exploration = 0
            print(f"觸發探索檢查點 (遊戲場次: {self.current_session_games})")
            
            if self.current_session_games > 0:  # 確保有足夠的數據來計算勝率
                current_win_rate = self.current_session_wins / self.current_session_games
                print(f"當前回合勝率: {current_win_rate:.2%}")
                
                # 如果還沒有基準勝率，設定當前勝率為基準
                if not self.has_baseline:
                    self.best_win_rate = current_win_rate
                    self.best_weights = copy.deepcopy(self.weights)
                    self.has_baseline = True
                    print("設定初始基準勝率:", self.best_win_rate)
                
                # 開始探索新的權重組合
                
                # 如果有待評估的權重，進行評估
                if hasattr(self, 'pending_evaluation'):
                    current_win_rate = self.current_session_wins / self.current_session_games if self.current_session_games > 0 else 0
                    old_win_rate = (self.pending_evaluation['old_stats']['wins'] / 
                                  self.pending_evaluation['old_stats']['total_games'])
                    
                    print(f"評估新權重效果 - 新勝率: {current_win_rate:.2%}, 舊勝率: {old_win_rate:.2%}")
                    
                    # 如果新權重沒有帶來足夠的改善，恢復舊權重
                    if current_win_rate < old_win_rate + self.improvement_threshold:
                        print("新權重效果不佳，恢復舊權重")
                        self.weights = self.pending_evaluation['old_weights']
                        self.current_session_wins = self.pending_evaluation['old_stats']['wins']
                        self.current_session_losses = self.pending_evaluation['old_stats']['losses']
                        self.current_session_draws = self.pending_evaluation['old_stats']['draws']
                        self.current_session_games = self.pending_evaluation['old_stats']['total_games']
                    else:
                        print("保留新權重組合")
                        if current_win_rate > self.best_win_rate:
                            self.best_win_rate = current_win_rate
                            self.best_weights = copy.deepcopy(self.weights)
                            print(f"更新最佳勝率: {self.best_win_rate:.2%}")
                    
                    delattr(self, 'pending_evaluation')
                
                if random.random() < self.exploration_rate:
                    print("開始探索新的權重組合")
                    new_weights = self.explore_weights()
                    # 保存當前權重和統計數據
                    old_weights = copy.deepcopy(self.weights)
                    old_stats = {
                        'wins': self.current_session_wins,
                        'losses': self.current_session_losses,
                        'draws': self.current_session_draws,
                        'total_games': self.current_session_games
                    }
                    
                    # 使用新權重
                    self.weights = new_weights
                    # 重置當前回合統計數據以計算新權重的效果
                    self.current_session_wins = 0
                    self.current_session_losses = 0
                    self.current_session_draws = 0
                    self.current_session_games = 0
                    
                    # 在下一個探索週期檢查新權重的效果
                    self.pending_evaluation = {
                        'old_weights': old_weights,
                        'old_stats': old_stats
                    }
                    print("已設置新的權重組合，等待評估")
        
        # 每次更新後都保存模型
        self.save_model()
        
    def get_statistics(self):
        """獲取統計資料"""
        if self.total_games == 0:
            return 0, 0, 0
            
        win_rate = self.wins / self.total_games
        loss_rate = self.losses / self.total_games
        draw_rate = self.draws / self.total_games
        return win_rate, loss_rate, draw_rate
        
    def save_model(self, path=None):
        """保存模型到文件"""
        if path is None:
            path = 'mahjong_agent.pkl'
            
        try:
            model_state = {
                'weights': self.weights,
                'best_weights': self.best_weights,
                'wins': self.wins,
                'losses': self.losses,
                'draws': self.draws,
                'total_games': self.total_games,
                'best_win_rate': self.best_win_rate,
                'games_since_last_exploration': self.games_since_last_exploration,
                'has_baseline': self.has_baseline,
                'current_session_wins': self.current_session_wins,
                'current_session_losses': self.current_session_losses,
                'current_session_draws': self.current_session_draws,
                'current_session_games': self.current_session_games
            }
            with open(path, 'wb') as f:
                pickle.dump(model_state, f)
            return True
        except Exception as e:
            print(f"保存模型時發生錯誤: {e}")
            return False
            
    def load_model(self, path=None):
        """從文件載入模型"""
        if path is None:
            path = 'mahjong_agent.pkl'
            
        try:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    model_state = pickle.load(f)
                    
                self.weights = model_state['weights']
                self.best_weights = model_state['best_weights']
                self.wins = model_state['wins']
                self.losses = model_state['losses']
                self.draws = model_state['draws']
                self.total_games = model_state['total_games']
                self.best_win_rate = model_state['best_win_rate']
                self.games_since_last_exploration = model_state['games_since_last_exploration']
                self.has_baseline = model_state['has_baseline']
                self.current_session_wins = model_state.get('current_session_wins', 0)
                self.current_session_losses = model_state.get('current_session_losses', 0)
                self.current_session_draws = model_state.get('current_session_draws', 0)
                self.current_session_games = model_state.get('current_session_games', 0)
                return True
        except Exception as e:
            print(f"載入模型時發生錯誤: {e}")
        return False
