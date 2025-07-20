#!/usr/bin/env python3
"""
Quote generation service using LangChain and OpenAI
"""

import random
from typing import Dict, List
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate

from ..core.config import Config, Templates, HashtagPools
from ..models.schemas import QuoteRequest, AudienceType, ThemeType, FormatType
from ..utils.text_utils import ViralQuoteParser, ViralityCalculator, HashtagGenerator, CaptionBuilder

class QuoteGenerator:
    """Generate viral quotes using AI"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = OpenAI(
            openai_api_base=Config.OPENAI_API_BASE,
            openai_api_key=Config.OPENAI_API_KEY,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
        
        # Initialize utilities
        self.parser = ViralQuoteParser()
        self.hashtag_pools = [
            HashtagPools.POOLS,
            HashtagPools.GENERAL_HASHTAGS
        ]
        self.hashtag_generator = HashtagGenerator(
            hashtag_pools=HashtagPools.POOLS,
            general_hashtags=HashtagPools.GENERAL_HASHTAGS
        )
        self.caption_builder = CaptionBuilder(
            Templates.CAPTION_TEMPLATES,
            Templates.HOOK_OPTIONS
        )
        
        # Templates
        self.viral_templates = Templates.VIRAL_TEMPLATES
    
    def generate_quote(self, request: QuoteRequest) -> Dict[str, any]:
        """Generate a viral quote based on request parameters"""
        
        # Select format
        if request.format_preference == FormatType.mixed:
            format_type = random.choice([f.value for f in FormatType if f != FormatType.mixed])
        else:
            format_type = request.format_preference.value
            
        # Select theme
        if request.theme == ThemeType.mixed:
            theme = random.choice([t.value for t in ThemeType if t != ThemeType.mixed])
        else:
            theme = request.theme.value
            
        # Get template
        template = self.viral_templates.get(format_type, self.viral_templates["deep_quote"])
        
        # Create prompt
        prompt = PromptTemplate(
            input_variables=["audience", "theme", "custom_topic"],
            template=template
        )
        
        # Create chain using new syntax
        chain = prompt | self.llm | self.parser
        
        # Generate quote
        result = chain.invoke({
            "audience": request.audience.value,
            "theme": theme,
            "custom_topic": request.custom_topic or "life wisdom and personal growth"
        })
        
        # Extract title and quote
        title = result.get('title', 'Deep Thoughts')
        quote = result.get('quote', 'Every ending is a new beginning.')
        
        # Generate hashtags and caption
        hashtags = self.hashtag_generator.generate(theme, format_type)
        full_caption = self.caption_builder.build(title, quote, theme, hashtags)
        virality_score = ViralityCalculator.calculate_score(quote, theme, format_type)
        
        return {
            'title': title,
            'quote': quote,
            'full_caption': full_caption,
            'theme': theme,
            'format_type': format_type,
            'virality_score': virality_score,
            'hashtags': hashtags
        }
    
    def get_trending_combinations(self) -> List[Dict[str, any]]:
        """Get trending viral combinations"""
        return [
            {"audience": AudienceType.gen_z, "theme": ThemeType.relationships, "format": FormatType.painful_truth},
            {"audience": AudienceType.mixed, "theme": ThemeType.life_lessons, "format": FormatType.maturity_when},
            {"audience": AudienceType.gen_z, "theme": ThemeType.mental_health, "format": FormatType.not_everyone_understands},
            {"audience": AudienceType.mixed, "theme": ThemeType.success, "format": FormatType.realization},
        ]
