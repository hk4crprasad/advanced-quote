#!/usr/bin/env python3
"""
Test script for the random choice API endpoint
"""

import sys
import json
sys.path.append('/home/cp/advanced-quote')

from src.models.schemas import RandomChoiceRequest, RandomChoiceResponse

def test_random_choice_api():
    """Test the random choice functionality"""
    print("🎲 Testing Random Choice API")
    print("=" * 50)
    
    # Test case 1: Simple random choice
    print("\n📝 Test 1: Choose 1 from 5 anime styles")
    choices1 = ["anime", "anime1", "paper", "modern", "minimal"]
    request1 = RandomChoiceRequest(choices=choices1, count=1)
    print(f"Choices: {request1.choices}")
    print(f"Count: {request1.count}")
    
    # Test case 2: Multiple random choices
    print("\n📝 Test 2: Choose 3 from 5 themes")
    choices2 = ["motivation", "relationships", "success", "life_lessons", "business"]
    request2 = RandomChoiceRequest(choices=choices2, count=3)
    print(f"Choices: {request2.choices}")
    print(f"Count: {request2.count}")
    
    # Test case 3: Edge case - choose all
    print("\n📝 Test 3: Choose all from a small list")
    choices3 = ["option1", "option2"]
    request3 = RandomChoiceRequest(choices=choices3, count=2)
    print(f"Choices: {request3.choices}")
    print(f"Count: {request3.count}")
    
    print("\n✅ All test cases created successfully!")
    print("📡 Ready to test with actual API calls")

if __name__ == "__main__":
    test_random_choice_api()
