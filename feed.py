import streamlit as st
import feedparser
from datetime import datetime
from newspaper import Article


# Function to format publication dates in "24th Jan 2024" style
def format_date(pub_date):
    try:
        from datetime import datetime

        dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
        day = dt.day

        def ordinal(n):
            if 10 <= n % 100 <= 20:
                suffix = "th"
            else:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
            return f"{n}{suffix}"

        formatted_date = dt.strftime(f"%b %Y")
        return f"{ordinal(day)} {formatted_date}"
    except ValueError:
        return pub_date


# Initialize or load saved articles into session state
if "saved_articles" not in st.session_state:
    st.session_state.saved_articles = []

# Define RSS feeds for ASEAN news
rss_feeds = {
    "Alpha Southeast Asia": "https://alphasoutheastasia.com/feed/",
    "Southeast Asia Globe": "https://southeastasiaglobe.com/feed/",
    "Kyoto Review": "https://kyotoreview.org/feed/",
    "The Diplomat": "https://thediplomat.com/regions/southeast-asia/feed/",
    "ASEAN.org": "https://asean.org/category/news/feed/",
    "TechCrunch: Southeast Asia": "https://techcrunch.com/tag/southeast-asia/feed/",
    # "Financial Times: South-East Asia": "https://www.ft.com/south-east-asia?format=rss",
}

menu_options = ["News Sources", "Saved Articles"]
selected_menu = st.sidebar.radio("Choose an option:", menu_options)

if selected_menu == "News Sources":
    st.logo("assets/ant.png", size="large", link=None, icon_image=None)

    selected_feed = st.sidebar.radio("Choose a news source:", list(rss_feeds.keys()))

    # Parse the selected RSS feed
    feed_url = rss_feeds[selected_feed]
    feed = feedparser.parse(feed_url)

    st.subheader(f"News from {selected_feed}")

    if feed.entries:
        for entry in feed.entries[:1000]:
            formatted_date = format_date(entry.published)

            # Use newspaper3k to get a snippet of the content from the link
            try:
                article = Article(entry.link)
                article.download()
                article.parse()

                snippet = (
                    article.text[:300] + "..."
                )  # Take the first 300 characters as snippet

                st.markdown(f"### [{entry.title}]({entry.link})")
                st.write(f"**Published on:** {formatted_date}")
                st.write(f"**Snippet:** {snippet}")

                if st.button("Save Article", key=f"save_{entry.link}"):
                    if {
                        "title": entry.title,
                        "link": entry.link,
                        "published": formatted_date,
                    } not in st.session_state.saved_articles:
                        st.session_state.saved_articles.append(
                            {
                                "title": entry.title,
                                "link": entry.link,
                                "published": formatted_date,
                            }
                        )
                        st.success("Article saved!")

                st.markdown("---")

            except Exception as e:
                st.write("Failed to fetch snippet from the article link.")

    else:
        st.write("No articles found. Please try another source.")

elif selected_menu == "Saved Articles":
    st.title("Your Articles")

    if st.session_state.saved_articles:
        for idx, article in enumerate(st.session_state.saved_articles):
            st.markdown(f"### [{article['title']}]({article['link']})")
            st.write(f"**Published on:** {article['published']}")

            if st.button("Unsave Article", key=f"unsave_{article['link']}"):
                st.session_state.saved_articles = [
                    a
                    for a in st.session_state.saved_articles
                    if a["link"] != article["link"]
                ]
                st.success("Article removed from saved list.")

            st.markdown("---")
    else:
        st.write("No saved articles yet.")
