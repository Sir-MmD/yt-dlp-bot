#v1.0
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import yt_dlp
import os
import subprocess
import re
# Create a Client instance with your API ID and API hash
#allowed_ids = [ID]
app = Client("App_Title", api_id="API_ID", api_hash="API_HASH", bot_token="BOT_TOKEN")

# Global dictionary to store video format details
links_data = {}
user_states = {}

def is_user_allowed(chat_id):
    return chat_id in allowed_ids
    
# Define the /start command handler
@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Please send a link")

# Handler for receiving a message with a link
@app.on_message(filters.regex(r'https?://[^\s]+'))
def handle_link(client, message):
    chat_id = message.chat.id

    #if not is_user_allowed(chat_id):
        #return

    # Check if the user is already in a downloading state
    if user_states.get(chat_id, None) == 'downloading':
        message.reply_text("Please wait, your previous request is still being processed.")
        return

    user_folder = f'downloads/{chat_id}'

    # Check if the folder exists, if not, create it
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    link = message.text
    # Get video formats using yt-dlp
    ydl_opts = {
        'quiet': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            formats = info_dict.get('formats', [info_dict])
            title = info_dict.get('title', 'Video')
    except Exception as e:
        # Error handling when link is not supported or other exceptions occur
        message.reply_text(f"Error fetching link info. The link may not be supported.")
        return

    # Extracting rows with resolutions
    button_rows = []
    current_row = []
    format_ids = {}
    for f in formats:
        format_id = f['format_id']
        resolution = f.get('format_note', f.get('resolution'))
        protocol = f.get('protocol', 'Unknown Proto')  # Extract the protocol
        if resolution and resolution != 'unknown':
            button_text = f"{resolution} ({protocol})"  # Include protocol in the button text
            if button_text not in format_ids:  # Avoid duplicate buttons
                format_ids[button_text] = format_id
                current_row.append(KeyboardButton(button_text))
                # Grouping buttons, 2 per row for better layout
                if len(current_row) == 2:
                    button_rows.append(current_row)
                    current_row = []

    # Add any remaining buttons to the last row
    if current_row:
        button_rows.append(current_row)

    # Storing link and format IDs
    links_data[message.chat.id] = (link, format_ids, title)

    # Sending a message with buttons if any were found
    if button_rows:
        reply_markup = ReplyKeyboardMarkup(button_rows, resize_keyboard=True, one_time_keyboard=True)
        message.reply_text("Choose a resolution and protocol:", reply_markup=reply_markup)
    else:
        message.reply_text("No downloadable links found.")

@app.on_message(filters.regex("Cancel Download"))
def cancel_download(client, message):
    chat_id = message.chat.id

    # Check if the user is in a downloading state
    if user_states.get(chat_id) == 'downloading':
        # Code to cancel the download
        # This could be setting a flag that is checked during the download process
        # and stops the download if the flag is set
        user_states[chat_id] = 'cancel'
        message.reply_text("Download cancelled.")
    else:
        message.reply_text("No active download to cancel.")

# Handler for processing the user's choice
@app.on_message(filters.text)
def download_video(client, message):
    chat_id = message.chat.id

    #if not is_user_allowed(chat_id):
        #return
    
    if user_states.get(chat_id, None) == 'downloading':
        message.reply_text("Please wait, your previous request is still being processed.")
        return
        
    # Check if the user is already in a downloading state
    if user_states.get(chat_id) == 'cancel':
            message.reply_text("Download cancelled by user.")
            user_states.pop(chat_id, None)
            return

    user_folder = f'downloads/{chat_id}'
    if chat_id in links_data:
        link, format_ids, title = links_data[chat_id]
        chosen_resolution = message.text

        if chosen_resolution in format_ids:
            format_id = format_ids[chosen_resolution]

            # Set the user state to 'downloading'
            user_states[chat_id] = 'downloading'

            # Notify the user that the download has started
            cancel_button = KeyboardButton("Cancel Download")
            reply_markup = ReplyKeyboardMarkup([[cancel_button]], resize_keyboard=True, one_time_keyboard=True)
            message.reply_text("Downloading... Press 'Cancel Download' to stop.", reply_markup=reply_markup)

            # Attempt to download the video using yt-dlp
            try:
                ydl_opts = {
                    'format': format_id,
                    'outtmpl': f'{user_folder}/{chat_id}_%(title)s.%(ext)s',
                    'progress_hooks': [lambda d: check_cancel(d, chat_id, message)]
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([link])

                # Find the downloaded file and check its size
                for file in os.listdir(user_folder):
                    if file.startswith(str(chat_id)):
                        full_path = os.path.join(user_folder, file)
                        file_size = os.path.getsize(full_path)
                        message.reply_text("Download finished, sending the video to you...", reply_markup=ReplyKeyboardRemove())
                        # Check if the file size is greater than 4GB
                        if file_size > 4 * 1024 * 1024 * 1024:  # 4GB in bytes
                            message.reply_text("Error: The downloaded video is too large to be sent via Telegram.")
                            os.remove(full_path)  # Remove the large file
                            break
                        
                        try:
                            message.reply_video(full_path, caption=title)
                        except Exception as upload_error:
                            message.reply_text(f"Error uploading the video: {upload_error}")

                        os.remove(full_path)  # Remove the file after sending
                        break
                else:
                    message.reply_text("Downloaded file not found.")

            except Exception as e:
                message.reply_text(f"Error downloading the video: {e}. Please choose another resolution or try again later.")

            finally:
                # Remove the user state lock regardless of outcome
                user_states.pop(chat_id, None)

        else:
            message.reply_text("Invalid resolution selected. Please choose another resolution or try again later.")
            user_states.pop(chat_id, None)  # Remove the state lock in case of invalid selection
    else:
        message.reply_text("No link found. Please send a link first.")
        user_states.pop(chat_id, None)  # Remove the state lock in case no link was found

def check_cancel(data, chat_id, message):
    """Check if the download should be cancelled."""
    if user_states.get(chat_id) == 'cancel':
        message.reply_text("Download cancelled by user.")
        raise Exception("Download cancelled by user")
# Run the bot
app.run()
