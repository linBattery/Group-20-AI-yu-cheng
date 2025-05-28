import tkinter as tk
from mahjong_gui import MahjongGame
import matplotlib.pyplot as plt
from agent import MahjongAgent  # 新增 import

game_num = 1000


class GameManager:
    def __init__(self, total_games=game_num):
        self.total_games = total_games
        self.current_game = 0
        self.stats = {
            'player_win': 0,
            'ai_win': 0,
            'draw': 0
        }
        self.win_rate_history = []  # 用於記錄勝率變化
        self.game_intervals = []  # 用於記錄遊戲場次
        
        # 創建主窗口
        self.root = tk.Tk()
        self.root.title("麻將對戰統計")
        self.root.geometry("400x300")
        
        # 創建統計顯示
        self.stats_frame = tk.Frame(self.root)
        self.stats_frame.pack(pady=20)
        
        self.progress_label = tk.Label(self.stats_frame, text=f"進度: 0/{game_num}", font=("Arial", 12))
        self.progress_label.pack()
        
        self.player_win_label = tk.Label(self.stats_frame, text="Strong AI 勝場: 0", font=("Arial", 12))
        self.player_win_label.pack()
        
        self.ai_win_label = tk.Label(self.stats_frame, text="Normal AI 勝場: 0", font=("Arial", 12))
        self.ai_win_label.pack()
        
        self.draw_label = tk.Label(self.stats_frame, text="和局: 0", font=("Arial", 12))
        self.draw_label.pack()
        
        self.win_rate_label = tk.Label(self.stats_frame, text="Strong AI 勝率: 0%", font=("Arial", 12))
        self.win_rate_label.pack()

        # 添加控制按鈕
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)
        
        self.start_button = tk.Button(self.control_frame, text="開始測試", command=self.start_testing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(self.control_frame, text="停止", command=self.stop_testing)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.config(state=tk.DISABLED)

        # 添加玩家模式按鈕
        self.player_mode_button = tk.Button(self.control_frame, text="與一般AI對戰", command=lambda: self.start_player_mode("normal"))
        self.player_mode_button.pack(side=tk.LEFT, padx=5)

        # 添加與 Agent 對戰按鈕
        self.agent_mode_button = tk.Button(self.control_frame, text="與強化學習AI對戰", command=lambda: self.start_player_mode("agent"))
        self.agent_mode_button.pack(side=tk.LEFT, padx=5)

        # 遊戲狀態
        self.is_testing = False
        self.game_window = None
        self.game = None
        
    def update_stats(self):
        """更新統計顯示"""
        self.progress_label.config(text=f"進度: {self.current_game}/{self.total_games}")
        self.player_win_label.config(text=f"Strong AI 勝場: {self.stats['player_win']}")
        self.ai_win_label.config(text=f"Normal AI 勝場: {self.stats['ai_win']}")
        self.draw_label.config(text=f"和局: {self.stats['draw']}")
        
        total_finished = sum(self.stats.values())
        if total_finished > 0:
            if (self.stats['player_win'] + self.stats['ai_win']) > 0:
                win_rate = (self.stats['player_win'] / (self.stats['player_win'] + self.stats['ai_win'])) * 100
            else:
                win_rate = 0
            self.win_rate_label.config(text=f"Strong AI 勝率: {win_rate:.1f}%")
            
            # 每50場記錄一次勝率
            if self.current_game % 50 == 0 or self.current_game == self.total_games:
                self.win_rate_history.append(win_rate)
                self.game_intervals.append(self.current_game)
                self.save_win_rate_plot()
    
    def save_win_rate_plot(self):
        """保存勝率變化圖"""
        plt.figure(figsize=(10, 6))
        plt.plot(self.game_intervals, self.win_rate_history, 'b-', marker='o', linewidth=2, markersize=6)
        
        # 設置x軸的刻度
        plt.xticks(range(0, max(self.game_intervals) + 50, 50))
        
        # 設置y軸的範圍和刻度
        min_rate = min(self.win_rate_history) - 0.5
        max_rate = max(self.win_rate_history) + 0.5
        plt.ylim(min_rate, max_rate)
        
        # 使用較小的網格
        plt.grid(True, linestyle='--', alpha=0.7, which='both')
        plt.minorticks_on()  # 啟用次要刻度
        
        plt.xlabel('Number of Games')
        plt.ylabel('Strong AI Win Rate (%)')
        plt.title('Strong AI Win Rate Trend')
        
        # 調整圖表邊距
        plt.tight_layout()
        
        plt.savefig('win_rate_history.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def check_game_status(self):
        """檢查當前遊戲狀態"""
        if not self.is_testing:
            return
            
        if not self.game_window or not self.game_window.winfo_exists():
            self.start_new_game()
            return
            
        result = self.game.get_game_result()
        if result:
            # 記錄結果
            self.stats[result] += 1
            self.current_game += 1
            self.update_stats()
            
            # 關閉遊戲窗口
            self.game_window.destroy()
            
            # 如果還沒完成所有遊戲，開始下一場
            if self.current_game < self.total_games:
                self.root.after(game_num, self.start_new_game)
            else:
                self.stop_testing()
        else:
            # 如果遊戲還在進行，繼續檢查
            self.root.after(game_num, self.check_game_status)
    
    def start_new_game(self):
        """開始一場新遊戲"""
        if not self.is_testing:
            return
            
        self.game_window = tk.Toplevel(self.root)
        self.game = MahjongGame(self.game_window, is_auto_mode=True)
        self.check_game_status()

    def start_player_mode(self, opponent_type="normal"):
        """開始玩家模式
        opponent_type: 'normal' 為一般AI，'agent' 為強化學習AI
        """
        # 創建新窗口用於玩家模式
        player_window = tk.Toplevel(self.root)
        # 創建遊戲實例，is_auto_mode設為False表示玩家模式，並傳入對手類型
        MahjongGame(player_window, is_auto_mode=False, opponent_type=opponent_type)
        
    def start_testing(self):
        """開始測試"""
        self.is_testing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.player_mode_button.config(state=tk.DISABLED)  # 在測試時禁用玩家模式按鈕
        self.start_new_game()
        
    def stop_testing(self):
        """停止測試"""
        self.is_testing = False
        if self.game_window and self.game_window.winfo_exists():
            self.game_window.destroy()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.player_mode_button.config(state=tk.NORMAL)  # 測試結束後重新啟用玩家模式按鈕

if __name__ == "__main__":
    manager = GameManager(total_games=game_num)
    manager.root.mainloop()