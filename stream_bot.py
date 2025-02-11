import discord,asyncio
from discord import ActivityType
from discord.ext import commands
import pandas as pd


#Bot token saved in a .txt flie in the containing directory, which is not in the repository. This is a security feature--if you publish your bot token on Github, Discord will revoke it immediately
with open('../tok.txt') as f:
    token = f.readlines()[0]


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!',intents=intents)
client = discord.Client(intents=intents)
intents.members = True

global act_cols,game_cols,streaming_cols,spotify_cols,custom_cols
act_cols = ['application_id','name','url','type','state','details','timestamps','assets','party','buttons','emoji','start','end','large_img_url','small_image_url','large_image_text','small_image_text']
game_cols = ['end','name','start','type']
streaming_cols = ['details','game','name','platform','twitch_name','type','url']#'assets', <--  Had to remove assets because it doesn't work as a dictionary key. Can bring back if I want but not worth it working out the logic right now.
spotify_cols = ['album','album_cover_url','artist','artists','color','colour','created_at','duration','end','name','party_id','start','title','track_id','track_url','type']
custom_cols = ['emoji','name','type']


def activity_process(activity,mem_id,mem_name):
    global base_activities_df,game_df,streaming_df,spotify_df,custom_activity_df
    if activity.type == ActivityType.listening:
        spot_dict = {}
        for col in spotify_cols:
            spot_dict[col]=getattr(activity,col)
        new_spot_df = pd.DataFrame.from_dict(spot_dict,orient='index').T
        new_spot_df['member_id']=mem_id
        new_spot_df['member_name']=mem_name
        artists = activity.artists
        if len(artists)==1:
            artists=artists[0]
        elif len(artists)==2:
            artists = f'{artists[0]} and {artists[1]}'
        else:
            artists_pre = ', '.join(artists[:-1])
            artists_post = artists[-1]
            artists = f'{artists_pre}, and {artists_post}'
        new_spot_df['processed_artists'] = artists
        spotify_df = pd.merge(spotify_df,new_spot_df,how='outer')
    ##Game
    elif activity.type == ActivityType.playing:
        game_dict = {}
        for col in game_cols:
            game_dict[col]=getattr(activity,col)
        new_game_df = pd.DataFrame.from_dict(game_dict,orient='index').T
        new_game_df['member_id']=mem_id
        new_game_df['member_name']=mem_name
        game_df = pd.merge(game_df,new_game_df,how='outer')
    ##Streaming
    elif activity.type == ActivityType.streaming:
        stream_dict = {}
        for col in streaming_cols:
            stream_dict[col]=getattr(activity,col)
        new_stream_df = pd.DataFrame.from_dict(stream_dict,orient='index').T
        new_stream_df['member_id']=mem_id
        new_stream_df['member_name']=mem_name
        streaming_df = pd.merge(streaming_df,new_stream_df,how='outer')
    ##Custom Status
    elif activity.type == ActivityType.custom:
        cust_dict = {}
        for col in custom_cols:
            cust_dict[col]=getattr(activity,col)
        new_custom_activity_df = pd.DataFrame.from_dict(cust_dict,orient='index').T
        new_custom_activity_df['member_id']=mem_id
        new_custom_activity_df['member_name']=mem_name
        custom_activity_df = pd.merge(custom_activity_df,new_custom_activity_df,how='outer')
    else:
        print('Something went wrong, and this is weird because it should be impossible.')


@bot.event
async def on_ready():
    print('Awaiting orders, Captain.')
    while True:
        global act_cols,game_cols,streaming_cols,spotify_cols,custom_cols
        cols_list = [act_cols,game_cols,streaming_cols,spotify_cols,custom_cols]
        df_list = [pd.DataFrame(columns=['member_id','member_name']+cols) for cols in cols_list]
        global base_activities_df,game_df,streaming_df,spotify_df,custom_activity_df
        base_activities_df,game_df,streaming_df,spotify_df,custom_activity_df=df_list

        guilds = [guild.id async for guild in bot.fetch_guilds()]
        member_obj_list,member_name_list,member_id_list,member_activities_list,member_status_list = [],[],[],[],[]
        for guild_id in guilds:
            guild_obj = bot.get_guild(guild_id)
            members = guild_obj.members
            for member in members:
                mem_name,activities,mem_id = member.name,member.activities,member.id
                member_obj_list.append(member)
                member_name_list.append(mem_name)
                member_id_list.append(mem_id)
                member_activities_list.append(activities)
                member_status_list.append(member.status)
        df = pd.DataFrame()
        for col_name,col_list in zip(['member_obj','member_name','member_id','member_activities','member_status'],[member_obj_list,member_name_list,member_id_list,member_activities_list,member_status_list]):
            df[col_name]=col_list
        df.drop_duplicates(inplace=True)
        online_users = df[[('online' in tup) or ('idle' in tup) for tup in df.member_status.tolist()]]
        active_users = online_users[online_users.member_activities != ()]
        raw_activities_list,mem_name_list,mem_id_list = active_users.member_activities.values.tolist(),active_users.member_name.tolist(),active_users.member_id.tolist()
        for activity_list,mem_id,mem_name in zip(raw_activities_list,mem_id_list,mem_name_list):
            for activity in activity_list:
                activity_process(activity,mem_id,mem_name)
        for df_,file_name in zip([game_df,streaming_df,spotify_df,custom_activity_df],['game_df','streaming_df','spotify_df','custom_activity_df']):
            df_.to_csv(f'{file_name}.csv',index=False,encoding='utf-8')
            # print(f'{file_name} written.')
        await asyncio.sleep(5)



##TODO: This function should update the df whenever someone changes status. I'm putting this on hold until I bother to figure out what's going on with the multiple firings that come from multiple devices. Mobile and desktop and others make it fire that many times per device.
# @bot.event
# async def on_presence_update(before,after):
#     global base_activities_df,game_df,streaming_df,spotify_df,custom_activity_df
#     before_activities,after_activities = [act for act in before.activities],[act for act in after.activities]
#     before_types,after_types = [act.type for act in before_activities],[act.type for act in after_activities]
#     ##Scans activity objects in the after list to check for new or continued activity
#     for act in after_activities:
#         ##Means this activity is started
#         if act.type not in [before_types]:
#             print(f'Started: {act.name}')
#         ##Means this activity is continued from last update
#         elif act.type in [before_types]:
#             print(f'Continued {act.name}')
#         ##Should never happen in theory
#         # else:
#         #     print(f'Weird case in after: {act.name}')
#     ##Scans objects in the before list to check against new, verifying the activity has stopped
#     for act in before_activities:
#         if act.type not in after_types:
#             print(f'Stopped: {act.name}')
#         ##Should never happen in theory
#         # else:
#         #     print(f'Weird case in before: {act.name}')
bot.run(f'{token}')