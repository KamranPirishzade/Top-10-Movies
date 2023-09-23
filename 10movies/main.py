import sqlalchemy.orm.query
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///top10movies.db"

headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2NzUwYzQ5ZDI2OTRiYWNhZDZjZDM3NGNiMzZmMGE1YyIsInN1YiI6IjY0ZGUwYzYzZDEwMGI2MTRiNWY3NzViNiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IfaeHX3krzml3HztyejoUGQ5dlDXD-fe4ymuj1oEnAc",

        }



db=SQLAlchemy(app)

class Form(FlaskForm):
    rating=StringField("Your Rating Out of 10",validators=[DataRequired()])
    review=StringField("Your review", validators=[DataRequired()])
    submit=SubmitField("Done")

class FormTitle(FlaskForm):
    title=StringField("Movie Title",validators=[DataRequired()])
    submit=SubmitField("Add Movie")



class Movie(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f"Movie {self.title}"


@app.route("/")
def home():
    with app.app_context():
    #     db.create_all()
    #     new_movie = Movie(
    #         title="Phone Booth",
    #         year=2002,
    #         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    #         rating=7.3,
    #         ranking=10,
    #         review="My favourite character was the caller.",
    #         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    #     )
    #     db.session.add(new_movie)
    #     db.session.commit()

        movie = Movie.query.order_by(Movie.rating).all()

        for i in range(len(movie)):
            movie[i].ranking=len(movie)-i



    return render_template("index.html",movie=movie)

@app.route("/edit",methods=('GET', 'POST'))
def edit():
    form=Form()
    id=request.args.get('id')
    with app.app_context():
        movie=Movie.query.get(id)
    if form.validate_on_submit():
        with app.app_context():
            movie = Movie.query.get(id)
            movie.rating=float(request.form.get("rating"))
            movie.review=request.form.get("review")
            db.session.commit()
        return redirect(url_for("home"))

    return render_template("edit.html",movie=movie,form=form)

@app.route("/delete",methods=('GET', 'POST'))
def delete():
    id=int(request.args.get("id"))
    with app.app_context():
        movie=Movie.query.get(id)
        db.session.delete(movie)
        db.session.commit()
    return redirect(url_for('home'))


@app.route("/add",methods=('GET', 'POST'))
def add():
    form=FormTitle()
    if form.validate_on_submit():
        title=request.form.get("title")
        url = f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=false&language=en-US&page=1"



        response = requests.get(url, headers=headers)

        data=response.json()
        print(data)
        return render_template("select.html",movies=data)
    return render_template("add.html",form=form)

@app.route("/find")
def find():
    id=request.args.get('id')
    if id:
        url = f"https://api.themoviedb.org/3/movie/{id}?language=en-US"
        response=requests.get(url=url,headers=headers)
        movie_data=response.json()
        with app.app_context():
            new_movie=Movie(title=movie_data["title"] , img_url=f"https://www.themoviedb.org/t/p/original{movie_data['poster_path']}" , year=int(movie_data["release_date"].split("-")[0]) , description=movie_data['overview'])
            db.session.add(new_movie)
            db.session.commit()
            return redirect("/")
if __name__ == '__main__':
    app.run(debug=True)
