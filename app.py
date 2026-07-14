import os
import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="WhatsApp Chat Analyzer", page_icon="💬")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .hero-card {
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        border-radius: 18px;
        padding: 1.4rem 1.4rem;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(18, 140, 126, 0.18);
    }
    .info-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
    }
    div[data-testid="stSidebar"] {
        background: #f8fafc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <h1 style="margin-bottom: 0.2rem;">💬 WhatsApp Chat Analyzer</h1>
        <p style="margin: 0; font-size: 1rem; opacity: 0.95;">Upload an exported chat and uncover conversation trends, busy times, and popular words in a polished dashboard.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Upload chat")
    if os.path.exists("whatsapp.png"):
        st.image("whatsapp.png", width=260)
    else:
        st.markdown("💬")
    st.caption("Export your WhatsApp chat and upload the text file here.")
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "text"])

    if uploaded_file is not None:
        st.success(f"Loaded {uploaded_file.name}")

    st.markdown("---")
    st.caption("Tip: use the 'Overall' view for group-wide insights or choose a specific participant for a detailed breakdown.")

if uploaded_file is None:
    st.markdown(
        """
        <div class="info-card">
            <h3>Start analyzing your chat</h3>
            <ul>
                <li>See daily and monthly activity trends</li>
                <li>Find the busiest users and time periods</li>
                <li>Explore word frequency and emoji patterns</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("Upload a WhatsApp chat export from the sidebar to begin.")
    st.stop()

with st.spinner("Preparing your insights..."):
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

st.success("Analysis ready")
st.caption("Select a participant or view the full group's activity below.")

# Fetch unique users
user_list = df["user"].unique().tolist()
if "group_notification" in user_list:
    user_list.remove("group_notification")
user_list.sort()
user_list.insert(0, "Overall")

st.sidebar.caption("Selection updates automatically — no extra click needed.")
selected_user = st.sidebar.selectbox("Show analysis for", user_list, key="selected_user")

if st.session_state.get("selected_user") is not None:
    if selected_user == "Overall":
        st.markdown("## Group overview")
        st.markdown(
            """
            <div class="info-card">
                <strong>Group-wide insights</strong> help you understand how the conversation evolves over time.
            </div>
            """,
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns(2)
        with col1:
            day, month, year = helper.group_created_date(selected_user, df)
            st.markdown("### 📅 Group created on")
            st.markdown(f"<h2 style='color: #128C7E;'>{day}th, {month} {year}</h2>", unsafe_allow_html=True)
        with col2:
            day, month, year = helper.last_message_date(selected_user, df)
            st.markdown("### 📨 Last message received on")
            st.markdown(f"<h2 style='color: #25D366;'>{day}th, {month} {year}</h2>", unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            number = helper.count_group_member(selected_user, df)
            st.markdown("### 👥 Group member count")
            st.markdown(f"<h2 style='color: #F59E0B;'>{number}</h2>", unsafe_allow_html=True)
        with col4:
            num = helper.group_active_day(selected_user, df)
            st.markdown("### ⏱️ Group active for")
            st.markdown(f"<h2 style='color: #3B82F6;'>{num} days</h2>", unsafe_allow_html=True)
    else:
        st.markdown(f"## Analysis for {selected_user}")
        st.markdown(
            f"""
            <div class="info-card">
                <strong>{selected_user}</strong> is highlighted below with their activity and conversation patterns.
            </div>
            """,
            unsafe_allow_html=True,
        )

    num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
    st.markdown("## 📊 Top statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Messages", num_messages)
    with col2:
        st.metric("Total Words", words)
    with col3:
        st.metric("Media Shared", num_media_messages)
    with col4:
        st.metric("Links Shared", num_links)

    st.markdown("---")
    st.markdown("## 📈 Activity over time")

    timeline = helper.monthly_timeline(selected_user, df)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(timeline["time"], timeline["message"], color="#25D366")
    ax.set_title("Monthly Timeline")
    ax.set_xlabel("Time")
    ax.set_ylabel("Messages")
    plt.xticks(rotation="vertical")
    st.pyplot(fig)

    daily_timeline = helper.daily_timeline(selected_user, df)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(daily_timeline["only_date"], daily_timeline["message"], color="#E11D48")
    ax.set_title("Daily Timeline")
    ax.set_xlabel("Date")
    ax.set_ylabel("Messages")
    plt.xticks(rotation="vertical")
    st.pyplot(fig)

    st.markdown("## 🕒 Most busy period")
    df2 = helper.most_busy_period(selected_user, df)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(df2.index, df2.values, color="#8B5CF6")
    ax.set_title("Most Busy Period")
    ax.set_xlabel("Duration of time")
    ax.set_ylabel("No of messages")
    plt.xticks(rotation="vertical")
    st.pyplot(fig)

    st.markdown("## 🗓️ Activity map")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Most busy day")
        busy_day = helper.week_activity_map(selected_user, df)
        fig, ax = plt.subplots()
        ax.bar(busy_day.index, busy_day.values, color="#8B5CF6")
        ax.set_title("Most Busy Day")
        ax.set_xlabel("Day")
        ax.set_ylabel("Messages")
        plt.xticks(rotation="vertical")
        st.pyplot(fig)
    with col2:
        st.markdown("### Most busy month")
        busy_month = helper.month_activity_map(selected_user, df)
        fig, ax = plt.subplots()
        ax.bar(busy_month.index, busy_month.values, color="#F59E0B")
        ax.set_title("Most Busy Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Messages")
        plt.xticks(rotation="vertical")
        st.pyplot(fig)

    st.markdown("## 🌡️ Weekly activity heatmap")
    user_heatmap = helper.activity_heatmap(selected_user, df)
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(user_heatmap, ax=ax, cmap="YlGnBu")
    ax.set_title("Weekly Activity Heatmap")
    st.pyplot(fig)

    if selected_user == "Overall":
        st.markdown("## 👤 Most busy users")
        x, new_df = helper.most_busy_users(df)
        fig, ax = plt.subplots()
        col1, col2 = st.columns(2)
        with col1:
            ax.bar(x.index, x.values, color="#E11D48")
            ax.set_title("Most Busy Users")
            ax.set_xlabel("Users")
            ax.set_ylabel("Messages")
            plt.xticks(rotation="vertical")
            st.pyplot(fig)
        with col2:
            st.dataframe(new_df)

    st.markdown("## ☁️ Word cloud")
    df_wc = helper.create_wordcloud(selected_user, df)
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.imshow(df_wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    st.markdown("## 🗣️ Most common words")
    most_common_df = helper.most_common_words(selected_user, df)
    fig, ax = plt.subplots()
    ax.barh(most_common_df[0], most_common_df[1], color="#38BDF8")
    ax.set_title("Most Common Words")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Words")
    plt.xticks(rotation="vertical")
    st.pyplot(fig)

    st.markdown("## 😊 Emoji analysis")
    emoji_df = helper.emoji_helper(selected_user, df)
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(emoji_df)
    with col2:
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(emoji_df["count"].head(), labels=emoji_df["emoji"].head(), autopct="%0.2f")
        ax.set_title("Top Emojis")
        st.pyplot(fig)


