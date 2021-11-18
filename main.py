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
    places = db_sess.query(Survey).all()
    coords = list(set([returne_coords(i.birthplace) for i in places]))
    map_request = "http://static-maps.yandex.ru/1.x/?ll=87.182329,64.202375&z=2&size=450,450&l=map&pt="
    map_request += '~'.join(coords)
    response = requests.get(map_request)
    if response:
        with open('static/img/map.png', "wb") as file:
            file.write(response.content)


@app.route('/', methods=['GET', 'POST'])
def main_window():
    if request.method == 'GET':
        #statistics()
        nation = ['русский', 'казах', 'монгол']
        return render_template('index.html', nation=nation)
    db_sess = db_session.create_session()
    new_survey = Survey(
        age=int(request.form['age']),
        gender=request.form['gender'],
        birthplace=request.form['birthplace'],
        nationality=request.form['nationality'],
        disability=bool(int(request.form['disability']))
    )
    db_sess.add(new_survey)
    db_sess.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run()