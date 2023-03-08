import discord, random, re, time, csv, threading, asyncio
from datetime import datetime as dt
from datetime import timedelta as td
from discord.ext import commands
import collections
import pandas as pd
import math
import os
from dice import *
from difflib import SequenceMatcher
with open('../tok.txt') as f:
    token = f.readlines()[0]
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!',intents=intents)
client = discord.Client(intents=intents)
intents.members = True

#Checks message input to parse out AM or PM and adjust timestamping accordingly
def time_check(str):
    str = str.lower()
    ampm = ''
    if '.' in str:
        str = str.replace('.','')
    if 'm' in str:
        str = str.replace('m','')
    if 'a' in str:
        str = str.replace('a','')
        ampm = 'am'
    if 'p' in str:
        str = str.replace('p','')
        ampm = 'pm'
    str = str.strip()
    return str, ampm

#Second step of checking AM/PM, adds 12 to the hour when appropriate
def mid_noon(hour,ampm):
    hour = int(hour)
    if ampm == '':
        return hour
    elif ampm == 'am':
        if hour == 12:
            hour = 0
            return hour
        else:
            return hour
    elif ampm == 'pm':
        if hour == 12:
            return hour
        else:
            hour += 12
            return hour

def get_times():
    with open('sw.txt','r') as f:
        global sw_time
        sw_time = int(f.readlines()[0])
    with open('coc.txt','r') as f:
        global coc_time
        coc_time = int(f.readlines()[0])

#Pre-defined intervals for utility
debug = 5
minutes_15 = 900
one_hour = 3600
one_day = 86400
quarter_hours = [0,15,30,45]

@bot.event
async def on_ready():
    try:
        print('Awaiting orders, Captain.')
        server = bot.get_guild(399052850488934401)
        sw_channel = server.get_channel(801970982663225414)
        coc_channel = server.get_channel(794640287741902903)
        global coc_alert
        coc_alert = False
        global sw_alert
        sw_alert = False
        while True: 
            get_times()
            sw_alert_1 = sw_time-one_hour
            coc_alert_1 = coc_time-one_hour
            sw_alert_prev_day = (dt.fromtimestamp(sw_time)-td(1)).strftime('%d')
            coc_alert_prev_day = (dt.fromtimestamp(coc_time)-td(1)).strftime('%d')
            now = dt.now().timestamp()
            today = dt.now().strftime('%d')
            if (now > sw_alert_1) and (now < sw_time):
                await sw_channel.send(f'Star Wars <t:{sw_time}:R>!')
                await asyncio.sleep(one_hour)
            elif (int(dt.now().strftime('%H'))>=12) and (today==sw_alert_prev_day) and (sw_alert==False):
                sw_alert=True
                await sw_channel.send(f'Star Wars tomorrow, <t:{sw_time}:R>!')
            elif (now > coc_alert_1) and (now < coc_time):
                await coc_channel.send(f'Call of Cthulhu <t:{coc_time}:R>!')
                await asyncio.sleep(one_hour)
            elif (int(dt.now().strftime('%H'))>=12) and (today==coc_alert_prev_day) and (coc_alert==False):
                coc_alert=True
                await coc_channel.send(f'Call of Cthulhu <t:{coc_time}:R>!')
            if dt.now().minute not in quarter_hours:
                for i in range(len(quarter_hours)-1):
                    curr_minutes = dt.now().minute
                    if (quarter_hours[i]<curr_minutes) and (curr_minutes<quarter_hours[i+1]):
                        date_holder = dt.now()
                        year,month,day,hour = date_holder.year,date_holder.month,date_holder.day,date_holder.hour
                        sleep_time = (dt(year,month,day,hour,quarter_hours[i+1])-dt.now()).seconds
                        if sleep_time > 0:
                            await asyncio.sleep(sleep_time)
                        else:                    
                            await asyncio.sleep(60)
                    elif curr_minutes>quarter_hours[-1]:
                        date_holder = dt.now()
                        year,month,day,hour = date_holder.year,date_holder.month,date_holder.day,date_holder.hour
                        sleep_time = (dt(year,month,day,hour+1,quarter_hours[0])-dt.now()).seconds
                        if sleep_time > 0:
                            await asyncio.sleep(sleep_time)
                        else:
                            await asyncio.sleep(60)
            else:
                await asyncio.sleep(minutes_15)
    except TypeError:
        print(type(sw_time))
        print(type(coc_time))
        print(type(sw_alert_1))
        print(type(coc_alert_1))
        print(type(now))


#Checks to see if the user has a nickname or not
def name_check(ctx):
    try:
        if ctx.message.author.nick == None:
            sender = ctx.message.author.name
        else:
            sender = ctx.message.author.nick
    except AttributeError:
        sender = ctx.message.author.name
    return sender

#Loads titles from .csv file in case of bot interruption
def load_titles():
    with open('titles.csv',newline='') as f:
        reader = csv.reader(f,delimiter=',')
        i=0
        for row in reader:
            if i==0:
                titles_ = row
                i+=1
            else:
                pass
    return titles_

def sim_search(synt,df,search=False):
    similarities = {}
    for i in range(len(df)):
        word = df.iloc[i].name
        similarity = similar(synt,word)
        similarities[word] = similarity
    sdf = pd.DataFrame.from_dict(similarities,orient='index',columns=['sim'])
    sdf.sort_values(by='sim',ascending=False,inplace=True)
    if search:
        send = ', '.join(list(sdf.head(5).sim.index))
        return send
    else:
        found_tal = sdf.iloc[0].name
        return found_tal
    
def name_sim(player,players):
    if player.lower()=='bd':
        return 'BD'
    else:
        similarities = []
        for i in range(len(players)):
            word = players[i]
            similarity = similar(player,word)
            similarities.append((similarity,word))
        similarities.sort(reverse=True)
        name = similarities[0][1]
        if name == 'bd':
            return 'BD'
        else:
            return name.title()

#Easter egg from Rocky Horror Picture Show
@bot.command()
async def transvestite(ctx):
    await ctx.send('I see you shiver with antici...')
    await asyncio.sleep(5)
    await ctx.send('...pation!')

@bot.command()
async def set_gametime(ctx):
    game_and_time = (ctx.message.content)[14:]
    game_and_time, ampm = time_check(game_and_time)
    if game_and_time[0].lower()=='s':
        game = 'sw'
        time = game_and_time[2:]
        year,month,day_hour = time.split(sep='-')
        day, hour = day_hour.split(sep=' ')
        hour,minute = hour.split(sep=':')
        hour = mid_noon(hour,ampm)
        epoch = dt(int(year),int(month),int(day),int(hour),int(minute)).timestamp()
        new_time = int(epoch)
        with open(f'{game}.txt','w') as f:
            f.write(str(new_time))
        global sw_time
        sw_time = new_time
        global sw_alert
        sw_alert = False
        await ctx.send(f'Next Star Wars game at <t:{str(new_time)}>')
    elif game_and_time[0].lower()=='c':
        game='coc'
        time = game_and_time[3:]
        year,month,day_hour = time.split(sep='-')
        day, hour = day_hour.split(sep=' ')
        hour,minute = hour.split(sep=':')
        hour = mid_noon(hour,ampm)
        epoch = dt(int(year),int(month),int(day),int(hour),int(minute)).timestamp()
        new_time = int(epoch)
        with open(f'{game}.txt','w') as f:
            f.write(str(new_time))
        global coc_time
        coc_time = new_time
        global coc_alert
        coc_alert = False
        await ctx.send(f'Next Call of Cthulhu game at <t:{str(new_time)}>')


@bot.command()
async def stamp(ctx):
    time = ctx.message.content[7:]
    time, ampm = time_check(time)
    if len(time.split())==2:
        year,month,day_hour = time.split(sep='-')
        day, hour = day_hour.split(sep=' ')
        hour,minute = hour.split(sep=':')
        hour = mid_noon(hour,ampm)
        epoch = dt(int(year),int(month),int(day),int(hour),int(minute)).timestamp()
        new_time = int(epoch)
        await ctx.send(new_time)
    elif len(time.split(sep=':'))==2:
        hour,minute=time.split(sep=':')
        hour = mid_noon(hour,ampm)
        now=dt.now()
        new_time = int(dt(now.year,now.month,now.day,int(hour),int(minute)).timestamp())
        await ctx.send(str(new_time))

@bot.command()
async def day_convert(ctx):
    time = ctx.message.content[13:]
    time, ampm = time_check(time)
    hour,minute = time.split(sep=':')
    hour = mid_noon(hour,ampm)
    now = dt.now()
    new_time = int(dt(now.year,now.month,now.day,int(hour),int(minute)).timestamp())
    await ctx.send(f'<t:{new_time}:t>, <t:{new_time}:R>')


@bot.command()
async def gametime(ctx):
    game = (ctx.message.content)[10:]
    with open(f'{game}.txt','r') as f:
        time = f.readlines()[0]
    await ctx.send(f'Next {game} session is at <t:{time}>, <t:{time}:R>')

#Needed dictionary to store variables
dice_types = {
    'ability':ability,
    'proficiency':proficiency,
    'boost':boost,
    'difficulty':difficulty,
    'challenge':challenge,
    'setback':setback,
    'force':force
}

@bot.command()
async def roll(ctx):
    if ctx.message.author.nick == None:
        sender = ctx.message.author.name
    else:
        sender = ctx.message.author.nick
    raw = (ctx.message.content)[6:]
    number_and_die = [i.strip() for i in raw.split(',')]
    number = []
    die_ = []
    for i in number_and_die:
        substring = i.split(' ')
        number.append(int(substring[0]))
        die_type = dice_types[substring[1]]
        die_.append(die_type)
    result_ = roll_sw_dice(number,die_)
    await ctx.send(f'{sender} rolled {result_}')

#Kept in for legacy, but changing to work for Star Wars TTRPG
# @bot.command()
# async def roll(ctx):
#     #This check will assign a name for the bot to respond to. It can be removed so long as the 'sender' variable is removed from the return.
#     if ctx.message.author.nick == None:
#         sender = ctx.message.author.name
#     else:
#         sender = ctx.message.author.nick
#     diesearch = re.compile(r'(\d+)(d)*(\d*)([+/-]\d*)?', re.I)
#     userinput = ctx.message.content
#     diceformat = diesearch.search(userinput)
#     try:
#         diceformat[4] == None
#         modifier = int(diceformat[4][1:])
#         sign = diceformat[4][0]
#     except TypeError:
#         modifier = 0
#         sign = ''
#     if diceformat.group(2) is None:
#         dN = int(diceformat.group(1))
#         print(type(diceformat.group(0)))
#         dice = random.randint(1, dN)
#         print('-' in diceformat.group(0))
#         if '-' in diceformat.group(0):
#             await ctx.send(sender + ' rolled ' + str(dice - modifier) + ' from a d' + str(dN - modifier) + '!')
#         elif '+' in diceformat.group(0):
#             await ctx.send(sender + ' rolled ' + str(dice + modifier) + ' from a d' + str(dN + modifier) + '!')
#         else:
#             await ctx.send(sender + ' rolled ' + str(dice) + ' from a d' + str(dN) + '!')
#     elif diceformat.group(3) == '':
#         sign = diceformat[4][0]
#         dN = int(diceformat.group(1))
#         dice = random.randint(1, dN)
#         if sign == '-':
#             await ctx.send(sender + ' rolled ' + str(dice - modifier) + ' from a d' + str(dN - modifier) + '!')
#         else:
#             await ctx.send(sender + ' rolled ' + str(dice + modifier) + ' from a d' + str(dN + modifier) + '!')        
#     else:
#         dN = int(diceformat.group(3))
#         multiplier = int(diceformat.group(1))
#         amt = 0
#         for _ in range(multiplier):
#             amt += random.randint(1, dN)
#         if sign == '-':
#             await ctx.send(sender + ' rolled ' + str(amt - modifier) + ' out of a possible ' + str((dN * multiplier)-modifier) + '!')
#         else:
#             await ctx.send(sender + ' rolled ' + str(amt + modifier) + ' out of a possible ' + str((dN * multiplier)+modifier) + '!')

@bot.command()
async def pick(ctx):
    listmake = (re.compile(r'[^,]*'))
    choices = listmake.findall(str(ctx.message.content))
    cleanedchoices = []
    if len(choices) == 2:
        await ctx.send("Captain, I am unable to make a choice without a choice.")
    else:
        cleanedchoices.append((choices[0]).split()[1])
        for i in range(len(choices)):
            if choices[i] != '' and '.pick' not in choices[i]:
                stripped = choices[i].strip()
                cleanedchoices.append(stripped)
        if ctx.message.author.nick == None:
            picker = ctx.message.author.name
        else:
            picker = ctx.message.author.nick
        await ctx.send(picker + ' has randomly chosen ' + random.choice(cleanedchoices) + '!')

entrants = []
showtitles = {}
votes = []
index = 1

@bot.command()
async def refresh(ctx):
    global votes
    votes = []
    with open('titles.csv','w') as f:
        writer = csv.writer(f)
        writer.writerow('')
    with open('vote_hist.csv','w') as f:
        writer = csv.writer(f)
        writer.writerow('')
    with open('votes.csv','w') as f:
        writer = csv.writer(f)
        writer.writerow('')
    sender = name_check(ctx)
    global vote_hist
    vote_hist = []
    await ctx.send(f'List purged, Captain {sender}.')

@bot.command()
async def s(ctx):
    sender = name_check(ctx)
    title = (ctx.message.content)[3:]
    titles = load_titles()
    titles.append(title)
    with open('titles.csv','w') as f:
        writer = csv.writer(f)
        writer.writerow(titles)
    await ctx.send('Title added, Captain ' + sender)

@bot.command()
async def titles(ctx):
    titles_ = load_titles()
    title_list = []
    for i in range(len(titles_)):
        title_list.append(str(i+1)+': '+str(titles_[i]))
    await ctx.send('\n'.join(title_list))


@bot.command()
async def tirer(ctx):
    if entrants != []:
        if str(ctx.message.author) == 'TaliZorEl#0331':
            winner = random.choice(entrants)
            await ctx.send('%s a gagné. Félicitations!!!' % winner.mention)
        else:
            await ctx.send(file=discord.File('D:\Python\\jpno.gif'))
    else:
        await ctx.send('La liste est vide.')

@bot.command()
async def clearlist(ctx):
    if str(ctx.message.author) == 'TaliZorEl#0331':
        global entrants
        entrants = []
        await ctx.send('Liste supprimée.')       
    else:
        await ctx.send(file=discord.File('D:\Python\\visageno.gif'))


@bot.command(pass_context=True)
async def coc(ctx):
    talia = await ctx.guild.fetch_member(183026490890256384)
    heather = await ctx.guild.fetch_member(213737842625609730)
    angela = await ctx.guild.fetch_member(220377751906025472)
    james = await ctx.guild.fetch_member(286536094990729216)
    jason = await ctx.guild.fetch_member(171473872078635015)
    await jason.edit(nick='Alan')
    await talia.edit(nick='Anii')
    await heather.edit(nick='Siobhan')
    await angela.edit(nick='Kenzo')
    await james.edit(nick='Tom')

@bot.command(pass_context=True)
async def dnd(ctx):
    talia = await ctx.guild.fetch_member(183026490890256384)
    heather = await ctx.guild.fetch_member(213737842625609730)
    jeannie = await ctx.guild.fetch_member(213789322309009418)
    angela = await ctx.guild.fetch_member(220377751906025472)
    james = await ctx.guild.fetch_member(286536094990729216)
    await talia.edit(nick='Eth')
    await jeannie.edit(nick='Lu')
    await heather.edit(nick='Ori')
    await angela.edit(nick='Wil')
    await james.edit(nick='Adisi')

@bot.command(pass_context=True)
async def sw(ctx):
    talia = await ctx.guild.fetch_member(183026490890256384)
    heather = await ctx.guild.fetch_member(213737842625609730)
    jeannie = await ctx.guild.fetch_member(213789322309009418)
    angela = await ctx.guild.fetch_member(220377751906025472)
    james = await ctx.guild.fetch_member(286536094990729216)
    await talia.edit(nick='Virai')
    await heather.edit(nick='Khaylia')
    await angela.edit(nick='Kavin')
    await james.edit(nick='Cho')
    await jeannie.edit(nick='Culkoo')

@bot.command(pass_context=True)
async def dnd2(ctx):
    estrolof = await ctx.guild.fetch_member(465335472995041291)
    heather = await ctx.guild.fetch_member(213737842625609730)
    raj = await ctx.guild.fetch_member(204817747983466497)
    peregryn = await ctx.guild.fetch_member(204816776326807553)
    beans = await ctx.guild.fetch_member(204076896059785225)
    mike = await ctx.guild.fetch_member(147036443120762880)
    await estrolof.edit(nick='DM - Estrolof')
    await heather.edit(nick="Roan'Myra Torian")
    await raj.edit(nick='Larkin Blacksilver')
    await peregryn.edit(nick='Syndra Greybane')
    await beans.edit(nick='Gronn Madmun')
    await mike.edit(nick='Kira Longbrooke')

@bot.command(pass_context=True)
async def vote(ctx):
    sender = name_check(ctx)
    vote = ctx.message.content[6:]
    vote_entry = f'{sender}-{vote}'
    with open("vote_hist.csv",'r') as f:
        reader = csv.reader(f,delimiter=',')
        i=0
        for row in reader:
            if i==0:
                vote_hist = row
                i+=1
            else:
                pass
    try:
        if vote_entry in vote_hist:
            await ctx.send(f'You have already voted for that title, Captain {sender}.')
        else:
            numvote = int(vote)
            votes.append(numvote)
            with open('votes.csv','w') as f:
                writer = csv.writer(f)
                writer.writerow(votes)
            vote_hist.append(vote_entry)
            with open('vote_hist.csv','w') as f:
                writer = csv.writer(f)
                writer.writerow(vote_hist)
            await ctx.send(f'Vote recorded, Captain {sender}.')
    except ValueError:
        await ctx.send(f'That is not a number, Captain {sender}.')

@bot.command(pass_context=True)
async def votecount(ctx):
    with open("votes.csv",'r') as f:
        reader = csv.reader(f,delimiter=',')
        j=0
        for row in reader:
            if j==0:
                votes_ = row
                j+=1
            else:
                pass
    votecount = collections.Counter(votes_)
    showtitles = load_titles()
    df = pd.Series(votecount).sort_values(ascending=False)
    send_titles = [f'{df.iloc[i]}: {showtitles[int(df.index[i])-1]}' for i in range(len(df))]
    await ctx.send('\n'.join(send_titles))

@bot.command(pass_context=True)
async def stim(ctx):
    df = pd.read_csv('stims.csv',encoding='utf-8',index_col=['Name'])
    synt = (ctx.message.content[6:]).lower()
    pc_list = ['Kavin', 'Virai', 'Khaylia', 'Culkoo', 'Okchota', 'Doc']
    pcs = [name.lower() for name in pc_list]
    name = name_sim(synt,pcs)
    old = df.loc[name].Status
    new = old+1
    df.loc[name].Status=new
    df.to_csv('stims.csv',encoding='utf-8')
    await ctx.send(f'{name} stimmed, {5-new} left.')

@bot.command(pass_context=True)
async def undo(ctx):
    df = pd.read_csv('stims.csv',encoding='utf-8',index_col=['Name'])
    synt = (ctx.message.content[6:]).lower()
    pc_list = ['Kavin', 'Virai', 'Khaylia', 'Culkoo', 'Okchota', 'Doc']
    pcs = [name.lower() for name in pc_list]
    name = name_sim(synt,pcs)
    old = df.loc[name].Status
    new = old-1
    df.loc[name].Status=new
    df.to_csv('stims.csv',encoding='utf-8')
    await ctx.send(f'Stim removed from {name}, {5-new} left.')
 
@bot.command(pass_context=True)
async def heal(ctx):
    df = pd.read_csv('stims.csv',index_col=['Name'])
    for ele in list(df.index):
        df.loc[ele]=0
    df.to_csv('stims.csv')
    await ctx.send('Party refreshed.')    

@bot.command(pass_context=True)
async def status(ctx):
    synt = ctx.message.content[8:]
    df = pd.read_csv('stims.csv',index_col=['Name'])
    pc_list = ['Kavin', 'Virai', 'Khaylia', 'Culkoo', 'Okchota', 'Doc']
    if synt == '':
        mess = []
        for pc in pc_list:
            mess.append(f'{pc} has been stimmed {df.loc[pc].Status} time(s), {5-df.loc[pc].Status} jab(s) remaining.')
        await ctx.send('\n'.join(mess))
    else:
        pcs = [ele.lower() for ele in pc_list]
        name = name_sim(synt.lower(),pcs)
        await ctx.send(f'{name} has been stimmed {df.loc[name].Status} time(s), {5-df.loc[name].Status} jab(s) remaining.')

@bot.command(pass_context=True)
async def crit(ctx):
    rating = int((ctx.message.content)[6:])
    df = pd.read_csv('crits.csv')
    divided = rating/5
    if divided <= 26 and rating%5!=0:
        await ctx.send('Range: '+df.iloc[math.floor(divided)]['Rating']+'\nSeverity: '+str(df.iloc[math.floor(divided)]['Severity'])+'\nResult: '+df.iloc[math.floor(divided)]['Result']+'\nDetails: '+df.iloc[math.floor(divided)]['Details'])
    elif divided <= 26 and rating%5==0:
        await ctx.send('Range: '+df.iloc[math.floor(divided-1)]['Rating']+'\nSeverity: '+str(df.iloc[math.floor(divided-1)]['Severity'])+'\nResult: '+df.iloc[math.floor(divided-1)]['Result']+'\nDetails: '+df.iloc[math.floor(divided-1)]['Details'])
    elif divided > 26 and divided <= 28 and rating%5!=0:
        await ctx.send('Range: '+df.iloc[26]['Rating']+'\nSeverity: '+str(df.iloc[26]['Severity'])+'\nResult: '+df.iloc[26]['Result']+'\nDetails: '+df.iloc[26]['Details'])
    elif divided > 26 and divided <= 28 and rating%5==0:
        await ctx.send('Range: '+df.iloc[26]['Rating']+'\nSeverity: '+str(df.iloc[26]['Severity'])+'\nResult: '+df.iloc[26]['Result']+'\nDetails: '+df.iloc[26]['Details'])
    elif divided >28 and divided <= 30 and rating%5!=0:
        await ctx.send('Range: '+df.iloc[27]['Rating']+'\nSeverity: '+str(df.iloc[27]['Severity'])+'\nResult: '+df.iloc[27]['Result']+'\nDetails: '+df.iloc[27]['Details'])
    elif divided >28 and divided <= 30 and rating%5==0:
        await ctx.send('Range: '+df.iloc[27]['Rating']+'\nSeverity: '+str(df.iloc[27]['Severity'])+'\nResult: '+df.iloc[27]['Result']+'\nDetails: '+df.iloc[27]['Details'])
    elif divided > 30:
        await ctx.send('Range: '+df.iloc[28]['Rating']+'+\nSeverity: '+str(df.iloc[28]['Severity'])+'\nResult: '+df.iloc[28]['Result']+'\nDetails: '+df.iloc[28]['Details'])
    else:
        await ctx.send("Somethin' ain't right.")

@bot.command(pass_context=True)
async def critchara(ctx):
    critrate = random.randint(0,101)
    if critrate < 31:
        await ctx.send(str(critrate) + ', Brawn')
    elif critrate < 61 and critrate > 30:
        await ctx.send(str(critrate) + ', Agility')
    elif critrate < 71 and critrate > 60:
        await ctx.send(str(critrate) + ', Intellect')
    elif critrate < 81 and critrate > 70:
        await ctx.send(str(critrate) + ', Cunning')
    elif critrate < 91 and critrate > 80:
        await ctx.send(str(critrate) + ', Presence')
    elif critrate < 101 and critrate > 90:
        await ctx.send(str(critrate) + ', Willpower')
    else:
        await ctx.send('What the fuck is happening?')

@bot.command(pass_context=True)
async def quality(ctx):
    df = pd.read_csv('qualities.csv',index_col=['Quality'])
    qual = ctx.message.content[9:].title()
    if qual == '':
        quals = list(df.index)
        qualsep = [quals[i] for i in range(len(quals))]
        await ctx.send('\n'.join(qualsep))
    elif df.loc[qual]['Activation']=='Passive':
        await ctx.send(df.loc[qual].name + '\n'+df.loc[qual]['Activation']+'\n'+df.loc[qual]['Description'])
    elif df.loc[qual]['Activation']=='1':
        await ctx.send(df.loc[qual].name + '\nActivation: '+df.loc[qual]['Activation']+' Advantage\n'+df.loc[qual]['Description'])
    else:
        await ctx.send(df.loc[qual].name + '\nActivation: '+df.loc[qual]['Activation']+' Advantages\n'+df.loc[qual]['Description'])

@bot.command(pass_context=True)
async def talent(ctx):
    master = pd.read_csv('master_talents.csv',index_col=['Talent'])
    synt = ctx.message.content[8:]
    if '?' in synt:
        res = sim_search(synt,master,search=True)
        await ctx.send(f'The top 5 results matching your criteria are as follows: {res}')
    else:
        talent = sim_search(synt,master)
        entry = master.loc[talent]
        name = entry.name
        act = entry.Activation
        desc = entry.Description
        ranked = entry.Ranked
        link = entry.link
        if act == 'Force Ability':
            await ctx.send(f'Talent: {name}\nActivation: {act}\nRanked: {ranked}\nDescription: {desc}\nLink: <{link}>\nFor more detailed information use !force {name}')
        elif act == 'Signature Ability':
            await ctx.send(f'Talent: {name}\nActivation: {act}\nRanked: {ranked}\nDescription: {desc}\nLink: <{link}>\nFor more detailed information use !sig {name}')
        else:
            await ctx.send(f'Talent: {name}\nActivation: {act}\nRanked: {ranked}\nDescription: {desc}\nLink: <{link}>')

@bot.command(pass_context=True)
async def sig(ctx):
    df = pd.read_csv('signature_abilities_expanded.csv',encoding='utf-8',index_col='Talent')
    synt = ctx.message.content[5:]
    tal = sim_search(synt,df)
    cut = df.loc[tal]
    link = cut.link
    if cut.imp:
        cols = ['top1', 'top2', 'top3', 'top4', 'bot1', 'bot2', 'bot3', 'bot4']
        desc = ['top1_desc', 'top2_desc', 'top3_desc', 'top4_desc', "bot1_desc", 'bot2_desc', 'bot3_desc' ,'bot4_desc']
        mess = []
        for i in range(len(cols)):
            if 'top' in cols[i]:
                mess.append(f'Top slot {i+1}: {cut[cols[i]]} - {cut[desc[i]]}')
            elif 'bot' in cols[i]:
                mess.append(f'Bottom slot {i+1}: {cut[cols[i]]} - {cut[desc[i]]}')
        await ctx.send(f'{tal}\nBase: {cut.Base}\nAssociated career: {cut.Career}\n'+'\n'.join(mess)+f'\nMore: <{link}>')
    else:
        with open('to_add.txt','a') as f:
            f.writelines(f'\n{tal}')
        await ctx.send(f'{tal} is not yet implemented, it has been appended to the list for Talia to add. Here is the link: {link}')

@bot.command(pass_context=True)
async def force(ctx):
    df = pd.read_csv('force_abilities_expanded.csv',encoding='utf-8',index_col='Talent')
    synt = ctx.message.content[7:]
    tal = sim_search(synt,df)
    cut = df.loc[tal].copy()
    link = cut.link
    if cut.imp:
        cut.dropna(inplace=True)
        cut.drop('imp',axis=0,inplace=True)
        base = cut.Base
        grid = [ele for ele in list(cut.index) if ele[-1].isnumeric()]
        mess = []
        for loc in grid:
            desc = f'{loc}-desc'
            mess.append(f'Row {loc[1]} Spot {loc[3]}: {cut[loc]} - {cut[desc]}')
        raw_send_message = f'{tal}\nBase: {base}\n'+'\n'.join(mess)+f'\nLink: <{link}>'
        if len(raw_send_message) < 2000:
            await ctx.send(raw_send_message)
        else:
            splitpoint = int(len(mess)/2)
            await ctx.send(f'{tal}\nBase: {base}\n'+'\n'.join(mess[:splitpoint]))
            await ctx.send('\n'.join(mess[splitpoint:])+f'\nLink: <{link}>')
    else:
        with open('to_add.txt','a') as f:
            f.writelines(f'\n{tal}')
        await ctx.send(f'{tal} is not yet implemented, it has been appended to the list for Talia to add. Here is the link: {link}')  

@bot.command(pass_context=True)
async def pc(ctx):
    master = pd.read_csv('master_talents.csv',index_col=['Talent'])
    synt = ctx.message.content[4:].lower().split()
    if len(synt) ==1:
        pc = synt[0]
        rank = pd.read_csv('ranked_talents.csv',encoding='utf-8')
        pcs = [name.lower() for name in list(rank.columns)]
        name = name_sim(pc,pcs)
        unrank = pd.read_csv('unranked_talents.csv',encoding='utf-8')
        ranktals = list(rank[rank[name]!=0].Talent.values)
        unranktals = list(unrank[unrank[name]=='True'].Talent.values)
        force = pd.read_csv('force_ranks.csv',encoding='utf-8',index_col=['Talent','grid'])
        sigranks = pd.read_csv('sigranks.csv',encoding='utf-8',index_col=['Talent','loc'])
        forcetals = list((force[name][:,'base'])[force[name][:,'base']].index)
        sigtals = list((sigranks[name][:,'base'])[sigranks[name][:,'base']].index)
        all_tals = ranktals+unranktals+forcetals+sigtals
        all_tals.sort()
        to_send = '\n'.join(all_tals)
        await ctx.send(f'{name} has these talents:\n{to_send}')
    else:
        pc,raw_tal = synt[0],' '.join(synt[1:])
        tal = sim_search(raw_tal,master)
        ranked,force,comp = master.loc[tal].rankbool,master.loc[tal].Force,master.loc[tal].comp
        pc_list = ['Kavin', 'Virai', 'Khaylia', 'Culkoo', 'Okchota', 'Doc'] ##TODO: write this and timestamps to shelf
        pcs = [name.lower() for name in pc_list]
        name = name_sim(pc,pcs)
        if force and comp:
            df = pd.read_csv('force_ranks.csv',encoding='utf-8',index_col=['Talent','grid'])
            view = df.loc[tal][name]
            if view.base:
                if True not in view.drop('base',axis=0).unique():
                    await ctx.send(f'{name} has just the basic ability for {tal}.')
                else:
                    filt = view[view].index[1:]
                    force_ref = (pd.read_csv('force_abilities_expanded.csv',encoding='utf-8',index_col='Talent')).loc[tal][filt]
                    have_tals = force_ref.values 
                    mess = []
                    for i in range(len(filt)):
                        mess.append(f'{have_tals[i]} from Row {filt[i][1]} Spot {filt[i][3]}')
                    await ctx.send(f'In addition to the base ability, {name} has:\n'+'\n'.join(mess))
            else:
                await ctx.send(f'{name} does not have {tal}.')
        elif force!=True and comp:
            df = pd.read_csv('sigranks.csv',encoding='utf-8',index_col=['Talent','loc'])
            view = df.loc[tal][name]
            if view['base']:
                locs=list(view[view].index[1:])
                if locs==[]:
                    await ctx.send(f'{name} has just the base ability for {tal}')
                else:
                    sigex = pd.read_csv('signature_abilities_expanded.csv',encoding='utf-8',index_col='Talent')
                    ups = list(sigex.loc[tal][locs].values)
                    locs = [loc.replace('bot','bottom') for loc in locs]
                    mess = []
                    for i in range(len(locs)):
                        mess.append(f'{ups[i]} from {locs[i][:-1]} slot {locs[i][-1]}')
                    await ctx.send(f'{name} has:\n' + '\n'.join(mess) + f'\nin addition to the base ability of {tal}.')
            else:
                await ctx.send(f'{name} does not have {tal}.')
        elif ranked:
            df = pd.read_csv('ranked_talents.csv',encoding='utf-8',index_col=['Talent'])
            ranks = df.loc[tal][name]
            if ranks == 1:
                plur = 'rank'
            else:
                plur = 'ranks'
            await ctx.send(f'{name} has {ranks} {plur} in {tal}.')
        else:
            df = pd.read_csv('unranked_talents.csv',encoding='utf-8',index_col=['Talent'])
            if df.loc[tal][name]=='True':
                await ctx.send(f'{name} has {tal}.')
            else:
                await ctx.send(f'{name} does not have {tal}.')
        
@bot.command(pass_context=True)
async def upgrade(ctx):
    synt = ctx.message.content[9:].split()
    pc_list = ['Kavin', 'Virai', 'Khaylia', 'Culkoo', 'Okchota', 'Doc']
    pcs = [name.lower() for name in pc_list]
    for ele in synt[1:]:
        if ele[0].isnumeric():
            loc = ele
            synt.remove(ele)
            break
        else:
            loc = None
    name = name_sim(synt[0],pcs)
    master = pd.read_csv('master_talents.csv',index_col=['Talent'])
    tal = sim_search(' '.join(synt[1:]),master)
    ranked,force,comp = master.loc[tal].rankbool,master.loc[tal].Force,master.loc[tal].comp
    if force and comp:
        df = pd.read_csv('force_ranks.csv',encoding='utf-8',index_col=['Talent','grid'])
        if loc == None:
            loc = 'base'
            if df.loc[tal,loc][name]:
                await ctx.send(f'{name} already has the base ability for {tal}.')
            else:
                df.loc[tal,loc][name] = True
                df.to_csv('force_ranks.csv',encoding='utf-8')
                await ctx.send(f'{name} now has the base ability for {tal}.')
        else:
            fref = pd.read_csv('force_abilities_expanded.csv',encoding='utf-8',index_col='Talent') 
            loc = f't{loc}'
            up = fref.loc[tal][loc]
            if df.loc[tal,loc][name]:
                await ctx.send(f'{name} already has {up} in Row {loc[1]} Slot {loc[3]} of {tal}.')
            else:
                df.loc[tal,loc][name] = True
                df.to_csv('force_ranks.csv',encoding='utf-8')
                await ctx.send(f'{name} now has {up} in Row {loc[1]} Slot {loc[3]} of {tal}.')
    elif force!=True and comp:
        df = pd.read_csv('sigranks.csv',encoding='utf-8',index_col=['Talent','loc'])
        if loc == None:
            loc = 'base'
            if df.loc[tal,loc][name]:
                await ctx.send(f'{name} already has the base ability for {tal}.')
            else:
                df.loc[tal,loc][name] = True
                df.to_csv('sigranks.csv',encoding='utf-8')
                await ctx.send(f'{name} now has the base ability for {tal}.')
        else:
            sref = pd.read_csv('signature_abilities_expanded.csv',encoding='utf-8',index_col='Talent')
            if sref.loc[tal].imp:
                if loc[0]=='1':
                    loc = loc.replace('1.','top')
                    row = 'top'
                else:
                    loc = loc.replace('2.','bot')
                    row = 'bottom'
                up = sref.loc[tal][loc]
                if df.loc[tal,loc][name]:
                    await ctx.send(f'{name} already has {up} in the {row} slot {loc[-1]} for {tal}.')
                else:
                    df.loc[tal,loc][name] = True
                    df.to_csv('sigranks.csv',encoding='utf-8')
                    await ctx.send(f'{name} now has {up} in the {row} slot {loc[-1]} for {tal}.')
            else:
                with open('to_add.txt','a') as f:
                    f.writelines(f'\n{tal}')
                await ctx.send(f'{tal} is not yet implemented, it has been appended to the list for Talia to add.')
    elif ranked:
        df = pd.read_csv('ranked_talents.csv',encoding='utf-8',index_col='Talent')
        rank = int(df.loc[tal][name])+1
        df.loc[tal][name] = rank
        df.to_csv('ranked_talents.csv',encoding='utf-8')
        if rank == 1:
            await ctx.send(f'{name} now has {rank} rank in {tal}.')
        else:
            await ctx.send(f'{name} now has {rank} ranks in {tal}.')
    elif ranked != True:
        df = pd.read_csv('unranked_talents.csv',encoding='utf-8',index_col='Talent')
        if df.loc[tal][name]:
            await ctx.send(f'{name} already has {tal}.')
        else:
            df.loc[tal][name]=True
            df.to_csv('unranked_talents.csv',encoding='utf-8')
            await ctx.send(f'{name} now has {tal}.')
    else:
        await ctx.send('There was an error with either the input or programming.')

@bot.command(pass_context=True)
async def downgrade(ctx):
    synt = ctx.message.content[11:].split()
    pc_list = ['Kavin', 'Virai', 'Khaylia', 'Culkoo', 'Okchota', 'Doc']
    pcs = [name.lower() for name in pc_list]
    for ele in synt[1:]:
        if ele[0].isnumeric():
            loc = ele
            synt.remove(ele)
            break
        else:
            loc = None
    name = name_sim(synt[0],pcs)
    master = pd.read_csv('master_talents.csv',index_col=['Talent'])
    tal = sim_search(' '.join(synt[1:]),master)
    ranked,force,comp = master.loc[tal].rankbool,master.loc[tal].Force,master.loc[tal].comp
    if force and comp:
        df = pd.read_csv('force_ranks.csv',encoding='utf-8',index_col=['Talent','grid'])
        if loc == None:
            loc = 'base'
            if df.loc[tal,loc][name]:
                df.loc[tal,loc][name] = False
                df.to_csv('force_ranks.csv',encoding='utf-8')
                await ctx.send(f'{tal} base ability removed from repertoire of {name}.')
            else:
                await ctx.send(f'{name} already does not have the base ability for {tal}.')
        else:
            fref = pd.read_csv('force_abilities_expanded.csv',encoding='utf-8',index_col='Talent') 
            loc = f't{loc}'
            up = fref.loc[tal][loc]
            if df.loc[tal,loc][name]:
                df.loc[tal,loc][name] = False
                df.to_csv('force_ranks.csv',encoding='utf-8')
                await ctx.send(f'{up} in Row {loc[1]} Slot {loc[3]} of {tal} removed from repertoire of {name}.')
            else:
                await ctx.send(f'{name} already does not have {up} in Row {loc[1]} Slot {loc[3]} of {tal}.')
    elif force!=True and comp:
        df = pd.read_csv('sigranks.csv',encoding='utf-8',index_col=['Talent','loc'])
        if loc == None:
            loc = 'base'
            if df.loc[tal,loc][name]:
                df.loc[tal,loc][name] = False
                df.to_csv('sigranks.csv',encoding='utf-8')
                await ctx.send(f'{tal} base ability removed from repertoire of {name}.')
            else:
                await ctx.send(f'{name} already does not have the base ability for {tal}.')
        else:
            sref = pd.read_csv('signature_abilities_expanded.csv',encoding='utf-8',index_col='Talent')
            if sref.loc[tal].imp:
                if loc[0]=='1':
                    loc = loc.replace('1.','top')
                    row = 'top'
                else:
                    loc = loc.replace('2.','bot')
                    row = 'bottom'
                up = sref.loc[tal][loc]
                if df.loc[tal,loc][name]:
                    row = row.title()
                    df.loc[tal,loc][name] = True
                    df.to_csv('sigranks.csv',encoding='utf-8')
                    await ctx.send(f'{row} slot {loc[-1]} for {tal} removed from repertoire of {name}.')
                else:
                    await ctx.send(f'{name} already does not have {up} in the {row} slot {loc[-1]} for {tal}.')
            else:
                with open('to_add.txt','a') as f:
                    f.writelines(f'\n{tal}')
                await ctx.send(f'{tal} is not yet implemented, it has been appended to the list for Talia to add.')
    elif ranked:
        df = pd.read_csv('ranked_talents.csv',encoding='utf-8',index_col='Talent')
        rank = int(df.loc[tal][name])-1
        if rank<0:
            rank=0
        df.loc[tal][name] = rank
        df.to_csv('ranked_talents.csv',encoding='utf-8')
        if rank == 1:
            await ctx.send(f'{name} now has {rank} rank in {tal}.')
        else:
            await ctx.send(f'{name} now has {rank} ranks in {tal}.')
    elif ranked != True:
        df = pd.read_csv('unranked_talents.csv',encoding='utf-8',index_col='Talent')
        if df.loc[tal][name]:
            df.loc[tal][name]=False
            df.to_csv('unranked_talents.csv',encoding='utf-8')
            await ctx.send(f'{tal} removed from repertoire of {name}.')
        else:
            await ctx.send(f'{name} already does not have {tal}.')
    else:
        await ctx.send('There was an error with either the input or programming.')

command_descriptions = {
    'vote':'Vote for a number in the title list. You can vote for higher numbers that are not in the list, but why would you do that? !vote [title number]',
    'stim':'!stim [name], will add one stimpack use to this character and tell you how many more can be used on them.',
    'undo':'Accidentally stim someone? Reverse it with !undo [name]',
    'status':'!status [name] provides the current amount of stimpacks that have been used and are remaining for that character.',
    'heal':'Clear everyone of all stimpack uses. Resets all to 0',
    'crit':'!crit [crit rating]. Input a number to find out what the description and severity a crit of that number has.',
    'critchara':'Get a crit that affects a random characteristic? Find out which one with !critchara',
    'quality':'Provides a description of an item quality, whether it is passive or active, and what is needed to trigger it if relevant.\nType !quality [quality name] to get a description or just !quality if you want a list of all of them.',
    'talent':'Provides a description of a talent.\n!talent [talent] will give you a description of that talent and relevant information.',
    'pc':'Provides information about a certain PC (or BD).\n!pc [name] will list all the talents for the character.\n!pc [name] [talent] will tell you if the pc has that ability or not, and the current rank if relevant. If the talent is a signature or force ability that is not the base description, then you will also need to provide the coordinates for the talent in the form of [row].[spot] with the row count starting from the first row below the base ability then the spot count starting with the first ability from the left of the row. ',
    'upgrade':'Rank up or add a talent. !upgrade [name] [talent] [coordinates-if needed for signature or force ability]',
    'downgrade':'Rank down or remove a talent. !downgrade [name] [talent] [coordinates-if needed for signature or force ability]',
    'weapon':'Look up stats for a weapon !weapon [weapon] or search for similar names with !weapon search [search term]',
    'armor':'Look up stats for armor !armor [armor] or search for similar name with !armor search [search term]'
}

@bot.command(pass_context=True)
async def bothelp(ctx):
    synt = ctx.message.content[9:].lower()
    botcommands = ['vote','stim','undo','status','heal','crit','critchara','quality','talent','pc','upgrade','downgrade']
    if synt=='':
        await ctx.send('Here is a list of the commands you can use:\nvote\nstim\nundo\nheal\ncrit\ncritchara\nquality\ntalent\npc\nupgrade\ndowngrade\n\nIf a command asks for your name, you only need to provide enough spelling to differentiate yourself, it will search for the closest match.\nFor more information on a command, type !bothelp then the command.')
    elif synt in botcommands:
        await ctx.send(command_descriptions[synt])
    else:
        await ctx.send('I believe you have a typo, Captain.')

@bot.command(pass_context=True)
async def weapon(ctx):
    df = pd.read_csv('weapons.csv',index_col=['Weapon']).fillna('N/A')
    wep = ctx.message.content[8:]
    similarities = {}
    for i in range(len(df)):
        word = df.iloc[i].name
        similarity = similar(wep,word)
        similarities[word] = similarity
    sdf = pd.DataFrame.from_dict(similarities,orient='index',columns=['sim'])
    if wep.split()[0]=='search' or wep.split()[0]=='Search':
        top_five = []
        for i in range(5):
            top_five.append(sdf.sort_values(by='sim',ascending=False).iloc[i].name)
        await ctx.send('Top five closest matches:\n'+'\n'.join(top_five)) 
    else:
        found_wep = sdf.sort_values(by='sim',ascending=False).iloc[0].name
        cols = df.columns
        send_lines = [col+': '+df.loc[found_wep][col] for col in cols]
        await ctx.send(found_wep+':\n'+'\n'.join(send_lines))  

@bot.command(pass_context=True)
async def armor(ctx):
    df = pd.read_csv('armor.csv',index_col=['Armour']).fillna('N/A')
    armor = ctx.message.content[7:]
    similarities = {}
    for i in range(len(df)):
        word = df.iloc[i].name
        similarity = similar(armor,word)
        similarities[word] = similarity
    sdf = pd.DataFrame.from_dict(similarities,orient='index',columns=['sim']).sort_values(by='sim',ascending=False)
    if armor.split()[0]=='search' or armor.split()[0]=='Search':
        top_five = []
        for i in range(5):
            top_five.append(sdf.iloc[i].name)
        await ctx.send('Top five closest matches:\n'+'\n'.join(top_five)) 
    else:
        found_armor = sdf.iloc[0].name
        cols = df.columns
        send_lines = [str(col)+': '+str(df.loc[found_armor][col]) for col in cols]
        await ctx.send(found_armor+':\n'+'\n'.join(send_lines))  

#Next two commands are utility for finding out user and server information. They will print to the console, not send anywhere on the server
@bot.command()
async def info(ctx):
    print(ctx.message.author)
    print(ctx.message.author.name)

@bot.command(pass_context=True)
async def userinfo(ctx):
    guild_id = ctx.message.guild.id
    channel = ctx.message.channel.id
    guild = bot.get_guild(guild_id)
    print(guild)
    print(channel)
    async for member in guild.fetch_members(limit=150):
        print(member.name)
        print(member.id)
        print(ctx.message.channel)
        print(ctx.message.guild)
        channel = ctx.message.channel
        channel

bot.run(f'{token}')