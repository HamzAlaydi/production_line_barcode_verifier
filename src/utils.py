"""
Utility functions and helpers for the barcode scanner
"""

import configparser
import logging
import logging.handlers
import os
from pathlib import Path


class Config:
    """Configuration manager for the scanner application"""
    
    def __init__(self, config_path='config/config.ini'):
        self.config = configparser.ConfigParser()
        self.config_path = config_path
        self.load()
    
    def load(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        self.config.read(self.config_path)
    
    def get(self, section, key, fallback=None):
        """Get configuration value"""
        return self.config.get(section, key, fallback=fallback)
    
    def getint(self, section, key, fallback=None):
        """Get integer configuration value"""
        return self.config.getint(section, key, fallback=fallback)
    
    def getfloat(self, section, key, fallback=None):
        """Get float configuration value"""
        return self.config.getfloat(section, key, fallback=fallback)
    
    def getboolean(self, section, key, fallback=None):
        """Get boolean configuration value"""
        return self.config.getboolean(section, key, fallback=fallback)


def setup_logging(config):
    """
    Setup logging configuration
    
    Args:
        config: Config object with logging settings
    """
    log_file = config.get('Logging', 'log_file')
    log_level = config.get('Logging', 'log_level', fallback='INFO')
    max_bytes = config.getint('Logging', 'max_log_size', fallback=10) * 1024 * 1024
    backup_count = config.getint('Logging', 'backup_count', fallback=3)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def ensure_directories():
    """Ensure all required directories exist"""
    directories = ['logs', 'data', 'config']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def validate_environment():
    """
    Validate the environment is ready for production
    
    Returns:
        tuple: (is_valid, error_message)
    """
    errors = []
    
    # Check required directories
    required_dirs = ['logs', 'data', 'config']
    for directory in required_dirs:
        if not os.path.exists(directory):
            errors.append(f"Missing directory: {directory}")
    
    # Check config file
    if not os.path.exists('config/config.ini'):
        errors.append("Missing configuration file: config/config.ini")
    
    # Check write permissions
    try:
        test_file = 'data/.write_test'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
    except Exception as e:
        errors.append(f"No write permission in data directory: {e}")
    
    if errors:
        return False, '\n'.join(errors)
    
    return True, None


class Theme:
    """Theme configuration for the GUI"""
    
    def __init__(self, config):
        """Initialize theme from configuration"""
        self.bg_primary = config.get('Theme', 'bg_primary', fallback='#0a0e14')
        self.bg_secondary = config.get('Theme', 'bg_secondary', fallback='#151b23')
        self.bg_card = config.get('Theme', 'bg_card', fallback='#1a2029')
        self.accent_cyan = config.get('Theme', 'accent_cyan', fallback='#00d9ff')
        self.accent_magenta = config.get('Theme', 'accent_magenta', fallback='#ff006e')
        self.accent_lime = config.get('Theme', 'accent_lime', fallback='#39ff14')
        self.accent_blue = config.get('Theme', 'accent_blue', fallback='#0080ff')
        self.accent_red = config.get('Theme', 'accent_red', fallback='#ff3366')
        self.text_white = config.get('Theme', 'text_white', fallback='#ffffff')
        self.text_dim = config.get('Theme', 'text_dim', fallback='#6a7a8a')
        self.text_bright = config.get('Theme', 'text_bright', fallback='#e0e8f0')
        
        # Font definitions (optimized for 800x480)
        self.font_title = ('Segoe UI', 18, 'bold')
        self.font_header = ('Segoe UI', 12, 'bold')
        self.font_subheader = ('Segoe UI', 10, 'bold')
        self.font_body = ('Segoe UI', 9)
        self.font_body_bold = ('Segoe UI', 9, 'bold')
        self.font_small = ('Segoe UI', 7)
        self.font_stat = ('Segoe UI', 24, 'bold')
        self.font_mono = ('Consolas', 8)

