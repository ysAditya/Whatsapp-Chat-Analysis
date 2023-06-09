# -*- coding: utf-8 -*-
"""Whatsapp_Chat_Analysis_NLP

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16pYwVRrwHyYpOtKMKOxITE7VkLxqhcJf
"""

from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter

def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    num_messages = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media shared

    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch the number of links
    links = []
    extractor = URLExtract()
    for message in df['message']:
        links.extend(extractor.find_urls(message))

    num_links = len(links)

    return num_messages, len(words), num_media_messages, num_links


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round(df['user'].value_counts() / df.shape[0] * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x, df


def create_wordcloud(selected_user, df):
    f = open('Stopwords.txt', 'r')
    stopwords = f.read()

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != "group notification"]
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stopwords(message):
        y = []
        for word in message.lower().split():
            if word not in stopwords:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500, height=300, min_font_size=10, background_color='black')
    temp['message'] = temp['message'].apply(remove_stopwords)
    df_wc = wc.generate(temp['message'].str.cat(sep=' '))
    return df_wc


def most_common_words(selected_user, df):
    f = open('Stopwords.txt', 'r')
    stopwords = f.read()

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != "group notification"]
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stopwords:
                words.append(word)

    return_df = pd.DataFrame(Counter(words).most_common(20))

    return return_df


def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline


def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


def monthly_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]


    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap
#Preprocessor

import re
import pandas as pd


def preprocess(data):
    pattern = '\d{1,2}/\d{1,2}/\d{1,2},\s\d{1,2}:\d{2}\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    # convert message_date types
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M - ')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # username
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df

import streamlit as st

#import helper
#import preprocessor
import matplotlib.pyplot as plt
import seaborn as sns

st.image("WhatsappWizard.png", width = 400)
st.sidebar.title("Let's analyze your whatsapp chat!")
st.sidebar.text("Buddy! Just download your chat using")
st.sidebar.text("Export Chat (without media) option")
st.sidebar.text("in your chat and upload it here.")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    df = preprocess(data)

#    st.dataframe(df)

    # fetch active users

    user_list = df['user'].unique().tolist()
    user_list.remove('group notification')
    user_list.sort()
    user_list.insert(0, "Overall")
        


    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    num_messages, words, num_media_messages, num_links = fetch_stats(selected_user, df)

    if st.sidebar.button("Show Analysis"):

        st.title("Top Statistics")

        col1, col2, col3, col4 = st.columns(4)



        with col1:
            st.header("Total Messages")
            st.title(num_messages)

        with col2:
            st.header('Total words')
            st.title(words)

        with col3:
            st.header('Media Shared')
            st.title(num_media_messages)

        with col4:
            st.header('Links provided')
            st.title(num_links)

        # Monthly Timeline
        st.title("Monthly Timeline")
        timeline = monthly_timeline(selected_user, df)

        fig, ax = plt.subplots()
        
        ax.plot(timeline['time'].values, timeline['message'].values, color='Green')

        plt.xticks(rotation='vertical')

        st.pyplot(fig)

        # Daily Timeline
        st.title("Daily Timeline")
        daily_timeline = daily_timeline(selected_user, df)

        fig, ax = plt.subplots()
        
        ax.plot(daily_timeline['only_date'].values, daily_timeline['message'].values, color='Black')

        plt.xticks(rotation='vertical')

        st.pyplot(fig)

        # Weekly Activity Map
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header('Most Busy Month')
            busy_month = monthly_activity_map(selected_user,df)
            fig, ax=plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # finding the busiest users in the group
        if selected_user == 'Overall':
            st.title("Most Busy User")
            x, new_df = most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # Wordcloud
        st.title("Wordcloud")
        df_wc = create_wordcloud(selected_user, df)
        fig, ax =plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

    # Most common words

    most_common_df = most_common_words(selected_user, df)

    fig, ax =plt.subplots()
    ax.barh(most_common_df[0], most_common_df[1])
    plt.xticks(rotation='vertical')

    st.title('Most Common Words')
    st.pyplot(fig)

#Helper





