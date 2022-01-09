#!//usr/bin/python3

import sys
import requests
from bs4 import BeautifulSoup
import subprocess
from PIL import (
    ImageFont,
    ImageDraw,
    Image
)


def get_image_url(word):
    url = 'https://www.google.com/search?q=%s&source=lnms&tbm=isch' % word
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    image_url = soup.find_all('img')[2]['src']
    return image_url


def add_corners(image, rad):
    im = Image.open(image)
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def resize_image(image, width, height):
    img = Image.open(image)
    new_size = (width, height)
    img = img.resize(new_size, Image.ANTIALIAS)
    return img


def write_text_on_image(image, text, font_size, y):
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(
        '/usr/share/fonts/truetype/tlwg/Purisa.ttf', 
        size=font_size)
    w, h = draw.textsize(text)
    # (img.width-w)/2-30
    draw.text((10,y), text, (0,0,0), font=font)
    img.save(image)


def get_concat_h(image):
    img = Image.open(image)
    width, height = img.size
    dst = Image.new('RGB', (width*4+50, (height+10)*2+10), (9,108,128))
    for i in range(0, 4): dst.paste(img, ((width+10)*i+10, 10))
    for i in range(0, 4): dst.paste(img, ((width+10)*i+10, height+20))
    return dst


def montage():
    top_img = Image.open('top.png')
    bottom_img = Image.open('bottom.png')
    dst = Image.new('RGB', (430+20, 400), 'skyblue')
    dst.paste(top_img, (int(430/2)-40, 40))
    dst.paste(bottom_img, (0, top_img.height + 70))
    return dst

 
if __name__ == '__main__':
    try:
        # with open('words.txt', 'r') as words_file:
        #     for word in words_file.readlines():
        #         word = word.strip()
        words = subprocess.Popen(
            'egrep "*bit$" /usr/share/dict/words', shell=True, 
            stdout=subprocess.PIPE).\
                stdout.read().decode().split('\n')

        for word in words:
            word = word.strip()
            # word = sys.argv[1]
            image_file_name = 'temp.png'
            image_url = get_image_url(word)
            response = requests.get(image_url, allow_redirects=True)
            open(image_file_name, 'wb').write(response.content) # save image  
             
            # add_corners(image_file_name, 20).save(image_file_name)
            resize_image(image_file_name, 100, 100).save('top.png')
            resize_image(image_file_name, 100, 100).save(image_file_name)
            get_concat_h(image_file_name).save('bottom.png')
            
            image = './output/%s.png' % word
            montage().save(image)
            write_text_on_image(image, word, 25, 10)
            write_text_on_image(image, word.replace('bit', 'byte'), 25, 140)
            # add_corners(image, 10).save(image)
            print(f'image {word} completed.')

    except Exception as error:
        pass  
