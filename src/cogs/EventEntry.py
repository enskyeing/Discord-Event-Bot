import discord
from discord.ext import commands
from PIL import Image
import requests
from io import BytesIO


ENTERED_ROLE: int = 1520966554785681550  # Role that is given to users who have entered the event
ENTRY_CHANNEL: int = 1521361334816739459  # Channel that users sends their submissions
SUBMISSION_CHANNEL: int = 1521361083464679615  # Channel that holds all user submissions
VOTING_CHANNEL: int = 1521361174145531944  # Channel that holds all user submissions for voting
EMBED_COLOR: str = "#0f7ed3"
SUBMISSIONS_DIR: str = f"src\\submissions"  # Directory to save submissions


class EventEntry(commands.Cog):
    """Cog for event entry that requires image submissions."""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.total_entries = 0

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.channel.id != ENTRY_CHANNEL:
            return
        
        # Check if author is still in server and not a bot
        author = message.author
        if not isinstance(author, discord.Member):
            # User is not a member of the guild, cannot add role
            return
        if author.bot:
            # Ignore messages from bots
            return
        
        # Get role
        guild = message.guild
        role = guild.get_role(ENTERED_ROLE) if guild else None
        if role is None:
            print(f"Role with ID {ENTERED_ROLE} not found.")
            await message.channel.send(f"{author.mention}, there was an error processing your submission. Please contact modmail <@623557041776230403>.", delete_after=10)
            await message.delete()
            return
        
        # Get submission from attachments
        has_image: bool = False
        save_path: str = ""
        content_type: str = ""
        submission: Image.Image | None = None
        for att in message.attachments:
            if att.content_type and att.content_type.startswith("image/"):
                has_image = True
                content_type = att.content_type.split("/")[1]  # Get the image type (e.g., 'png', 'jpeg')
                save_path = f"{SUBMISSIONS_DIR}/{self.total_entries + 1}-{author.id}.{content_type}"
                submission = self.download_attachment(att, save_path)
                if submission is None:
                    break  # Stop processing if the image could not be downloaded
                break  # Only download the first image attachment

        if not has_image:
            # No attachments found
            await message.channel.send(f"{author.mention}, you must attach an image submission to enter the event.", delete_after=10)
            await message.delete()  # Delete the original message
            return
        
        if submission is None:
            # Image could not be downloaded
            await message.channel.send(f"{author.mention}, there was an error processing your submission. Please contact modmail <@623557041776230403>.", delete_after=10)
            await message.delete()  # Delete the original message
            return

        # Successful entry
        self.total_entries += 1
        await self.send_submission(save_path, f"{author.id}.{content_type}", author)
        await author.add_roles(role)
        await message.channel.send(f"{author.mention} you have successfully entered the event. Thank you for your submission!", delete_after=10)
        await message.delete()  # Delete the original message
    
    def download_attachment(self, attachment: discord.Attachment, save_path: str) -> Image.Image | None:
        """Download an attachment to a specified path using PIL."""
        r = requests.get(attachment.url)
        if r.status_code == 200:
            try:
                image = Image.open(BytesIO(r.content))
                image.save(save_path)
                return image
            except ValueError as e:
                print(f"Failed to process image from {attachment.url}. Potential invalid file type.Error: {e}")
                return None
            except Exception as e:
                print(f"An unexpected error occurred while processing the image from {attachment.url}. Error: {e}")
                return None
        else:
            print(f"Failed to download attachment from {attachment.url}. Status code: {r.status_code}")
            return None

    def submission_embed(self) -> discord.Embed:
        """Create an embed for the submission."""
        
        embed = discord.Embed(title=f"Entry #{self.total_entries}", color=discord.Color.from_str(EMBED_COLOR))
        return embed

    async def send_submission(self, file_path: str, file_name: str, author: discord.Member) -> None:
        """Send the submission to the submission channel."""
        submission_channel = self.bot.get_channel(SUBMISSION_CHANNEL)
        if submission_channel is None:
            print(f"Submission channel with ID {SUBMISSION_CHANNEL} not found.")
            return
        elif not isinstance(submission_channel, discord.TextChannel):
            print(f"Submission channel with ID {SUBMISSION_CHANNEL} is not a text channel.")
            return
        
        voting_channel = self.bot.get_channel(VOTING_CHANNEL)
        if voting_channel is None:
            print(f"Voting channel with ID {VOTING_CHANNEL} not found.")
            return
        elif not isinstance(voting_channel, discord.TextChannel):
            print(f"Voting channel with ID {VOTING_CHANNEL} is not a text channel.")
            return
        
        submission_embed = self.submission_embed()

        file = discord.File(fp=file_path, filename=file_name)
        submission_embed.set_image(url=f"attachment://{file_name}")
        await submission_channel.send(f"New submission from {author.mention}, `{author.id}`!", embed=submission_embed, file=file)

        file = discord.File(fp=file_path, filename=file_name)
        submission_embed.set_image(url=f"attachment://{file_name}")
        voting_message = await voting_channel.send(embed=submission_embed, file=file)
        await voting_message.add_reaction("⬆️")
        await voting_message.add_reaction("⬇️")


async def setup(bot) -> None:
    await bot.add_cog(EventEntry(bot))
        