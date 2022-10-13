import streamlit as st
import csv
import numpy as np

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
try:
    votes = load_votes('votes')
except UnboundLocalError:
    st.write('No votes cast yet, initializing list.')
    votes = []
print(votes)
st.markdown('Tabletop session titles!')
for i in range(len(titles)):
    if st.checkbox(titles[i],key=f'{titles[i]}-{i}'):
        votes.append(titles[i])
        print(votes)
button_container = st.container()
# if button_container.button('Name (for duplicate prevention):'):
name = button_container.text_input('Name (for duplicate prevention):')
if button_container.button('Cast vote(s)'):
    with open('votes.csv','w') as f:
        writer = csv.writer(f)
        writer.writerow(votes)