"""
Polymarket Whale Tracker - SIMPLE & CLEAN VERSION (Visuals Improved)
"""

import streamlit as st
import requests
import re
import time
import pandas as pd
from typing import Optional, List, Dict
import urllib.parse

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
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
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
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        letter-spacing: -1px !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 { 
        color: #f0f2f5 !important;
        font-weight: 600 !important;
        font-size: 1.75rem !important;
        letter-spacing: -0.5px !important;
        margin-top: 2rem !important;
    }
    
    h3 { 
        color: #d1d5db !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
        margin-top: 1.5rem !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-size: 0.95rem !important;
        padding: 0.75rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }
    
    .stTextInput label, .stSelectbox label {
        color: #d1d5db !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Primary Button */
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
    
    /* Download Button */
    .stDownloadButton > button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #d1d5db !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Alert Boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        color: #e4e7eb !important;
    }
    
    div[data-baseweb="notification"] > div {
        background: rgba(99, 102, 241, 0.1) !important;
        border-left: 4px solid #6366f1 !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #9ca3af !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
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
        background: rgba(99, 102, 241, 0.15) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.5px !important;
        padding: 1rem !important;
        border-bottom: 2px solid rgba(99, 102, 241, 0.3) !important;
    }
    
    /* Table Rows */
    .stDataFrame tbody tr {
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    .stDataFrame tbody tr:hover {
        background: rgba(255, 255, 255, 0.03) !important;
    }
    
    .stDataFrame tbody tr td {
        padding: 0.75rem 1rem !important;
        color: #e4e7eb !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
        margin: 2rem 0 !important;
    }
    
    /* P&L Styling */
    .positive { 
        color: #10b981 !important; 
        font-weight: 600 !important; 
    }
    
    .negative { 
        color: #ef4444 !important; 
        font-weight: 600 !important; 
    }
    
    .neutral { 
        color: #9ca3af !important; 
    }
    
    /* Link Button (Twitter) */
    .stLinkButton > a {
        background: linear-gradient(135deg, #1da1f2 0%, #0c8bd9 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        text-decoration: none !important;
        display: inline-block !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(29, 161, 242, 0.3) !important;
    }
    
    .stLinkButton > a:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(29, 161, 242, 0.4) !important;
    }
    
    /* Code blocks (for tweet preview) */
    .stCodeBlock {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    
    /* Caption/Footer */
    .stCaption {
        color: #6b7280 !important;
        font-size: 0.85rem !important;
    }

</style>
""", unsafe_allow_html=True)

st.title("📊 Polymarket Holdings Analysis")
st.write("Track and analyze the top traders in any Polymarket prediction market. Identify smart money patterns and profitable positions.")
st.divider()

# ===== CORE FUNCTIONS (No Change needed here for visuals) =====

def extract_slug(url: str) -> Optional[str]:
    match = re.search(r'polymarket\.com/event/([^?#/]+)', url)
    return match.group(1) if match else None

def fetch_market_data(slug: str):
    url = f"https://gamma-api.polymarket.com/events?slug={slug}"
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

# ===== CUSTOM FORMATTING FUNCTIONS for DataFrame Styling =====

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

def format_currency_with_pnl_style(s):
    """Applies formatting and P&L color to a Pandas Series."""
    formatted_series = s.apply(lambda x: f'${x:,}' if pd.notna(x) else 'N/A')
    styled_series = [format_pnl_style(val) for val in s]
    return [f'{style}; {formatted}' for style, formatted in zip(styled_series, formatted_series)]

# --- Helper function for displaying results ---
def display_results(df: pd.DataFrame, title: str, color_code: str):
    """Reusable function to display a holder section."""
    st.header(f"{color_code} {title}")
    
    # Apply custom styling to the DataFrame
    # Calculate height to show all rows without scrolling (approximately 35px per row + 38px for header)
    table_height = len(df) * 35 + 38
    
    st.dataframe(
        df.style.format({
            'Shares': '{:,}',
            'Entry': '${:.3f}',
            'Current': '${:.3f}',
            'Value': '${:,}',
            'Market P&L': lambda x: f'${x:,}',
            'All-Time P&L': lambda x: f'${x:,.0f}' if pd.notna(x) else 'N/A'
        })
        .applymap(format_pnl_style, subset=['Market P&L', 'All-Time P&L'])
        .set_properties(**{'background-color': '#161b22', 'color': '#c9d1d9'}), # Dark theme background/text for table cells
        use_container_width=True,
        hide_index=True,
        height=table_height
    )
    
    # Metrics
    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)
    avg_pnl = df['All-Time P&L'].mean()
    
    col1.metric("**Average All-Time P&L**", 
                f"${avg_pnl:,.0f}" if pd.notna(avg_pnl) else "N/A", 
                delta_color="off") # Use off to prevent the delta icon from appearing
    col2.metric("**Total Position Value**", f"${df['Value'].sum():,}")
    
    # Calculate Volume-Weighted Average Price (VWAP) for Entry
    total_shares = df['Shares'].sum()
    if total_shares > 0:
        avg_entry = (df['Shares'] * df['Entry']).sum() / total_shares
        col3.metric("**Volume-Weighted Avg Entry**", f"${avg_entry:.3f}")
    else:
        col3.metric("**Volume-Weighted Avg Entry**", "N/A")


# ===== IMAGE GENERATION FOR TWITTER SHARING =====

# ===== MAIN APP (Updated to use new styling and functions) =====

# Initialize session state for URL
if 'current_url' not in st.session_state:
    st.session_state['current_url'] = ""

url = st.text_input(
    "🔗 Polymarket Event URL:", 
    value=st.session_state['current_url'],
    placeholder="https://polymarket.com/event/..."
)

# Update session state when URL changes
if url != st.session_state['current_url']:
    st.session_state['current_url'] = url
    # Clear old analysis data when URL changes
    for key in ['analysis_yes_data', 'analysis_no_data', 'analysis_slug', 'analysis_market_title', 'share_image', 'image_generated']:
        if key in st.session_state:
            del st.session_state[key]

if url:
    slug = extract_slug(url)
    if not slug:
        st.error("❌ Invalid URL. Please ensure it starts with `https://polymarket.com/event/`")
        st.stop()
    
    try:
        with st.spinner("🚀 Loading market details..."):
            market_data = fetch_market_data(slug)
    except Exception as e:
        st.error(f"Failed to fetch market data: {e}")
        st.stop()
        
    st.success(f"✅ **{market_data.get('title')}**")
    
    markets = [m for m in market_data.get('markets', []) if m.get('enableOrderBook')]
    if not markets:
        st.error("No yes/no markets found in this event.")
        st.stop()
    
    # Compact market selection
    if len(markets) > 1:
        st.markdown("##")
        options = [m.get('question', f'Market {i}') for i, m in enumerate(markets, 1)]
        selected_question = st.selectbox(
            "📊 Select Market to Analyze:", 
            options,
            key="market_select"
        )
        idx = options.index(selected_question)
        selected = markets[idx]
    else:
        selected = markets[0]
    
    st.markdown("##")
    
    if st.button("🔍 ANALYZE MARKET", type="primary", use_container_width=True):
        condition_id = selected.get('conditionId')
        
        # Fetch holders data
        with st.spinner("🎣 Fetching top holders for YES and NO outcomes..."):
            try:
                holders_data = fetch_holders(condition_id)
            except Exception as e:
                st.error(f"Failed to fetch holder data: {e}")
                st.stop()
        
        yes_raw, no_raw = [], []
        for outcome in holders_data:
            holders = outcome.get('holders', [])
            if holders:
                if holders[0].get('outcomeIndex') == 0:
                    yes_raw = holders[:15]
                else:
                    no_raw = holders[1:16]
        
        # Combined analysis section
        st.markdown("---")
        st.markdown("### 🔄 Analyzing Holders")
        st.write("Fetching position data and all-time P&L for all holders...")
        
        # Create progress tracking
        total_holders = len(yes_raw) + len(no_raw)
        progress_bar = st.progress(0, text="Starting analysis...")
        status_text = st.empty()
        
        yes_data = []
        no_data = []
        current_holder = 0
        
        # Analyze YES holders
        status_text.info("🟢 **Analyzing YES holders...**")
        for i, h in enumerate(yes_raw):
            current_holder += 1
            holder_name = h.get('name') or h.get('proxyWallet', 'Unknown')[:10]
            percentage = int((current_holder / total_holders) * 100)
            progress_bar.progress(current_holder/total_holders, 
                                text=f"Progress: {percentage}% - YES Holder: {holder_name} ({i+1}/{len(yes_raw)})")
            
            enriched = enrich_holder(h, condition_id)
            if enriched:
                yes_data.append(enriched)
            time.sleep(0.15)
        
        # Analyze NO holders
        status_text.info("🔴 **Analyzing NO holders...**")
        for i, h in enumerate(no_raw):
            current_holder += 1
            holder_name = h.get('name') or h.get('proxyWallet', 'Unknown')[:10]
            percentage = int((current_holder / total_holders) * 100)
            progress_bar.progress(current_holder/total_holders, 
                                text=f"Progress: {percentage}% - NO Holder: {holder_name} ({i+1}/{len(no_raw)})")
            
            enriched = enrich_holder(h, condition_id)
            if enriched:
                no_data.append(enriched)
            time.sleep(0.15)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Success message
        st.success("✅ Analysis Complete!")
        
        st.markdown("---")
        st.markdown("##")
        
        # Display YES results
        if yes_data:
            df_yes = pd.DataFrame(yes_data)
            display_results(df_yes, "YES Holders (Top 15)", "🟢")
            
            csv_yes = df_yes.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download YES Holders CSV",
                data=csv_yes,
                file_name=f"polymarket_yes_holders_{slug}.csv",
                mime="text/csv",
            )
        else:
            st.warning("No significant YES holders found.")
        
        # Add spacing
        st.markdown("##")
        st.markdown("---")
        st.markdown("##")
        
        # Display NO results
        if no_data:
            df_no = pd.DataFrame(no_data)
            display_results(df_no, "NO Holders (Top 15)", "🔴")
            
            csv_no = df_no.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download NO Holders CSV",
                data=csv_no,
                file_name=f"polymarket_no_holders_{slug}.csv",
                mime="text/csv",
            )
        else:
            st.warning("No significant NO holders found.")
        
        # Store data in session state for Twitter share functionality
        st.session_state['analysis_yes_data'] = yes_data
        st.session_state['analysis_no_data'] = no_data
        st.session_state['analysis_slug'] = slug
        st.session_state['analysis_market_title'] = market_data.get('title')
        
        # ===== COMPARISON SECTION =====
        if yes_data and no_data:
            st.markdown("##")
            st.markdown("---")
            st.header("⚖️ YES vs NO Comparison")
            
            df_yes = pd.DataFrame(yes_data)
            df_no = pd.DataFrame(no_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🟢 YES Side")
                yes_avg_pnl = df_yes['All-Time P&L'].mean()
                yes_total_value = df_yes['Value'].sum()
                yes_total_shares = df_yes['Shares'].sum()
                yes_avg_entry = (df_yes['Shares'] * df_yes['Entry']).sum() / yes_total_shares if yes_total_shares > 0 else 0
                
                st.metric("Avg All-Time P&L", f"${yes_avg_pnl:,.0f}" if pd.notna(yes_avg_pnl) else "N/A")
                st.metric("Total Capital", f"${yes_total_value:,}")
                st.metric("Total Shares", f"{yes_total_shares:,}")
                st.metric("Avg Entry Price", f"${yes_avg_entry:.3f}")
                
                # Smart money indicator
                profitable_yes = len(df_yes[df_yes['All-Time P&L'] > 0])
                total_yes = len(df_yes[df_yes['All-Time P&L'].notna()])
                if total_yes > 0:
                    win_rate = (profitable_yes / total_yes) * 100
                    st.metric("Profitable Traders", f"{profitable_yes}/{total_yes} ({win_rate:.0f}%)")
            
            with col2:
                st.markdown("### 🔴 NO Side")
                no_avg_pnl = df_no['All-Time P&L'].mean()
                no_total_value = df_no['Value'].sum()
                no_total_shares = df_no['Shares'].sum()
                no_avg_entry = (df_no['Shares'] * df_no['Entry']).sum() / no_total_shares if no_total_shares > 0 else 0
                
                st.metric("Avg All-Time P&L", f"${no_avg_pnl:,.0f}" if pd.notna(no_avg_pnl) else "N/A")
                st.metric("Total Capital", f"${no_total_value:,}")
                st.metric("Total Shares", f"{no_total_shares:,}")
                st.metric("Avg Entry Price", f"${no_avg_entry:.3f}")
                
                # Smart money indicator
                profitable_no = len(df_no[df_no['All-Time P&L'] > 0])
                total_no = len(df_no[df_no['All-Time P&L'].notna()])
                if total_no > 0:
                    win_rate = (profitable_no / total_no) * 100
                    st.metric("Profitable Traders", f"{profitable_no}/{total_no} ({win_rate:.0f}%)")
            
            # Smart money verdict
            st.markdown("###")
            if pd.notna(yes_avg_pnl) and pd.notna(no_avg_pnl):
                if yes_avg_pnl > no_avg_pnl:
                    diff = yes_avg_pnl - no_avg_pnl
                    st.info(f"💡 **Smart Money Indicator:** YES holders are more profitable on average (+${diff:,.0f} vs NO)")
                elif no_avg_pnl > yes_avg_pnl:
                    diff = no_avg_pnl - yes_avg_pnl
                    st.info(f"💡 **Smart Money Indicator:** NO holders are more profitable on average (+${diff:,.0f} vs YES)")
                else:
                    st.info("💡 **Smart Money Indicator:** Both sides have equally profitable traders")
            
            # ===== TWITTER SHARE SECTION =====
            st.markdown("##")
            st.markdown("---")
            st.header("🐦 Share on Twitter")
            
            # Create a nicely formatted text table for Twitter
            market_title_short = market_data.get('title')[:60] + "..." if len(market_data.get('title')) > 60 else market_data.get('title')
            
            # Determine smart money verdict
            if pd.notna(yes_avg_pnl) and pd.notna(no_avg_pnl):
                if yes_avg_pnl > no_avg_pnl:
                    diff = yes_avg_pnl - no_avg_pnl
                    verdict = f"YES holders +${diff:,.0f} more profitable"
                    winner_emoji = "🟢"
                elif no_avg_pnl > yes_avg_pnl:
                    diff = no_avg_pnl - yes_avg_pnl
                    verdict = f"NO holders +${diff:,.0f} more profitable"
                    winner_emoji = "🔴"
                else:
                    verdict = "Both sides equally profitable"
                    winner_emoji = "⚖️"
            else:
                verdict = "Insufficient data"
                winner_emoji = "❓"
            
            # Format values before putting them in the tweet
            yes_pnl_str = f"${yes_avg_pnl:,.0f}" if pd.notna(yes_avg_pnl) else "N/A"
            no_pnl_str = f"${no_avg_pnl:,.0f}" if pd.notna(no_avg_pnl) else "N/A"
            yes_winners_str = f"{profitable_yes}/{total_yes} ({(profitable_yes/total_yes*100):.0f}%)" if total_yes > 0 else "N/A"
            no_winners_str = f"{profitable_no}/{total_no} ({(profitable_no/total_no*100):.0f}%)" if total_no > 0 else "N/A"
            
            # Shorten the URL
            full_url = f"https://polymarket-holders.streamlit.app/"
            try:
                response = requests.get(f"https://tinyurl.com/api-create.php?url={full_url}", timeout=3)
                short_url = response.text if response.status_code == 200 else full_url
            except:
                short_url = full_url
            
            # Create the tweet text
            tweet_text = f""" 
{market_title_short} @polymarket
{selected.get('question', '')}
TOP 15 HOLDERS
🟢YES Side:
├ Avg P&L: {yes_pnl_str}
├ Capital: ${yes_total_value:,}
🔴NO Side:
├ Avg P&L: {no_pnl_str}
├ Capital: ${no_total_value:,}
🔗 {short_url}
"""
            
            # Display the tweet preview
            st.markdown("### 📝 Your Tweet (Ready to Post!)")
            st.code(tweet_text, language=None)
            
            # Create the Twitter URL with encoded text
            twitter_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(tweet_text)}"
            
            st.link_button("🐦 Post to Twitter", twitter_url, use_container_width=True, type="primary")
            
            st.success("✅ Click the button above - your tweet is ready! Twitter will open with this text pre-filled.")

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
