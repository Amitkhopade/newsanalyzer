from typing import List, Dict, Any
from datetime import datetime
import os
import traceback
from anthropic import Anthropic

def save_message_content(content: str, filename: str) -> None:
    """Save the given content to a file."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs("analysis_output", exist_ok=True)
        filepath = os.path.join("analysis_output", filename)
        
        with open(filepath, "a", encoding="utf-8") as file:
            file.write(f"\n{'='*50}\n{datetime.now().isoformat()}\n{'='*50}\n")
            file.write(content + "\n")
        print(f"[save_message_content] Successfully saved analysis to {filepath}")
        return filepath
    except Exception as e:
        print(f"[save_message_content] Error saving analysis to file: {str(e)}")
        traceback.print_exc()
        return None

class NewsAnalyzer:
    def __init__(self):
        """Initialize News Analyzer with Claude"""
        print("[NewsAnalyzer] Initializing...")
        from config.settings import get_api_key
        api_key = get_api_key("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in configuration")
        self.client = Anthropic(api_key=api_key)
        print("[NewsAnalyzer] Initialized with Claude Sonnet")

    def analyze_articles(self, selected_articles: List[Dict[str, Any]], business_context: str) -> List[Dict[str, Any]]:
        """Analyze selected articles using Claude Sonnet"""
        print(f"[analyze_articles] Starting analysis of {len(selected_articles)} articles")
        results = []
        for idx, article in enumerate(selected_articles, 1):
            try:
                print(f"[analyze_articles] Processing article {idx}/{len(selected_articles)}")
                result = self.analyze_article(article, business_context)
                results.append(result)
                print(f"[analyze_articles] Successfully analyzed article {idx}")
            except Exception as e:
                print(f"[analyze_articles] Error analyzing article {idx}: {str(e)}")
                traceback.print_exc()
                continue
        return results

    def analyze_article(self, article: Dict[str, Any], business_context: str) -> Dict[str, Any]:
        """Analyze a single article using Claude Sonnet"""
        title = article.get('title', 'Untitled')
        content = article.get('content', '')
        
        print(f"[analyze_article] Starting analysis for: {title}")
        print(f"[analyze_article] Business context: {business_context}")

        try:
            # Create more detailed system prompt for richer analysis
            system_prompt = (
                f"Analyze this news article in the context of {business_context}. Provide:\n"
                "1. Overall sentiment (clearly state POSITIVE/NEGATIVE/NEUTRAL)\n"
                "2. Key facts and figures extracted from the article\n"
                "3. Main implications for the business/industry\n"
                "4. Strategic recommendations\n"
                "5. Key stakeholders mentioned\n"
                "6. Related industry trends\n"
                "Format the analysis in clear sections with markdown headings."
            )
            
            # Create message for Claude
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"News Article: {content}\nBusiness Context: {business_context}"
                            }
                        ]
                    }
                ]
            )
            
            # Extract and save analysis
            analysis_text = response.content[0].text
            print(f"[analyze_article] Got response length: {len(analysis_text)}")
            
            # Save to file with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"analysis_{timestamp}_{title[:30]}.txt"
            saved_path = save_message_content(analysis_text, filename)
            
            # Extract key information for chat context
            result = {
                'title': title,
                'source': article.get('source', 'Unknown'),
                'url': article.get('url', ''),
                'content': content,  # Include full content for chat context
                'analysis': analysis_text,
                'analysis_file': saved_path,
                'timestamp': datetime.now().isoformat(),
                'key_facts': [],  # Will be populated in future versions
                'sentiment': 'UNKNOWN'  # Will be populated in future versions
            }
            
            print(f"[analyze_article] Analysis complete for: {title}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"[analyze_article] Error during analysis: {error_msg}")
            traceback.print_exc()
            return {
                'title': title,
                'error': f"Analysis failed: {error_msg}",
                'source': article.get('source', 'Unknown'),
                'url': article.get('url', ''),
                'content': content  # Include content even if analysis fails
            }
