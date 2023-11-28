import discord, random, re, asyncio, shelve,collections,sys, os
from datetime import datetime as dt
from datetime import timedelta as td
from discord.ext import commands#, utils
import pandas as pd
from dice import *
from difflib import SequenceMatcher
#Bot token saved in a .txt flie in the containing directory, which is not in the repository. This is a security feature--if you publish your bot token on Github, Discord will revoke it immediately
with open('../tok.txt') as f:
    token = f.readlines()[0]
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!',intents=intents)
client = discord.Client(intents=intents)
intents.members = True

wiki_df = pd.read_csv('wiki.csv',encoding='utf-8',index_col='Entry')
wiki_df = wiki_df[['body','status']]
wiki_topics = wiki_df.index.tolist()
done_df,prog_df = wiki_df[wiki_df['status']=='Complete'],wiki_df[wiki_df['status']=='In Progress']
done_entries,prog_entries = [t.lower().strip() for t in done_df.index.tolist()],[t.lower().strip() for t in prog_df.index.tolist()]
global wiki_log
wiki_log = []

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
    with shelve.open('vars') as f:
        global sw_time
        sw_time = f['star wars']
        global coc_time
        coc_time = f['call of cthulhu']

def get_channel(game):
    with shelve.open('vars') as f:
        game_dic = f['game_dic']
    channel_id = game_dic[game][0]
    guild_id = game_dic[game][1]
    guild = bot.get_guild(guild_id)
    channel = guild.get_channel(channel_id)
    return channel

#Pre-defined intervals for utility
debug = 5
minutes_15 = 900
one_hour = 3600
one_day = 86400
quarter_hours = [0,15,30,45]

@bot.event
async def on_ready():
    print('Awaiting orders, Captain.')
    sw_channel = get_channel('sw')
    coc_channel = get_channel('coc')
    if len(sys.argv)>1:
        if sys.argv[1]=='quiet':
            coc_alert = True
            sw_alert = True
        elif sys.argv[1]=='sw':
            coc_alert = False
            sw_alert = True
        elif sys.argv[1]=='coc':
            coc_alert = True
            sw_alert = False
    else:
        coc_alert = False
        sw_alert = False
    print(f'Coc: {coc_alert}, SW: {sw_alert}')
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


@bot.event
async def on_voice_state_update(member,before,after):
    try:
        channel = after.channel
        user = str(member.id)
        if channel != None and before.channel == None:
            with shelve.open('vars') as f:
                voice_map = f['voice_map']
                prev_names = f['prev_names']
                prev_names[user]=member.display_name
                f['prev_names']=prev_names
            name = voice_map[channel.name][user]
            await member.edit(nick=name)
        elif channel != None and before.channel != None:
            with shelve.open('vars') as f:
                voice_map = f['voice_map']
            name = voice_map[channel.name][user]
            await member.edit(nick=name)
        elif channel == None:
            with shelve.open('vars') as f:
                name = f['prev_names'][user]
            await member.edit(nick=name)            
    except KeyError:
        print(f'{channel} not registered or {user} not registered there.')

@bot.command()
async def set_gametime(ctx, *args):
    args = [arg.lower() for arg in args]
    ampm = None
    with shelve.open('vars') as f:
        alias_dict = f['active_games']
    gamescan = [name for seq in list(alias_dict.values()) for name in seq] 
    for arg in args.copy():
        if arg in gamescan:
            with shelve.open('vars') as f:
                alias_dict = f['active_games']
            for key in alias_dict.keys():
                if arg in alias_dict[key]:
                    game,_ = key,args.pop(args.index(arg))
    for arg in args.copy():
        if arg in ['pm','am','a.m.','p.m.','p.m','a.m','pm.','am.']:
            if 'p' in arg:
                ampm = 'pm'
                args.remove(arg)
            elif 'a' in arg:
                ampm = 'am'
                args.remove(arg)
    for arg in args.copy():
        if ':' in arg:
            hour,minute = arg.split(':')
            if ampm == 'am' and hour=='12':
                hour = 0
                minute = int(minute)
            elif ampm == 'pm' and hour!='12':
                hour= int(hour)+12
                minute = int(minute)
            else:
                hour,minute=int(hour),int(minute)
            args.remove(arg)
        elif '-' not in arg and '/' not in arg:
            hour = arg
            minute = 0
    if len(args)==1:
        new_date = args[0]
        for sep in ['-','/']:
            if sep in new_date:
                new_date = new_date.split(sep)
        year,month,day = [int(ele) for ele in new_date] 
        new_time = int(dt(year,month,day,hour,minute).timestamp())
    else:
        for arg in args:
            if '-' in arg or '/' in arg:
                for sep in ['-','/']:
                    if sep in arg:
                        new_date = arg.split(sep)
                year,month,day = [int(ele) for ele in new_date] 
            else:
                minute = 0
                if ampm == 'pm':
                    hour = int(arg)+12
                else:
                    hour = int(arg)
        new_time = int(dt(year,month,day,hour,minute).timestamp())
    with shelve.open('vars') as f:
        f[game]=new_time
    await ctx.send(f'Next {game} game on <t:{new_time}>')

@bot.command()
async def gametime(ctx,*args):
    game = ' '.join(args)
    if game == '':
        await ctx.send(f'Please provide the name of the game session. Available sessions: ')
    else:
        try:
            with shelve.open('vars') as f:
                alias_dict = f['active_games']
                if game in alias_dict.keys():
                    time=f[game]
                else:
                    for session in alias_dict.keys():
                        if game in alias_dict[session]:
                            time=f[session]
                            game=session
                        else:
                            continue
            await ctx.send(f'Next {game.title()} session is on <t:{int(time)}>, <t:{int(time)}:R>')
        except KeyError:
            await ctx.send(f'Unable to find {game} in session list.')

# #Checks to see if the user has a nickname or not
##DEPRECATED##
# def name_check(ctx):
#     try:
#         if ctx.message.author.nick == None:
#             sender = ctx.message.author.name
#         else:
#             sender = ctx.message.author.nick
#     except AttributeError:
#         sender = ctx.message.author.name
#     return sender

#Loads titles from shelf file in case of bot interruption
def load_titles():
    with shelve.open('vars') as f:
        titles_ = f['titles']
    return titles_

def load_pcs():
    with shelve.open('vars') as f:
        pcs = f['pcs']
    return pcs

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
    
def name_sim(player):
    if player.lower()=='bd':
        return 'BD'
    else:
        players = load_pcs()
        similarities = []
        for i in range(len(players)):
            word = players[i]
            similarity = similar(player,word)
            similarities.append((similarity,word))
        similarities.sort(reverse=True)
        name = similarities[0][1]
        return name.title()

#Easter egg from Rocky Horror Picture Show
@bot.command()
async def transvestite(ctx):
    await ctx.send('I see you shiver with antici...')
    await asyncio.sleep(5)
    await ctx.send('...pation!')
    
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

@bot.command()
async def refresh(ctx):
    sender = ctx.message.author.display_name
    # sender = name_check(ctx)
    with shelve.open('vars') as f:
        f['votes']=[]
        f['vote_hist']=[]
        f['titles']=[]
    await ctx.send(f'List purged, Captain {sender}.')

@bot.command()
async def runoff(ctx):
    sender = ctx.message.author.display_name
    # sender = name_check(ctx)
    with shelve.open('vars') as f:
        f['vote_hist']=[]
    await ctx.send(f'Vote history purged, Captain {sender}.')

@bot.command()
async def s(ctx):
    sender = ctx.message.author.display_name
    # sender = name_check(ctx)
    title = (ctx.message.content)[3:]
    titles = load_titles()
    titles.append(title)
    with shelve.open('vars') as f:
        f['titles']=titles
    await ctx.send(f'Title added, Captain {sender}')

@bot.command()
async def titles(ctx):
    titles_ = load_titles()
    title_list = []
    for i in range(len(titles_)):
        title_list.append(str(i+1)+': '+str(titles_[i]))
    await ctx.send('\n'.join(title_list))

@bot.command(pass_context=True)
async def vote(ctx):
    try:
        sender = ctx.message.author.display_name
        # sender = name_check(ctx)
        voter = ctx.message.author.name
        vote = ctx.message.content[6:]
        entry = f'{voter}-{vote}'
        with shelve.open('vars') as f:
            vote_hist = f['vote_hist']
            votes = f['votes']
            titlecount = len(f['titles'])
        numvote = int(vote)
        if numvote>titlecount:
            await ctx.send(f'That number does not correspond to the amount of submitted votes.')
        else:
            if entry in vote_hist:
                await ctx.send(f'You have already voted for that title, Captain {sender}.')
            else:
                votes.append(numvote)
                vote_hist.append(entry)
                with shelve.open('vars') as f:
                    f['votes']=votes
                    f['vote_hist']=vote_hist
                await ctx.send(f'Vote recorded, Captain {sender}.')
    except ValueError:
        await ctx.send(f'That is not a number, Captain {sender}.')

@bot.command(pass_context=True)
async def votecount(ctx):
    with shelve.open('vars') as f:
        votes_ = f['votes']
    votecount = collections.Counter(votes_)
    showtitles = load_titles()
    df = pd.Series(votecount).sort_values(ascending=False)
    send_titles = [f'{df.iloc[i]}: {showtitles[int(df.index[i])-1]}' for i in range(len(df))]
    await ctx.send('\n'.join(send_titles))

@bot.command(pass_context=True)
async def stim(ctx):
    synt = (ctx.message.content[6:]).lower()
    name = name_sim(synt)
    with shelve.open('vars') as f:
        stims=f['stims']
        old=stims[name]
        new=old+1
        stims[name]=new
        f['stims']=stims
    await ctx.send(f'{name} stimmed, {5-new} left.')

@bot.command(pass_context=True)
async def undo(ctx):
    synt = (ctx.message.content[6:]).lower()
    name = name_sim(synt)
    with shelve.open('vars') as f:
        stims=f['stims']
        old=stims[name]
        new=old-1
        stims[name]=new
        f['stims']=stims
    await ctx.send(f'Stim removed from {name}, {5-new} left.')
 
@bot.command(pass_context=True)
async def heal(ctx):
    with shelve.open('vars') as f:
        stims = f['stims']
        for pc in list(stims.keys()):
            stims[pc]=0
        f['stims']=stims
    await ctx.send('Party refreshed.')    

@bot.command(pass_context=True)
async def status(ctx):
    synt = ctx.message.content[8:]
    with shelve.open('vars') as f:
        stims=f['stims']
    if synt == '':
        mess = []
        for pc in list(stims.keys()):
            mess.append(f'{pc} has been stimmed {stims[pc]} time(s), {5-stims[pc]} jab(s) remaining.')
        await ctx.send('\n'.join(mess))
    else:
        name = name_sim(synt)
        await ctx.send(f'{name} has been stimmed {stims[name]} time(s), {5-stims[name]} jab(s) remaining.')

@bot.command(pass_context=True)
async def crit(ctx):
    try:
        value = int((ctx.message.content)[6:])
        with shelve.open('vars') as f:
            crits=f['crits']
        ratings = list(crits.keys())
        for rating in ratings:
            if value > 150:
                entry = '151'
            else:
                if value in range(int(rating.split('-')[0]),1+int(rating.split('-')[1])):
                    entry = rating
                    break                                
                else:
                    continue
        result = crits[entry]
        await ctx.send(f'Result: {result[0]}\nRange: {entry}\nSeverity: {result[1]}\nDescription: {result[2]}')
    except ValueError:
        await ctx.send(f'That is not a number.')

@bot.command(pass_context=True)
async def critchara(ctx):
    critrate = random.randint(1,10)
    with shelve.open('vars') as f:
        charas = f['critchara']
    attr = charas[critrate]
    await ctx.send(f'Rolled {critrate}, which is {attr}.')

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
async def forceability(ctx):
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
        name = name_sim(pc)
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
        name = name_sim(pc)
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
            if df.loc[tal][name]:
                await ctx.send(f'{name} has {tal}.')
            else:
                await ctx.send(f'{name} does not have {tal}.')
        
@bot.command(pass_context=True)
async def upgrade(ctx):
    synt = ctx.message.content[9:].split()
    for ele in synt[1:]:
        if ele[0].isnumeric():
            loc = ele
            synt.remove(ele)
            break
        else:
            loc = None
    name = name_sim(synt[0])
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
    for ele in synt[1:]:
        if ele[0].isnumeric():
            loc = ele
            synt.remove(ele)
            break
        else:
            loc = None
    name = name_sim(synt[0])
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
    'armor':'Look up stats for armor !armor [armor] or search for similar name with !armor search [search term]',
    'forceability':'Look up details for a Force-specific ability that is not in the ranked or unranked list.',
    'sig':'Look up details for a signature ability.'
}

@bot.command(pass_context=True)
async def bothelp(ctx):
    synt = ctx.message.content[9:].lower()
    botcommands = ['vote','stim','undo','status','heal','crit','critchara','quality','talent','pc','upgrade','downgrade','forceability','sig']
    if synt=='':
        await ctx.send('Here is a list of the commands you can use:\nvote\nstim\nundo\nheal\ncrit\ncritchara\nquality\ntalent\npc\nupgrade\ndowngrade\nforceability\nsig\n\nIf a command asks for your name, you only need to provide enough spelling to differentiate yourself, it will search for the closest match.\nFor more information on a command, type !bothelp then the command.')
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
    print(guild.channels)
    names,ids = [],[]
    async for member in guild.fetch_members(limit=150):
        names.append(member.name)
        ids.append(member.id)
    df = pd.DataFrame()
    df['name'],df['id'],df['guild_id'],df['guild_name']=names,ids,guild_id,guild
    df.to_csv('name_guild.csv',encoding='utf-8',index=False)

@bot.command(pass_context=True)
async def set_channel(ctx):
    synt = ctx.message.content[13:]
    game_name = synt 
    if game_name == '':
        await ctx.send('Please provide a game name with which this channel is to be associated.')
    else:
        server = ctx.message.guild.id
        channel = ctx.message.channel.id
        with shelve.open('vars') as f:
            game_dic = f['game_dic']
            game_dic[game_name]=[channel,server]
            f['game_dic']=game_dic
        await ctx.send(f'{game_name} set as game name for this channel.')

@bot.command(pass_context=True)
async def addme(ctx):
    try:
        synt = ctx.message.content[7:].split(',')
        with shelve.open('vars') as f:
            game_dic = f['game_dic']
        game_list = list(game_dic.keys())
        game_switch=False
        for ele in synt:
            if ele.strip() in game_list:
                game=ele
                game_switch=True
                synt.remove(ele)
        if game_switch==False:
            val_search = list(game_dic.items())
            channel,guild = ctx.message.channel.id,ctx.message.guild.id
            for ele in val_search:
                if ele[1][0]==channel and ele[1][1]==guild:
                    game=ele[0]
        game_info = game_dic[game]
        user = ctx.message.author.id
        if len(game_info)==2:
            game_info.append([user])
        else:
            player_list = game_info[2]
            if user in player_list:
                await ctx.send(f'{ctx.message.author} is already in the player list for {game}.')
            else:
                player_list.append(user)
                game_info[2] = player_list
                with shelve.open('vars')as f:
                    f['game_dic']=game_dic
                await ctx.send(f'{ctx.message.author} added to {game} player list.')
    except UnboundLocalError:
        await ctx.send('Unable to determine associated game player list to which to add you. Please provide a game name, make this request in the dedicated channel, or set this channel with an associated game.')
    
@bot.command(pass_context=True)
async def register(ctx):
    try:
        synt = ctx.message.content[10:].split(',')
        with shelve.open('vars') as f:
            game_dic = f['game_dic']
        game_list = list(game_dic.keys())
        game_switch=False
        for ele in synt:
            if ele.strip() in game_list:
                game=ele
                game_switch=True
                channel,guild = game_dic[game][0],game_dic[game][1]
                synt.remove(ele)
        if game_switch==False:
            val_search = list(game_dic.items())
            channel,guild = ctx.message.channel.id,ctx.message.guild.id
            for ele in val_search:
                if ele[1][0]==channel and ele[1][1]==guild:
                    game=ele[0]
        name=''.join(synt).strip()
        with shelve.open('vars') as f:
            name_dic = f['name_dic']
            user = ctx.message.author.id
            ent_tup = (game,user)
            name_dic[ent_tup]=(name,channel,guild)
            print(name_dic)
            f['name_dic']=name_dic
        await ctx.send(f'{ctx.message.author} added to {game} under the name {name}.')
    except UnboundLocalError:
        await ctx.send('Unable to determine associated game with which to register you. Please provide a game name, make this request in the dedicated channel, or set this channel with an associated game.')

@bot.command(pass_context=True)
async def nameswitch(ctx):
    synt = ctx.message.content[12:]
    with shelve.open('vars') as f:
        game_dic = f['game_dic']
    if synt=='':
        channel,guild = ctx.message.channel.id,ctx.message.guild.id
        val_search = list(game_dic.items())
        for ele in val_search:
            if ele[1][0]==channel and ele[1][1]==guild:
                game=ele[0]
    elif synt.strip() in list(game_dic.keys()):
        game = synt.strip()
    else:
        await ctx.send(f'{synt.strip()} is not in the list of known games.')
    user_list = game_dic[game][2]
    with shelve.open('vars')as f:
        name_dic = f['name_dic']
    for user in user_list:
        ent_tup = (game,user)
        name = name_dic[ent_tup][0]
        user_obj = await ctx.guild.fetch_member(user)
        await user_obj.edit(nick=name)

@bot.command()
async def wiki(ctx,*args):
    # args = [arg.lower() for arg in args]
    search = ' '.join(args)
    if '?' in search:
        entry = sim_search(search,wiki_df)
        results = sim_search(search,wiki_df,search=True)
        body = wiki_df.loc[entry]['body']
        await ctx.send(f'Showing results for closest match {entry}: {body}')
        await ctx.send(f"Not what you're looking for? Here are the 5 closest entry matches: {results}")
    elif search.lower() in done_entries:
        entry = search
        body = wiki_df.loc[search.title()]['body']
        await ctx.send(f'{entry.title()}: {body}')
    elif search.lower() in prog_entries:
        global wiki_log
        wiki_log.append(f'Search for incomplete entry: {search}')
        await ctx.send(f'{search} is in the wiki but does not currently have an article. This topic has been submitted for higher priority.')
    else:
        await ctx.send(f'I am sorry, but I cannot find {search} in my database. React to this message if you would like to add it to the list of topics to be added.')

@bot.event
async def on_reaction_add(reaction, user):
    content = reaction.message.content
    if content.startswith('I am sorry, but I cannot find'):
        parser = 'I am sorry, but I cannot find in my database. React to this message if you would like to add it to the list of topics to be added.'.split(' ')
        term = ' '.join([t for t in content.split(' ') if t not in parser])
        chan = reaction.message.channel
        global wiki_log
        wiki_log.append(f'Search for nonexistent entry: {term}')
        name = user.display_name
        await chan.send(f'{term} added to topic log by {name}.')

@bot.command()
async def log_dump(ctx):
    log_df = pd.DataFrame()
    global wiki_log
    log_df['term']=wiki_log
    path = os.getcwd()
    time_ = int(dt.now().timestamp())   
    log_df.to_csv(f'wiki_log_{time_}.csv',encoding='utf-8',index=False)
    await ctx.send(f'wiki_log_{time_}.csv dumped to {path}')
    wiki_log = []



bot.run(f'{token}')