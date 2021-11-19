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
    f = [int(i) for i in open("static/results.txt", mode='rt', encoding='utf8').read().split()]
    f2 = [int(i) for i in open("static/nation.txt", mode='rt', encoding='utf8').read().split()]
    nation = ['русские', 'башкиры', 'белорусы', 'татары', 'чеченцы', 'чуваши', 'украинцы', 'армяне', 'другое']
    return [round(f[i] / f[0] * 100, 2) if f[0] > 0 else 0.0 for i in range(1, 5)],\
           [[nation[i], round(f2[i] / f[0] * 100, 2) if f[0] > 0 else 0.0] for i in range(9)]


@app.route('/', methods=['GET', 'POST'])
def main_window():
    nation = ['русские', 'башкиры', 'белорусы', 'татары', 'чеченцы', 'чуваши', 'украинцы', 'армяне', 'другое']
    if request.method == 'GET':
        statistics()
        ans, anal = analytics()
        return render_template('index.html', nation=nation, ans=ans, anal=anal)
    db_sess = db_session.create_session()
    ans = list(request.form)
    fr = open("static/results.txt", mode='rt', encoding='utf8').read().split()
    fr[0] = str(int(fr[0]) + 1)
    fw = open("static/results.txt", mode='wt', encoding='utf8')
    f1, f2, f3 = False, False, False
    if 'f1' in ans:
        f1 = True
        fr[1] = str(int(fr[1]) + 1)
    if 'f2' in ans:
        fr[2] = str(int(fr[2]) + 1)
        f2 = True
    if 'f3' in ans:
        fr[3] = str(int(fr[3]) + 1)
        f3 = True
    if request.form['disability'] == '1':
        fr[4] = str(int(fr[4]) + 1)
    f1r = open("static/nation.txt", mode='rt', encoding='utf8').read().split()
    f1w = open("static/nation.txt", mode='wt', encoding='utf8')
    ind = nation.index(request.form['nationality'])
    f1r[ind] = str(int(f1r[ind]) + 1)
    f1w.write(' '.join(f1r))
    f1w.close()
    fw.write(' '.join(fr))
    fw.close()
    new_survey = Survey(
        gender=request.form['gender'],
        birthplace=request.form['birthplace'],
        nationality=request.form['nationality'],
        disability=bool(int(request.form['disability'])),
        f1=f1,
        f2=f2,
        f3=f3
    )
    db_sess.add(new_survey)
    db_sess.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(port=80)