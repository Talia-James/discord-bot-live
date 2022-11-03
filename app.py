import streamlit as st
import csv
import base64
import numpy as np
from datetime import datetime
today = datetime.today().weekday()


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
if today > 2 or today==0:
    camp = 'SW'
    spacer = 3
else:
    camp = 'coc'
    spacer = 7
add_bg_from_local(f'{camp}.png')    
def load_csv(csvfile):
    global list_
    with open(f'{csvfile}.csv',newline='') as f:
        reader = csv.reader(f,delimiter=',')
        i=0
        for row in reader:
            if i==0:
                list_ = row
                i+=1
            else:
                pass
    return list_
def load_votes(csvfile):
    with open(f'{csvfile}.csv',newline='') as f:
        reader = csv.reader(f,delimiter=',')
        i=0
        for row in reader:
            if i==0:
                votes = row
                i+=1
            else:
                pass
        return votes
titles = load_csv('titles')
indexed = list(enumerate(titles,start=1))
try:
    votes = load_votes('votes')
except UnboundLocalError:
    st.write('No votes cast yet, initializing list.')
    votes = []
for i in range(spacer):
  st.markdown('')
st.title('Tabletop session titles!')
for i in range(len(titles)):
  if st.checkbox(titles[i],key=f'{titles[i]}-{i}'):
    votes.append(indexed[i][0])
button_container = st.container()
# if button_container.button('Name (for duplicate prevention):'):
# name = str(button_container.text_input('Name (for duplicate prevention):'))
if button_container.button('Cast vote(s)'):
    with open('votes.csv','w') as f:
        writer = csv.writer(f)
        writer.writerow(votes)
    st.markdown('Votes recorded!')
    # with open('vote_hist.csv') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(f'{name}')