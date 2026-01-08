import os
import json
import logging
from datetime import datetime
from http.cookies import SimpleCookie

class CookieManager:
    """Manages ARD authentication cookies for downloading age-restricted content"""

    def __init__(self, cookie_file='cookies.json', data_dir='/app/data'):
        # Ensure data directory exists
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            try:
                os.makedirs(self.data_dir, exist_ok=True)
                logging.info(f"Created data directory: {self.data_dir}")
            except Exception as e:
                logging.warning(f"Could not create data directory {self.data_dir}: {e}, using current directory")
                self.data_dir = '.'

        self.cookie_file = os.path.join(self.data_dir, cookie_file)
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

    def create_netscape_cookie_file(self, filepath='cookies.txt'):
        """
        Create a Netscape-format cookie file for yt-dlp
        This format is required by yt-dlp for proper cookie handling
        """
        try:
            # Use full path in data directory
            full_path = os.path.join(self.data_dir, filepath)
            with open(full_path, 'w') as f:
                # Write Netscape cookie file header
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# This file is generated by OpenAudiothekDownloader\n")
                f.write("# Edit at your own risk.\n\n")

                # Write each cookie in Netscape format
                # Format: domain, flag, path, secure, expiration, name, value
                for name, value in self.cookies.items():
                    # ARD Mediathek uses multiple domains with path scoping
                    # Critical: sso.ardmediathek.de/sso for age verification
                    # Also need: .ardmediathek.de, .ard.de, .daserste.de

                    # Write cookies for all relevant domains and paths
                    # SSO domain with /sso path is critical for age verification
                    # Netscape format rules: domains with leading dot use TRUE, without use FALSE
                    cookie_entries = [
                        (".ardmediathek.de", "/", "TRUE"),
                        (".sso.ardmediathek.de", "/sso", "TRUE"),  # Use leading dot for domain flag TRUE
                        (".sso.ardmediathek.de", "/", "TRUE"),
                        (".ard.de", "/", "TRUE"),
                        (".daserste.de", "/", "TRUE"),
                    ]

                    for domain, path, flag in cookie_entries:
                        secure = "TRUE"  # ARD uses HTTPS
                        expiration = "2147483647"  # Far future expiration

                        f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n")

            logging.info(f"Created Netscape cookie file: {full_path} with {len(self.cookies)} cookies")

            # Log the cookie file content for debugging
            with open(full_path, 'r') as f:
                content = f.read()
                logging.info(f"Cookie file content preview (first 500 chars):\n{content[:500]}")

            return full_path
        except Exception as e:
            logging.error(f"Error creating Netscape cookie file: {e}")
            return None
