import requests
import json
from tqdm import tqdm
from pprint import pprint

class VK:
    BASE_URL = 'https://api.vk.com/method/'

    def __init__(self, access_token, version='5.131'):
        self.access_token = access_token
        self.version = version

    def get_photos(self, user_id, photo_count=5):
        photos_url = self.BASE_URL + 'photos.get'
        params = {
            'access_token': self.access_token,
            'v': self.version,
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1,
            'count': photo_count
        }
        response = requests.get(photos_url, params=params).json()
        print(response)
        return response['response']['items']

class YandexDisk:
    BASE_URL = 'https://cloud-api.yandex.net/v1/disk/'

    def __init__(self, token):
        self.token = token

    def headers(self):
        return {'Authorization': f'OAuth {self.token}'}

    def upload_file(self, file_path, url):
        upload_url = self.BASE_URL + 'resources/upload'
        headers = self.headers()
        params = {'url': url, 'path': file_path, 'overwrite': 'true'}
        try:
            response = requests.post(upload_url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'Ошибка загрузки файла: {e}')

    def create_folder(self, folder_name):
        create_folder_url = self.BASE_URL + 'resources'
        headers = self.headers()
        params = {'path': folder_name}
        response = requests.put(create_folder_url, headers=headers, params=params)
        if response.status_code == 201 or response.status_code == 409:
            print(f'Папка {folder_name} уже существует или была успешно создана')

def main(vk_token, yandex_token, user_id):
    vk_client = VK(vk_token)
    yandex_client = YandexDisk(yandex_token)
    folder_name = 'vk_photos'
    yandex_client.create_folder(folder_name)

    photos = vk_client.get_photos(user_id)
    photos_info = []

    for photo in tqdm(photos, desc="Загрузка фотографий"):
        likes = photo['likes']['count']
        date = photo['date']
        max_size = max(photo['sizes'], key=lambda x: x['width'] * x['height'])
        file_name = f"{likes}_{date}.jpg" if str(likes) in [p['file_name'] for p in photos_info] else f"{likes}.jpg"
        yandex_client.upload_file(f'{folder_name}/{file_name}', max_size['url'])
        photos_info.append({"file_name": file_name, "size": max_size['type']})

    with open('photos_info.json', 'w', encoding='utf-8') as f:
        json.dump(photos_info, f, ensure_ascii=False, indent=4)

    print("Загрузка завершена. Информация о файлах сохранена в photos_info.json")


if __name__ == "__main__":
    vk_token = input("Введите токен VK: ")
    yandex_token = input("Введите токен Яндекс.Диск: ")
    user_id = input("Введите ID пользователя VK: ")
    main(vk_token, yandex_token, user_id)
