# WCBot

Discord bot that will help with transcription/retrieval of timelines
Currently there are two supported commands
1. /transcribe_tl <br />
   params: <br />
   boss - boss number from 1-5 <br />
   unit1-5 - the units used in the timeline <br />
   This command will transcribe a tl into a google sheet titled Timelines data store that looks like this: <br />
   ![image](https://github.com/xutheo/WCBot/assets/142357842/ef66de73-2361-4ce4-8403-5f71f7f223b1) <br />
   Note: A copy of this sheet can be found here:   https://docs.google.com/spreadsheets/d/19G9Juc0a1XuSu1_6y3NotZkpVEFpPonDjug_kHZ6KRg/edit#gid=0 <br /> <br />
   Step by step images of how the command works: <br />
   ![image](https://github.com/xutheo/WCBot/assets/142357842/4055c3ca-2fd9-48fe-bf84-e1800d078baa) <br />
   Command inputs <br /> <br />

   ![image](https://github.com/xutheo/WCBot/assets/142357842/7808e43f-cf70-4682-9abb-7c09417184be) <br />
   Responds with a woody-grade technology translation and follows up with an input if you want to save this TL or not <br />
   
2. /list_tls <br />
   parameters: <br />
   boss - boss number from 1-5 <br />
   unit_filter1-5 - filter by these units when looking for tls <br />
   This command will list all timelines for a boss that contain units in the unit_filters <br />
   Ex. /list_tls boss: 1 unit_filter1: Ruka will list all timelines for boss 1 that have Ruka <br /> <br />
   Step by step images of how the command works: <br />
   ![image](https://github.com/xutheo/WCBot/assets/142357842/ba149eae-5b8d-47a7-b158-c87c70227207) <br />
   Command inputs to find all tls for boss 1 with ruka in it <br /> <br />

   ![image](https://github.com/xutheo/WCBot/assets/142357842/5cbf4cde-2799-4bb8-ae02-7008b0664717) <br />
   Responds with a list of tls that you can view with the previous and next buttons <br />

# How to setup WCBot locally:
1. Follow the instructions here: https://developers.google.com/workspace/guides/create-credentials#service-account to create a service account
2. After creating one, go to https://console.cloud.google.com/iam-admin/serviceaccounts -> keys and click Add Key -> Json to generate a json to auth to google sheets
3. Your key will have an email associated with it.  For example, mine is pcrbot@massive-anagram-336417.iam.gserviceaccount.com.  Give this email editor access to the two sheets that you need to run this bot (Local copy of Woody's Translations sheet and local copy of the sheet above.  Make sure to rename them accordingly.)
4. Rename the file to service_account.json and add it to the base folder of your project
5. If you haven't already, follow instructions online to create a discord bot and add it to a server or dm zalteo for an already created bot.
6. Add a new field to the service_account.json called 'discord_token' and input your discord bot token.
7. Run main.py
   
