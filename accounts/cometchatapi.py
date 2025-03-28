import requests
import json

from hoti.settings import cometchat_headers,cometchat_base_url,cometchat_api_version


def create_cometchat_profile(user_id,profile_image_url, username, profile_name, user_type):
    comet_chat_api_url = cometchat_base_url+cometchat_api_version+"/users"

    data = json.dumps(

        {
            "uid": user_id,
            "name": profile_name,
            "metadata": {
                "profile_image": profile_image_url,
                "username": username,
                "profile_name": profile_name,
                "user_type": user_type
            }

        })

    response = requests.request("POST", comet_chat_api_url, headers=cometchat_headers, data=data)

    if response.status_code == 200:
        return True
    else:
        return False


def update_cometchat_profile(user_id,profile_image_url, username, profile_name, user_type):
    comet_chat_api_url = cometchat_base_url + cometchat_api_version + "/users/"+str(user_id)


    data = json.dumps({
        "metadata": {
            "name":profile_name ,
            "user_type": user_type,
            "profile_image":profile_image_url,
            "username": username,
            "profile_name": profile_name,

            }
        })
    response = requests.request("PUT", comet_chat_api_url, headers=cometchat_headers, data=data)

    if response.status_code == 200:
        return True
    else:
        return False
