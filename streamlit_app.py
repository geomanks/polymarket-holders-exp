# Format values before putting them in the tweet
            yes_pnl_str = f"${yes_avg_pnl:,.0f}" if pd.notna(yes_avg_pnl) else "N/A"
            no_pnl_str = f"${no_avg_pnl:,.0f}" if pd.notna(no_avg_pnl) else "N/A"
            yes_winners_str = f"{profitable_yes}/{total_yes} ({(profitable_yes/total_yes*100):.0f}%)" if total_yes > 0 else "N/A"
            no_winners_str = f"{profitable_no}/{total_no} ({(profitable_no/total_no*100):.0f}%)" if total_no > 0 else "N/A"
            
            # Create the tweet text
            tweet_text = f"""🐋 Polymarket Whale Analysis
{market_title_short}
{selected.get('question', '')}

📊 TOP 15 HOLDERS COMPARISON

🟢 YES Side:
├ Avg P&L: {yes_pnl_str}
├ Capital: ${yes_total_value:,}
└ Winners: {yes_winners_str}

🔴 NO Side:
├ Avg P&L: {no_pnl_str}
├ Capital: ${no_total_value:,}
└ Winners: {no_winners_str}

{winner_emoji} Smart Money: {verdict}

🔗 https://polymarket.com/event/{slug}

#Polymarket #PredictionMarkets"""
            
            # Display the tweet preview
            st.markdown("### 📝 Your Tweet (Ready to Post!)")
            st.code(tweet_text, language=None)
            
            # Create the Twitter URL with encoded text
            twitter_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(tweet_text)}"
            
            st.link_button("🐦 Post to Twitter", twitter_url, use_container_width=True, type="primary")
            
            st.success("✅ Click the button above - your tweet is ready! Twitter will open with this text pre-filled.")
