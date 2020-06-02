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

voice_0 = 'en-US_AllisonV3Voice'
voice_1 = 'en-US_KevinV3Voice'
voice_2 = 'en-US_LisaV3Voice'


def text_to_speech(msg, num, voice=voice_0):
    print('tts_' + str(num))
    with open('./static/resources/recorded/{}.wav'.format(num), 'wb') as audio_file:
        audio_file.write(
            text_to_speech_service.synthesize(
                msg, voice=voice, accept='audio/wav'
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
        "Hello there! I'm Jonathan",
        "I'm craving for something with chicken, beef, and pork!",
        "Why not?",
        "I'm in the mood for something spicy! An indian curry probably?",
        "I'd like a chicken tikka masala and three diet cokes please",
        "Could you remove the all meat platter please?",
        "Please repeat my order",
        "You know what? Scratch that",
        "What pizza do you have?",
        "Do you serve meat lovers pizza by chance?",
        "Nevermind",
        "Could you recommend something that is both sweet and tangy?",
        "make it three",
        "That's all that I want",
        "That is correct"
    ]
    [text_to_speech(v, i) for i, v in enumerate(transcript)]

    text_to_speech('. '.join(transcript), 99, voice=voice_1)


def demo_transcript():
    transcript = [
        "We are Team 11, and we present to you Hunger A.I., the one stop shop for lazy, hungry people! Did you know that the average american spends upwards of a hundred hours annually, deciding what to eat?, Double that if its a group, or a couple.",
        "Most of us have some idea of what we want, but the last step, the decision itself, is something we hesitate to make. This is where Hunger A.I. comes in.",
        "With our voice assisted food recommendation system, we help users decide what they want, by taking general clues from them. Say goodbye to browsing gigantic menu cards, and to typing! Just speak up your mind, and order away!",
        "If you know what you want, no harm! Search by food, ingredients, cuisines, dietary requirements, and, more. Edit your cart with ease and finalize your order with the click of a button. Wait, you don't even need to do that, because we listen to you!",
        "All this for only nine ninety nine a month, or five ninety nine a month for an annual plan. Restaurants can use it for a 5% commission and free users can use it for 3% commission. We plan to constantly update our databases with information from restaurants and intents and suggestions from users.",
        "In the long term, we plan to expand to the e-commerce sector, where large swaths of labelled data resides. The bigger the data, the better our recommendation system. We plan to expand the supported languages beyond english as well as add accessibilities for people with special needs with better a voice support.",
        "Now, to get technical, our system is powered by an h.t.m.l. c.s.s. javascript front end chat application supported on web application or mobile web, and a python flask server over a my sequel database. ",
        "The app receives audio from the client, converts it to text using watson's speech to text a.p.i, and forwards that to watson assistant. With over a dozen intents, hundreds of entities, all linked to the database with en ETL process, the assistant supports features like item recommendation based on tags, fuzzy item search, and more.",
        "The flask cache is used to temporarily store the user order till checkout. Watson assistant also recognizes commands to add, remove, update and reset the cart. Conditional replies are then forwarded to watson's text to speech a.p.i, which then sends the audio to the client app. Let's proceed to the demo."
    ]
    [text_to_speech(v, i + 200, voice=voice_1) for i, v in enumerate(transcript)]


if __name__ == '__main__':
    # demo_transcript()
    prep_recording()
    # text_to_speech('Please repeat my order.         ________                     hello', 102, voice=voice_1)
    # etl()
