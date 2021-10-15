from PIL import Image, ImageDraw, ImageFont
import os
### Cada img fa 50 px x 50 px i s'escriu al mig (primera es 25 px)
### La img general s'escala segons el numero de coins que hi ha 75 px x coin

def drawRisks(risks):

    fontR = ImageFont.truetype('fonts/Roboto-Bold.ttf', 50)
    fontC = ImageFont.truetype('fonts/Roboto-Bold.ttf', 30)
    fontT = ImageFont.truetype('fonts/Roboto-Bold.ttf', 30)
    bg = Image.new(mode="RGB" , size=(500, 20+70*len(risks)), color=(242,255,174))
    for i, key in enumerate(risks):
        if os.path.exists(f'img/{key}.png'):
            coin = Image.open(f'img/{key}.png').resize((50,50))
            mask = Image.new('RGBA', coin.size, 0)
            mask.paste(coin)
            bg.paste(coin,(50, 20+(70*i)),mask)
        else:
            name = key.split("-")[0]
            ImageDraw.Draw(bg).text((25, 28+(70*i)), name, fill=(0, 0, 0), font=fontC)

        ImageDraw.Draw(bg).text((175, 28 + (70 * i)), f"{risks[key]['token']}", fill=(0, 0, 0), font=fontT)

        if risks[key]['risk'] >= 50:
            color = (round(risks[key]['risk']*255/100),0,0)
        else:
            color = (0,round((100-risks[key]['risk'])*255/100), 0)
        ImageDraw.Draw(bg).text((300, 15 + (70 * i)), f"{risks[key]['risk']} %", fill=color, font=fontR)
    bg.save("risks.png")
