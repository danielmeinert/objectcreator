import os
from json import load, dump


dirs = next(os.walk('.'))[1]
# dirs = ['fulltile']

for dir in dirs:
    images = os.listdir(f'{dir}/images')
    data = load(fp=open(f'{dir}/object.json'))

    for im in images:
        if im == '.png':
            os.replace(f'{dir}/images/{im}', f'{dir}/images/0.png')

    with open(f'{dir}/object.json', mode='w') as file:
        dump(obj=data, fp=file, indent=2)
