"""Chat functionality for the Business News Analyzer."""
from typing import List, Dict, Any
from anthropic import Anthropic
from datetime import datetime
from config.settings import get_api_key

def get_chat_response(user_message: str, articles_context: List[Dict[str, Any]], chat_history: List[Dict[str, Any]]) -> str:
    """Get a response from Claude for a chat message with article context.
    
    Args:
        user_message: The user's chat message
        articles_context: List of analyzed articles for context
        chat_history: List of previous chat messages
        
    Returns:
        Claude's response text
    """
    try:
        # Initialize Claude client
        api_key = get_api_key("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in configuration")
        client = Anthropic(api_key=api_key)
        
        # Prepare article context
        articles_text = "\n\n".join([
            f"Article: {article['title']}\n"
            f"Content: {article['content']}\n"
            f"Analysis: {article.get('analysis', 'No analysis available')}"
            for article in articles_context
        ])
        
        # Prepare chat history context
        history_text = ""
        if chat_history:
            history_text = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                for msg in chat_history[-5:]  # Include last 5 messages for context
            ])
        
        # Create the system prompt
        system_prompt = (
            "You are an AI assistant helping to analyze business news articles. "
            "You have access to article content and previous analyses. "
            "Provide clear, concise answers based on the article information. "
            "If information is not in the articles, acknowledge this and provide general business insights instead."
        )
        
        # Get response from Claude
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            temperature=0.7,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Using the following articles and chat history as context, "
                            f"please answer this question: {user_message}\n\n"
                            f"Previous chat context:\n{history_text}\n\n"
                            f"Article context:\n{articles_text}"
                        )
                    }
                ]
            }]
        )
        
        return response.content[0].text
        
    except Exception as e:
        return f"Error getting chat response: {str(e)}"
