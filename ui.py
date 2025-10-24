import gradio as gr
from gradio_calendar import Calendar
import os
import main
import json

max_events = 0

def myDateToStrDate(date):
    return f'{date["year"]}-{str(date["month"]).zfill(2)}-{str(date["day"]).zfill(2)}'

def strDateToMyDate(date):
    return {"day": int(date[8:]), "month": int(date[5:7]), "year": int(date[:4])}

def create(FILE_NAME):
    with open(f'data/timelines/{FILE_NAME}') as f:
        data = json.load(f)
    timelineData = data['timeline']
    settings = data['settings']
    return main.createTimeline(timelineData, settings)

def writeToFile(FILE_NAME, *newStuff):
    with open(f'data/timelines/{FILE_NAME}') as f:
        data = json.load(f)
    numOfSections = len(data['timeline'])
    numOfEvents = [len(section['events']) for section in data['timeline']]
    
    newStuff = list(newStuff)
    newSettings = newStuff[:5]
    newSectionNames = newStuff[5:5+numOfSections]
    newSectionColours = newStuff[5+numOfSections:5+2*numOfSections]
    newEventNames = [newStuff[5+2*numOfSections+sum(numOfEvents[:n]):5+2*numOfSections+sum(numOfEvents[:n+1])] for n in range(numOfSections)]
    newStartDates = [newStuff[5+2*numOfSections+sum(numOfEvents)+sum(numOfEvents[:n]):5+2*numOfSections+sum(numOfEvents)+sum(numOfEvents[:n+1])] for n in range(numOfSections)]
    newEndDates = [newStuff[5+2*numOfSections+2*sum(numOfEvents)+sum(numOfEvents[:n]):5+2*numOfSections+2*sum(numOfEvents)+sum(numOfEvents[:n+1])] for n in range(numOfSections)]
    newEventShapes = [newStuff[5+2*numOfSections+3*sum(numOfEvents)+sum(numOfEvents[:n]):5+2*numOfSections+3*sum(numOfEvents)+sum(numOfEvents[:n+1])] for n in range(numOfSections)]
    
    data['settings']['pixels_per_day'] = newSettings[0]
    data['settings']['output_name'] = newSettings[1]
    data['settings']['show_year_ticks'] = newSettings[2]
    data['settings']['show_month_ticks'] = newSettings[3]
    data['settings']['show_day_ticks'] = newSettings[4]
    for m, section in enumerate(data['timeline']):
        data['timeline'][m]['name'] = newSectionNames[m]
        data['timeline'][m]['colour'] = newSectionColours[m]
        for l, _ in enumerate(section['events']):
            data['timeline'][m]['events'][l]['name'] = newEventNames[m][l]
            data['timeline'][m]['events'][l]['startDate'] = strDateToMyDate(newStartDates[m][l])
            data['timeline'][m]['events'][l]['endDate'] = strDateToMyDate(newEndDates[m][l])
            data['timeline'][m]['events'][l]['shape'] = newEventShapes[m][l]
    
    for SECTION_INDEX, section in enumerate(data['timeline']):
        data['timeline'][SECTION_INDEX]['events'] = sorted(data['timeline'][SECTION_INDEX]['events'], key=lambda x: (x['startDate']['year'], x['startDate']['month'], x['startDate']['day']))
    
    with open(f'data/timelines/{FILE_NAME}', 'w') as f:
        json.dump(data, f, indent=4)
    return 'Successfully Written Data to File!'

def updateSectionName(newSectionName):
    return gr.update(label=newSectionName)

def createNewEvent(FILE_NAME, SECTION_INDEX, eventName, startDate, endDate, eventShape):
    with open(f'data/timelines/{FILE_NAME}') as f:
        data = json.load(f)
    data['timeline'][SECTION_INDEX]['events'].append(
        {
            "name": eventName,
            "startDate": strDateToMyDate(startDate),
            "endDate": strDateToMyDate(endDate),
            "shape": eventShape
        }
    )
    data['timeline'][SECTION_INDEX]['events'] = sorted(data['timeline'][SECTION_INDEX]['events'], key=lambda x: (x['startDate']['year'], x['startDate']['month'], x['startDate']['day']))
    with open(f'data/timelines/{FILE_NAME}', 'w') as f:
        json.dump(data, f, indent=4)
    return f'Successfully added Event: {eventName}! To view this in gradio, a rerun is required.'

def deleteEvent(FILE_NAME, SECTION_INDEX, EVENT_INDEX):
    with open(f'data/timelines/{FILE_NAME}') as f:
        data = json.load(f)
    data['timeline'][SECTION_INDEX]['events'].pop(EVENT_INDEX)
    with open(f'data/timelines/{FILE_NAME}', 'w') as f:
        json.dump(data, f, indent=4)
    return f'Successfully removed event! To view this in gradio, a rerun is required.'

def updateVisibility(k):
    return [gr.Textbox(visible=True)]*k + [gr.Textbox(visible=False)]*(max_events-k)

def updateStartDate(newStartDate, hasEndDate, oldEndDate):
    if newStartDate > oldEndDate or not hasEndDate:
        return gr.update(value=newStartDate)
    else:
        return gr.update(value=oldEndDate)

def updateHasEndDate(startDate, x):
    return gr.update(visible=x), gr.update(value=startDate)

with gr.Blocks() as app:
    #setup
    dir = sorted(os.listdir('data/timelines'))
    
    generateButtons = []
    filenames = []
    outs = []
    outsImage = []
    saveButtons = []
    ppds = []
    outputNames = []
    yearTicks = []
    monthTicks = []
    dayTicks = []
    sectionNames = []
    sectionColours = []
    sectionIndexes = []
    newEventNames = []
    newStartDates = []
    newHasEndDates = []
    newEndDates = []
    newEventShapes = []
    newEventButtons = []
    eventIndexes = []
    deleteEventButtons = []
    eventNames = []
    startDates = []
    hasEndDates = []
    endDates = []
    eventShapes = []
    with open('data/other/colours.json') as f:
        colourdata = json.load(f)
    colours = list(colourdata.keys())
    shapes = ['circle', 'triangle', 'diamond', 'pentagon']
    
    #structure
    for n, filename in enumerate(dir):
        sectionNamesFile = []
        sectionColoursFile = []
        sectionIndexesFile = []
        newEventNamesFile = []
        newStartDatesFile = []
        newHasEndDatesFile = []
        newEndDatesFile = []
        newEventShapesFile = []
        newEventButtonsFile = []
        eventIndexesFile = []
        deleteEventButtonsFile = []
        eventNamesFile = []
        startDatesFile = []
        hasEndDatesFile = []
        endDatesFile = []
        eventShapesFile = []
        with open(f'data/timelines/{filename}') as f:
            data = json.load(f)
        with gr.Tab(filename.removesuffix('.json')):
            with gr.Row():
                generateButtons.append(gr.Button('Generate this timeline!', variant='primary'))
                outs.append(gr.Textbox(label='Output', value=' '))
            filenames.append(gr.Textbox(value=filename, visible=False))
            with gr.Row():
                outsImage.append(gr.Image(label='Output Preview'))
            saveButtons.append(gr.Button('Write to File'))
            gr.Markdown('# Settings')
            with gr.Row():
                ppds.append(gr.Number(label='Pixels per Day', value=data['settings']['pixels_per_day'], minimum=0.01, step=0.01, interactive=True))
                outputNames.append(gr.Textbox(label='Output Name', value=data['settings']['output_name'], interactive=True))
                with gr.Column():
                    yearTicks.append(gr.Checkbox(label='Show Year Ticks', value=data['settings']['show_year_ticks'], interactive=True))
                    monthTicks.append(gr.Checkbox(label='Show Month Ticks', value=data['settings']['show_month_ticks'], interactive=True))
                    dayTicks.append(gr.Checkbox(label='Show Day Ticks', value=data['settings']['show_day_ticks'], interactive=True))
            gr.Markdown('# Sections')
            for m, section in enumerate(data['timeline']):
                eventIndexesSection = []
                deleteEventButtonsSection = []
                eventNamesSection = []
                startDatesSection = []
                hasEndDatesSection = []
                endDatesSection = []
                eventShapesSection = []
                with gr.Tab(section['name']) as globals()[f'f{n}section{m}']:
                    gr.Markdown('## Settings')
                    with gr.Row():
                        sectionNamesFile.append(gr.Textbox(label='Section Name', value=section['name'], interactive=True))
                        sectionColoursFile.append(gr.Dropdown(label='Colour', choices=colours, value=section['colour'], interactive=True))
                    sectionIndexesFile.append(gr.Number(value=m, visible=False))
                    gr.Markdown('## Events')
                    gr.Markdown('### Create a New Event:')
                    with gr.Row():
                        newEventNamesFile.append(gr.Textbox(label='Name', placeholder='Enter a new event name here...', interactive=True))
                        newStartDatesFile.append(Calendar(label='Start Date', type='string', interactive=True))
                        with gr.Column():
                            newHasEndDatesFile.append(gr.Checkbox(label='End Date', value=False, interactive=True))
                            newEndDatesFile.append(Calendar(show_label=False, type='string', interactive=True, visible=False))
                        newEventShapesFile.append(gr.Dropdown(label='Shape', choices=shapes, value='circle', interactive=True))
                    newEventButtonsFile.append(gr.Button('Create this Event'))
                    for l, event in enumerate(section['events']):
                        eventIndexesSection.append(gr.Number(value=l, visible=False))
                        with gr.Row():
                            gr.Markdown(f'### Event {l+1}')
                            deleteEventButtonsSection.append(gr.Button(f'Delete Event {l+1}', variant='stop', size='sm'))
                        with gr.Row():
                            eventNamesSection.append(gr.Textbox(label='Name', value=event['name'], interactive=True))
                            startDatesSection.append(Calendar(label='Start Date', type='string', value=myDateToStrDate(event['startDate']), interactive=True))
                            with gr.Column():
                                hasEndDatesSection.append(gr.Checkbox(label='End Date', value=(True if event['startDate'] != event['endDate'] else False), interactive=True))
                                endDatesSection.append(Calendar(show_label=False, type='string', value=myDateToStrDate(event['endDate']), interactive=True, visible=hasEndDatesSection[-1].value))
                            eventShapesSection.append(gr.Dropdown(label='Shape', choices=shapes, value=event['shape'], interactive=True))
                    gr.Button('Delete this Section', variant='stop')
                eventIndexesFile.append(eventIndexesSection)
                deleteEventButtonsFile.append(deleteEventButtonsSection)
                eventNamesFile.append(eventNamesSection)
                startDatesFile.append(startDatesSection)
                hasEndDatesFile.append(hasEndDatesSection)
                endDatesFile.append(endDatesSection)
                eventShapesFile.append(eventShapesSection)
            gr.Button('Delete this Timeline', variant='stop')
        sectionNames.append(sectionNamesFile)
        sectionColours.append(sectionColoursFile)
        sectionIndexes.append(sectionIndexesFile)
        newEventNames.append(newEventNamesFile)
        newStartDates.append(newStartDatesFile)
        newHasEndDates.append(newHasEndDatesFile)
        newEndDates.append(newEndDatesFile)
        newEventShapes.append(newEventShapesFile)
        newEventButtons.append(newEventButtonsFile)
        eventIndexes.append(eventIndexesFile)
        deleteEventButtons.append(deleteEventButtonsFile)
        eventNames.append(eventNamesFile)
        startDates.append(startDatesFile)
        hasEndDates.append(hasEndDatesFile)
        endDates.append(endDatesFile)
        eventShapes.append(eventShapesFile)
    
    #functionality
    for n, filename in enumerate(dir):
        with open(f'data/timelines/{filename}') as f:
            data = json.load(f)
        generateButtons[n].click(create, inputs=[filenames[n]], outputs=[outs[n], outsImage[n]])
        saveButtons[n].click(writeToFile, inputs=[filenames[n]] + [ppds[n]] + [outputNames[n]] + [yearTicks[n]] + [monthTicks[n]] + [dayTicks[n]] + sectionNames[n] + sectionColours[n] + sum(eventNames[n], []) + sum(startDates[n], []) + sum(endDates[n], []) + sum(eventShapes[n], []), outputs=[outs[n]])
        for m, section in enumerate(data['timeline']):
            sectionNames[n][m].change(updateSectionName, inputs=[sectionNames[n][m]], outputs=[globals()[f'f{n}section{m}']])
            newStartDates[n][m].change(updateStartDate, inputs=[newStartDates[n][m], newHasEndDates[n][m], newEndDates[n][m]], outputs=[newEndDates[n][m]])
            newHasEndDates[n][m].change(updateHasEndDate, inputs=[newStartDates[n][m], newHasEndDates[n][m]], outputs=[newEndDates[n][m], newEndDates[n][m]])
            newEventButtons[n][m].click(createNewEvent, inputs=[filenames[n], sectionIndexes[n][m], newEventNames[n][m], newStartDates[n][m], newEndDates[n][m], newEventShapes[n][m]], outputs=[outs[n]])
            for l, event in enumerate(section['events']):
                deleteEventButtons[n][m][l].click(deleteEvent, inputs=[filenames[n], sectionIndexes[n][m], eventIndexes[n][m][l]], outputs=[outs[n]])
                startDates[n][m][l].change(updateStartDate, inputs=[startDates[n][m][l], hasEndDates[n][m][l], endDates[n][m][l]], outputs=[endDates[n][m][l]])
                hasEndDates[n][m][l].change(updateHasEndDate, inputs=[startDates[n][m][l], hasEndDates[n][m][l]], outputs=[endDates[n][m][l], endDates[n][m][l]])

app.launch()