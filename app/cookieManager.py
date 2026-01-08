import os
import json
import logging
from datetime import datetime
from http.cookies import SimpleCookie

class CookieManager:
    """Manages ARD authentication cookies for downloading age-restricted content"""

    def __init__(self, cookie_file='cookies.json'):
        self.cookie_file = cookie_file
        self.cookies = {}
        self.load_cookies()

    def load_cookies(self):
        """Load cookies from JSON file"""
        if os.path.exists(self.cookie_file):
            try:
                with open(self.cookie_file, 'r') as f:
                    data = json.load(f)
                    self.cookies = data.get('cookies', {})
                    logging.info(f"Loaded {len(self.cookies)} cookies from {self.cookie_file}")
            except Exception as e:
                logging.error(f"Error loading cookies: {e}")
                self.cookies = {}
        else:
            logging.info("No cookie file found, starting with empty cookies")

    def save_cookies(self):
        """Save cookies to JSON file"""
        try:
            data = {
                'cookies': self.cookies,
                'updated_at': datetime.now().isoformat()
            }
            with open(self.cookie_file, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info(f"Saved {len(self.cookies)} cookies to {self.cookie_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving cookies: {e}")
            return False

    def set_cookies_from_string(self, cookie_string):
        """
        Parse cookie string from browser and save
        Accepts formats:
        - Name=Value; Name2=Value2
        - Name: Value\nName2: Value2
        - JSON format: {"Name": "Value", "Name2": "Value2"}
        """
        self.cookies = {}

        try:
            # Try JSON format first
            if cookie_string.strip().startswith('{'):
                self.cookies = json.loads(cookie_string)
                logging.info(f"Parsed {len(self.cookies)} cookies from JSON format")
            else:
                # Try browser cookie string format (Name=Value; Name2=Value2)
                cookie = SimpleCookie()
                cookie.load(cookie_string)
                for key, morsel in cookie.items():
                    self.cookies[key] = morsel.value

                # If SimpleCookie didn't parse anything, try simple split
                if not self.cookies:
                    # Try Name: Value format (separated by newlines or semicolons)
                    parts = cookie_string.replace('\n', ';').split(';')
                    for part in parts:
                        if '=' in part:
                            name, value = part.split('=', 1)
                            self.cookies[name.strip()] = value.strip()
                        elif ':' in part:
                            name, value = part.split(':', 1)
                            self.cookies[name.strip()] = value.strip()

                logging.info(f"Parsed {len(self.cookies)} cookies from string format")

            self.save_cookies()
            return True
        except Exception as e:
            logging.error(f"Error parsing cookie string: {e}")
            return False

    def get_cookies_dict(self):
        """Get cookies as dictionary for requests library"""
        return self.cookies.copy()

    def get_cookies_for_yt_dlp(self):
        """
        Get cookies in format suitable for yt-dlp
        Returns a dict that can be used with 'cookies' parameter
        """
        return self.cookies.copy()

    def get_cookie_header(self):
        """Get cookies as HTTP Cookie header string"""
        return '; '.join([f"{name}={value}" for name, value in self.cookies.items()])

    def clear_cookies(self):
        """Clear all stored cookies"""
        self.cookies = {}
        self.save_cookies()
        logging.info("Cleared all cookies")

    def has_cookies(self):
        """Check if any cookies are stored"""
        return len(self.cookies) > 0

    def get_cookie_info(self):
        """Get information about stored cookies"""
        return {
            'count': len(self.cookies),
            'cookie_names': list(self.cookies.keys()),
            'has_cookies': self.has_cookies()
        }
