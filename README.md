Genshin & Star Rail Discord Bot
<p align="center">
<a href="https://github.com/KT-Yeh/Genshin-Discord-Bot/blob/master/LICENSE"><img src="https://img.shields.io/github/license/KT-Yeh/Genshin-Discord-Bot?style=flat-square"></a>
<a href="https://github.com/KT-Yeh/Genshin-Discord-Bot"><img src="https://img.shields.io/github/stars/KT-Yeh/Genshin-Discord-Bot?style=flat-square"></a>
<a href="https://discord.com/application-directory/943351827758460948"><img src="https://img.shields.io/badge/bot-%E2%9C%93%20verified-5865F2?style=flat-square&logo=discord&logoColor=white"></a>
<a href="https://discord.com/application-directory/943351827758460948"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgenshin-dc-bot.kty.one%2Fguilds-count&style=flat-square&logo=Discord&logoColor=white&cacheSeconds=3600"></a>
<a href="https://discord.gg/myugWxgRjd"><img src="https://img.shields.io/discord/963975812443414538?style=flat-square&logo=Discord&logoColor=white&label=support&color=5865F2"></a>
</p>

Welcome to use all or part of the code from this project in your own bot. You just need to include the author and link to this project on your project's website, README, or any public documentation.

Feel free to take all or part of the code to your own bot, just put the author and URL of this project in your project's website, README or any public documentation.

Invite Genshin Helper
(https://i.imgur.com/ULhx0EP.png)

Click the image above or the invitation link: https://bit.ly/原神小幫手邀請
Discord Support Server: https://discord.gg/myugWxgRjd

Introduction
Use the bot directly in Discord chat channels to view various information from Genshin Impact and Honkai: Star Rail, including:

Genshin Impact, Honkai Impact 3rd, Honkai: Star Rail, Tears of Themis, Zenless Zone Zero:

Auto Check-in: Set a time to automatically check in to Hoyolab daily to claim rewards.

Genshin Impact, Honkai: Star Rail, Zenless Zone Zero:

Query Real-time Notes

Genshin Impact: Includes Resin, Daily Commissions, Realm Currency, Parametric Transformer, Expedition Dispatches.

Honkai: Star Rail: Includes Trailblaze Power, Daily Training, Simulated Universe, Echo of War, Assignment Execution.

Zenless Zone Zero: Includes Battery, Daily Activity, Scratch Card, Video Store Management.

Auto Check Real-time Notes: Sends reminders when Resin (Trailblaze Power, Battery), Dailies, Realm Currency, Parametric Transformer, Expeditions are almost full.

Query Spiral Abyss, Forgotten Hall, Pure Fiction records, and save records for each period.

Query Character Showcases of any player, displaying character stats and artifact details in the showcase.

Genshin Impact:

Personal record card, including game days, achievements, Oculi, world exploration progress, etc.

Query Traveler's Diary.

View in-game announcements, including event and banner information.

Search database, including characters, weapons, various items, achievements, and Genius Invokation TCG card data.

How to Use
After inviting the bot to your server, type slash / to view various commands.

For the first time, please use the /cookie設定 (cookie settings) command. How to obtain cookies: https://bit.ly/3LgQkg0

To set up auto check-in and real-time note reminders, use the /schedule排程 (schedule) command.

Demo
For more demo images and GIFs, please refer to the Bahamut introduction article: https://forum.gamer.com.tw/Co.php?bsn=36730&sn=162433

(https://i.imgur.com/LcNJ2as.png)
(https://i.imgur.com/IEckUqY.jpg)
(https://i.imgur.com/PA5HIDO.gif)

Project Folder Structure
Genshin-Discord-Bot
├── assets           = Folder for assets
|   ├── font         = Fonts used for drawing
|   └── image        = Assets and background images used for drawing
├── cogs             = Folder for discord.py cogs, containing all bot commands
├── cogs_external    = Folder for custom discord.py cogs, you can put your own command files here
├── configs          = Folder for configuration files
├── database         = SQLAlchemy ORM, database operation related code
|   ├── alembic      = Database schema migration version control
|   ├── dataclass    = Custom data classes
|   └── legacy       = Old database code, only used for migrating old data
├── enka_network     = Code related to Enka Network API
|   └── enka_card    = Submodule, code related to drawing Enka images
├── genshin_db       = Code related to genshin-db API
|   └── models       = Pydantic models for genshin-db data
├── genshin_py       = Code related to genshin.py
|   ├── auto_task    = Code related to automatic scheduled tasks (e.g., check-in)
|   ├── client       = Code related to requesting data from API
|   └── parser       = Converts API data into discord embed format
├── star_rail        = Honkai: Star Rail showcase code
└── utility          = Settings, utility functions, Log, emojis, Prometheus, etc. used in this project

Self-Installation & Bot Setup
Web Side
You need to obtain the following in this step:

Bot Application ID

Bot Token

Your management server ID

<details><summary>>>> Click here to view full content <<<</summary>

Go to Discord Developer and log in to your Discord account.

(https://i.imgur.com/dbDHEM3.png)

Click "New Application" to create an application, enter the desired name, then click "Create".

(https://i.imgur.com/BcJcSnU.png)

On the Bot page, click "Add Bot" to add a new bot.

(https://i.imgur.com/lsIgGCi.png)

In OAuth2/URL Generator, check "bot" and "applications.commands" and "Send Messages". The URL generated at the bottom is the bot's invitation link. Open the link to invite the bot to your server.

(https://i.imgur.com/y1Ml43u.png)

Obtain IDs required for configuration files
In General Information, obtain the bot's Application ID.

(https://i.imgur.com/h07q5zT.png)

On the Bot page, click "Reset Token" to obtain the bot's Token.

(https://i.imgur.com/BfzjewI.png)

Right-click on your Discord server name or icon and copy the server ID (the "Copy ID" button requires enabling Developer Mode in Settings -> Advanced).

(https://i.imgur.com/tCMhEhv.png)

</details>

Local Side
First Time Use
Install Docker (please Google tutorials if you don't know how to install it)

Windows: Go to Docker official website to download and install. After installation, launch Docker Desktop. You will see a whale icon in the bottom right corner of the Windows desktop.
(https://i.imgur.com/FlLszWB.png)

Linux: Official documentation, with different Distributions available on the left.

From now on, unless otherwise specified, all instructions will be for Windows, using Powershell.

Find a location where you want to store the data, create a new folder Genshin-Discord-Bot, then enter it.

Download the docker-compose.yml file and place it in the folder.

Open the docker-compose.yml file with a text editor. Generally, you don't need to change anything except filling in the three fields below with the information you obtained in #Web Side. Other settings can be modified according to your needs. Save after completion.

APPLICATION_ID=123456789

TEST_SERVER_ID=123456789

BOT_TOKEN=ABCD123456789

Open Powershell in this folder and enter the following command to run:

docker-compose up

If you want to close Powershell and run in the background, use:

docker-compose up -d

You can open Docker Desktop from the whale icon in the bottom right of Windows to manage the bot's running status at any time.

Note 1: When you see 【System】on_ready: You have logged in as XXXXX after running, it means the parameters are set correctly and the bot has started successfully. At this point, the bot will automatically synchronize all commands to your test server, which is called "local synchronization".

Note 2: If you type slash / and don't see commands, please try CTRL + R to refresh or completely close and restart Discord software.

Note 3: If you want to use it across multiple servers, type $jsk sync in the bot's private message channel and wait (a few minutes) for Discord to push the commands. This is called "global synchronization".

Upgrading from old v1.2.1 (New installers can skip this)
<details><summary>>>> Click here to view full content <<<</summary>

Create a new folder Genshin-Discord-Bot, and follow steps 1-4 above.

Copy the data from the old version's data folder: bot.db (emoji.json), to the corresponding location in the new folder.

So now the new folder structure is as follows:

Genshin-Discord-Bot/
    ├── docker-compose.yml
    └── data/
        ├── bot/
        │   └── bot.db
        ├── app_commands.json
        └── emoji.json

Go back to the Genshin-Discord-Bot directory. Since the database structure has changed, you need to run the command first:

Windows (Powershell): docker run -v ${pwd}/data:/app/data ghcr.io/kt-yeh/genshin-discord-bot:latest python main.py --migrate_database

Linux: sudo docker run -v $(pwd)/data:/app/data ghcr.io/kt-yeh/genshin-discord-bot:latest python main.py --migrate_database

After completing the database migration, run docker-compose up to start the bot.

</details>

File Description & Data Backup
After successfully running the bot, your folder structure should look like this:

Genshin-Discord-Bot/
    ├── docker-compose.yml  = Docker configuration file, all bot startup settings are in this file
    ├── cogs_external/      = You can put your own discord.py cogs in this directory
    └── data/               = All data generated during bot operation is stored in this directory
        ├── bot/
        │   └── bot.db          = Database file
        ├── font/           = Folder for font data
        ├── image/          = Folder for image data
        ├── _app_commands.json  = Command mention configuration file
        ├── _emoji.json         = Emoji configuration file
        ├── grafana_dashboard.json = Grafana dashboard configuration file
        └── prometheus.yml      = Prometheus server configuration file

All data is stored in the data folder. You can back up the entire folder; to restore, simply overwrite the data folder with your backup.

How to Update
When the project has an update, go to the Genshin-Discord-Bot directory and open Powershell.

Pull the new image

docker-compose pull

Restart the bot

docker-compose up -d

Emoji Configuration (data/emoji.json)
<details><summary>Click here to view full content</summary>

Optional, the bot can run normally without configuring emojis.

Go to the data directory and rename _emoji.json to emoji.json.

Upload relevant emojis to your own server.

Fill in the corresponding emojis in the emoji.json file according to Discord format.

Note:

Discord emoji format: <:emoji_name:emoji_ID>, for example: <:Mora:979597026285200002>

You can type \:emoji_name: in a Discord message channel to get the above format.

</details>

Sentry Configuration
<details><summary>Click here to view full content</summary>

Optional. Sentry is used to track uncaught exceptions during program execution and sends detailed information such as function calls, variables, exceptions, etc., at the time of the exception to a web page for developers to track. If you don't need this feature, you can skip this setting.

Register an account on the official website: https://sentry.io/

Create a Python project within your account. After creation, you can obtain the project's DSN URL (format: https://xxx@xxx.sentry.io/xxx).

Paste this DSN URL into the SENTRY_SDK_DSN field in the docker-compose.yml file.

Note:

If not specified, Sentry defaults to only sending exceptions that are not caught by try/except.

If you want to send specific caught exceptions to Sentry, use sentry_sdk.capture_exception(exception) within that except block.

</details>

Admin Management Commands
<details><summary>Click here to view full content</summary>

Management commands can only be used within the test server configured in the settings file.

/status: Displays bot status, including latency, number of connected servers, connected server names.
/system: Immediately starts daily check-in tasks, downloads new Enka showcase assets.
/system precense string1,string2,string3,...: Changes the bot's display status (playing...), randomly changes to one of the set strings every minute, unlimited string quantity.
/maintenance: Sets game maintenance time. Automatic schedules (check-in, resin check) will not execute during this time.
/config: Dynamically changes values of some settings.

Additionally, the bot includes the jsk command which can load/reload modules, synchronize commands, execute code, etc. Please refer to the jishaku website for details.
To use jsk commands, you can:

Use them in the bot's private messages, e.g., $jsk ping

Tag the bot in a regular channel, e.g., @Genshin Helper jsk ping

</details>

Prometheus / Grafana Monitoring Dashboard
<details><summary>Click here to view full content</summary>

Dashboard Demo Image
(https://i.imgur.com/SOctABS.png)

A total of three steps are required:

Obtain an API Key from the Grafana official website.

Configure the Prometheus server.

Import the Dashboard into Grafana.

1. Grafana Account Registration
Register an account on the Grafana official website. During registration, you will be asked to select a Cloud region; the default is fine.

After registration, return to the official website. In the top right corner, select My Account. As shown in the image below, you can see Grafana and Prometheus under GRAFANA CLOUD. Select Send Metrics on Prometheus.
(https://i.imgur.com/YLaV2fB.png)

Scroll to the middle of the page, select Generate now under Password / API Key, then the black-background section under Sending metrics is very important, stay on this page.
(https://i.imgur.com/RlY8ovi.png)

2. Configure Prometheus
Go back to the bot folder, open the docker-compose.yml file with a text editor.

Uncomment the entire prometheus section at the bottom (pay attention to indentation).

Uncomment - PROMETHEUS_SERVER_PORT=9091 in the bot's advanced settings.

Go to the data folder, open the prometheus.yml file with a text editor.

Return to the Grafana webpage. You will see that the remote_write field on the webpage corresponds to the bottom of the prometheus.yml file. Fill in the settings from the webpage's remote_write into the corresponding fields in prometheus.yml, then save the file.

remote_write:
- url: https://....(Fill in Remote Write Endpoint here)
  basic_auth:
    username: 123456(Fill in Username / Instance ID here)
    password: XXXXXX(Fill in Password / API Key here)

Restart the bot with docker-compose up -d.

Grafana Dashboard Import
Once you have data, you also need to display it on a dashboard.

Similar to steps 1-2, return to the official website. In the top right corner, select My Account, and this time click Launch on Grafana to start it.

On the left, select Dashboards, then on the right, click New → Import, and then click the Upload JSON file button.
(https://i.imgur.com/6TFw9EM.png)

Go to the data folder, upload grafana_dashboard.json to Grafana, or you can copy and paste it into Grafana.

After successfully importing the dashboard, you can see various bot data on the dashboard. This completes the process.

</details>

Acknowledgements
APIs:

Hoyolab: https://github.com/thesadru/genshin.py

Discord: https://github.com/Rapptz/discord.py

Enka Network: https://github.com/EnkaNetwork/API-docs

Mihomo: https://march7th.xiaohei.moe/en/resource/mihomo_api.html

Genshin-DB: https://github.com/theBowja/genshin-db

Cards:

hattvr/enka-card

DEViantUA/HSRCard

DEViantUA/GenshinPyRail

Misc:

Apollo-Roboto/discord.py-ext-prometheus
