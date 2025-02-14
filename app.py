import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns

# Sidebar Configuration
st.sidebar.title("WhatsApp Chat Analyzer")

# File uploader
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")  # Convert bytes to string
    df = preprocessor.preprocess(data)  # Process data
    st.dataframe(df)

    # Fetch unique users
    user_list = df['user'].unique().tolist()

    # Safely remove 'group_notification' if it exists
    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()  # Sort list in ascending order
    user_list.insert(0, "Overall")  # Insert "Overall" at the beginning

    # Display select box with user options
    selected_user = st.sidebar.selectbox("Show analysis with respect to", user_list)

    if st.sidebar.button("Show Analysis"):
        # Fetch statistics (total messages, words, media, and links)
        num_messages, total_words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        # Display Stats
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.subheader(num_messages)

        with col2:
            st.header("Total Words")
            st.subheader(total_words)

        with col3:
            st.header("Media Shared")
            st.subheader(num_media_messages)

        with col4:
            st.header("Links Shared")
            st.subheader(num_links)

        # Get Monthly Timeline Data
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)

        # Display Timeline Chart
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='blue')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily Timeline
        st.title("Daily Timeline")
        daily_timeline_data = helper.daily_timeline(selected_user, df)

        # Display Timeline Chart
        fig, ax = plt.subplots()
        ax.plot(daily_timeline_data['only_date'], daily_timeline_data['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity Map
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            st.pyplot(fig)

        # Weekly Activity Heatmap
        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax, cmap="coolwarm")
        st.pyplot(fig)

        # Most Busy Users (only if selected_user is 'Overall')
        if selected_user == 'Overall':
            st.title("Most Busy Users")

            # Get most busy users
            X, new_df = helper.most_busy_users(df)

            # Plot and display
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Top User Activity")
                fig, ax = plt.subplots()
                ax.bar(X.index, X.values, color='skyblue')
                ax.set_xlabel("Users")
                ax.set_ylabel("Messages Sent")
                st.pyplot(fig)

            with col2:
                st.subheader("User Activity Details")
                st.dataframe(new_df)

        # WordCloud
        st.title("WordCloud")
        try:
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis("off")
            st.pyplot(fig)
        except ValueError as e:
            st.error(f"Error creating WordCloud: {e}")

        # Most Common Words
        st.title("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.bar(most_common_df[0], most_common_df[1], color='orange')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Emoji Analysis
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)

        if not emoji_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)  # Display the DataFrame

            with col2:
                fig, ax = plt.subplots()
                ax.pie(emoji_df['Count'], labels=emoji_df['Emoji'], autopct='%1.1f%%')
                st.pyplot(fig)
        else:
            st.write("No emojis found in the selected user's chat.")
