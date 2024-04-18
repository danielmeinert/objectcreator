import os
from json import load, dump


dirs = next(os.walk('.'))[1]
# dirs = ['fulltile']

for dir in dirs:
    images = os.listdir(f'{dir}/images')
    data = load(fp=open(f'{dir}/object.json'))

    for im in images:
        if im[0] == '0':
            os.replace(f'{dir}/images/{im}', f'{dir}/images/{im[1:]}')

    for im in data['json']['images']:
        if im['path'][7] == '0':
            im['path'] = f'images/{im["path"][8:]}'

    with open(f'{dir}/object.json', mode='w') as file:
        dump(obj=data, fp=file, indent=2)
