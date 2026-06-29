import discord
from discord.ext import commands
import PIL


ENTERED_ROLE: int = 1520966554785681550
ENTRY_CHANNEL: int = 0
SUBMISSION_CHANNEL: int = 0 


class EventEntry(commands.Cog):
    """Cog for event entry that requires image submissions."""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.channel.id != ENTRY_CHANNEL:
            return
        
        author = message.author
        if not isinstance(author, discord.Member):
            # user is not a member of the guild, cannot add role
            return
        
        guild = message.guild
        role = guild.get_role(ENTERED_ROLE) if guild else None
        if role is None:
            print(f"Role with ID {ENTERED_ROLE} not found.")
            return

        has_image = False
        for att in message.attachments:
            if att.content_type and att.content_type.startswith("image/"):
                has_image = True
                save_path = f"submissions/{author.id}"
                self.download_attachment(att, save_path)
                break  # Only download the first image attachment

        if not has_image:
            await message.channel.send(f"{message.author.mention}, you must attach an image submission to enter the event.")
            return
        
        await author.add_roles(role)
        await message.channel.send(f"{author.mention} you have successfully entered the event. Thank you for your submission!")
    
    def download_attachment(self, attachment: discord.Attachment, save_path: str) -> None:
        """Download an attachment to a specified path using PIL."""
        pass

    def submission_embed(self):
        """Create an embed for the submission."""
        pass
        