import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

# Set layout
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        .styled-heading {
            text-align: center;
            font-size: 2.25rem;
            font-weight: 700;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 2.5rem 0 1rem 0;
        }
        .styled-heading.first-heading {
            margin-top: -3rem !important;
        }
        .blue { color: #3366cc; }
        .green { color: #2e8b57; }
        .red { color: #cc3300; }
        .purple { color: #800080; }
        .orange { color: #ff6600; }
        .pink { color: #cc3399; }

        .info-box {
            background-color: #f0f8ff;
            border-left: 6px solid #1e90ff;
            padding: 1rem 1.5rem;
            margin: 1rem 0 2.5rem 0;
            border-radius: 8px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 1rem;
            color: #003366;
        }
    </style>
""", unsafe_allow_html=True)

# Helper function for styled headings
def styled_heading(text, color="blue", is_first=False):
    extra_class = "first-heading" if is_first else ""
    st.markdown(f"""
        <div class='styled-heading {color} {extra_class}'>
            {text}
        </div>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Whatsapp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a .txt file", type="txt")

# Save upload state
st.session_state['uploaded_file'] = uploaded_file

# Show info box only before file is uploaded
if not uploaded_file:
    st.markdown("""
        <div class='info-box'>
            <strong>Important:</strong><br>
            • Upload <strong>only WhatsApp chat files (.txt)</strong>.<br>
            • Make sure your chat is in <strong>either</strong> 12-hour format 
            <em>(e.g. 11:15 AM)</em> <strong>or</strong> 24-hour format 
            <em>(e.g. 23:15)</em>.<br>
            • <strong>Mixing both formats is not supported</strong> and will cause an error.
        </div>
    """, unsafe_allow_html=True)

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        # --- Top Stats ---
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        styled_heading("Top Statistics", "blue", is_first=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("**Total Messages**", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color:#3366cc'>{num_messages}</h4>", unsafe_allow_html=True)

        with col2:
            st.markdown("**Total Words**", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color:#3366cc'>{words}</h4>", unsafe_allow_html=True)

        with col3:
            st.markdown("**Media Shared**", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color:#3366cc'>{num_media_messages}</h4>", unsafe_allow_html=True)

        with col4:
            st.markdown("**Links Shared**", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color:#3366cc'>{num_links}</h4>", unsafe_allow_html=True)

        # --- Most Busy Users ---
        if selected_user == 'Overall':
            styled_heading("Most Busy Users", "pink")
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # --- Wordcloud ---
        styled_heading("Wordcloud", "green")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)

        # --- Most Common Words ---
        styled_heading("Most Common Words", "red")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # --- Emoji Analysis ---
        styled_heading("Emoji Analysis", "purple")
        emoji_df = helper.emoji_helper(selected_user, df)
        col1, col2 = st.columns([3, 4])
        with col1:
            st.subheader("Emoji Frequency Table")
            st.dataframe(emoji_df)
        with col2:
            st.subheader("Emoji Usage Distribution")
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.pie(emoji_df['Count'].head(), labels=emoji_df['Emoji'].head(), autopct="%0.2f%%")
            st.pyplot(fig)

        # --- Activity Map ---
        styled_heading("Activity Map", "orange")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.subheader("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # --- Weekly Activity Map ---
        styled_heading("Weekly Activity Map", "blue")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax)
        st.pyplot(fig)

        # --- Monthly Timeline ---
        styled_heading("Monthly Timeline", "green")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # --- Daily Timeline ---
        styled_heading("Daily Timeline", "red")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
