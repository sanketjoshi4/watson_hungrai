from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import TextToSpeechV1

import csv

text_to_speech_credentials = {
    "apikey": "BLKaQ3nnYTTKruLeb9dL8gtbtxjI856Zx9WFKy0spZET",
    "iam_apikey_description": "Auto-generated for key ed5fac4a-bc22-4d9f-9859-2b248804035e",
    "iam_apikey_name": "wdp-writer",
    "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Writer",
    "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::a/eed7635af9de4ec1a02ed80b7edae9dc::serviceid:ServiceId-d7acec2a-7f78-4eac-ba33-8407e8edca8b",
    "url": "https://api.us-east.text-to-speech.watson.cloud.ibm.com/instances/30ac0c7e-f8e4-48e9-9222-59dbb1f4fc82",
}

text_to_speech_authenticator = IAMAuthenticator(text_to_speech_credentials['apikey'])
text_to_speech_service = TextToSpeechV1(authenticator=text_to_speech_authenticator)
text_to_speech_service.set_service_url(text_to_speech_credentials['url'])


def text_to_speech(msg, num):
    with open('./static/resources/recorded/{}.wav'.format(num), 'wb') as audio_file:
        audio_file.write(
            text_to_speech_service.synthesize(
                msg, voice='en-US_KevinV3Voice', accept='audio/wav'
            ).get_result().content
        )
        audio_file.close()


def etl(update=False):
    tag_map = {}
    tag_lookup = {}
    with open('data/master/master_tag.csv') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        header_parsed = False
        for row in spamreader:
            if not header_parsed:
                header_parsed = True
                continue
            id = int(row[0])
            name = row[1]
            if name is not '':
                tag_map[id] = name
                tag_lookup[name] = id

    item_map = {}
    item_lookup = {}
    tag_item_map = {}
    item_tag_map = {}

    with open('data/master/master_item.csv') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        header_parsed = False
        for row in spamreader:
            if not header_parsed:
                header_parsed = True
                continue

            item_id = int(row[0])
            item_name = row[1]
            item_map[item_id] = item_name
            item_lookup[item_name] = item_id

            candidate_tags = [int(i) for i in row[2:] if str(i) is not '']
            candidate_tags.sort()
            item_tag_map[item_id] = candidate_tags

            for tag_id in candidate_tags:
                if tag_id not in tag_item_map:
                    tag_item_map[tag_id] = []
                tag_item_map[tag_id].append(int(row[0]))

    if update:
        with open('data/entities/entity_items.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            for item_id, item_name in item_map.items():
                spamwriter.writerow(['Item', item_name])

        with open('data/entities/entity_ingredients.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            for tag_id, tag_name in tag_map.items():
                spamwriter.writerow(['Ingredient', tag_name])

    return {
        'master': {
            'tag': tag_map,
            'item': item_map
        },
        'lookup': {
            'tag': tag_lookup,
            'item': item_lookup
        },
        'mapping': {
            'tag_item': tag_item_map,
            'item_tag': item_tag_map
        }
    }


def prep_recording():
    transcript = [
        "Hi! I'm Edward",
        "I'm in the mood for some spicy indian curry",
        "I'd like chicken tikka masala and two mutton masalas",
        "please suggest some indian bread to go with it",
        "I'd like a garlic naan bread and two naan breads. Also add a paneer butter masala",
        "do you serve any pastas?",
        "Could i have  a chicken alfredo pasta please?",
        "and please remove the naan breads",
        "please remind me what my order is again",
        "you know what? scratch that",
        "I'll prefer to have something that's healthy and light instead",
        "do you have fruit salad?",
        "make it four",
        "That's all that i want",
        "roger that"
    ]



if __name__ == '__main__':
    etl()
    # full_text = 'James. What pizzas do you have?. Add two cheese pizzas, one fish taco, and a veggie salad. What have i ordered?. Do you serve pork tacos? Make it three. I dont want the cheese pizzas. What\'s in my cart?. What veggies do you serve?. Add a veggie pizza and two veggie tacos please. That\'s all. That\'s correct.'
    # text_to_speech(full_text, 666)
    # text_to_speech('James', 0)
    # text_to_speech('What pizzas do you have?', 1)
    # text_to_speech('add two cheese pizzas, one fish taco, and a veggie salad', 2)
    # text_to_speech('what have i ordered?', 3)
    # text_to_speech('do you serve pork tacos?', 4)
    # text_to_speech('make it three', 5)
    # text_to_speech('i dont want the cheese pizzas', 6)
    # text_to_speech('what\'s in my cart?', 7)
    # text_to_speech('what veggies do you serve?', 8)
    # text_to_speech('add a veggie pizza and two veggie tacos please?', 9)
    # text_to_speech('that\'s all', 10)
    # text_to_speech('that\'s correct', 11)
