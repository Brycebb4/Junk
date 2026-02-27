# Lead Filtering Logic for CincyJunkBot
# Processes raw leads and determines priority/value

import re
from datetime import datetime
from config import Config

class LeadFilter:
    """Filters and qualifies leads based on various criteria"""

    def __init__(self):
        self.config = Config()

    def process(self, raw_lead):
        """Process a raw lead and return qualified lead with metadata"""

        # Combine text for analysis
        text = f"{raw_lead.get('title', '')} {raw_lead.get('description', '')}".lower()

        # Check negative keywords first
        if self._has_negative_keyword(text):
            return None

        # Detect keywords
        detected_keywords = self._detect_keywords(text)

        # Check geographic eligibility
        location = raw_lead.get('location', '')
        if not self._is_in_service_area(location):
            return None

        # Estimate value
        estimated_value = self._estimate_value(detected_keywords, text)
        if estimated_value == 'Under $175':
            return None

        # Calculate priority score
        priority_score = self._calculate_priority_score(
            detected_keywords,
            estimated_value,
            location,
            raw_lead.get('posted_time', '')
        )

        # Build qualified lead
        qualified_lead = {
            'source': raw_lead.get('source', 'unknown'),
            'source_url': raw_lead.get('source_url', ''),
            'title': raw_lead.get('title', ''),
            'description': raw_lead.get('description', ''),
            'location': location,
            'keywords_detected': detected_keywords,
            'estimated_value': estimated_value,
            'priority_score': priority_score,
            'posted_time': raw_lead.get('posted_time', datetime.now().isoformat()),
            'discovered_time': raw_lead.get('discovered_time', datetime.now().isoformat()),
            'status': 'new',
            'notes': ''
        }

        return qualified_lead

    def _has_negative_keyword(self, text):
        """Check if lead contains negative keywords"""
        for keyword in self.config.NEGATIVE_KEYWORDS:
            if keyword.lower() in text:
                return True
        return False

    def _detect_keywords(self, text):
        """Detect relevant keywords in the text"""
        detected = []

        # Check high-value keywords
        for keyword in self.config.HIGH_VALUE_KEYWORDS:
            if keyword.lower() in text:
                detected.append(keyword)

        # Check medium-value keywords
        for keyword in self.config.MEDIUM_VALUE_KEYWORDS:
            if keyword.lower() in text and keyword not in detected:
                detected.append(keyword)

        return detected

    def _is_in_service_area(self, location):
        """Check if location is in service area"""
        location_lower = location.lower()

        # Extract zip code if present
        zip_match = re.search(r'\b(\d{5})\b', location)
        if zip_match:
            zip_code = zip_match.group(1)
            if zip_code in self.config.TIER_1_ZIPS:
                return True
            if zip_code in self.config.TIER_2_ZIPS:
                return True

        # Check for known city names
        tier1_cities = ['mason', 'west chester', 'indian hill', 'hyde park', 'fort mitchell', 'union', 'loveland', 'maineville']
        tier2_cities = ['cincinnati', 'covington', 'newport', 'florence', 'blue ash', 'sharonville', 'fairfield', 'hamilton', 'ft mitchell']

        for city in tier1_cities:
            if city in location_lower:
                return True

        for city in tier2_cities:
            if city in location_lower:
                return True

        return False

    def _estimate_value(self, keywords, text):
        """Estimate the value of the job based on keywords"""
        high_value_count = sum(1 for kw in keywords if kw in self.config.HIGH_VALUE_KEYWORDS)

        # Check for volume indicators
        volume_indicators = [
            'full house', 'entire home', 'whole house', 'multi-room',
            'full garage', 'full basement', 'full attic',
            'estate', 'hoarder', 'construction', 'renovation',
            'everything must go', 'entire contents'
        ]

        volume_score = sum(1 for indicator in volume_indicators if indicator in text)

        # Check for heavy items
        heavy_items = ['hot tub', 'piano', 'pool table', 'safe', 'marble', 'granite']
        has_heavy = any(item in text for item in heavy_items)

        # Determine value range
        if high_value_count >= 2 or volume_score >= 2 or has_heavy:
            return '$500+'
        elif high_value_count >= 1 or volume_score >= 1:
            return '$300-$500'
        elif any(keywords):  # Has at least some relevant keywords
            return '$175-$300'
        else:
            return 'Under $175'

    def _calculate_priority_score(self, keywords, estimated_value, location, posted_time):
        """Calculate priority score (0-100)"""
        score = 0

        # Base score from estimated value
        value_scores = {
            '$500+': 40,
            '$300-$500': 30,
            '$175-$300': 20,
            'Under $175': 0
        }
        score += value_scores.get(estimated_value, 0)

        # Keyword bonuses
        score += min(len(keywords) * 10, 30)  # Up to 30 points for keywords

        # Location bonus (Tier 1 areas get bonus)
        location_lower = location.lower()
        for zip_code in self.config.TIER_1_ZIPS:
            if zip_code in location:
                score += 15
                break

        # Urgency bonus (posts with time-sensitive language)
        urgency_words = ['asap', 'urgent', 'today', 'this week', 'deadline', 'moving']
        if any(word in location_lower for word in urgency_words):
            score += 10

        # Recency bonus (posts from today get bonus)
        try:
            if posted_time:
                posted = datetime.fromisoformat(posted_time.replace('Z', '+00:00'))
                hours_old = (datetime.now() - posted.replace(tzinfo=None)).total_seconds() / 3600
                if hours_old < 1:
                    score += 10
                elif hours_old < 6:
                    score += 5
        except:
            pass

        return min(score, 100)  # Cap at 100
