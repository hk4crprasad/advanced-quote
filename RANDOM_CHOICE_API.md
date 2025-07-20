# Random Choice API Documentation

## Overview
The Random Choice API provides a simple endpoint to select ONE random choice from a list of options.

## Endpoint
```
POST /random-choice
```

## Request Schema
```json
{
  "choices": ["option1", "option2", "option3", ...]
}
```

## Response Schema
```json
{
  "choices": ["option1", "option2", "option3"],
  "selected": "option2",
  "timestamp": "2025-07-20T10:30:00.123456"
}
```

## Usage Examples

### Example 1: Choose 1 anime style
**Request:**
```json
{
  "choices": ["anime", "anime1", "paper", "modern", "minimal"]
}
```

**Response:**
```json
{
  "choices": ["anime", "anime1", "paper", "modern", "minimal"],
  "selected": "anime1",
  "timestamp": "2025-07-20T10:30:00.123456"
}
```

### Example 2: Choose a theme
**Request:**
```json
{
  "choices": ["motivation", "relationships", "success", "life_lessons", "business"]
}
```

**Response:**
```json
{
  "choices": ["motivation", "relationships", "success", "life_lessons", "business"],
  "selected": "relationships",
  "timestamp": "2025-07-20T10:30:00.123456"
}
```

### Example 3: Simple yes/no choice
**Request:**
```json
{
  "choices": ["yes", "no"]
}
```

**Response:**
```json
{
  "choices": ["yes", "no"],
  "selected": "yes",
  "timestamp": "2025-07-20T10:30:00.123456"
}
```

## Error Handling

### Empty choices list
**Status:** 400 Bad Request
```json
{
  "detail": "Choices list cannot be empty"
}
```

## Features
- ✅ Simple one random choice selection
- ✅ Input validation and error handling
- ✅ Timestamp for each selection
- ✅ Returns both original choices and selected item
- ✅ Works with any number of input choices

## Use Cases
- Random style selection for image generation
- Random theme selection for content
- Simple decision making
- A/B testing option selection
- Quick choice from multiple options
