# input_handler.py

def create_user_data():

    client_name  = input("Client name: ")
    court = input("Court: ")
    offence = input("Offence: ")
    facts = input("Facts : ")
    language = input("Language (english/hindi): ")

    return {
         "client_name": client_name,
        "court": court,
        "offence": offence,
        "facts": facts,
        "language": language,
        "draft_type": "bail_application"
    }


