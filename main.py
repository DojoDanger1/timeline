import json
import copy
import time
from PIL import Image, ImageDraw, ImageColor, ImageFont

with open('data/other/colours.json') as f:
    colours = json.load(f)

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

titleFont = ImageFont.truetype(r'fonts/Montserrat-Medium.ttf', 40)
dateFont = ImageFont.truetype(r'fonts/Montserrat-Medium.ttf', 30)
sectionFont = ImageFont.truetype(r'fonts/Montserrat-SemiBold.ttf', 40)

def isLeapYear(year):
    if (year % 4 == 0 and not year % 100 == 0) or (year % 400 == 0):
        return True
    return False

def calcDaysBetween(startDateOriginal, endDate):
    startDate = copy.copy(startDateOriginal)
    total = 1
    while startDate != endDate:
        total += 1
        startDate['day'] += 1
        if (
            startDate['month'] in [1, 3, 5, 7, 8, 10, 12] and startDate['day'] == 32) or (
            startDate['month'] in [4, 6, 9, 11] and startDate['day'] == 31) or (
            isLeapYear(startDate['year']) and startDate['month'] == 2 and startDate['day'] == 30) or (
            (not isLeapYear(startDate['year'])) and startDate['month'] == 2 and startDate['day'] == 29
        ):
            startDate['day'] = 1
            startDate['month'] += 1
        if startDate['month'] == 13:
                startDate['month'] = 1
                startDate['year'] += 1
    return total-1

def generateImage(data, colour, current, total, settings):
    print(f'({current}/{total}) generating event for {data["name"]}...')
    text_colour = ImageColor.getcolor(colours[colour]['text'], "RGBA")
    if data['endDate'] == data['startDate']:
        event_colour = ImageColor.getcolor(colours[colour]['event'], "RGBA")
        title = data['name']
        date = f'{months[data["startDate"]["month"]-1]} {data["startDate"]["day"]} {data["startDate"]["year"]}'
        img = Image.new('RGBA', (int(max(titleFont.getlength(title),dateFont.getlength(date)))+70, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        if data['shape'] == 'circle':
            draw.ellipse((10, 30, 50, 70), fill=event_colour)
        if data['shape'] == 'pentagon':
            draw.regular_polygon(bounding_circle=(30,50,25), n_sides=5, fill=event_colour)
        if data['shape'] == 'diamond':
            draw.regular_polygon(bounding_circle=(30,50,25), n_sides=4, rotation=45, fill=event_colour)
        if data['shape'] == 'triangle':
            draw.regular_polygon(bounding_circle=(30,50,25), n_sides=3, fill=event_colour)
        if settings['show_numbers']:
            textW = dateFont.getlength(str(current))
            textH = 35
            draw.text((10+((40-textW)/2),30+((40-textH)/2)), str(current), fill=text_colour, font=dateFont)
        draw.text((60,5), title, fill=text_colour, font=titleFont, align="left")
        draw.text((60,50), date, fill=text_colour, font=dateFont, align="left")
    else:
        main_colour = ImageColor.getcolor(colours[colour]['main'], "RGBA")
        title = data['name']
        rectangleWidth = int(calcDaysBetween(data['startDate'], data['endDate']) * settings['pixels_per_day'])
        dateRange = f'{months[data["startDate"]["month"]-1]} {data["startDate"]["day"]} {data["startDate"]["year"]} - {months[data["endDate"]["month"]-1]} {data["endDate"]["day"]} {data["endDate"]["year"]}'
        img = Image.new('RGBA', (int(max(titleFont.getlength(title),dateFont.getlength(dateRange)))+rectangleWidth+30, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((10, 10, rectangleWidth+10, 80), fill=main_colour, radius=8)
        if settings['show_numbers']:
            textW = dateFont.getlength(str(current))
            textH = 35
            draw.text((10+((rectangleWidth-textW)/2),10+((70-textH)/2)), str(current), fill=text_colour, font=dateFont)
        draw.text((rectangleWidth+20,5), title, fill=text_colour, font=titleFont, align="left")
        draw.text((rectangleWidth+20,50), dateRange, fill=text_colour, font=dateFont, align="left")

    return img

def calculatePositions(imgs, startDates, layerStartY, universalStartDate, isNotRange, settings):
    print('calculating image positions for this section...')
    positions = []
    widths = [img.size[0] for img in imgs]
    for n, _ in enumerate(imgs):
        x = int(calcDaysBetween(universalStartDate, startDates[n]) * settings['pixels_per_day']) + 390
        x = (x-20 if isNotRange[n] else x)
        y = layerStartY - 100 + 20
        okay = False
        while not okay:
            y += 100
            collision = False
            for m, position in enumerate(positions):
                if (position[1] == y):
                    if (position[0] < x and x < position[0] + widths[m]) or (position[0] < x + widths[n] and x + widths[n] < position[0] + widths[m]):
                        collision = True
            if collision == False:
                okay = True
        positions.append((x, y))
    uniqueYs = []
    for position in positions:
        if position[1] not in uniqueYs:
            uniqueYs.append(position[1])
    layersUsed = len(uniqueYs)
    return positions, layersUsed

def createTimeline(data, settings):
    imgs = []
    positions = []
    allStartDates = []
    layersInEachSection = []
    for section in data:
        allStartDates += [event['startDate'] for event in section['events']]
    universalStartYear = sorted(allStartDates, key=lambda x:x['year'])[0]['year']
    universalStartDate = {"day": 1, "month": 1, "year": universalStartYear}
    for n, section in enumerate(data):
        imgsInThisSection = []
        for m, event in enumerate(section['events']):
            img = generateImage(event, section['colour'], m+1, len(section['events']), settings)
            imgs.append(img)
            imgsInThisSection.append(img)
        startDates = [event['startDate'] for event in section['events']]
        returns = calculatePositions(imgsInThisSection, startDates, (128 if n == 0 else max([x[1] for x in positions])+100+20), universalStartDate, [(True if event['endDate'] == event['startDate'] else False) for event in section['events']], settings)
        positions += returns[0]
        layersInEachSection.append(returns[1])
    widths = [img.size[0] for img in imgs]
    width = max([x[0] + widths[n] for n, x in enumerate(positions)]) + 50
    height = max([x[1] for x in positions]) + 100 + 20
    print('creating the main image...')
    mainImg = Image.new('RGBA', (width,height), ImageColor.getcolor('#696969', 'RGBA'))
    draw = ImageDraw.Draw(mainImg)
    for n, section in enumerate(data):
        print(f'({n+1}/{len(data)}) creating section {section["name"]}...')
        sectionYpos = sum(layersInEachSection[:n])*100+(n*2*20)+128
        sectionHeight = layersInEachSection[n]*100+(20*2)
        draw.rectangle((0, sectionYpos, 400, sectionYpos+sectionHeight), fill=ImageColor.getcolor(colours[section['colour']]['main'], 'RGBA'))
        draw.rectangle((400, sectionYpos, width, sectionYpos+sectionHeight), fill=ImageColor.getcolor(colours[section['colour']]['background'], 'RGBA'))
        words = section['name'].split(' ')
        prevSplit = -1
        textToDraw = []
        for m, word in enumerate(words):
            nextLength = sectionFont.getlength(' '.join(words[prevSplit+1:m+2]))
            if nextLength > 380 or word == words[-1]:
                textToDraw.append(' '.join(words[prevSplit+1:m+1]))
                prevSplit = m
        textHeight = len(textToDraw)*40
        for m, text in enumerate(textToDraw):
            y = ((sectionHeight-textHeight)/2)+(40*m)+sectionYpos
            draw.text((10, y), text, fill=colours[section['colour']]['text'], font=sectionFont, align='left')
    draw.rectangle((0, 0, width, 128), fill=(255,255,255,255))
    dayLayer = 86
    monthLayer = (86 if settings['show_day_ticks'] == False else 47)
    yearLayer = (86 if (settings['show_month_ticks'] == False and settings['show_day_ticks'] == False) else 47 if (settings['show_month_ticks'] == False or settings['show_day_ticks'] == False) else 8)
    if settings['show_day_ticks'] == True:
        print('adding day ticks...')
        x = 400
        day = 1
        month = 1
        year = universalStartYear
        while x < width:
            draw.line((int(x), dayLayer, int(x), height), fill=(215,215,215,255), width=1)
            draw.text((int(x)+10, dayLayer), str(day), fill=(215,215,215,255), font=dateFont)
            x += settings['pixels_per_day']
            day += 1
            if (
                month in [1, 3, 5, 7, 8, 10, 12] and day == 32) or (
                month in [4, 6, 9, 11] and day == 31) or (
                isLeapYear(year) and month == 2 and day == 30) or (
                (not isLeapYear(year)) and month == 2 and day == 29
            ):
                day = 1
                month += 1
            if month == 13:
                month = 1
                year += 1
    if settings['show_month_ticks'] == True:
        print('adding month ticks...')
        x = 400
        month = 1
        year = universalStartYear
        while x < width:
            draw.line((int(x), monthLayer, int(x), height), fill=(200,200,200,255), width=1)
            draw.text((int(x)+10, monthLayer), months[month-1][:3], fill=(200,200,200,255), font=dateFont)
            x += (31 if month in [1, 3, 5, 7, 8, 10, 12] else 30 if month in [4, 6, 9, 11] else 29 if (month == 2 and isLeapYear(year)) else 28)*settings['pixels_per_day']
            month += 1
            if month == 13:
                month = 1
                year += 1
    if settings['show_year_ticks'] == True:
        print('adding year ticks...')
        x = 400
        year = universalStartYear
        while x < width:
            draw.line((int(x), yearLayer, int(x), height), fill=(185,185,185,255), width=1)
            draw.text((int(x)+10, yearLayer), str(year), fill=(185,185,185,255), font=dateFont)
            x += (366 if isLeapYear(year) else 365)*settings['pixels_per_day']
            year += 1
    print('adding event images...')
    for n, img in enumerate(imgs):
        mainImg.paste(img, positions[n], mask=img)
    print('saving image...')
    mainImg.save(f'out/{settings["output_name"]}.png', 'PNG')
    print('done!')
    return f'Successfully created Timeline Image at out/{settings["output_name"]}.png!', mainImg

if __name__ == '__main__':
    start = time.time()
    FILE_NAMES = ['traitors']

    for FILE_NAME in FILE_NAMES:
        with open(f'data/timelines/{FILE_NAME}.json') as f:
            data = json.load(f)
        timelineData = data['timeline']
        settings = data['settings']
        createTimeline(timelineData, settings)

    print(f'created {len(FILE_NAMES)} timelines in {round(time.time()-start, 2)} seconds')