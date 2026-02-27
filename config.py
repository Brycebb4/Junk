# Configuration Settings for CincyJunkBot

import os

class Config:
    """Main configuration class"""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cincy-junk-bot-secret-key-2024')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

    # Database settings
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'data/leads.db')

    # Bot settings
    SCRAPE_INTERVAL = int(os.environ.get('SCRAPE_INTERVAL', 60))  # seconds
    MAX_LEADS_PER_CHECK = int(os.environ.get('MAX_LEADS_PER_CHECK', 20))

    # Geographic settings
    SERVICE_RADIUS_MILES = int(os.environ.get('SERVICE_RADIUS_MILES', 35))
    CENTER_LAT = 39.1031  # Cincinnati center
    CENTER_LON = -84.5120

    # Priority thresholds
    HOT_LEAD_THRESHOLD = 75  # Priority score for hot leads
    MEDIUM_LEAD_THRESHOLD = 50  # Priority score for medium leads

    # Notification settings (optional)
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')
    NOTIFY_PHONE = os.environ.get('NOTIFY_PHONE', '')

    # Notification preferences
    NOTIFY_HOT_LEADS = os.environ.get('NOTIFY_HOT_LEADS', 'true').lower() == 'true'
    NOTIFY_MEDIUM_LEADS = os.environ.get('NOTIFY_MEDIUM_LEADS', 'false').lower() == 'true'

    # High-value zip codes (Tier 1)
    TIER_1_ZIPS = [
        '45040',  # Mason
        '45069',  # West Chester
        '45243',  # Indian Hill
        '45208',  # Hyde Park
        '41017',  # Ft. Mitchell
        '41091',  # Union
        '45140',  # Loveland
        '45039',  # Maineville
    ]

    # Volume area zip codes (Tier 2)
    TIER_2_ZIPS = [
        '45202',  # Downtown Cincy
        '41011',  # Covington
        '41071',  # Newport
        '41042',  # Florence
        '45236',  # Blue Ash
        '45241',  # Sharonville
        '45215',  # Glendale
        '45014',  # Fairfield
        '45011',  # Hamilton
    ]

    # High-value keywords
    HIGH_VALUE_KEYWORDS = [
        'garage cleanout',
        'estate cleanout',
        'moving debris',
        'construction waste',
        'hoarder',
        'eviction',
        'office furniture',
        'hot tub removal',
        'shed demolition',
        'basement cleanout',
        'attic cleanout',
        'full house cleanout',
        'multi-room',
        'tear down',
        'demo',
        'renovation debris',
        'property cleanout',
        'storage unit',
        'warehouse',
        'restaurant equipment'
    ]

    # Medium-value keywords
    MEDIUM_VALUE_KEYWORDS = [
        'junk removal',
        'furniture removal',
        'appliance removal',
        'debris removal',
        'haul away',
        'clean out',
        'remove junk',
        'dumpster',
        'trash removal',
        'old furniture'
    ]

    # Negative keywords (filter out)
    NEGATIVE_KEYWORDS = [
        'curbside',
        'free dirt',
        'scrap metal only',
        'single item',
        'donation pickup',
        'just one',
        'small job',
        'curb alert',
        'free to pick up',
        'willing to haul',
        'i can haul',
        'help me move'
    ]

    # Craigslist URLs
    CINCINNATI_CRAIGSLIST_URL = 'https://cincinnati.craigslist.org'
    NKY_CRAIGSLIST_URLS = [
        'https://lexington.craigslist.org',
        'https://cincinnati.craigslist.org/nky/'
    ]

    # User agents
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
