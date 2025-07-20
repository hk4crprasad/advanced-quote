#!/usr/bin/env python3
"""
Utility functions for text processing and analysis
"""

import re
import random
from typing import List, Dict
from langchain.schema import BaseOutputParser

class ViralQuoteParser(BaseOutputParser):
    """Custom output parser for structured quote generation"""
    
    def parse(self, text: str) -> Dict[str, str]:
        result = {}
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('TITLE:'):
                result['title'] = line.replace('TITLE:', '').strip()
            elif line.startswith('QUOTE:'):
                result['quote'] = line.replace('QUOTE:', '').strip()
        
        return result

class TextProcessor:
    """Text processing utilities"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,!?;:\'"()]', '', text)
        
        return text
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        if not text:
            return 0
        return len(text.split())
    
    @staticmethod
    def truncate_text(text: str, max_words: int) -> str:
        """Truncate text to maximum word count"""
        if not text:
            return ""
        
        words = text.split()
        if len(words) <= max_words:
            return text
        
        return ' '.join(words[:max_words]) + '...'
    
    @staticmethod
    def format_hashtags(hashtags: List[str], max_per_line: int = 5) -> str:
        """Format hashtags for social media"""
        if not hashtags:
            return ""
        
        lines = []
        current_line = ""
        
        for hashtag in hashtags:
            hashtag_with_symbol = f"#{hashtag}"
            
            if len(current_line.split()) >= max_per_line:
                if current_line:
                    lines.append(current_line.strip())
                current_line = hashtag_with_symbol + " "
            else:
                current_line += hashtag_with_symbol + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return "\n".join(lines)

class ViralityCalculator:
    """Calculate virality scores for quotes"""
    
    TRIGGER_WORDS = [
        "truth", "reality", "painful", "deep", "understand", "realize", 
        "mature", "never", "always", "everyone", "nobody", "secret",
        "hidden", "powerful", "change", "transform", "level"
    ]
    
    VIRAL_FORMATS = [
        "painful_truth", "not_everyone_understands", "maturity_when"
    ]
    
    VIRAL_THEMES = [
        "relationships", "life_lessons", "mental_health"
    ]
    
    @classmethod
    def calculate_score(cls, quote: str, theme: str, format_type: str) -> int:
        """Calculate potential virality score based on quote characteristics"""
        score = 70  # Base score
        
        # Length bonus (shorter is better for viral content)
        word_count = len(quote.split())
        if word_count <= 15:
            score += 15
        elif word_count <= 25:
            score += 10
        else:
            score -= 5
            
        # Format bonus
        if format_type in cls.VIRAL_FORMATS:
            score += 10
            
        # Theme bonus
        if theme in cls.VIRAL_THEMES:
            score += 5
            
        # Emotional trigger words
        quote_lower = quote.lower()
        for word in cls.TRIGGER_WORDS:
            if word in quote_lower:
                score += 3
                
        return min(score, 100)  # Cap at 100

class HashtagGenerator:
    """Generate relevant hashtags for content"""
    
    def __init__(self, hashtag_pools: Dict[str, List[str]], general_hashtags: List[str]):
        self.hashtag_pools = hashtag_pools
        self.general_hashtags = general_hashtags
    
    def generate(self, theme: str, format_type: str, count: int = 18) -> List[str]:
        """Generate relevant hashtags"""
        # Get theme-specific hashtags
        theme_tags = self.hashtag_pools.get(theme, self.hashtag_pools.get("motivation", []))
        
        # Select theme hashtags
        selected_theme_tags = random.sample(theme_tags, min(10, len(theme_tags)))
        
        # Add general hashtags
        selected_general_tags = random.sample(self.general_hashtags, min(6, len(self.general_hashtags)))
        
        # Add some bonus viral hashtags
        bonus_tags = ["reels", "instaquotes", "dailyquotes", "wisdom"]
        
        # Combine and ensure we have the right count
        all_hashtags = selected_theme_tags + selected_general_tags + bonus_tags
        
        return all_hashtags[:count]

class CaptionBuilder:
    """Build complete captions with call-to-action, quote, and hashtags"""
    
    def __init__(self, caption_templates: List[str], hook_options: List[str]):
        self.caption_templates = caption_templates
        self.hook_options = hook_options
    
    def build(self, title: str, quote: str, theme: str, hashtags: List[str]) -> str:
        """Generate complete caption"""
        # Select random options
        cta = random.choice(self.caption_templates)
        hook = random.choice(self.hook_options)
        
        # Create the full caption
        full_caption = f'{cta}\n\n"{title}" - {hook}\n\n'
        
        # Add formatted hashtags
        hashtag_section = TextProcessor.format_hashtags(hashtags[:18])
        
        # Combine everything
        full_caption += hashtag_section
        
        return full_caption
