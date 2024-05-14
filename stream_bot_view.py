import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

def load_df(name):
    df = pd.read_csv(f'{name}.csv',encoding='utf-8',index_col='member_name')
    return df

def main():
    st.title('Games')
    game_df = load_df('game_df')
    all_games = game_df.name.tolist()
    game_list = list(set(all_games))
    counts = [all_games.count(game) for game in game_list]
    fig, ax = plt.subplots()
    ax.pie(counts, labels=game_list,autopct='%1.1f%%')
    st.pyplot(fig=fig)
    st.title('Songs')
    spotify_df = load_df('spotify_df')
    listeners = spotify_df.index.tolist()
    for listener in listeners:
        st.write(f'{listener} is listening to {spotify_df.at[listener,"title"]} by {spotify_df.at[listener,"processed_artists"]}')
    custom_activity_df = load_df('custom_activity_df')
    cust_names = custom_activity_df.index.tolist()
    st.title('Custom Statuses')
    name = st.selectbox(label='User',options=cust_names,key='spy_bot')
    emoji,text = custom_activity_df.at[name,'emoji'],custom_activity_df.at[name,'name']
    message = ' '.join([emoji,text])
    st.write(message)

if __name__ == "__main__":
    main()
