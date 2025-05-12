
import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

# Set page title and icon
st.set_page_config(page_title="WhatsApp Chat Analyzer", page_icon="💬")
st.sidebar.image("whatsapp.png", width=300)
# Sidebar setup
st.sidebar.success("WhatsApp Chat Analyzer")


uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    
    # Fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        #Group Created on
        if(selected_user=='Overall'):
          
          st.markdown(
         '<div style="text-align: center;"><p style="color:red; font-size:36px;">Group Info</p></div>',
         unsafe_allow_html=True)
          col1, col2 = st.columns(2)
          with col1:
           day,month,year=helper.group_created_date(selected_user,df)
           st.markdown("### Group Created on")
           st.markdown(f"<h1 style='color: purple;'>{day}th,{month},{year}</h1>", unsafe_allow_html=True)
          with col2:
            day,month,year=helper.last_message_date(selected_user,df)
            st.markdown("     ### Last message received on ")
            st.markdown(f"<h1 style='color: green;'>{day}th,{month},{year}</h1>", unsafe_allow_html=True)
        if(selected_user=='Overall'):
         col1, col2 = st.columns(2)
         with col1:
           number=helper.count_group_member(selected_user,df)
           st.markdown("### Group member count")
           st.markdown(f"<h1 style='color: orange;'> {number} </h1>", unsafe_allow_html=True)
         with col2:
           num=helper.group_active_day(selected_user,df)
           st.markdown("### Group active for")
           st.markdown(f"<h1 style='color: blue;'> {num} days</h1>", unsafe_allow_html=True)
        # Stats Area
        if(selected_user!='Overall'):
           st.markdown(
         '<div style="text-align: center;"><p style="color:black; font-size:36px;">Analysis For Group member </p></div>',
         unsafe_allow_html=True)
           st.markdown(
         f'<div style="text-align: center;"><p style="color:purple; font-size:36px;"> {selected_user}</p></div>',
         unsafe_allow_html=True)
          
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.markdown(
         '<div style="text-align: center;"><p style="color:red; font-size:36px;">Top statistics</p></div>',
         unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("### Total Messages")
            st.markdown(f"<h1 style='color: red;'>{num_messages}</h1>",unsafe_allow_html=True)
        with col2:
            st.markdown("### Total Words")
            st.markdown(f"<h1 style='color: green;'>{words}</h1>", unsafe_allow_html=True)
        with col3:
            st.markdown("### Media Shared")
            st.markdown(f"<h1 style='color: blue;'>{num_media_messages}</h1>", unsafe_allow_html=True)
        with col4:
            st.markdown("### Links Shared")
            st.markdown(f"<h1 style='color: purple;'> {num_links}</h1>", unsafe_allow_html=True)

        # Monthly Timeline
        st.markdown("## Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(timeline['time'], timeline['message'], color='green')
        ax.set_title('Monthly Timeline')
        ax.set_xlabel('Time')
        ax.set_ylabel('Messages')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily Timeline
        st.markdown("## Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='red')
        ax.set_title('Daily Timeline')
        ax.set_xlabel('Date')
        ax.set_ylabel('Messages')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
       #Most Busy Period
        st.markdown("## Most_Busy_period")
        df2 = helper.most_busy_period(selected_user,df)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(df2.index, df2.values, color='purple')
        ax.set_title('Most Busy Period')
        ax.set_xlabel('Duration of time')
        ax.set_ylabel('No of messags')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
        # Activity Map
        st.markdown("## Activity Map")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            ax.set_title('Most Busy Day')
            ax.set_xlabel('Day')
            ax.set_ylabel('Messages')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            st.markdown("### Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            ax.set_title('Most Busy Month')
            ax.set_xlabel('Month')
            ax.set_ylabel('Messages')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Weekly Activity Map
        st.markdown("## Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.heatmap(user_heatmap, ax=ax, cmap='YlGnBu')
        ax.set_title('Weekly Activity Heatmap')
        st.pyplot(fig)

        # Busiest Users (Group level)
        if selected_user == 'Overall':
            st.markdown("## Most Busy Users")
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values, color='red')
                ax.set_title('Most Busy Users')
                ax.set_xlabel('Users')
                ax.set_ylabel('Messages')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.markdown("## Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.imshow(df_wc, interpolation='bilinear')
       
      
        st.pyplot(fig)

        # Most Common Words
        st.markdown("## Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1], color='skyblue')
        ax.set_title('Most Common Words')
        ax.set_xlabel('Frequency')
        ax.set_ylabel('Words')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Emoji Analysis
        # Uncomment if the helper.emoji_helper function is defined
        # Emoji Analysis
        st.markdown("## Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots(figsize=(5, 5))  # Adjust the size as needed
            ax.pie(emoji_df['count'].head(), labels=emoji_df['emoji'].head(), autopct="%0.2f")
            ax.set_title('Top Emojis')
            st.pyplot(fig)











