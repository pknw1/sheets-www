from flask import Flask, request, render_template, redirect, current_app
import pygsheets
import re
import os
import signal
import sys
import webbrowser
from datetime import datetime
import glob
import requests
from pushbullet import API

api = API()

access_token = os.environ['pushbullet_access_token']
api.set_token(access_token)

client = pygsheets.authorize(service_file='config/auth.json')

try:
    headless = os.environ['HEADLESS']
except:
    headless = True



app = Flask(__name__,
        static_url_path='/assets',
        static_folder='web/static/assets',
        template_folder='web/templates')


document = client.open_by_key('1XPlTkHDci5QfDd6K_2Cu61GujArrr7FNJgY4Zb6avEU')
home = document.worksheet('title','Config')
#template = document.worksheet('title','Shows')
#music_src = document.worksheet('title','Music')

def ntfy(topic=None,message=None):
    if message==None:
        message="No Message"
    if topic==None:
        topic="DeannaJadeWWWalerts"
    match topic:
        case "alert":
            topic="DeannaJadeWWWalerts"
        case "system":
            topic="DeannaJadeWWWsystem"
        case _:
            topic="DeannaJadeWWWalerts"
    
    url = 'https://ntfy.sh/'+topic
    x = requests.post(url, data=message.encode(encoding='utf-8') )
    return topic+" - logged "+message

@app.route('/ntfy/<message>')
def send_ntfy(message=None):
    response = ntfy(message)
    return response


@app.route('/cc')
def rm_files():
    ntfy("system","Cache Cleaner Started")
    files=glob.glob("web/templates/rendered/*")
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')

@app.route('/home')
@app.route('/config')
def config():
    data = home.range("A9:F19")
    site_title = home.cell('B2').value
    page_data=[]
    for i in data:
        if i[1].value == 'Enabled':
            match i[0].value:
                case "upcoming_gigs":
                    events_source = document.worksheet('title','Data[Events]')
                    raw_data = []
                    for row in events_source:
                        try:
                            if row[0] != 'ID':
                                checktime = str(row[3]) 
                                past = datetime.strptime(checktime, "%d/%m/%Y")
                                present = datetime.now()
                                if past.date() < present.date():
                                    print("old")
                                else:
                                    raw_data.append(row)
                        except:
                            print("no")
                    page = {'name': i[0].value, 'title': i[2].value, 'subtitle': i[3].value, 'text': i[4].value, "data": raw_data }

                case "previous_gigs":
                    events_source = document.worksheet('title','Data[Events]')
                    raw_data = []
                    for row in events_source:
                        try:
                            if row[0] != 'ID':
                                checktime = str(row[3])
                                print(checktime)
                                past = datetime.strptime(checktime, "%d/%m/%Y")
                                present = datetime.now()
                                if past.date() > present.date():
                                    print("new")
                                else:
                                    raw_data.append(row)
                        except:
                            print("no")
                    page = {'name': i[0].value, 'title': i[2].value, 'subtitle': i[3].value, 'text': i[4].value, "data": raw_data }

                case "set_list":
                    media_source = document.worksheet('title','Data[Media]')
                    raw_data = []
                    for row in media_source:
                        try:
                            if row[0] != 'ID':
                                if row[1] != "Social":
                                    if row[1] != 'Image':
                                        raw_data.append(row)
                        except:
                            print("no")
                    page = {'name': i[0].value, 'title': i[2].value, 'subtitle': i[3].value, 'text': i[4].value, "data": raw_data }


                case "testimonials":
                    data_source = document.worksheet('title','Data[Forms]')
                    raw_data = []
                    for row in data_source:
                        try:
                            if row[0] != 'timestamp':
                                if row[1] == 'testimonial':
                                    if row[9] == 'Approved':
                                        raw_data.append(row)
                        except:
                            print("no")
                    page = {'name': i[0].value, 'title': i[2].value, 'subtitle': i[3].value, 'text': i[4].value, "data": raw_data }


                case "socials":
                    data_source = home.range('D23:F27')
                    raw_data = []
                    for row in data_source:
                        try:
                            if row[0] != '':
                                raw_data.append(row)
                        except:
                            print("no")
                    page = {'name': i[0].value, 'title': i[2].value, 'subtitle': i[3].value, 'text': i[4].value, "data": raw_data }

                case "nav":
                    raw_data = []

                    menu_data = home.range("A23:C32")
                    menu = {}
                    for opt in menu_data:
                        print("m")
                        print(opt[2])
                        try:
                            if opt[2].value == 'Enabled':
                                menu = {'name': opt[0].value, 'link': opt[1].value}
                                raw_data.append(menu)
                        except:
                            print("no")
                    page = {'name': i[0].value, 'title': i[2].value, 'subtitle': i[3].value, 'text': i[4].value, 'image': i[5].value, "data": raw_data }

                case _:
                    page = {'name': i[0].value, 'title': i[2].value, 'subtitle': i[3].value, 'text': i[4].value, 'image': i[5].value }
            page_data.append(page)

    response = render_template('components/base.html', title=site_title)
    for p in page_data:
        print("page")
        data = []
        match p['name']:
            case "upcoming_gigs":
                data = p['data']
            case "previous_gigs":
                data = p['data']
            case "set_list":
                data = p['data']
            case "testimonials":
                data = p['data']
            case "socials":
                data = p['data']
            case "nav":
                data = p['data']
            case _:
                data = []
                
        response = response + render_template('components/'+p['name']+'.html', page_data=p, data=data)


    file_path="web/templates/rendered/home.html"
    with open(file_path, 'w') as file:
        file.write(response)
    ntfy("system","home template rendered")


    if headless == "42":
        ntfy("system","Headless Render Content Started")

        f = open("web/templates/rendered/index.html", "w")
        f.write(response)
        f.close()
        response = redirect('/shutdown')
    else:
        response = redirect('/')

    return response

@app.route('/shutdown', methods=['GET','POST'])
def shutdown():
    ntfy("system","Shutdown Initiated")

    pid = os.getpid()
    print(pid)
    #sys.exit(0)
    os.kill(pid, signal.SIGKILL)
    return str(pid)

@app.route('/splash')
def app_splash():
    #shows = events.cell('B2').value
    page_data = {}
    page_data['site_title'] = home.cell('B2').value
    page_data['header_title'] = home.cell('B6').value
    page_data['header_text'] = home.cell('B7').value
    page_data['header_button_text'] = home.cell('B8').value
    page_data['header_button_link'] = home.cell('B9').value

    social_list = []
    for i in range(30,36):
        site = {'name': home.cell('A'+str(i)).value,'info': home.cell('B'+str(i)).value,'icon': home.cell('C'+str(i)).value, 'link': home.cell('D'+str(i)).value}
        if home.cell('D'+str(i)).value != '':
            social_list.append(site)

    response = render_template('splash/index.html', page_data=page_data, social=social_list)

    f = open("web/templates/rendered/index.html", "w")
    f.write(response)
    f.close()

    #return redirect("/", code=302)
    if headless == "42":
        return redirect('/shutdown')
    else:
        return response

@app.route('/cd')
def app_cd():
    due_date=str(home.cell('D7').value)
    page_data={}
    page_data['site_title'] = home.cell('C2').value
    page_data['header_title'] = home.cell('D5').value
    page_data['header_text'] = home.cell('D6').value

    media_source = document.worksheet('title','Data[Media]')

    social_list = []
                    
    data_source = home.range('D23:F27')
    raw_data = []
    for row in data_source:
        try:
            if row[0] != '':
                social_list.append(row)
        except:
            print("error")

    response = render_template('components/base.html')
    if  home.cell('B9').value == 'Enabled':
        response = response + render_template('components/nav.html', page_data=page_data)
    response = response + render_template('components/countdown.html', socials=social_list, due_date=due_date, page_data=page_data)
    if home.cell('B17').value == 'Enabled':
        response = response + render_template('components/contact_form.html', page_data=page_data)
    if home.cell('B18').value == 'Enabled':
        response = response + render_template('components/socials.html', data=social_list)

    file_path="web/templates/rendered/countdown.html"
    with open(file_path, 'w') as file:
        file.write(response)

    #f = open("web/templates/rendered/countdown.html", "w")    
    #f.write(response)
    #f.close()
    if headless == "42":
        f = open("web/templates/rendered/index.html", "w")
        f.write(response)
        f.close()
        response = redirect('/shutdown')
    else:
        response = redirect('/')

    return response


@app.route('/')
def app_root():
    homepage = home.cell('B4').value.lower()
    match homepage:
        case "countdown":
            if headless == "42":
                response = redirect('/cd')
            else:
                try:
                    response = render_template('rendered/countdown.html')
                except:
                    response = redirect('/cd')
        case "content":
            if headless == "42":
                response = redirect('/home')
            else:
                try:
                    response = render_template('rendered/home.html')
                except:
                    response = redirect('/home')
        case _:
            response = render_template('error.html' )

    return response




if __name__ == "__main__":
    app.run(debug=True)
