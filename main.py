from flask import Flask, render_template, redirect, request
from data import db_session
from data.surveys import Survey
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/survey_data.db")


def returne_coords(find):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={find}&format=json"
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        return ','.join(toponym["Point"]["pos"].split(' ')) + f',pm2rdm'


def statistics():
    db_sess = db_session.create_session()
    places = db_sess.query(Survey.birthplace).all()
    coords = list(set([returne_coords(i[0]) for i in places]))
    map_request = "http://static-maps.yandex.ru/1.x/?ll=87.182329,64.202375&z=2&size=450,450&l=map&pt="
    map_request += '~'.join(coords)
    response = requests.get(map_request)
    if response:
        with open('static/img/map.png', "wb") as file:
            file.write(response.content)


def analytics():
    peopler = open("static/people.txt", mode='rt', encoding='utf8').read().split()
    resultr = open("static/results.txt", mode='rt', encoding='utf8').read().split()
    natr = open("static/nation.txt", mode='rt', encoding='utf8').read().split()
    nation = ['русские', 'башкиры', 'белорусы', 'татары', 'чеченцы', 'чуваши', 'украинцы', 'армяне', 'другое']
    ans = []
    for i in range(9):
        if int(peopler[i]) > 0:
            ans.append(round(int(resultr[i]) / int(peopler[i]), 2) * 100)
        else:
            ans.append(0.0)
    if int(peopler[-1]) == 0:
        anal = [[0.0, nation[i]] for i in range(9)]
    else:
        anal = []
        for i in range(9):
            anal.append([round(int(natr[i]) / int(peopler[-1]), 2) * 100, nation[i]])
    return ans, anal


@app.route('/', methods=['GET'])
def main_window():
    nation = ['русские', 'башкиры', 'белорусы', 'татары', 'чеченцы', 'чуваши', 'украинцы', 'армяне', 'другое']
    statistics()
    ans, anal = analytics()
    return render_template('index.html', nation=nation, ans=ans, anal=anal)


@app.route('/survey', methods=['GET', 'POST'])
def survey():
    nation = ['русские', 'башкиры', 'белорусы', 'татары', 'чеченцы', 'чуваши', 'украинцы', 'армяне', 'другое']
    if request.method == 'GET':
        return render_template('survey.html', nation=nation, zam='none')
    if request.form['birthplace'] == '':
        return render_template('survey.html', nation=nation, zam='birthplace')
    if 'gender' not in request.form:
        return render_template('survey.html', nation=nation, zam='gender')
    if 'disability' not in request.form:
        return render_template('survey.html', nation=nation, zam='disability')
    val = request.form['gender'][-1]
    peopler = [int(i) for i in open("static/people.txt", mode='rt', encoding='utf8').read().split()]
    peoplew = open("static/people.txt", mode='wt', encoding='utf8')
    resultr = [int(i) for i in open("static/results.txt", mode='rt', encoding='utf8').read().split()]
    resultw = open("static/results.txt", mode='wt', encoding='utf8')
    ans = list(request.form)
    if val == '1' and request.form['disability'] == '1':
        peopler[0] += 1
        if 'f1' in ans:
            resultr[0] += 1
    if val == '2' and request.form['disability'] == '1':
        peopler[1] += 1
        if 'f2' in ans:
            resultr[1] += 1
    if val == '1' and request.form['disability'] != '1':
        peopler[2] += 1
        if 'f3' in ans:
            resultr[2] += 1
    if val == '2' and request.form['disability'] != '1':
        peopler[3] += 1
        if 'f3' in ans:
            resultr[3] += 1
    if val == '1':
        peopler[4] += 1
        if 'f2' in ans:
            resultr[4] += 1
    if val == '2':
        peopler[5] += 1
        if 'f2' in ans:
            resultr[5] += 1
    if request.form['gender'][:-1] == '"Женщина':
        peopler[6] += 1
        if 'f4' in ans:
            resultr[6] += 1
    if request.form['gender'][:-1] == '"Мужчина':
        peopler[7] += 1
        if 'f4' in ans:
            resultr[7] += 1
    peopler[8] += 1
    if 'f5' in ans:
        resultr[8] += 1
    peoplew.write(' '.join([str(i) for i in peopler]))
    peoplew.close()
    resultw.write(' '.join([str(i) for i in resultr]))
    resultw.close()
    vopr = [False for _ in range(5)]
    for i in range(5):
        if f'f{i + 1}' in ans:
            vopr[i] = True
    ind = nation.index(request.form['nationality'])
    natr = open("static/nation.txt", mode='rt', encoding='utf8').read().split()
    narw = open("static/nation.txt", mode='wt', encoding='utf8')
    natr[ind] = str(int(natr[ind]) + 1)
    narw.write(' '.join(natr))
    narw.close()
    new_survey = Survey(
        gender=request.form['gender'][:-1],
        birthplace=request.form['birthplace'],
        nationality=request.form['nationality'],
        disability=bool(int(request.form['disability'])),
        f1=vopr[0],
        f2=vopr[1],
        f3=vopr[2],
        f4=vopr[3],
        f5=vopr[4]
    )
    db_sess = db_session.create_session()
    db_sess.add(new_survey)
    db_sess.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(port=80)