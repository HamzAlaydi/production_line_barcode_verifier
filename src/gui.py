"""
Futuristic GUI implementation for the barcode scanner
"""

import logging
import math
import tkinter as tk
from datetime import datetime
from queue import Empty

logger = logging.getLogger(__name__)


class FuturisticButton(tk.Canvas):
    """Custom animated button with glow effects"""
    
    def __init__(self, parent, text, command, theme, width=380, height=55, **kwargs):
        super().__init__(parent, bg=theme.bg_primary, highlightthickness=0, 
                        width=width, height=height, **kwargs)
        self.text = text
        self.command = command
        self.theme = theme
        self.hover = False
        self.disabled = False
        self.btn_width = width
        self.btn_height = height
        self.bg_color = theme.bg_secondary
        self.glow_color = theme.accent_cyan
        
        self.bind('<Button-1>', self.on_click)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
        self.after(10, self.draw)
    
    def draw(self):
        """Draw the button with current state"""
        self.delete('all')
        w = self.btn_width
        h = self.btn_height
        
        # Glow effect (only when hovering and not disabled)
        if self.hover and not self.disabled:
            for i in range(4):
                self.create_rectangle(
                    -i*2, -i*2, w+i*2, h+i*2,
                    outline=self.glow_color,
                    width=2,
                    tags='glow'
                )
        
        # Main button body
        color = '#1a1f26' if self.disabled else (self.glow_color if self.hover else self.bg_color)
        self.create_rectangle(
            0, 0, w, h,
            fill=color,
            outline=self.glow_color if not self.disabled else '#2a2f36',
            width=2,
            tags='body'
        )
        
        # Text
        text_color = '#4a5a6a' if self.disabled else self.theme.text_white
        self.create_text(
            w//2, h//2,
            text=self.text,
            fill=text_color,
            font=('Segoe UI', 12, 'bold'),
            tags='text'
        )
    
    def on_click(self, event):
        if not self.disabled and self.command:
            self.command()
    
    def on_enter(self, event):
        if not self.disabled:
            self.hover = True
            self.draw()
    
    def on_leave(self, event):
        self.hover = False
        self.draw()
    
    def set_state(self, enabled):
        self.disabled = not enabled
        self.draw()
    
    def set_text(self, text):
        self.text = text
        self.draw()
    
    def set_colors(self, bg_color, glow_color):
        self.bg_color = bg_color
        self.glow_color = glow_color
        self.draw()


class ScannerGUI:
    """Main GUI for the barcode scanner"""
    
    def __init__(self, root, config, theme, scanner, state):
        """
        Initialize the GUI
        
        Args:
            root: Tkinter root window
            config: Configuration object
            theme: Theme object
            scanner: BarcodeScanner object
            state: ScannerState object
        """
        self.root = root
        self.config = config
        self.theme = theme
        self.scanner = scanner
        self.state = state
        
        # Animation variables
        self.scan_animation_phase = 0
        self.pulse_phase = 0
        
        # Chart data
        self.recent_scans = []
        self.max_scans_display = config.getint('Scanner', 'max_chart_scans', fallback=15)
        
        self.setup_window()
        self.setup_ui()
        self.start_animations()
        self.update_ui()
        
        logger.info("GUI initialized")
    
    def setup_window(self):
        """Configure the main window"""
        self.root.title("NEXUS SCANNER")
        
        width = self.config.getint('Display', 'screen_width', fallback=800)
        height = self.config.getint('Display', 'screen_height', fallback=480)
        
        self.root.geometry(f'{width}x{height}')
        self.root.configure(bg=self.theme.bg_primary)
        
        # Fullscreen if configured
        if self.config.getboolean('Display', 'fullscreen', fallback=False):
            self.root.attributes('-fullscreen', True)
        
        # Key bindings
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', 
                                        not self.root.attributes('-fullscreen')))
    
    def setup_ui(self):
        """Create the futuristic UI layout"""
        main = tk.Frame(self.root, bg=self.theme.bg_primary)
        main.pack(fill=tk.BOTH, expand=True)
        
        # === TOP BAR ===
        top_bar = tk.Canvas(main, bg=self.theme.bg_primary, height=50, highlightthickness=0)
        top_bar.pack(fill=tk.X, padx=15, pady=(8, 5))
        
        # Title
        top_bar.create_text(
            10, 15,
            text="◢ NEXUS SCAN",
            fill=self.theme.accent_cyan,
            font=self.theme.font_title,
            anchor='w',
            tags='title'
        )
        
        # Status indicator
        self.status_canvas = tk.Canvas(top_bar, bg=self.theme.bg_primary, 
                                      width=250, height=30, highlightthickness=0)
        self.status_canvas.place(relx=1.0, x=-5, y=10, anchor='ne')
        
        self.status_text = "SYSTEM READY"
        self.status_color = self.theme.text_dim
        
        # Session timer
        top_bar.create_text(
            10, 38,
            text="SESSION: 00:00:00",
            fill=self.theme.text_dim,
            font=self.theme.font_mono,
            anchor='w',
            tags='timer'
        )
        self.timer_id = top_bar.find_withtag('timer')[0]
        self.timer_canvas = top_bar
        
        # === CONTENT AREA ===
        content = tk.Frame(main, bg=self.theme.bg_primary)
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # Left column
        left_col = tk.Frame(content, bg=self.theme.bg_primary)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        # Reference card
        ref_card = tk.Canvas(left_col, bg=self.theme.bg_card, height=120, 
                            highlightthickness=1, highlightbackground=self.theme.accent_cyan)
        ref_card.pack(fill=tk.X, pady=(0, 8))
        
        ref_card.create_text(
            10, 10,
            text="REFERENCE CODE",
            fill=self.theme.text_dim,
            font=self.theme.font_small,
            anchor='w'
        )
        
        self.ref_value_id = ref_card.create_text(
            190, 65,
            text="NOT REGISTERED",
            fill=self.theme.text_dim,
            font=('Consolas', 16, 'bold'),
            anchor='center'
        )
        self.ref_canvas = ref_card
        
        # Chart area
        self.chart_canvas = tk.Canvas(left_col, bg=self.theme.bg_card, height=140, 
                                     highlightthickness=1, highlightbackground=self.theme.accent_cyan)
        self.chart_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.chart_canvas.create_text(
            10, 10,
            text="RECENT SCANS",
            fill=self.theme.text_dim,
            font=self.theme.font_small,
            anchor='w',
            tags='chart_title'
        )
        
        self.draw_scan_chart()
        
        # Right column - Statistics
        right_col = tk.Frame(content, bg=self.theme.bg_primary)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        
        stats_card = tk.Canvas(right_col, bg=self.theme.bg_card, 
                              highlightthickness=1, highlightbackground=self.theme.accent_cyan)
        stats_card.pack(fill=tk.BOTH, expand=True)
        
        stats_card.create_text(
            10, 10,
            text="STATISTICS",
            fill=self.theme.text_dim,
            font=self.theme.font_small,
            anchor='w'
        )
        
        # Stats display
        y_pos = 40
        spacing = 55
        
        stats_card.create_text(12, y_pos, text="TOTAL", fill=self.theme.text_dim, 
                             font=self.theme.font_small, anchor='w')
        self.total_id = stats_card.create_text(360, y_pos, text="0", fill=self.theme.text_white, 
                                              font=self.theme.font_stat, anchor='e')
        
        y_pos += spacing
        stats_card.create_text(12, y_pos, text="MATCH", fill=self.theme.text_dim, 
                             font=self.theme.font_small, anchor='w')
        self.matches_id = stats_card.create_text(360, y_pos, text="0", fill=self.theme.accent_lime, 
                                                 font=self.theme.font_stat, anchor='e')
        
        y_pos += spacing
        stats_card.create_text(12, y_pos, text="ERROR", fill=self.theme.text_dim, 
                             font=self.theme.font_small, anchor='w')
        self.errors_id = stats_card.create_text(360, y_pos, text="0", fill=self.theme.accent_red, 
                                                font=self.theme.font_stat, anchor='e')
        
        y_pos += spacing - 10
        stats_card.create_line(12, y_pos, 360, y_pos, fill=self.theme.bg_secondary, width=1)
        
        y_pos += 15
        stats_card.create_text(12, y_pos, text="LAST SCAN", fill=self.theme.text_dim, 
                             font=('Segoe UI', 7, 'bold'), anchor='w')
        y_pos += 18
        self.last_scan_id = stats_card.create_text(12, y_pos, text="—", fill=self.theme.text_dim, 
                                                   font=self.theme.font_mono, anchor='w', width=350)
        
        self.stats_canvas = stats_card
        
        # === BOTTOM BAR ===
        bottom_bar = tk.Frame(main, bg=self.theme.bg_primary, height=105)
        bottom_bar.pack(fill=tk.X, padx=15, pady=(5, 8))
        bottom_bar.pack_propagate(False)
        
        # Buttons
        button_row = tk.Frame(bottom_bar, bg=self.theme.bg_primary, height=55)
        button_row.pack(fill=tk.X, pady=(0, 8))
        
        self.register_btn = FuturisticButton(
            button_row,
            "▶ REGISTER",
            self.on_register_click,
            self.theme,
            width=380,
            height=55
        )
        self.register_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        self.scan_btn = FuturisticButton(
            button_row,
            "▶ START SCAN",
            self.on_scan_click,
            self.theme,
            width=380,
            height=55
        )
        self.scan_btn.glow_color = self.theme.accent_lime
        self.scan_btn.pack(side=tk.RIGHT)
        self.scan_btn.set_state(False)
        
        # Activity log
        log_frame = tk.Frame(bottom_bar, bg=self.theme.bg_card, height=38, 
                            highlightthickness=1, highlightbackground=self.theme.accent_cyan)
        log_frame.pack(fill=tk.X)
        log_frame.pack_propagate(False)
        
        tk.Label(
            log_frame,
            text="▸ ACTIVITY",
            bg=self.theme.bg_card,
            fg=self.theme.text_dim,
            font=('Segoe UI', 7, 'bold')
        ).pack(anchor='w', padx=8, pady=(3, 0))
        
        self.log_text = tk.Text(
            log_frame,
            height=1,
            bg=self.theme.bg_card,
            fg=self.theme.accent_cyan,
            font=self.theme.font_mono,
            relief=tk.FLAT,
            bd=0,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.X, padx=8, pady=(0, 3))
    
    def draw_scan_chart(self):
        """Draw real-time chart of recent scan results with metrics"""
        self.chart_canvas.delete('chart_data')
        
        w = self.chart_canvas.winfo_width() or 380
        h = self.chart_canvas.winfo_height() or 140
        
        if not self.recent_scans:
            self.chart_canvas.create_text(
                w//2, h//2 - 10,
                text="NO DATA",
                fill=self.theme.text_dim,
                font=('Segoe UI', 11, 'bold'),
                tags='chart_data'
            )
            self.chart_canvas.create_text(
                w//2, h//2 + 10,
                text="Start scanning to see metrics",
                fill=self.theme.text_dim,
                font=self.theme.font_small,
                tags='chart_data'
            )
            return
        
        # Calculate metrics
        num_scans = len(self.recent_scans)
        matches = sum(1 for s in self.recent_scans if s['result'] == 'match')
        errors = num_scans - matches
        success_rate = (matches / num_scans * 100) if num_scans > 0 else 0
        
        # Chart area
        chart_top = 30
        chart_bottom = h - 40
        chart_left = 15
        chart_right = w - 15
        chart_height = chart_bottom - chart_top
        
        # Draw bars
        bar_width = (chart_right - chart_left) / self.max_scans_display
        
        for i, scan in enumerate(self.recent_scans):
            x1 = chart_left + (i * bar_width)
            x2 = x1 + bar_width - 2
            
            if scan['result'] == 'match':
                color = self.theme.accent_lime
                y1 = chart_top
                y2 = chart_bottom
            else:
                color = self.theme.accent_red
                y1 = chart_top + chart_height // 2
                y2 = chart_bottom
            
            self.chart_canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline='',
                tags='chart_data'
            )
            
            # Glow on latest scan
            if i == num_scans - 1 and self.state.scanning_active:
                pulse = math.sin(self.scan_animation_phase * 0.1) * 0.3 + 0.7
                self.chart_canvas.create_rectangle(
                    x1-1, y1-1, x2+1, y2+1,
                    fill='',
                    outline=color,
                    width=2,
                    tags='chart_data'
                )
        
        # Baseline
        mid_y = chart_top + chart_height // 2
        self.chart_canvas.create_line(
            chart_left, mid_y, chart_right, mid_y,
            fill=self.theme.text_dim,
            width=1,
            dash=(2, 2),
            tags='chart_data'
        )
        
        # Labels
        self.chart_canvas.create_text(
            chart_left, chart_top - 5,
            text="MATCH",
            fill=self.theme.accent_lime,
            font=self.theme.font_small,
            anchor='w',
            tags='chart_data'
        )
        
        self.chart_canvas.create_text(
            chart_right, chart_top - 5,
            text=f"{num_scans}/{self.max_scans_display}",
            fill=self.theme.text_dim,
            font=self.theme.font_small,
            anchor='e',
            tags='chart_data'
        )
        
        # === METRICS BAR ===
        metrics_y = chart_bottom + 10
        
        # Success Rate
        success_color = (self.theme.accent_lime if success_rate >= 75 else 
                        (self.theme.accent_cyan if success_rate >= 50 else self.theme.accent_red))
        
        self.chart_canvas.create_text(
            chart_left, metrics_y,
            text="SUCCESS RATE",
            fill=self.theme.text_dim,
            font=('Segoe UI', 6),
            anchor='w',
            tags='chart_data'
        )
        
        self.chart_canvas.create_text(
            chart_left + 65, metrics_y,
            text=f"{success_rate:.0f}%",
            fill=success_color,
            font=('Segoe UI', 12, 'bold'),
            anchor='w',
            tags='chart_data'
        )
        
        # Match/Error counts
        center_x = w // 2
        self.chart_canvas.create_text(
            center_x - 35, metrics_y,
            text=f"✓ {matches}",
            fill=self.theme.accent_lime,
            font=('Segoe UI', 10, 'bold'),
            anchor='e',
            tags='chart_data'
        )
        
        self.chart_canvas.create_text(
            center_x - 30, metrics_y,
            text="│",
            fill=self.theme.text_dim,
            font=('Segoe UI', 10),
            tags='chart_data'
        )
        
        self.chart_canvas.create_text(
            center_x - 20, metrics_y,
            text=f"✗ {errors}",
            fill=self.theme.accent_red,
            font=('Segoe UI', 10, 'bold'),
            anchor='w',
            tags='chart_data'
        )
        
        # Trend indicator
        if num_scans >= 3:
            recent_3 = self.recent_scans[-3:]
            recent_matches = sum(1 for s in recent_3 if s['result'] == 'match')
            trend = "↗" if recent_matches >= 2 else "↘" if recent_matches <= 1 else "→"
            trend_color = (self.theme.accent_lime if recent_matches >= 2 else 
                          self.theme.accent_red if recent_matches <= 1 else self.theme.text_dim)
            
            self.chart_canvas.create_text(
                chart_right - 35, metrics_y,
                text="TREND",
                fill=self.theme.text_dim,
                font=('Segoe UI', 6),
                anchor='e',
                tags='chart_data'
            )
            
            self.chart_canvas.create_text(
                chart_right, metrics_y,
                text=trend,
                fill=trend_color,
                font=('Segoe UI', 14, 'bold'),
                anchor='e',
                tags='chart_data'
            )
        
        self.scan_animation_phase += 1
    
    def draw_status_indicator(self):
        """Draw animated status with pulse effect"""
        self.status_canvas.delete('all')
        w = self.status_canvas.winfo_width()
        h = self.status_canvas.winfo_height()
        
        # Pulsing dot
        pulse_size = 4 + math.sin(self.pulse_phase) * 1.5
        self.status_canvas.create_oval(
            8-pulse_size, h//2-pulse_size,
            8+pulse_size, h//2+pulse_size,
            fill=self.status_color,
            outline='',
            tags='pulse'
        )
        
        # Status text
        self.status_canvas.create_text(
            20, h//2,
            text=self.status_text,
            fill=self.status_color,
            font=('Segoe UI', 10, 'bold'),
            anchor='w'
        )
        
        self.pulse_phase += 0.1
    
    def update_timer(self):
        """Update session timer"""
        if self.state.stats['session_start']:
            elapsed = datetime.now() - self.state.stats['session_start']
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            seconds = int(elapsed.total_seconds() % 60)
            timer_text = f"SESSION: {hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_canvas.itemconfig(self.timer_id, text=timer_text)
    
    def start_animations(self):
        """Start all animation loops"""
        def animate():
            if self.state.running:
                self.draw_scan_chart()
                self.draw_status_indicator()
                self.update_timer()
                self.root.after(30, animate)
        animate()
    
    def on_register_click(self):
        """Handle register button click"""
        logger.info("Register button clicked")
        import threading
        threading.Thread(target=self.scanner.register_reference, daemon=True).start()
    
    def on_scan_click(self):
        """Handle scan button click"""
        logger.info("Scan button clicked")
        self.scanner.toggle_scanning()
    
    def update_ui(self):
        """Process GUI updates from queue"""
        try:
            while True:
                msg_type, data = self.state.gui_queue.get_nowait()
                
                if msg_type == 'status':
                    self.status_text = data
                    if 'ACTIVE' in data or 'SCANNING' in data:
                        self.status_color = self.theme.accent_lime
                    elif 'LOCKED' in data or 'REGISTERED' in data:
                        self.status_color = self.theme.accent_cyan
                    elif 'ERROR' in data or 'FAILED' in data:
                        self.status_color = self.theme.accent_red
                    else:
                        self.status_color = self.theme.text_dim
                
                elif msg_type == 'reference':
                    self.ref_canvas.itemconfig(self.ref_value_id, text=data, fill=self.theme.accent_cyan)
                    self.scan_btn.set_state(True)
                    self.scan_btn.glow_color = self.theme.accent_lime
                
                elif msg_type == 'scanning':
                    if data:
                        self.scan_btn.set_text("■ STOP SCAN")
                        self.scan_btn.set_colors(self.theme.accent_red, self.theme.accent_red)
                    else:
                        self.scan_btn.set_text("▶ START SCAN")
                        self.scan_btn.set_colors(self.theme.bg_secondary, self.theme.accent_lime)
                
                elif msg_type == 'stats':
                    self.stats_canvas.itemconfig(self.total_id, text=str(data['total_scans']))
                    self.stats_canvas.itemconfig(self.matches_id, text=str(data['matches']))
                    self.stats_canvas.itemconfig(self.errors_id, text=str(data['mismatches']))
                    
                    if data['last_scan']:
                        color = self.theme.accent_lime if data['last_result'] == 'MATCH' else self.theme.accent_red
                        self.stats_canvas.itemconfig(self.last_scan_id, text=data['last_scan'], fill=color)
                
                elif msg_type == 'scan_result':
                    # Add to chart
                    result_type = 'match' if data['match'] else 'error'
                    self.recent_scans.append({
                        'result': result_type,
                        'time': datetime.now()
                    })
                    
                    if len(self.recent_scans) > self.max_scans_display:
                        self.recent_scans.pop(0)
                    
                    # Flash effect
                    if data['match']:
                        self.flash_background(self.theme.accent_lime)
                    else:
                        self.flash_background(self.theme.accent_red)
                
                elif msg_type == 'log':
                    self.log_text.config(state=tk.NORMAL)
                    self.log_text.delete('1.0', tk.END)
                    self.log_text.insert('1.0', data)
                    self.log_text.config(state=tk.DISABLED)
                
                elif msg_type == 'error':
                    self.status_text = f"⚠ {data}"
                    self.status_color = self.theme.accent_red
        
        except Empty:
            pass
        
        self.root.after(50, self.update_ui)
    
    def flash_background(self, color):
        """Create a subtle flash effect"""
        original = self.root['bg']
        flash_color = '#0f1419' if color == self.theme.accent_lime else '#1a0f14'
        self.root.configure(bg=flash_color)
        self.root.after(100, lambda: self.root.configure(bg=original))

