"""
Polymarket Whale Tracker - SIMPLE & CLEAN VERSION (Visuals Improved & Interaction Enhanced)
"""

import streamlit as st
import requests
import re
import time
import pandas as pd
import numpy as np
from typing import Optional, List, Dict
import urllib.parse
import altair as alt # Import altair for interactive charts

# ===== PAGE SETUP =====
# Use a dark theme for a sleek, modern look, and a wider layout.
st.set_page_config(
    page_title="Polymarket Top Holders Tracker", 
    page_icon="💰", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ===== ENHANCED STYLING (Dark Theme & Typography) =====
st.markdown("""
<style>
    /* Import Professional Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .main { 
        /* Slightly deeper blue gradient for a more premium look */
        background: linear-gradient(135deg, #070a1a 0%, #101426 100%); 
        color: #e4e7eb;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Remove Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typography Hierarchy */
    h1 { 
        color: #ffffff !important;
        font-weight: 800 !important; /* Bolded more */
        font-size: 3rem !important; /* Slightly larger */
        letter-spacing: -1.5px !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 { 
        color: #f0f2f5 !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        letter-spacing: -0.75px !important;
        margin-top: 2.5rem !important;
    }
    
    h3 { 
        color: #d1d5db !important;
        font-weight: 600 !important;
        font-size: 1.5rem !important; /* Slightly larger */
        margin-top: 2rem !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stRadio > label { /* Target radio labels for interaction */
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-size: 0.95rem !important;
        padding: 0.75rem !important;
        transition: all 0.2s ease !important;
        margin-bottom: 0.5rem; /* Spacing for radio buttons */
    }

    /* Radio Button Focus/Hover */
    .stRadio > label:hover {
        background-color: rgba(99, 102, 241, 0.1) !important;
        border-color: #6366f1 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }
    
    .stTextInput label, .stSelectbox label, .stRadio label {
        color: #d1d5db !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Primary Button - Same good style */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
    }
    
    /* Metric Card Enhancements */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    /* DataFrames */
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: rgba(255, 255, 255, 0.02) !important;
    }
    
    /* Table Headers */
    .stDataFrame thead tr th {
        background: rgba(99, 102, 241, 0.2) !important; /* Slightly darker header */
        color: #ffffff !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.75px !important;
        padding: 1rem !important;
        border-bottom: 2px solid rgba(99, 102, 241, 0.4) !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
    }
    
    /* Alert/Info Boxes for Verdict */
    div[data-testid="stStatusContainer"] {
        border-left: 4px solid #6366f1;
        background-color: rgba(99, 102, 241, 0.1);
        padding: 1rem;
        border-radius: 8px;
    }

</style>
""", unsafe_allow_html=True)

st.title("💰 Polymarket Whale Tracker")
st.write("Track and analyze the top traders in any Polymarket prediction market. Identify smart money patterns and profitable positions.")
st.divider()

# ===== CORE FUNCTIONS (API functions) =====

def extract_slug(url: str) -> Optional[str]:
    match = re.search(r'polymarket\.com/event/([^?#/]+)', url)
    return match.group(1) if match else None

def fetch_market_data(slug: str):
    url = f"https://gamma-api.polymarket.com/events?slug={slug}"
    # Use st.cache_data for this as it's static per slug
    return requests.get(url).json()[0]

def fetch_holders(condition_id: str):
    url = f"https://data-api.polymarket.com/holders?market={condition_id}&limit=20&sort=shares&order=desc"
    return requests.get(url).json()

def fetch_user_positions(wallet: str, condition_id: str):
    url = f"https://data-api.polymarket.com/positions?user={wallet}&market={condition_id}"
    try:
        return requests.get(url, timeout=5).json()
    except:
        return []

def fetch_profit_leaderboard(wallet: str) -> Optional[float]:
    try:
        data = requests.get(f"https://lb-api.polymarket.com/profit?user={wallet}", timeout=5).json()
        return float(data.get('profit')) if data and 'profit' in data else None
    except:
        return None

def scrape_pnl(wallet: str) -> Optional[float]:
    # Placeholder for brevity - full implementation from source is assumed.
    try:
        html = requests.get(f"https://polymarket.com/profile/{wallet}", timeout=10).text
        
        # Strategy 1: Look for Profit/Loss
        match = re.search(r'Profit/Loss[^$]*?([\u2212\-])?\s*\$\s*([\d,]+\.[\d]{2})', html)
        if match:
            sign, number = match.groups()
            value = float(number.replace(',', ''))
            return -value if sign in ['\u2212', '-'] else value
        
        # Strategy 2: Context
        sections = html.split('Profit/Loss')
        if len(sections) > 1:
            section = sections[1][:600]
            is_neg = any(x in section.lower() for x in ['text-red', 'negative', 'loss'])
            is_neg = is_neg or '\u2212' in section[:100] or re.search(r'-\s*\$', section[:100])
            match = re.search(r'\$\s*([\d,]+\.[\d]{2})', section)
            if match:
                value = float(match.group(1).replace(',', ''))
                return -value if is_neg else value
        return None
    except:
        return None

def get_pnl(wallet: str) -> Optional[float]:
    pnl = fetch_profit_leaderboard(wallet)
    return pnl if pnl is not None else scrape_pnl(wallet)

def enrich_holder(holder: dict, condition_id: str) -> dict:
    wallet = holder.get('proxyWallet')
    if not wallet:
        return None
    
    positions = fetch_user_positions(wallet, condition_id)
    outcome_index = holder.get('outcomeIndex', 0)
    
    position = next((p for p in positions if p.get('outcomeIndex') == outcome_index), None)
    if not position:
        return None
    
    shares = float(position.get('size', 0))
    avg_price = float(position.get('avgPrice', 0))
    current_price = float(position.get('curPrice', 0))
    current_value = float(position.get('currentValue', 0))
    initial_value = float(position.get('initialValue', 0))
    
    return {
        'Name': holder.get('name') or wallet[:10],
        'Shares': int(shares),
        'Entry': avg_price,
        'Current': current_price,
        'Value': int(current_value),
        'Market P&L': int(current_value - initial_value),
        'All-Time P&L': get_pnl(wallet)
    }

# ===== CUSTOM FORMATTING FUNCTIONS for DataFrame Styling (Kept) =====

def format_pnl_style(val):
    """Applies CSS class for P&L based on value."""
    if pd.isna(val):
        return 'color: #8b949e' # Gray for N/A
    if val > 0:
        return 'color: #38b449; font-weight: bold' # Green
    elif val < 0:
        return 'color: #f85149; font-weight: bold' # Red
    else:
        return 'color: #c9d1d9' # White/Neutral

# --- Helper function for displaying results ---
def display_results(df: pd.DataFrame, title: str, color_code: str):
    """Reusable function to display a holder section with enhanced metrics."""
    st.header(f"{color_code} {title}")
    
    # Metrics in a container for better grouping
    with st.container(border=True):
        st.markdown("#### Key Position Metrics")
        col1, col2, col3 = st.columns(3)
        avg_pnl = df['All-Time P&L'].mean()
        
        col1.metric("**Average All-Time P&L**", 
                    f"${avg_pnl:,.0f}" if pd.notna(avg_pnl) else "N/A", 
                    delta_color="off") 
        col2.metric("**Total Position Value**", f"${df['Value'].sum():,}")
        
        # Calculate Volume-Weighted Average Price (VWAP) for Entry
        total_shares = df['Shares'].sum()
        if total_shares > 0:
            avg_entry = (df['Shares'] * df['Entry']).sum() / total_shares
            col3.metric("**Volume-Weighted Avg Entry**", f"${avg_entry:.3f}")
        else:
            col3.metric("**Volume-Weighted Avg Entry**", "N/A")

    # Apply custom styling to the DataFrame
    table_height = len(df) * 35 + 38
    
    st.dataframe(
        df.style.format({
            'Shares': '{:,}',
            'Entry': '${:.3f}',
            'Current': '${:.3f}',
            'Value': '${:,}',
            # Ensure P&L formatting is correct for display
            'Market P&L': lambda x: f'${x:,}',
            'All-Time P&L': lambda x: f'${x:,.0f}' if pd.notna(x) else 'N/A'
        })
        .applymap(format_pnl_style, subset=['Market P&L', 'All-Time P&L'])
        .set_properties(**{'background-color': '#161b22', 'color': '#c9d1d9'}),
        use_container_width=True,
        hide_index=True,
        height=table_height
    )
    
# ===== MAIN APP (Updated for better interaction) =====

# Initialize session state for URL and market selection
if 'current_url' not in st.session_state:
    st.session_state['current_url'] = ""
# FIX: Initialize 'market_data' to an empty dictionary instead of None.
if 'market_data' not in st.session_state:
    st.session_state['market_data'] = {}
if 'selected_market_index' not in st.session_state:
    st.session_state['selected_market_index'] = 0

url = st.text_input(
    "🔗 Polymarket Event URL:", 
    value=st.session_state['current_url'],
    placeholder="https://polymarket.com/event/..."
)

# Function to clear analysis data
def clear_analysis_data():
    for key in ['analysis_yes_data', 'analysis_no_data', 'analysis_slug', 'analysis_market_title']:
        if key in st.session_state:
            del st.session_state[key]
    # FIX: Reset 'market_data' to an empty dictionary instead of None.
    st.session_state['market_data'] = {} 
    st.session_state['selected_market_index'] = 0 # Reset selection index

# Update session state when URL changes
if url != st.session_state['current_url']:
    st.session_state['current_url'] = url
    clear_analysis_data()
    # Rerun to fetch new market data
    st.rerun()

if url:
    slug = extract_slug(url)
    if not slug:
        st.error("❌ Invalid URL. Please ensure it starts with `https://polymarket.com/event/`")
        st.stop()
    
    # The problematic line now works because st.session_state['market_data'] is guaranteed to be a dictionary or empty dictionary.
    if st.session_state.get('market_data', {}).get('slug') != slug: 
        try:
            with st.status("🚀 Loading market details...", expanded=True) as status:
                market_data = fetch_market_data(slug)
                st.session_state['market_data'] = market_data
                status.update(label=f"✅ Market Data Loaded: **{market_data.get('title')}**", state="complete", expanded=False)
        except Exception as e:
            st.error(f"Failed to fetch market data. Ensure the URL is correct and the market is active. Error: {e}")
            st.stop()
    
    market_data = st.session_state['market_data']
    st.subheader(f"✅ Event: **{market_data.get('title')}**")
    
    markets = [m for m in market_data.get('markets', []) if m.get('enableOrderBook')]
    if not markets:
        st.warning("No yes/no markets found in this event.")
        st.stop()
    
    st.markdown("### 🎯 Select Market to Analyze")
    
    # --- Interactive Selection Enhancement ---
    options = [m.get('question', f'Market {i}') for i, m in enumerate(markets, 1)]
    
    # Use st.radio for a more interactive selection (better than selectbox for few options)
    selected_question = st.radio(
        "Choose a market question:", 
        options,
        index=st.session_state['selected_market_index'], # Controlled by state
        key="market_radio",
        label_visibility="collapsed",
        horizontal=True
    )
    
    idx = options.index(selected_question)
    st.session_state['selected_market_index'] = idx
    selected = markets[idx]
    
    st.markdown("---")

    # --- Analysis Trigger ---
    if st.button(f"🔍 ANALYZE HOLDERS for: **{selected_question}**", type="primary", use_container_width=True):
        
        # Clear previous run's analysis data only, not the market data
        for key in ['analysis_yes_data', 'analysis_no_data']:
            if key in st.session_state:
                del st.session_state[key]
                
        condition_id = selected.get('conditionId')
        
        with st.status("🔄 **Analyzing Holders...**", expanded=True) as status_box:
            status_box.write("🎣 Fetching top holders for YES and NO outcomes...")
            try:
                holders_data = fetch_holders(condition_id)
            except Exception as e:
                st.error(f"Failed to fetch holder data: {e}")
                status_box.update(label="❌ Analysis Failed", state="error")
                st.stop()
        
            yes_raw, no_raw = [], []
            for outcome in holders_data:
                holders = outcome.get('holders', [])
                if holders:
                    # Outcome index 0 is typically YES
                    if holders[0].get('outcomeIndex') == 0:
                        yes_raw = holders[:15]
                    else: # Assuming only two outcomes: YES (0) and NO (1)
                        no_raw = holders[:15]
            
            # Combined analysis section
            status_box.write("Fetching position data and all-time P&L for all holders...")
            
            total_holders = len(yes_raw) + len(no_raw)
            progress_bar = st.progress(0, text="Starting analysis...")
            
            yes_data = []
            no_data = []
            current_holder = 0
            
            # Analyze YES holders
            for i, h in enumerate(yes_raw):
                current_holder += 1
                holder_name = h.get('name') or h.get('proxyWallet', 'Unknown')[:10]
                percentage = int((current_holder / total_holders) * 100)
                progress_bar.progress(current_holder/total_holders, 
                                    text=f"🟢 Progress: {percentage}% - Analyzing YES Holder: {holder_name} ({i+1}/{len(yes_raw)})")
                
                enriched = enrich_holder(h, condition_id)
                if enriched:
                    yes_data.append(enriched)
                time.sleep(0.05) # Reduced sleep for faster feel
            
            # Analyze NO holders
            for i, h in enumerate(no_raw):
                current_holder += 1
                holder_name = h.get('name') or h.get('proxyWallet', 'Unknown')[:10]
                percentage = int((current_holder / total_holders) * 100)
                progress_bar.progress(current_holder/total_holders, 
                                    text=f"🔴 Progress: {percentage}% - Analyzing NO Holder: {holder_name} ({i+1}/{len(no_raw)})")
                
                enriched = enrich_holder(h, condition_id)
                if enriched:
                    no_data.append(enriched)
                time.sleep(0.05)
            
            # Clear progress indicators
            progress_bar.empty()
            
            # Store data in session state for display
            st.session_state['analysis_yes_data'] = yes_data
            st.session_state['analysis_no_data'] = no_data
            st.session_state['analysis_slug'] = slug
            st.session_state['analysis_market_title'] = market_data.get('title')
            
            status_box.update(label="✅ Analysis Complete!", state="complete", expanded=False)


    # --- Display Results Section (Moved outside the button block to persist display) ---
    
    if st.session_state.get('analysis_yes_data') or st.session_state.get('analysis_no_data'):
        
        st.markdown("## Analysis Results")
        
        yes_data = st.session_state['analysis_yes_data']
        no_data = st.session_state['analysis_no_data']

        # Display YES results
        if yes_data:
            df_yes = pd.DataFrame(yes_data)
            display_results(df_yes, f"YES Holders (Top {len(df_yes)})", "🟢")
            
            csv_yes = df_yes.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download YES Holders CSV",
                data=csv_yes,
                file_name=f"polymarket_yes_holders_{slug}.csv",
                mime="text/csv",
                key='dl_yes'
            )
        else:
            st.warning("No significant YES holders found.")
        
        st.markdown("##")
        st.markdown("---")
        st.markdown("##")
        
        # Display NO results
        if no_data:
            df_no = pd.DataFrame(no_data)
            display_results(df_no, f"NO Holders (Top {len(df_no)})", "🔴")
            
            csv_no = df_no.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download NO Holders CSV",
                data=csv_no,
                file_name=f"polymarket_no_holders_{slug}.csv",
                mime="text/csv",
                key='dl_no'
            )
        else:
            st.warning("No significant NO holders found.")
        
        # ===== COMPARISON SECTION & VISUALIZATION =====
        if yes_data and no_data:
            st.markdown("##")
            st.markdown("---")
            st.header("⚖️ YES vs NO Comparison Dashboard")
            
            # Calculate Summary Metrics
            yes_avg_pnl = df_yes['All-Time P&L'].mean()
            yes_total_value = df_yes['Value'].sum()
            yes_total_shares = df_yes['Shares'].sum()
            yes_avg_entry = (df_yes['Shares'] * df_yes['Entry']).sum() / yes_total_shares if yes_total_shares > 0 else 0
            profitable_yes = len(df_yes[df_yes['All-Time P&L'] > 0])
            total_yes = len(df_yes[df_yes['All-Time P&L'].notna()])
            yes_win_rate = (profitable_yes / total_yes) * 100 if total_yes > 0 else np.nan
            
            no_avg_pnl = df_no['All-Time P&L'].mean()
            no_total_value = df_no['Value'].sum()
            no_total_shares = df_no['Shares'].sum()
            no_avg_entry = (df_no['Shares'] * df_no['Entry']).sum() / no_total_shares if no_total_shares > 0 else 0
            profitable_no = len(df_no[df_no['All-Time P&L'] > 0])
            total_no = len(df_no[df_no['All-Time P&L'].notna()])
            no_win_rate = (profitable_no / total_no) * 100 if total_no > 0 else np.nan

            
            # --- Interactive Visualizations (Altair) ---
            
            comparison_df = pd.DataFrame({
                'Side': ['YES', 'NO'],
                'Avg_PNL': [yes_avg_pnl, no_avg_pnl],
                'Total_Capital': [yes_total_value, no_total_value],
                'Win_Rate': [yes_win_rate, no_win_rate]
            }).fillna(0) # Fill NaN for chart compatibility

            st.markdown("### Capital and Profitability Overview")
            chart_col1, chart_col2 = st.columns(2)
            
            # Chart 1: Total Capital
            base_capital = alt.Chart(comparison_df).encode(
                x=alt.X('Total_Capital', title='Total Capital ($)', axis=alt.Axis(format='$,.0f')),
                y=alt.Y('Side', title=None),
                tooltip=['Side', alt.Tooltip('Total_Capital', format='$,.0f')]
            )
            chart_capital = base_capital.mark_bar(opacity=0.8, cornerRadiusEnd=4).encode(
                color=alt.Color('Side', scale=alt.Scale(domain=['YES', 'NO'], range=['#38b449', '#f85149'])),
            ).properties(title="Total Capital Deployed")
            
            with chart_col1:
                st.altair_chart(chart_capital, use_container_width=True)
                
            # Chart 2: Average All-Time P&L
            base_pnl = alt.Chart(comparison_df).encode(
                x=alt.X('Avg_PNL', title='Avg All-Time P&L ($)', axis=alt.Axis(format='$,.0f')),
                y=alt.Y('Side', title=None),
                color=alt.Color('Side', scale=alt.Scale(domain=['YES', 'NO'], range=['#38b449', '#f85149'])),
                tooltip=['Side', alt.Tooltip('Avg_PNL', format='$,.0f')]
            )
            # Use conditional color for P&L to show profitability direction
            chart_pnl = base_pnl.mark_bar(opacity=0.8, cornerRadiusEnd=4).encode(
                color=alt.condition(
                    alt.datum.Avg_PNL < 0,
                    alt.value('#f85149'),  # Red for negative
                    alt.value('#38b449')   # Green for positive
                )
            ).properties(title="Average All-Time Trader Profitability")

            with chart_col2:
                st.altair_chart(chart_pnl, use_container_width=True)

            # --- Verdict ---
            st.markdown("### 🧠 Smart Money Verdict")
            
            if pd.notna(yes_avg_pnl) and pd.notna(no_avg_pnl):
                if yes_avg_pnl > no_avg_pnl:
                    diff = yes_avg_pnl - no_avg_pnl
                    st.info(f"💡 **Smart Money Indicator:** YES holders are more profitable on average (+${diff:,.0f} vs NO). Their average trader P&L is **{f'${yes_avg_pnl:,.0f}'}**.")
                elif no_avg_pnl > yes_avg_pnl:
                    diff = no_avg_pnl - yes_avg_pnl
                    st.info(f"💡 **Smart Money Indicator:** NO holders are more profitable on average (+${diff:,.0f} vs YES). Their average trader P&L is **{f'${no_avg_pnl:,.0f}'}**.")
                else:
                    st.info("💡 **Smart Money Indicator:** Both sides have equally profitable traders on average.")
            else:
                st.info("💡 **Smart Money Indicator:** Insufficient data to determine a definitive smart money direction.")
            
            # --- TWITTER SHARE SECTION (Kept) ---
            st.markdown("##")
            st.markdown("---")
            st.header("🐦 Share Your Findings")
            
            market_title_short = market_data.get('title')[:60] + "..." if len(market_data.get('title')) > 60 else market_data.get('title')
            
            yes_pnl_str = f"${yes_avg_pnl:,.0f}" if pd.notna(yes_avg_pnl) else "N/A"
            no_pnl_str = f"${no_avg_pnl:,.0f}" if pd.notna(no_avg_pnl) else "N/A"
            
            full_url = f"https://polymarket-holders.streamlit.app/"
            try:
                # Attempt to get a short URL
                response = requests.get(f"https://tinyurl.com/api-create.php?url={full_url}", timeout=3)
                short_url = response.text if response.status_code == 200 else full_url
            except:
                short_url = full_url
            
            tweet_text = f""" 
{market_title_short} @polymarket
{selected.get('question', '')}
TOP HOLDERS ANALYSIS:
🟢YES Side:
├ Avg P&L: {yes_pnl_str}
├ Capital: ${yes_total_value:,}
🔴NO Side:
├ Avg P&L: {no_pnl_str}
├ Capital: ${no_total_value:,}
#Polymarket #WhaleTracker #Crypto
🔗 {short_url}
"""
            
            st.markdown("### 📝 Your Tweet Preview")
            st.code(tweet_text, language=None)
            
            twitter_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(tweet_text)}"
            
            st.link_button("🐦 Post to Twitter", twitter_url, use_container_width=True, type="primary")

st.markdown("---")
st.caption("A tool for tracking large positions on Polymarket. Data fetched via Polymarket APIs. [GitHub Repository](https://github.com/geomanks/polymarket-holders)")

# Add share section
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("[![Star on GitHub](https://img.shields.io/github/stars/geomanks/polymarket-holders?style=social)](https://github.com/geomanks/polymarket-holders)")
with col2:
    st.markdown("[![Twitter](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fgeomanks%2Fpolymarket-holders)](https://twitter.com/intent/tweet?text=Check%20out%20this%20Polymarket%20Whale%20Tracker!&url=https://polymarket-whale-tracker.streamlit.app)")
with col3:
    st.markdown("**Made with ❤️ for the Polymarket community**")