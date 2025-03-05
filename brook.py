import os
import discord
from discord.ext import commands
from discord.ui import Button
import yt_dlp as youtube_dl


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True 
intents.guilds = True  
intents.voice_states = True
bot = commands.Bot(command_prefix='-', intents=intents)

#path to directory where downloaded songs should be placed and then deleted from
download_directory = ""

ytdl_opts = {
    'verbose': True,
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(download_directory,'%(title)s.%(ext)s'),
    'restrictfilenames': False,
    'noplaylist': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    },

}


ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -loglevel verbose',

}


ytdl = youtube_dl.YoutubeDL(ytdl_opts)

guild_queues = {}


class MusicControls(discord.ui.View):
    def __init__(self, ctx, bot):
        super().__init__(timeout=3600)
        self.ctx = ctx
        self.bot = bot
        self.add_item(discord.ui.Button(label="Daj mi ba marku", style=discord.ButtonStyle.link, url="https://www.youtube.com/watch?v=EE-xtCF3T94"))

    @discord.ui.button(label="≧", style=discord.ButtonStyle.primary)
    async def pause(self, interaction: discord.Interaction, button: Button):
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if voice and voice.is_playing():
            voice.pause()
            await interaction.response.send_message("Paused the music.", ephemeral=True)
        elif voice and voice.is_paused():
            voice.resume()
            await interaction.response.send_message("Resumed the music.", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing is currently playing.", ephemeral=True)

    @discord.ui.button(label="⇉", style=discord.ButtonStyle.primary)
    async def skip(self, interaction: discord.Interaction, button: Button):
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if voice and voice.is_playing():
            voice.stop()
            await interaction.response.send_message("Skipped the current track.", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing is currently playing.", ephemeral=True)

    @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: Button):
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if voice and voice.is_playing():
            voice.stop()
            await interaction.response.send_message("Stopped the queue", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing is currently playing.", ephemeral=True)

    @discord.ui.button(label="⇊", style=discord.ButtonStyle.success)
    async def skini(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()  # Acknowledge the interaction
        
        # Retrieve the last 10 messages in the channel
        messages = [message async for message in self.ctx.channel.history(limit=4)]
        
        # Check for embeds in the last message
        for message in messages:
            if message.embeds:
                embed_description = message.embeds[0].description  # Get the title of the first embed
                break
        else:
            await self.ctx.send("No embed found in recent messages.")
            return

        await self.ctx.typing()
        try:
            ytdl_opts = {
    'verbose': True,
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(download_directory,'template.%(ext)s'),
    'restrictfilenames': False,
    'noplaylist': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],

}
            with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
                info = ytdl.extract_info(f"ytsearch:{embed_description}", download=True)['entries'][0]

                file_name = os.path.join(download_directory, 'template.mp3')

                await self.ctx.send(file=discord.File(file_name, filename=f"{info['title']}.mp3"))

                # After sending the file, delete it
                try:
                    os.remove(file_name)
                except Exception as delete_error:
                    print(f"Error deleting file: {delete_error}")

        except Exception as e:
            await self.ctx.send(f"An error occurred: {str(e)}")
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.event
async def on_connect():
    print("LETS FUCKING GOOOOOOOOO")

@bot.command()
async def ping(ctx):
    await ctx.send("volim jazzee-a")

@bot.command()
async def join(ctx):
    """Join the voice channel."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
            await ctx.send("Joined the voice channel.")
    else:
        await ctx.send("You are not connected to a voice channel.")


@bot.command()
async def leave(ctx):
    """Leave the voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I am not in a voice channel.")

@bot.command(aliases=['play'])
async def p(ctx, *, query: str):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
            await ctx.send("Joined the voice channel.")
    else:
        return await ctx.send("You are not connected to a voice channel.")

    if ctx.guild.id not in guild_queues:
        guild_queues[ctx.guild.id] = []  

    voice_client = ctx.voice_client
    
    async with ctx.typing():
        if "http" in query:
            info = ytdl.extract_info(query, download=False)
        else:
            info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
       
        if 'url' in info:
            url = info['url']
        else:
            return await ctx.send("Failed to extract audio URL from the provided link.")

    embed = discord.Embed(
        title=":notes: **Now playing:**",
        description=f"{info['title']}",
        color=16250871
    )
    embed.set_footer(text="Discord music player and downloader. Made by Veks, powered by jazz.")
    embed.set_image(url="https://cdn.discordapp.com/attachments/534843457056014367/536666736460562443/advertise_light_bar.gif?ex=66eaa518&is=66e95398&hm=c8e74534d8babf3af73ec95c16d7618fd4ff7e4b047e53b61b18267285bb25c7&")
    embed.url = info['url']
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/835857771403411469/1285651396942889072/shikanoko-by-murya.gif?ex=66eb0bab&is=66e9ba2b&hm=707a1f3170b425ef9cdaf5b999da45bf843f4cfca2313bf550656cfe17edb546&")

    if not voice_client.is_playing():
        voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options), after=lambda e: bot.loop.create_task(skip(ctx)))
        await ctx.send(embed=embed, view=MusicControls(ctx, bot))
    else:
        # Add the song to the queue if already playing
        guild_queues[ctx.guild.id].append({'title': f"{info['title']}" , 'url': url }) 
        await ctx.send(f"Added to queue: {info['title']}")

@bot.command(aliases=['s'])
async def skip(ctx, _=None):
    """Skip the currently playing song."""
    voice_client = ctx.voice_client
    
    if not voice_client or not voice_client.is_connected():
        return await ctx.send("Not connected to a voice channel.")
    
    if ctx.guild.id not in guild_queues or not guild_queues[ctx.guild.id]:
        return await ctx.send("The queue is empty.")
    
    voice_client.stop()  # Stop the currently playing song
    
    next_song = guild_queues[ctx.guild.id].pop(0)  # Pop the next song from the queue
    
    if next_song:  # Check if the next song exists
        async with ctx.typing():
            source = discord.FFmpegPCMAudio(next_song['url'], **ffmpeg_options)
            voice_client.play(source, after=lambda e: bot.loop.create_task(skip(ctx)))
            
            embed = discord.Embed(
                title=":notes: **Now playing:**",
                description=f"{next_song['title']}",
                color=16250871
            )
            embed.set_footer(text="Discord music player and downloader. Made by Veks, powered by jazz.")
            embed.set_image(url="https://cdn.discordapp.com/attachments/534843457056014367/536666736460562443/advertise_light_bar.gif?ex=66eaa518&is=66e95398&hm=c8e74534d8babf3af73ec95c16d7618fd4ff7e4b047e53b61b18267285bb25c7&")
            embed.url = next_song['url']
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/835857771403411469/1285652926769008671/shigure-ui-iasu.gif?ex=66eb0d18&is=66e9bb98&hm=ee82e13f33f60bf7390be34bbcd7f7a12269fb67b80d017133f7d327d1075277&")
            
            await ctx.send(embed=embed, view=MusicControls(ctx, bot))
    else:
        await ctx.send("No more songs in the queue.")


@bot.command(aliases=['queue'])
async def q(ctx):
    if ctx.guild.id not in guild_queues or not guild_queues[ctx.guild.id]:
        return await ctx.send("The queue is currently empty.")

    # Extracting song titles from the queue
    queue_list = "\n".join(f"{index + 1}. {item['title']}" for index, item in enumerate(guild_queues[ctx.guild.id]))

    # Create an embed to display the queue
    embed = discord.Embed(
        title=":notes: **Current Queue:**",
        description=queue_list,
        color=16250871
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/835857771403411469/1285652797034860647/mashle-bring-bang-bang.gif?ex=66eb0cf9&is=66e9bb79&hm=86bd1937ac5bff11a20a0e32d98f9a81dbd2bdb4196d837077e8f4b3c52dbe9a&")   
 
    await ctx.send(embed=embed)


@bot.command(aliases=['download'])
async def skini(ctx, *, query: str):
    async with ctx.typing():
        try:
            ytdl_opts = {
    'verbose': True,
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(download_directory,'template.%(ext)s'),
    'restrictfilenames': False,
    'noplaylist': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],

}
            with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
                # Check if the query is a URL or a search term
                if "youtube.com" in query or "youtu.be" in query:
                    info = ytdl.extract_info(query, download=True)
                else:
                    # Search for the top result
                    info = ytdl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]

                # Path to the downloaded file (always named template.mp3)
                downloaded_file_path = os.path.join(download_directory, 'template.mp3')

                # Debugging: check if the file exists after downloading
                if not os.path.exists(downloaded_file_path):
                    await ctx.send(f"File not found after download: {downloaded_file_path}")
                    return

                # Send the file with the name of the song (info['title']) in Discord
                await ctx.send(file=discord.File(downloaded_file_path, filename=f"{info['title']}.mp3"))

                # After sending the file, delete it
                try:
                    os.remove(downloaded_file_path)
                except Exception as delete_error:
                    print(f"Error deleting file: {delete_error}")

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")



@bot.command()
async def pause(ctx):
    """Pause the currently playing song."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Paused the music.")
    else:
        await ctx.send("No music is playing.")

@bot.command()
async def resume(ctx):
    """Resume the paused song."""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Resumed the music.")
    else:
        await ctx.send("No music is paused.")

@bot.command()
async def stop(ctx):
    """Stop the currently playing song."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Stopped the music.")
    else:
        await ctx.send("No music is playing.")

@bot.command()
async def shutdown(ctx):
    """Shut down the bot."""
    await ctx.send("Shutting down...")
    await bot.close() 

#your bot token here
bot.run('')
