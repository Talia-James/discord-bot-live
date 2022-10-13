import discord, random, re, time, csv
from discord.ext import commands
import collections
import pandas as pd
import math
import os
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!',intents=intents)
client = discord.Client(intents=intents)
intents.members = True



@bot.event
async def on_ready():
    print('Awaiting orders, Captain.')

def name_check(ctx):
    if ctx.message.author.nick == None:
        sender = ctx.message.author.name
    else:
        sender = ctx.message.author.nick
    return sender

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

@bot.command()
async def transvestite(ctx):
    await ctx.send('I see you shiver with antici...')
    time.sleep(5)
    await ctx.send('...pation!')

@bot.command()
async def roll(ctx):
    #This check will assign a name for the bot to respond to. It can be removed so long as the 'sender' variable is removed from the return.
    if ctx.message.author.nick == None:
        sender = ctx.message.author.name
    else:
        sender = ctx.message.author.nick
    diesearch = re.compile(r'(\d+)(d)*(\d*)([+/-]\d*)?', re.I)
    userinput = ctx.message.content
    diceformat = diesearch.search(userinput)
    try:
        diceformat[4] == None
        modifier = int(diceformat[4][1:])
        sign = diceformat[4][0]
    except TypeError:
        modifier = 0
        sign = ''
    if diceformat.group(2) is None:
        dN = int(diceformat.group(1))
        print(type(diceformat.group(0)))
        dice = random.randint(1, dN)
        print('-' in diceformat.group(0))
        if '-' in diceformat.group(0):
            await ctx.send(sender + ' rolled ' + str(dice - modifier) + ' from a d' + str(dN - modifier) + '!')
        elif '+' in diceformat.group(0):
            await ctx.send(sender + ' rolled ' + str(dice + modifier) + ' from a d' + str(dN + modifier) + '!')
        else:
            await ctx.send(sender + ' rolled ' + str(dice) + ' from a d' + str(dN) + '!')
    elif diceformat.group(3) == '':
        sign = diceformat[4][0]
        dN = int(diceformat.group(1))
        dice = random.randint(1, dN)
        if sign == '-':
            await ctx.send(sender + ' rolled ' + str(dice - modifier) + ' from a d' + str(dN - modifier) + '!')
        else:
            await ctx.send(sender + ' rolled ' + str(dice + modifier) + ' from a d' + str(dN + modifier) + '!')        
    else:
        dN = int(diceformat.group(3))
        multiplier = int(diceformat.group(1))
        amt = 0
        for _ in range(multiplier):
            amt += random.randint(1, dN)
        if sign == '-':
            await ctx.send(sender + ' rolled ' + str(amt - modifier) + ' out of a possible ' + str((dN * multiplier)-modifier) + '!')
        else:
            await ctx.send(sender + ' rolled ' + str(amt + modifier) + ' out of a possible ' + str((dN * multiplier)+modifier) + '!')


@bot.command()
async def rouler(ctx, inp):
    if ctx.message.author.nick == None:
        sender = ctx.message.author.name
    else:
        sender = ctx.message.author.nick
    diesearch = re.compile(r'(\d+)(d)*(\d*)', re.I)
    userinput = ctx.message.content
    diceformat = diesearch.search(userinput)
    if diceformat.group(2) is None:
        dN = int(diceformat.group(0))
        dice = random.randint(1, dN)
        await ctx.send(sender + ' a roulé ' + str(dice) + " sur un dé " + str(dN) + '!')
    elif diceformat.group(3) == '':
        dN = int(diceformat.group(1))
        dice = random.randint(1, dN)
        await ctx.send(sender + ' a roulé ' + str(dice) + " sur un dé " + str(dN) + '!')
    else:
        dN = int(diceformat.group(3))
        multiplier = int(diceformat.group(1))
        amt = 0
        for i in range(multiplier):
            amt += random.randint(1, dN)
        await ctx.send(sender + ' a roulé ' + str(amt) + " sur un total possible " + str(dN * multiplier) + '!')


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
async def choisir(ctx):
    listmake = (re.compile(r'[^,]*'))
    choices = listmake.findall(str(ctx.message.content))
    cleanedchoices = []
    if len(choices) == 2:
        await ctx.send("Captaine, je ne peux pas choisir avec ce que vous avez saisi.")
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
        await ctx.send(picker + ' a choisi ' + random.choice(cleanedchoices) + ' au hasard!')

entrants = []
showtitles = {}
votes = []
index = 1

@bot.command()
async def info(ctx):
    print(ctx.message.author)
    print(ctx.message.author.name)

@bot.command()
async def refresh(ctx):
    global titles
    titles = []
    global votes
    votes = []
    with open('titles.csv','w') as f:
        writer = csv.writer(f)
        writer.writerow(titles)
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
    await ctx.send('Titled added, Captain ' + sender)

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
    await talia.edit(nick='Claire')
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

vote_hist = []

@bot.command(pass_context=True)
async def vote(ctx):
    sender = name_check(ctx)
    vote = ctx.message.content[6:]
    vote_entry = f'{sender}-{vote}'
    try:
        if vote_entry in vote_hist:
            await ctx.send(f'You have already voted for that title, Captain {sender}.')
        else:
            numvote = int(vote)
            votes.append(numvote)
            await ctx.send(f'Vote recorded, Captain {sender}.')
    except ValueError:
        await ctx.send(f'That is not a number, Captain {sender}.')

@bot.command(pass_context=True)
async def votecount(ctx):
    votecount = collections.Counter(votes)
    showtitles = load_titles()
    df = pd.Series(votecount).sort_values(ascending=False)
    send_titles = [str(df.iloc[i])+': '+ showtitles[i] for i in range(len(df))]
    await ctx.send('\n'.join(send_titles))

@bot.command(pass_context=True)
async def userinfo(ctx):
    guild = ctx.message.guild
    async for member in guild.fetch_members(limit=150):
        print(member.name)
        print(member.id)

@bot.command(pass_context=True)
async def stim(ctx):
    df = pd.read_csv('stims.csv',index_col=['Name'])
    target = str(ctx.message.content)[6:]
    low = target.lower()
    if low.startswith('v'):
        name = 'Virai'
        num = int(df['Status'][name])+1
        df.loc[name] = num
        df.to_csv('stims.csv')
        await ctx.send('Virai stimmed.')
    elif low.startswith('kh'):
        name = 'Khaylia'
        num = int(df['Status'][name])+1
        df.loc[name] = num
        df.to_csv('stims.csv')
        await ctx.send('Khaylia stimmed.')
    elif low.startswith('ka'):
        name = 'Kavin'
        num = int(df['Status'][name])+1
        df.loc[name] = num
        df.to_csv('stims.csv')
        await ctx.send('Kavin stimmed.')
    elif low.startswith('ch'):
        name = 'Cho'
        num = int(df['Status'][name])+1
        df.loc[name] = num
        df.to_csv('stims.csv')
        await ctx.send('Cho stimmed.')
    elif low.startswith('cu'):
        name = 'Culkoo'
        num = int(df['Status'][name])+1
        df.loc[name] = num
        df.to_csv('stims.csv')
        await ctx.send('Culkooo stimmed.')
    elif low.startswith('d'):
        name = 'Doc'
        num = int(df['Status'][name])+1
        df.loc[name] = num
        df.to_csv('stims.csv')
        await ctx.send('Doc stimmed.')
    else:
        await ctx.send('Uh, what?')

@bot.command(pass_context=True)
async def undo(ctx):
    df = pd.read_csv('stims.csv',index_col=['Name'])
    target = str(ctx.message.content)[6:]
    low = target.lower()
    if low.startswith('v'):
        name = 'Virai'
        num = int(df['Status'][name])-1
        df.loc[name] = num
        df.to_csv('stims.csv')
        await ctx.send('Virai whoopsied.')
    elif low.startswith('kh'):
        name = 'Khaylia'
        num = int(df['Status'][name])-1
        df.loc[name] = num
        df.to_csv('stims.csv')
        await ctx.send('Khaylia whoopsied.')
    elif low.startswith('ka'):
        name = 'Kavin'
        num = int(df['Status'][name])-1
        df.loc[name] = num
        df.to_csv('stims.csv')
        await ctx.send('Kavin whoopsied.')
    elif low.startswith('ch'):
        name = 'Cho'
        num = int(df['Status'][name])-1
        df.loc[name] = num
        df.to_csv('stims.csv')
        await ctx.send('Cho whoopsied.')
    elif low.startswith('cu'):
        name = 'Culkoo'
        num = int(df['Status'][name])-1
        df.loc[name] = num
        df.to_csv('stims.csv')
        await ctx.send('Culkooo whoopsied.')
    elif low.startswith('d'):
        name = 'Doc'
        num = int(df['Status'][name])-1
        df.loc[name] = num
        df.to_csv('stims.csv')
        await ctx.send('Doc whoopsied.')
    else:
        await ctx.send('Uh, what?')
 
@bot.command(pass_context=True)
async def heal(ctx):
    df = pd.read_csv('stims.csv',index_col=['Name'])
    for ele in list(df.index):
        df.loc[ele]=0
    df.to_csv('stims.csv')
    await ctx.send('Party refreshed.')    

@bot.command(pass_context=True)
async def status(ctx):
    df = pd.read_csv('stims.csv',index_col=['Name'])
    low = (ctx.message.content)[8:].lower()
    if low.startswith('v'):
        name = 'Virai'
        status = int(df.loc[name])
        await ctx.send(name+' has been stimmed '+str(status)+' times and has '+str(5-status)+' jabs left.')
    elif low.startswith('kh'):
        name = 'Khaylia'
        status = int(df.loc[name])
        await ctx.send(name+' has been stimmed '+str(status)+' times and has '+str(5-status)+' jabs left.')
    elif low.startswith('ka'):
        name = 'Kavin'
        status = int(df.loc[name])
        await ctx.send(name+' has been stimmed '+str(status)+' times and has '+str(5-status)+' jabs left.')
    elif low.startswith('ch'):
        name = 'Cho'
        status = int(df.loc[name])
        await ctx.send(name+' has been stimmed '+str(status)+' times and has '+str(5-status)+' jabs left.')
    elif low.startswith('cu'):
        name = 'Culkoo'
        status = int(df.loc[name])
        await ctx.send(name+' has been stimmed '+str(status)+' times and has '+str(5-status)+' jabs left.')
    elif low.startswith('d'):
        name = 'Doc'
        status = int(df.loc[name])
        await ctx.send(name+' has been stimmed '+str(status)+' times and has '+str(5-status)+' jabs left.')
    else:
        await ctx.send('Uh, what?')

    
    

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
    df = pd.read_csv('abilities.csv',index_col=['Ability'])
    synt = ctx.message.content[8:].lower()
    annoying = ["let's ride","it's not that bad"]
    talents = [i.lower() for i in list(df.index)]
    if synt == "it's not that bad":
        await ctx.send(df.iloc[35]['Description'])
    elif synt == "let's ride":
        await ctx.send(df.iloc[41]['Description'])
    elif (synt in talents) and (synt not in annoying): 
        await ctx.send(df.loc[synt.title()]['Description'])
    elif synt[:4] == 'list':
        type = synt[5:].title()
        group_talents = list(df[df['Type']==type].index)
        send_talents = [group_talents[i] for i in range(len(group_talents))]
        await ctx.send('\n'.join(send_talents))
    elif synt[:5] == 'types':
        types = list(df['Type'].unique())
        send_types = [types[i] for i in range(len(types))]
        await ctx.send('\n'.join(send_types))
    else:
        await ctx.send('I believe you have a typo, Captain.')

@bot.command(pass_context=True)
async def pc(ctx):
    df = pd.read_csv('ranks.csv',index_col=['Ability'])
    synt = ctx.message.content[4:].lower().split()
    typeclass = [i.lower() for i in list(df['Type'].unique())]
    annoying = ["let's ride","it's not that bad"]
    if synt[0].startswith('v'):
        pcname = 'Virai'
    elif synt[0].startswith('kh'):
        pcname = 'Khaylia'
    elif synt[0].startswith('ka'):
        pcname = 'Kavin'
    elif synt[0].startswith('ch'):
        pcname = 'Okchota'
    elif synt[0].startswith('cu'):
        pcname = 'Culkoo'
    elif synt[0].startswith('d'):
        pcname = 'Doc'
    elif synt[0] == 'bd':
        pcname = 'BD'
    if len(synt)==1:
        abilities = list(df[pcname][df[pcname]!=0].index)
        send_abilities = [abilities[i] for i in range(len(abilities))]
        await ctx.send('\n'.join(send_abilities))
    elif ' '.join(synt[1:]) in typeclass:
        subtype = ' '.join(synt[1:]).title()
        abilities = list(df[(df['Type']==subtype)&(df[pcname]!=0)].index)
        send_abilities = [abilities[i] for i in range(len(abilities))]
        try:
            await ctx.send('\n'.join(send_abilities))
        except discord.errors.HTTPException:
            await ctx.send('I do not believe that player has any abilities in that category.')
    elif synt[1] not in typeclass:
        if ' '.join(synt[1:]) not in annoying:
            ability = ' '.join(synt[1:]).title()
        elif ' '.join(synt[1:]) == "it's not that bad":
            ability = "It's Not That Bad"
        elif ' '.join(synt[1:]) == "let's ride":
            ability = "Let's Ride"
        rank = df.loc[ability][pcname]
        await ctx.send(pcname + ', ' + ability+': Rank '+str(rank))
    else:
        await ctx.send('I believe you have a typo, Captain')
        

@bot.command(pass_context=True)
async def upgrade(ctx):
    df = pd.read_csv('ranks.csv',index_col=['Ability'])
    synt = ctx.message.content[9:].lower().split()
    if synt[0].startswith('v'):
        pc = 'Virai'
    elif synt[0].startswith('kh'):
        pc = 'Khaylia'
    elif synt[0].startswith('ka'):
        pc = 'Kavin'
    elif synt[0].startswith('ch'):
        pc = 'Okchota'
    elif synt[0].startswith('cu'):
        pc = 'Culkoo'
    elif synt[0].startswith('d'):
        pc = 'Doc'
    ability = ' '.join(synt[1:])
    if ability == "it's not that bad":
        ability = "It's Not That Bad"
    elif ability == "let's ride":
        ability = "Let's Ride"
    else:
        ability = ability.title()
    rank = int(df.at[ability,pc])
    rank += 1
    df.at[ability,pc] = rank
    df.to_csv('ranks.csv')
    await ctx.send(pc+"'s rank in "+ability+' upgraded to '+str(rank))

@bot.command(pass_context=True)
async def downgrade(ctx):
    df = pd.read_csv('ranks.csv',index_col=['Ability'])
    synt = ctx.message.content[11:].lower().split()
    if synt[0].startswith('v'):
        pc = 'Virai'
    elif synt[0].startswith('kh'):
        pc = 'Khaylia'
    elif synt[0].startswith('ka'):
        pc = 'Kavin'
    elif synt[0].startswith('ch'):
        pc = 'Okchota'
    elif synt[0].startswith('cu'):
        pc = 'Culkoo'
    elif synt[0].startswith('d'):
        pc = 'Doc'
    ability = ' '.join(synt[1:])
    if ability == "it's not that bad":
        ability = "It's Not That Bad"
    elif ability == "let's ride":
        ability = "Let's Ride"
    else:
        ability = ability.title()
    rank = int(df.at[ability,pc])
    rank += -1
    df.at[ability,pc] = rank
    df.to_csv('ranks.csv')
    await ctx.send(pc+"'s rank in "+ability+' downgraded to '+str(rank))

command_descriptions = {
    'vote':'Vote for a number in the title list. You can vote for higher numbers that are not in the list, but why would you do that? !vote [title number]',
    'stim':'!stim [name], will add one stimpack use to this character and tell you how many more can be used on them.',
    'undo':'Accidentally stim someone? Reverse it with !undo [name]',
    'status':'!status [name] provides the current amount of stimpacks that have been used and are remaining for that character.',
    'heal':'Clear everyone of all stimpack uses. Resets all to 0',
    'crit':'!crit [crit rating]. Input a number to find out what the description and severity a crit of that number has.',
    'critchara':'Get a crit that affects a random characteristic? Find out which one with !critchara',
    'quality':'Provides a description of an item quality, whether it is passive or active, and what is needed to trigger it if relevant.\nType !quality [quality name] to get a description or just !quality if you want a list of all of them.',
    'talent':'Provides a description or list of talent(s).\n!talent types will give you all the groups of talents.\n!talent list [type] will give you all abilities of that type.\n!talent [talent] will give you a description of that talent.',
    'pc':'Provides information about a certain PC (or BD).\n!pc [name] will list all the talents for the character.\n!pc [name] [type] will list all talents of that type for that character.\n!pc [name] [talent] will give you the rank of the ability for that PC.',
    'upgrade':'Rank up a talent. !upgrade [name] [talent]',
    'downgrade':'Rank down a talent. !downgrade [name] [talent]',
    'weapon':'Look up stats for a weapon !weapon [weapon] or search for similar names with !weapon search [search term]',
    'armor':'Look up stats for armor !armor [armor] or search for similar name with !armor search [search term]'
}

@bot.command(pass_context=True)
async def bothelp(ctx):
    synt = ctx.message.content[9:].lower()
    botcommands = ['vote','stim','undo','status','heal','crit','critchara','quality','talent','pc','upgrade','downgrade']
    if synt=='':
        await ctx.send('Here is a list of the commands you can use:\nvote\nstim\nundo\nheal\ncrit\ncritchara\nquality\ntalent\npc\nupgrade\ndowngrade\n\nIf a command asks for your name, you only need to provide the first two letters of the name to differentiate it from others. All input is case inensitive.\nFor more information on a command, type !bothelp then the command.')
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

bot.run('Njc1NDUzMTM5NDA2ODE1MjM3.XsVkHg.GLK7KaKgUE9XwW6ALbZqHpyHE5U')


