# WCBot

Discord bot that will help with transcription/retrieval of timelines
Currently there are two supported commands
1. /transcribe_tl
   parameters: 
   boss - boss number from 1-5
   unit1-5 - the units used in the timeline
   This command will transcribe a tl into a google sheet titled Timelines data store that looks like this:
   ![image](https://github.com/xutheo/WCBot/assets/142357842/ef66de73-2361-4ce4-8403-5f71f7f223b1)
   Note: A copy of this sheet can be found here:   https://docs.google.com/spreadsheets/d/19G9Juc0a1XuSu1_6y3NotZkpVEFpPonDjug_kHZ6KRg/edit#gid=0
   Step by step images of how the command works:
   ![image](https://github.com/xutheo/WCBot/assets/142357842/4055c3ca-2fd9-48fe-bf84-e1800d078baa)
   Command inputs

   ![image](https://github.com/xutheo/WCBot/assets/142357842/7808e43f-cf70-4682-9abb-7c09417184be)
   Responds with a woody-grade technology translation and follows up with an input if you want to save this TL or not
   
2. /list_tls
   parameters:
   boss - boss number from 1-5
   unit_filter1-5 - filter by these units when looking for tls
   This command will list all timelines for a boss that contain units in the unit_filters
   Ex. /list_tls boss: 1 unit_filter1: Ruka will list all timelines for boss 1 that have Ruka
   Step by step images of how the command works:
   ![image](https://github.com/xutheo/WCBot/assets/142357842/ba149eae-5b8d-47a7-b158-c87c70227207)
   Command inputs to find all tls for boss 1 with ruka in it

   ![image](https://github.com/xutheo/WCBot/assets/142357842/5cbf4cde-2799-4bb8-ae02-7008b0664717)
   Responds with a list of tls that you can view with the previous and next buttons

# How to setup WCBot locally:
1. Follow the instructions here: https://developers.google.com/workspace/guides/create-credentials#service-account to create a service account
2. After creating one, go to https://console.cloud.google.com/iam-admin/serviceaccounts -> keys and click Add Key -> Json to generate a json to auth to google sheets
3. Rename the file to service_account.json and add it to the base folder of your project
4. If you haven't already, follow instructions online to create a discord bot or dm zalteo for an already created bot.
5. Add a new field to the service_account.json called 'discord_token' and input your discord bot token.
6. Run main.py
   
