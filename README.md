# Business News Analyzer 📰

An AI-powered business news analysis tool using Claude AI and Tavily API.

## Features ✨

- 🤖 Advanced news analysis using Claude AI
- 📊 Interactive visualization of analysis results
- 💬 Chat interface for article Q&A
- 📈 Stock news tracking for major companies
- 🎯 Domain-specific article filtering
- 📱 Modern, responsive UI

## Installation 🚀

```bash
# Clone the repository
git clone https://github.com/Amitkhopade/newsanalyzer.git
cd newsanalyzer

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Configuration 🔧

Required API keys:
- ANTHROPIC_API_KEY (Claude AI)
- TAVILY_API_KEY (News Search)

Add these to your .env file.

## Usage 💻

```bash
streamlit run app/App.py
```

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request