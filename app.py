from flask import Flask, request, render_template, redirect
import pygsheets
import re
import os
import signal
import sys

client = pygsheets.authorize(service_file='config/auth.json')
headless = os.environ['HEADLESS']
app = Flask(__name__,
        static_url_path='/assets',
        static_folder='web/static/assets',
        template_folder='web/templates')


document = client.open_by_key('1QwxkEjg66O5tlfEDphjhjQmchkzXHLdzm9IWP4uh6us')
home = document.worksheet('title','H2')
template = document.worksheet('title','Shows')
music_src = document.worksheet('title','Music')

def shutdown_flask(self):
    from win32api import GenerateConsoleCtrlEvent
    CTRL_C_EVENT = 0
    GenerateConsoleCtrlEvent(CTRL_C_EVENT, 0)


@app.route('/shutdown', methods=['GET','POST'])
def shutdown():
    pid = os.getpid()
    sys.exit(0)
    os.kill(pid, signal.SIGKILL)
    return str(pid)

@app.route('/content/')
@app.route('/content')
@app.route('/r')
def app_data():
    page_data = {}
    events  = []
    shows  = []
    tracks = []
    page_data['site_title'] = home.cell('B2').value
    page_data['header_title'] = home.cell('B6').value
    page_data['header_text'] = home.cell('B7').value
    page_data['header_button_text'] = home.cell('B8').value
    page_data['header_button_link'] = home.cell('B9').value
    page_data['header_footer_text'] = home.cell('B10').value

    page_data['page2_title'] = home.cell('B12').value
    page_data['page2_text'] = home.cell('B13').value
    page_data['page2_button_text'] = home.cell('B14').value
    page_data['page2_button_link'] = home.cell('B15').value

    page_data['upcoming_events_title'] = home.cell('B17').value
    page_data['upcoming_events_text'] = home.cell('B18').value
    
    page_data['music_title'] = home.cell('B20').value
    page_data['music_text'] = home.cell('B21').value

    page_data['bookings_title'] = home.cell('B23').value
    page_data['bookings_subtitle'] = home.cell('B24').value
    page_data['bookings_text'] = home.cell('B25').value

    page_data['previous_events_title'] = home.cell('B27').value
    socials = ['facebook','Instagram','Twitch','Twitter','Youtube','TikTok']

    social_list = []
    for i in range(30,35):
        site = {'name': home.cell('A'+str(i)).value,'info': home.cell('B'+str(i)).value,'link': home.cell('C'+str(i)).value, 'icon': home.cell('D'+str(i)).value}
        if home.cell('C'+str(i)).value != '':
            social_list.append(site)


    for row in music_src:
        if row[1] != 'Name':
            tracks.append(row)

    for row in template:
        if row[1] != 'Name':
            if row[6] == 'Future':
                events.append(row)
            else:
                shows.append(row)

    response = render_template('mr1/dict.html', events=events, shows=shows, music=tracks, social=social_list, page_data=page_data)


    f = open("web/templates/rendered/index.html", "w")
    f.write(response)
    f.close()
    #return redirect("/", code=302)
    if headless == True:
        response = redirect('/shutdown')
    else:
        return response

@app.route('/splash')
def app_splash():
    #shows = events.cell('B2').value
    page_data = {}
    page_data['site_title'] = home.cell('B2').value
    page_data['header_title'] = home.cell('B6').value
    page_data['header_text'] = home.cell('B7').value
    page_data['header_button_text'] = home.cell('B8').value
    page_data['header_button_link'] = home.cell('B9').value


    response = render_template('splash/index.html', page_data=page_data)

    f = open("web/templates/rendered/index.html", "w")
    f.write(response)
    f.close()

    #return redirect("/", code=302)
    if headless == 'True':
        return redirect('/shutdown')
    else:
        return response

@app.route('/cd')
def app_cd():
    #shows = events.cell('B2').value
    due_date=home.cell('B5').value
    page_data={}
    page_data['site_title'] = home.cell('B2').value
    page_data['header_title'] = home.cell('B6').value
    page_data['header_text'] = home.cell('B7').value
    page_data['header_button_text'] = home.cell('B8').value
    page_data['header_button_link'] = home.cell('B9').value

    response = render_template('cd/index.html', page_data=page_data, due_date=due_date)

    f = open("web/templates/rendered/index.html", "w")
    f.write(response)
    f.close()

    #return redirect("/", code=302)
    if headless == True:
        response = redirect('/shutdown')
    else:
        return response



@app.route('/')
def app_index():
    homepage = home.cell('B4').value.lower()
    print(os.environ['HEADLESS'])
    match homepage:
        case "splash": 
            return redirect("/splash", code=302)
        case "countdown":
            return redirect("/cd", code=302)
        case "content":
            return redirect("/content", code=302)
        case _: 
            return redirect("/error", code=301)

@app.route('/error')
def app_error():
    response = render_template('error.html' )
    return response



def list(worksheet,cell):
    source = document.worksheet('title',worksheet)
    response = source.cell(cell).value
    response_list = response.split(",")
    return response_list

@app.route('/ui/nav')
def app_nav():
    pages = list('H2','B3')
    response = render_template('ui/navigation.html', pages=pages)
    return response


@app.route('/page/<name>')
def app_page(name=None):
    
    source = document.worksheet('title',name)
    page_title = source.cell('B2').value
    page_type = source.cell('B3').value
    page_header_image = source.cell('B4').value
    page_header_text = source.cell('B5').value
    page_bg_image = source.cell('B6').value
    page_bg_color = source.cell('B7').value
    include_menu =  source.cell('B8').value

    print(include_menu)
    response = render_template(page_type+'.html')
    if include_menu == 'TRUE': 
        response = response + app_nav()

    return response


if __name__ == "__main__":
    app.run(debug=True)

