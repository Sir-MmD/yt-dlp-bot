## Simple Video Downloader Telegram bot Powered by Pyrogram & YT-DLP

### Features
- Allowed users only filter
- Upload Files up to 4GB (2GB without Telegram Premium subscription)
- Full support of YT-DLP downloader
- Send caption as the title of video

###Get API

####Step 1:
Login into https://my.telegram.org/auth with your telegram phone number
####Step 2:
Click on "API development tools" 
####Step 3:
Filll "App title" and "Short name" and click on "Create application"
####Step 4:
Use @BotFather on telegram to create and get BOT TOKEN
####Step 5:
Open `yt_dlp_tgbot.py` with your text editor and replace `App_Title` and `API_ID` and `API_HASH` and `BOT_TOKEN` with your own information
###Install required packages:
`$ sudo apt update && apt install python3-pip -y && pip install pyrogram TgCrypto`
###Start the bot:
`$ python3 yt_dlp_tgbot.py`

###Important Tips

####Allowed users only:
You can make the bot to operate for only users that you want. You should place USER IDs in line 8 and comment out these lines: 28, 29, 108, 109
####Upload file up to 4GB:
For this should get API from an account which has Telegram Premium subscription and then change `if file_size > 2 * 1024 * 1024 * 1024:` on line 154 to `if file_size > 4 * 1024 * 1024 * 1024:`
####Prevent session termination and possible crashes:
You can run `yt_dlp_tgbot.sh` in `tmux` to prevent session termination and possible crashes:
`$ tmux`

`chmod +x yt_dlp_tgbot.sh`

`./yt_dlp_tgbot.sh`

The `yt_dlp_tgbot.sh` assumes that the  `yt_dlp_tgbot.py` is located on `/root`. You may need to change that.

##Credits:
######YT-DLP: https://github.com/yt-dlp/yt-dlp
######Pyrogram: https://github.com/pyrogram/pyrogram
######ChatGPT: https://chat.openai.com
