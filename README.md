# Genshin Impact & Star Dome Railway Discord Bot

<p align="center">
<a href="https://github.com/KT-Yeh/Genshin-Discord-Bot/blob/master/LICENSE"><img src="https://img.shields.io/github/license/KT-Yeh/Genshin-Discord-Bot?style=flat-square"></a>
<a href="https://github.com/KT-Yeh/Genshin-Discord-Bot"><img src="https://img.shields.io/github/stars/KT-Yeh/Genshin-Discord-Bot?style=flat-square"></a>
<a href="https://discord.com/application-directory/943351827758460948"><img src="https://img.shields.io/badge/bot-%E2%9C%93%20verified-5865F2?style=flat-square&logo=discord&logoColor=white"></a>
<a href="https://discord.com/application-directory/943351827758460948"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgenshin-dc-bot.kty.one%2Fguilds-count&style=flat-square&logo=Discord&logoColor=white&cacheSeconds=3600"></a>
<a href="https://discord.gg/myugWxgRjd"><img src="https://img.shields.io/discord/963975812443414538?style=flat-square&logo=Discord&logoColor=white&label=support&color=5865F2"></a>
</p>

Feel free to take all or part of the code to your own bot, just put the author and URL of this project in your project's website, README or any public documentation.

## Invite Genshin Impact Helper
[![](https://i.imgur.com/ULhx0EP.png)](https://bit.ly/原神小帮手邀请)
#### Click on the image above or the invitation link: https://bit.ly/原神小帮手邀请
Discord Supported servers: https://discord.gg/myugWxgRjd

## Introduction
Use the robot to view various information in Genshin Impact and Star Dome Railway directly in the Discord chat channel, including:

- Genshin Impact, Honkai Impact 3, Star Dome Railway, Undetermined Event Book, Absolute Zero:
- **Automatic sign-in**: Set a time to automatically sign in to Hoyolab every day to claim your prize

- Genshin Impact, Star Dome Railway, Absolute Zero:
- Check **Instant Note**
- Genshin Impact: including resin, daily commission, cave treasure money, parameter quality change instrument, exploration dispatch
- Star Dome Railway: including pioneering power, daily training, simulated universe, aftermath of battle, commission execution
- Absolute Zero: including power, today's activity, scratch cards, video store management
- **Automatic check instant notes**: resin (pioneering power, power), daily, treasure money, quality change instrument, exploration dispatch, send reminders when the quota is almost full
- Query the records of the Abyss, the Garden of Oblivion, and the Fictional Narrative, and save each record
- Query any player's **character showcase**, display the panel and relics details of the character in the showcase

- Genshin Impact:
- Personal record card, including game days, achievements, divine pupils, world exploration, etc.
- Query traveler's notes
- View in-game announcements, including activities and card pool information
- Search the database, including characters, weapons, various items, achievements, and Seven Saints card information

## How to use
- After inviting to your own server, enter the slash `/` to view various commands
- Please use the command `/cookie setting` for the first time, Cookie acquisition method: https://bit.ly/3LgQkg0
- Set automatic sign-in and instant note reminders, use the command `/schedule scheduling`

## Display
More display pictures, GIF Please refer to the Bahamut introduction article: https://forum.gamer.com.tw/Co.php?bsn=36730&sn=162433

<img src="https://i.imgur.com/LcNJ2as.png" width="350"/>
<img src="https://i.imgur.com/IEckUqY.jpg" width="500"/>
<img src="https://i.imgur.com/PA5HIDO.gif" width="500"/>

## Project folder structure
```
Genshin-Discord-Bot
├── assets = Folder for storing materials
| ├── font = Fonts used for drawing
| └── image = Materials and background images used for drawing
├── cogs = Folder for storing discord.py cog Folder, where all robot commands are located
├── cogs_external = Stores custom discord.py cog folder, where you can put your own command files
├── configs = Folder for storing configuration files
├── database = SQLAlchemy ORM, database operation related code
| ├── alembic = = Database structure change version control
| ├── dataclass = Customized data class
| └── legacy = Previous database code, which is useless except for migrating old data
├── enka_network = Code related to Enka Network API
| └── enka_card = Submodule, code related to drawing Enka pictures
├── genshin_db = Code related to genshin-db API
| └── models = Pydantic models for storing genshin-db data
├── genshin_py = Code related to genshin.py
| ├── auto_task = Code related to automatic scheduling tasks (e.g. check-in)
| ├── client = Code related to requesting data from the API
| └── parser = Converting API data to discord embed format
├── star_rail = Star Dome Railway Display Cabinet Code
└── utility = Some settings, public functions, Log, emoticons, Prometheus... and other codes used in this project
```

## Install & set up the robot yourself

### Web side
You need to obtain the following in this step:
- Robot Application ID
- Robot Bot token
- Your own management server ID

<details><summary>>>> Click here to view the full content <<<</summary>

1. Go to [Discord Developer](https://discord.com/developers/applications "Discord Developer") Log in to your Discord account

![](https://i.imgur.com/dbDHEM3.png)

2. Click "New Application" to create an application, enter the desired name and click "Create"

![](https://i.imgur.com/BcJcSnU.png)

3. On the Bot page, click "Add Bot" to add a new bot

![](https://i.imgur.com/lsIgGCi.png)

4. In OAuth2/URL Generator, check "bot", "applications.commands" and "Send Messages" respectively. The URL link generated at the bottom is the bot's invitation link. Open the link to invite the bot to your server

![](https://i.imgur.com/y1Ml43u.png)

#### Get the ID required for the configuration file

1. In General Information, get the robot's Application ID

![](https://i.imgur.com/h07q5zT.png)

2. On the Bot page, click "Reset Token" to get the robot's Token

![](https://i.imgur.com/BfzjewI.png)

3. Right-click on your Discord **server name or icon** and copy the **server ID** (the Copy ID button needs to be turned on in Settings->Advanced->Developer Mode)

![](https://i.imgur.com/tCMhEhv.png)

</details>

### Local side

#### First use
1. Install Docker (please follow Google instructions if you don't know how to install it)

- Windows: Download and install it from [Docker official website](https://www.docker.com/). After the installation is complete, start Docker Desktop. There will be a whale icon in the lower right corner of the Windows desktop
![](https://i.imgur.com/FlLszWB.png)
- Linux: [Official website description](https://docs.docker.com/engine/install/ubuntu/), there are different distribution options on the left

The following instructions are based on Windows and Powershell unless otherwise specified

2. Find the place where you want to put the data, create a new folder `Genshin-Discord-Bot`, and then enter

3. Download the [docker-compose.yml](https://github.com/KT-Yeh/Genshin-Discord-Bot/blob/master/docker-compose.yml) file and put it in the folder

4. Open the `docker-compose.yml` file in a text editor. Basically, you don’t need to modify it. Just fill in the three data you just got from [#网页端](#网页端) into the three fields below. Other settings can be modified according to your needs. Save after completion
- APPLICATION_ID=`123456789`
- TEST_SERVER_ID=`123456789`
- BOT_TOKEN=`ABCD123456789`

5. Open Powershell in this folder and enter the following command to run
```
docker-compose up
```
If you want to turn off Powershell and run it in the background, use
```
docker-compose up -d
```
Open Docker Desktop with the whale icon in the lower right corner of Windows to manage the robot's running status at any time

Note 1: After running, you will see `【System】on_ready: You have

logged in as XXXXX` means the parameters are set correctly and started successfully. At this time, the robot will automatically synchronize all commands to your test server, which is called "local synchronization".

Note 2: If you can't see the command after entering the slash /, try CTRL + R to refresh or completely close the Discord software and restart Discord.

Note 3: If you want to use it between multiple servers, enter `$jsk sync` in your robot's private message channel and wait (about a few minutes) for Discord to push the command, which is called "global synchronization".

#### Upgrade from the old version v1.2.1 (new installers do not need to read)

<details><summary>>>> Click here to view the full content <<<</summary>

1. Create a new folder `Genshin-Discord-Bot`, and follow the above step 4

2. Copy the data in the old version's `data` folder: `bot.db` (`emoji.json`) to the corresponding location of the new folder

3. So now the new folder structure is as follows:
```
Genshin-Discord-Bot/
├── docker-compose.yml
└── data/
├── bot/
│ └── bot.db
├── app_commands.json
└── emoji.json
```
4. Return to `Genshin-Discord-Bot` Directory, because the database structure has changed, you need to execute the command first
- Windows (Powershell): `docker run -v ${pwd}/data:/app/data ghcr.io/kt-yeh/genshin-discord-bot:latest python main.py --migrate_database`
- Linux: `sudo docker run -v $(pwd)/data:/app/data ghcr.io/kt-yeh/genshin-discord-bot:latest python main.py --migrate_database`
5. After completing the database change, execute `docker-compose up` to start running the robot

</details>

---

### File Description & Data Backup
After successfully running the robot, your folder structure should be like this:
```
Genshin-Discord-Bot/
├── docker-compose.yml = docker configuration file, all the settings related to starting the robot are in this file
├── cogs_external/ = You can put your own discord.py cog in this directory
└── data/ = All data generated by the robot when running are placed in this directory
├── bot/
│ └── bot.db = Database file
├── font/ = Font folder
├── image/ = Image folder
├── _app_commands.json = Command mention settings file
├── _emoji.json = Emoji settings file
├── grafana_dashboard.json = Grafana dashboard settings file
└── prometheus.yml = Prometheus server settings file
```
All data is placed in the `data` folder, just back up the entire folder; when restoring, overwrite the backed up data back to the `data` folder

### How to update
When the project is updated, go to Open Powershell in the `Genshin-Discord-Bot` directory
1. Get the new version of the image
```
docker-compose pull
```
2. Restart the robot
```
docker-compose up -d
```
## Emoji configuration instructions (data/emoji.json)

<details><summary>Click here to view the full content</summary>

It is not necessary, the robot can run normally without configuring emojis
1. Go to the `data` directory and rename `_emoji.json` to `emoji.json`
2. Upload the relevant emojis to your own server
3. Fill the corresponding emojis into the `emoji.json` file according to the Discord format

Note:
- Discord emoji format: `<:table name:table ID>`, for example: `<:Mora:979597026285200002>`
- You can enter in the Discord message channel `\:tab name:` Get the above format

</details>

## Sentry configuration instructions

<details><summary>Click here to view the full content</summary>

Optional, Sentry is used to track exceptions that are not received during program execution, and send detailed information such as function calls, variables, exceptions, etc. at the time of the exception to the web page for developers to track. If this function is not needed, you can skip this setting

1. Register an account on the official website: https://sentry.io/

2. Create a Python project in the account, and you can get the DSN address of the project after creation (format: `https://xxx@xxx.sentry.io/xxx`)

3. Paste this DSN address into the `SENTRY_SDK_DSN` field of the `docker-compose.yml` file

Note:
- If not specified, Sentry defaults to only sending exceptions without try/except
- If you want to send specific received exceptions to Sentry, use in the except `sentry_sdk.capture_exception(exception)`

</details>

## Admin management command description

<details><summary>Click here to view the full content</summary>

Management commands can only be used in the test server set in the configuration file

```python

/status: Display robot status, including delay, number of connected servers, and name of connected servers

/system: Start daily sign-in tasks immediately and download new Enka display cabinet materials

/system precense string1, string2, string3,...: Change the robot display status (playing...), randomly change to one of the set strings every minute, the number of strings is unlimited

/maintenance: Set the game maintenance time, and automatic scheduling (sign-in, resin inspection) will not be executed during this time

/config: Dynamically change the values of some settings

```

In addition, the robot contains the `jsk` command to load/reload modules, synchronize commands, execute code... and so on, please refer to [jishaku Website](https://github.com/Gorialis/jishaku) instructions.
To use jsk commands, you can
- Use it in the robot private message, for example: `$jsk ping`
- Use it in the general channel tag robot, for example: `@原神小帮手 jsk ping`

</details>

## Prometheus / Grafana monitoring dashboard description
<details><summary>Click here to view the full content</summary>

#### Dashboard display

![](https://i.imgur.com/SOctABS.png)

A total of three steps are required, namely
1. Grafana official website to open an account and obtain the API Key
2. Set up the Prometheus server
3. Import the dashboard in Grafana

#### 1. Grafana account registration
1. Go to [Grafana official website](https://grafana.com/) to register an account. During the process, you will be asked to select the Cloud region. Just preset it directly

2. After completing the registration, return to [Official website](https://grafana.com/), select My Account in the upper right corner. As shown in the figure below, you can see that there are Grafana and Prometheus in GRAFANA CLOUD. Select Send Metrics on Prometheus
![](https://i.imgur.com/YLaV2fB.png)

3. Scroll to the middle of the page, select Generate now in Password / API Key, and then the black background part of Sending metrics below is very important, stay on this page first
![](https://i.imgur.com/RlY8ovi.png)

#### 2. Set up Prometheus
1. Return to the robot folder and open the `docker-compose.yml` file in a text editor
1. Uncomment the entire `prometheus` section at the bottom (note that the field format must be aligned)
2. Uncomment `- PROMETHEUS_SERVER_PORT=9091` in the robot advanced settings

2. Go to `data` folder, open the `prometheus.yml` file in a text editor
3. Go back to the Grafana webpage just now, you will see that the `remote_write` field on the webpage corresponds to the bottom of the `prometheus.yml` file, fill in the settings of `remote_write` on the webpage one by one into the corresponding fields in `prometheus.yml`, and then save it
```
remote_write:
- url: https://....(fill in Remote Write Endpoint in this line)
basic_auth:
username: 123456(fill in Username / Instance ID in this line)
password: XXXXXX(fill in Password / API Key in this line)
```
4. Re-run the robot `docker-compose up -d`

#### Grafana import dashboard
After having the data, we also need to display the data on the dashboard

1. Same as steps 1-2, return to [Official website](https://grafana.com/), select My Account in the upper right corner, and this time we press Launch on Grafana

2. Select Dashboards on the left, then click New → Import on the right, and then press the Upload JSON file button
![](https://i.imgur.com/6TFw9EM.png)

3. Go to the `data` folder and upload `grafana_dashboard.json` to Grafana, or copy and paste it to Grafana

4. After successfully importing the dashboard, you can see the robot's data on the dashboard, and it's done

</details>

## Acknowledgements
API:
- Hoyolab: https://github.com/thesadru/genshin.py
- Discord: https://github.com/Rapptz/discord.py
- Enka Network: https://github.com/EnkaNetwork/API-docs
- Mihomo: https://march7th.xiaohei.moe/en/resource/mihomo_api.html
- Genshin-DB: https://github.com/theBowja/genshin-db

Card:
- [hattvr/enka-card](https://github.com/hattvr/enka-card)
- [DEViantUA/HSRCard](https://github.com/DEViantUA/HSRCard)
- [DEViantUA/GenshinPyRail](https://github.com/DEViantUA/GenshinPyRail)

Misc:
- [Apollo-Roboto/discord.py-ext-prometheus](https://github.com/Apollo-Roboto/discord.py-ext-prometheus)
