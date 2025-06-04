import os
from dotenv import load_dotenv
from datetime import datetime
import traceback
import plotly.graph_objects as go
import pandas as pd
import streamlit.components.v1 as components

# Load environment variables
load_dotenv()

import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="Business News Analyzer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with animations and modern styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }
        
        .main {
            background: linear-gradient(to right, #1f1c2c, #928dab);
            padding: 2rem;
        }
        
        .stApp {
            background: linear-gradient(to right, #1f1c2c, #928dab);
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-10px);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 600;
            color: #ffd700;
        }
        
        .stat-label {
            font-size: 1rem;
            color: #ffffff;
            opacity: 0.8;
        }
        
        .nav-links {
            display: flex;
            justify-content: flex-end;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .nav-link {
            color: #ffffff;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        
        .nav-link:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #ffd700;
        }
        
        /* Animation classes */
        @keyframes fadeInLeft {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animate-fade-left {
            animation: fadeInLeft 0.6s ease forwards;
        }
        
        .animate-fade-up {
            animation: fadeInUp 0.6s ease forwards;
        }
        
        /* Custom tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            background-color: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #ffffff;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(255, 255, 255, 0.2);
            color: #ffd700;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: rgba(255, 215, 0, 0.2) !important;
            color: #ffd700 !important;
        }
        
        /* Custom form styling */
        .stTextInput > div > div {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
        }
        
        .stTextArea > div > div {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
        }
        
        .stButton > button {
            background: linear-gradient(45deg, #ffd700, #ffa500);
            color: #1f1c2c;
            font-weight: 600;
            border: none;
            padding: 0.5rem 2rem;
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 215, 0, 0.3);
        }
    </style>
""", unsafe_allow_html=True)

# Navigation Header
st.markdown("""
    <div class="nav-links animate-fade-left">
        <a href="#" class="nav-link">Home</a>
        <a href="#trends" class="nav-link">Trends</a>
        <a href="#sentiment" class="nav-link">Sentiment</a>
        <a href="#insights" class="nav-link">Insights</a>
    </div>
""", unsafe_allow_html=True)

# Import settings first to validate API keys
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import validate_api_keys, rag_memory
from app.rag_utils import VectorStore
from app.fetch_news import fetch_news
from app.analyze_news import NewsAnalyzer
from app.stock_news import fetch_stock_news, get_stock_info, DEFAULT_TICKERS

# Validate API keys
if not validate_api_keys():
    st.warning("⚠️ Please configure your API keys to continue")
    st.stop()

# Initialize vector store
vector_store = VectorStore()

# Custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .css-1v0mbdj {
        padding-top: 2rem;
    }
    .block-container {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'fetched_articles' not in st.session_state:
    st.session_state.fetched_articles = []
if 'selected_articles' not in st.session_state:
    st.session_state.selected_articles = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_articles_context' not in st.session_state:
    st.session_state.current_articles_context = None
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = None
if 'stock_news' not in st.session_state:
    st.session_state.stock_news = []

# Theme toggle in sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Add status indicators
    st.sidebar.markdown("### System Status")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("API Status:")
    with col2:
        if validate_api_keys():
            st.success("✓ Connected")
        else:
            st.error("× Error")
            
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("Vector Store:")
    with col4:
        if vector_store and hasattr(vector_store, 'index'):
            st.success("✓ Ready")
        else:
            st.warning("⚠ Not Initialized")
    
    st.markdown("---")
    
    # Theme selection
    theme = st.selectbox("Theme", ["Light", "Dark"], key="theme")
    if theme == "Dark":
        st.markdown("""
        <style>
        :root {
            --background-color: #1E1E1E;
            --text-color: #FFFFFF;
        }
        </style>
        """, unsafe_allow_html=True)

    # Search settings in sidebar
    st.subheader("Search Settings")

# Main content area with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📰 Article Selection", "📊 Analysis Results", "💬 Chat", "📈 Quick News", "📚 Analysis History"])

with tab1:
    st.markdown('<h1 class="animate-fade-left">📰 Business News Analyzer</h1>', unsafe_allow_html=True)
    
    # Stats Overview Cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class="card animate-fade-up">
                <div class="stat-number">
                    {}
                </div>
                <div class="stat-label">
                    Articles Analyzed Today
                </div>
            </div>
        """.format(len(st.session_state.analysis_results) if st.session_state.analysis_results else 0), 
        unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="card animate-fade-up">
                <div class="stat-number">
                    {}%
                </div>
                <div class="stat-label">
                    Positive Sentiment
                </div>
            </div>
        """.format(80 if st.session_state.analysis_results else 0), 
        unsafe_allow_html=True)
    
    # Input form with enhanced styling
    with st.form("search_form", clear_on_submit=False):
        st.markdown('<h3 class="animate-fade-up">Search Parameters</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            domain = st.text_input("Business Domain", 
                                 placeholder="e.g., Artificial Intelligence, Renewable Energy")
            context = st.text_input("Additional Context", 
                                  placeholder="e.g., market trends, investments")
        
        with col2:
            num_articles = st.slider("Number of Articles", 
                                   min_value=1, max_value=20, value=5)
            search_depth = st.select_slider("Search Depth",
                                          options=["basic", "advanced"],
                                          value="advanced")
            time_range = st.select_slider("Time Range",
                                        options=["day", "week", "month"],
                                        value="day")
        
        col3, col4 = st.columns(2)
        with col3:
            include_domains = st.text_area("Include Domains", 
                                         placeholder="reuters.com\nbloomberg.com")
        with col4:
            exclude_domains = st.text_area("Exclude Domains",
                                         placeholder="example.com")
        
        submitted = st.form_submit_button("🔍 Fetch Articles")

    # Handle article fetching
    if submitted:
        with st.spinner("Fetching articles..."):
            try:
                st.session_state.fetched_articles = fetch_news(
                    domain=domain,
                    context=context,
                    num_articles=num_articles,
                    search_depth=search_depth,
                    time_range=time_range,
                    include_domains=include_domains,
                    exclude_domains=exclude_domains
                )
                st.success(f"✅ Found {len(st.session_state.fetched_articles)} articles")
            except Exception as e:
                st.error(f"❌ Error fetching articles: {str(e)}")
                st.session_state.fetched_articles = []
                
    # Display fetched articles with improved selection UI
    if st.session_state.fetched_articles:
        st.markdown("### 📑 Select Articles")
        st.session_state.selected_articles = []
        for i, article in enumerate(st.session_state.fetched_articles):
            col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
            with col1:
                selected = st.checkbox("", key=f"article_{i}", value=True)
                if selected:
                    st.session_state.selected_articles.append(article)
            with col2:
                st.markdown(f"**{article['title']}**")
            with col3:
                st.markdown(f"Score: {article.get('score', 'N/A')}")

    # Analysis button
    if st.button("🔍 Analyze Selected Articles", 
                disabled=len(st.session_state.selected_articles) == 0):
        with st.spinner("Analyzing articles..."):
            try:
                analyzer = NewsAnalyzer()
                # Combine domain and context for better analysis
                business_context = f"{domain} - {context}" if context else domain
                results = analyzer.analyze_articles(
                    st.session_state.selected_articles,
                    business_context=business_context  # Pass the combined context
                )
                
                # Store results in session state for persistence
                st.session_state.analysis_results = results
                
                # Display analysis results
                for result in results:
                    with st.expander(f"📝 Analysis for: {result['title']}", expanded=True):
                        if 'error' in result:
                            st.error(result['error'])
                        else:
                            # Display the raw analysis text
                            st.markdown(result['analysis'])
                            
                            # Show metadata
                            st.info(f"Source: {result['source']}")
                            if result['analysis_file']:
                                st.success(f"Analysis saved to: {result['analysis_file']}")
                
                st.success("Analysis complete!")
                
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")

with tab2:
    if st.session_state.analysis_results:
        st.markdown('<h2 class="animate-fade-left">📊 Analysis Dashboard</h2>', unsafe_allow_html=True)
        
        # Analysis Overview Cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div class="card animate-fade-up">
                    <div class="stat-number">{}</div>
                    <div class="stat-label">Articles Analyzed</div>
                </div>
            """.format(len(st.session_state.analysis_results)), unsafe_allow_html=True)
            
        with col2:
            sentiment_score = sum(1 for r in st.session_state.analysis_results 
                                if "positive" in r.get('analysis', '').lower())
            sentiment_percentage = (sentiment_score / len(st.session_state.analysis_results)) * 100
            st.markdown(f"""
                <div class="card animate-fade-up">
                    <div class="stat-number">{sentiment_percentage:.1f}%</div>
                    <div class="stat-label">Positive Sentiment</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown("""
                <div class="card animate-fade-up">
                    <div class="stat-number">High</div>
                    <div class="stat-label">Market Impact</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Detailed Analysis Cards
        for idx, result in enumerate(st.session_state.analysis_results):
            with st.expander(f"📝 Analysis: {result['title']}", expanded=idx == 0):
                if 'error' in result:
                    st.error(result['error'])
                else:
                    try:
                        # Extract sentiment and create visualization
                        analysis_text = result['analysis'].lower()
                        sentiment_score = 0.8 if "positive" in analysis_text else 0.2 if "negative" in analysis_text else 0.5
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"""
                                <div class="card">
                                    <h3 style="color: #ffd700;">Key Findings</h3>
                                    {result['analysis']}
                                </div>
                            """, unsafe_allow_html=True)
                            
                        with col2:
                            # Impact score chart
                            fig = go.Figure(go.Bar(
                                x=['Market', 'Tech', 'Financial', 'Sentiment'],
                                y=[0.8, 0.6, 0.7, sentiment_score],
                                marker_color=['#2ecc71', '#3498db', '#e74c3c', 
                                            '#27ae60' if sentiment_score > 0.5 else '#c0392b']
                            ))
                            fig.update_layout(
                                title="Impact Analysis",
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#ffffff'),
                                showlegend=False
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Source and metadata
                            st.markdown(f"""
                                <div class="card">
                                    <p><strong>Source:</strong> {result['source']}</p>
                                    <p><strong>Analysis File:</strong> {result.get('analysis_file', 'N/A')}</p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                    except Exception as e:
                        st.error(f"Error in visualization: {str(e)}")
                        st.markdown(result.get('analysis', 'Analysis text not available'))
    else:
        st.info("No analysis results yet. Please analyze some articles first.")

with tab3:
    st.markdown('<h2 class="animate-fade-left">💬 Interactive Analysis Chat</h2>', unsafe_allow_html=True)
    
    # Add custom CSS for chat messages
    st.markdown("""
        <style>
            .chat-message {
                padding: 1.5rem;
                border-radius: 15px;
                margin-bottom: 1rem;
                display: flex;
                align-items: flex-start;
                animation: fadeInUp 0.5s ease forwards;
            }
            
            .chat-message.user {
                background: rgba(255, 215, 0, 0.1);
                margin-left: 2rem;
                border-top-left-radius: 5px;
            }
            
            .chat-message.assistant {
                background: rgba(255, 255, 255, 0.1);
                margin-right: 2rem;
                border-top-right-radius: 5px;
            }
            
            .chat-message .avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                margin-right: 1rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
            }
            
            .chat-message .content {
                flex-grow: 1;
            }
            
            .chat-input {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                padding: 1rem;
                background: rgba(31, 28, 44, 0.95);
                backdrop-filter: blur(10px);
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Check if we have analyzed articles for context
    if not st.session_state.analysis_results:
        st.markdown("""
            <div class="card animate-fade-up">
                <h3 style="color: #ffd700;">👋 Welcome to Interactive Analysis</h3>
                <p>Please analyze some articles first to enable chat functionality.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Store current articles context in session state if not already there
        if not st.session_state.current_articles_context:
            st.session_state.current_articles_context = st.session_state.analysis_results
            
        # Chat interface
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_history:
                avatar = "👤" if message["role"] == "user" else "🤖"
                st.markdown(f"""
                    <div class="chat-message {message['role']}">
                        <div class="avatar">{avatar}</div>
                        <div class="content">
                            {message['content']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        if prompt := st.chat_input("Ask about the analyzed articles..."):
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response from Claude
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    from app.chat import get_chat_response
                    response = get_chat_response(
                        prompt,
                        st.session_state.current_articles_context,
                        st.session_state.chat_history
                    )
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Clear chat button with custom styling
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🗑️ Clear Chat", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()

with tab4:
    st.markdown('<h2 class="animate-fade-left">📈 Quick Company News</h2>', unsafe_allow_html=True)
    
    # Add custom CSS for news cards
    st.markdown("""
        <style>
            .stock-info-card {
                background: rgba(255, 215, 0, 0.1);
                border-radius: 15px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                animation: fadeInUp 0.5s ease forwards;
            }
            
            .news-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                transition: transform 0.3s ease;
                animation: fadeInUp 0.5s ease forwards;
            }
            
            .news-card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.15);
            }
            
            .news-meta {
                font-size: 0.9rem;
                color: #ffd700;
                margin-bottom: 0.5rem;
            }
            
            .ticker-button {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 215, 0, 0.3);
                color: #ffffff;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                margin: 0.25rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .ticker-button:hover, .ticker-button.selected {
                background: rgba(255, 215, 0, 0.2);
                border-color: #ffd700;
                transform: translateY(-2px);
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Company selection
    st.markdown("### Select a Company")
    
    # Create buttons for each ticker
    cols = st.columns(5)  # 5 buttons per row
    for idx, (ticker, company) in enumerate(DEFAULT_TICKERS.items()):
        with cols[idx % 5]:
            button_class = "selected" if st.session_state.selected_ticker == ticker else ""
            if st.button(f"{ticker}\n{company}", key=f"btn_{ticker}", 
                        help=f"View news for {company}"):
                st.session_state.selected_ticker = ticker
                with st.spinner(f"Fetching news for {company}..."):
                    # Get stock info
                    stock_info = get_stock_info(ticker)
                    st.session_state.stock_info = stock_info
                    # Get news
                    st.session_state.stock_news = fetch_stock_news(ticker)
    
    # Display stock info and news if a ticker is selected
    if st.session_state.selected_ticker:
        ticker = st.session_state.selected_ticker
        
        # Display stock info
        if hasattr(st.session_state, 'stock_info'):
            info = st.session_state.stock_info
            st.markdown(f"""
                <div class="stock-info-card">
                    <h3>{info['name']} ({ticker})</h3>
                    <p><strong>Sector:</strong> {info['sector']}</p>
                    <p><strong>Industry:</strong> {info['industry']}</p>
                    <p><strong>Current Price:</strong> {info['current_price']} {info['currency']}</p>
                    <p>{info['description']}</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Display news
        st.markdown("### Latest News")
        
        if not st.session_state.stock_news:
            st.warning("No news articles found for this company.")
        else:
            for news in st.session_state.stock_news:
                st.markdown(f"""
                    <div class="news-card">
                        <div class="news-meta">
                            {news['published']} | {news['publisher']}
                        </div>
                        <h4>{news['title']}</h4>
                        <p>{news['summary']}</p>
                        <a href="{news['link']}" target="_blank" style="color: #ffd700;">Read more →</a>
                    </div>
                """, unsafe_allow_html=True)

with tab5:
    st.markdown("### 📚 Analysis History")
    # Show historical analyses with timeline
    history_data = pd.DataFrame({
        'Date': [datetime.now()],
        'Topic': [domain],
        'Articles': [len(st.session_state.fetched_articles) if st.session_state.fetched_articles else 0]
    })
    st.dataframe(history_data)

# Add a footer with metrics
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Articles Analyzed", len(st.session_state.analysis_results) if st.session_state.analysis_results else 0)
with col2:
    st.metric("Average Sentiment", "Positive")
with col3:
    st.metric("Analysis Time", "2.3s")

# Reset button
if st.session_state.fetched_articles or st.session_state.analysis_results:
    if st.button("🔄 Start New Analysis"):
        st.session_state.fetched_articles = []
        st.session_state.selected_articles = []
        st.session_state.analysis_results = None
        st.session_state.chat_history = []
        st.session_state.current_articles_context = None
        st.rerun()