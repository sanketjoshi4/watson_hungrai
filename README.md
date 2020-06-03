COSC 189.02 - Final Project - HungrAI
GR Team 11 - Sanket Joshi, Anmol Chachra

Please follow these instructions to deploy your voice-assisted food recommendation chat-bot:

1. Create a new Watson Assistant Service with the following JSON file (Optional)
        ./data/skill-hungerai-skill.json
   OR
   Use the existing in-code credentials to access an existing service

2. Create a new Watson Speech-to-Text Service and include credentials in this file (Optional)
        ./app.py
   OR
   Use the existing in-code credentials to access an existing service

3. Create a new Watson Text-to-Speech Service and include credentials in this file (Optional)
        ./app.py
   OR
   Use the existing in-code credentials to access an existing service

4. Install Python Watson Library using the command:
        pip install --upgrade "ibm-watson>=4.3.0"

5. To customize data edit the following CSV files (Optional)
        ./data/master/master_item.csv
        ./data/master/master_tag.csv

   And change this flag to True and run
        ./app.py, line 12 : etl_update = False
   Now revert the flag 

   Upload the new intents and entities to Watson Assistant from these files
        ./data/master/entity_items.csv
        ./data/master/entity_ingredients.csv

6. To run the flask application, make sure this flag is false
    ./app.py, line 12 : etl_update = False

   Then type in the command to run this python file as a flask application
    ./app.py

7. Access the web application through your browser on this URL
    localhot:5000

