from flask import Flask, render_template,request
from app import app
import pandas as pd
import pymysql
from pymysql.constants import CLIENT

import math
import operator


@app.route("/")
@app.route("/index")
def index_func():
    return render_template("index.html", title="Home")

@app.route("/somepage", methods=["GET", "POST"])
def some_func():
    form_data = request.form

    if request.method == "POST":
        num1 = form_data["number1"]

        if form_data["button"] == "login":
            con = pymysql.connect(host='127.0.0.1', port=3306, user="root", password='3695',
                              db="ml_chap3", charset='utf8',client_flag=CLIENT.MULTI_STATEMENTS)
            cur = con.cursor()

            """기능1"""
            sql0 = "SELECT occupation FROM user WHERE userid="+str(num1)+";"
            cur.execute(sql0)
            rows = cur.fetchall()[0][0]
            sql2 = "select movieTitle,avg(ratingScore) as ratingScore from user natural join ratings natural join movie where occupation='"+str(rows)+"' group by movieid order by ratingScore desc,movieId desc limit 10;"
            cur.execute(sql2)
            result=cur.fetchall()
            """기능1"""

            """기능2"""
            sql3="SELECT age FROM user WHERE userid="+str(num1)+";"
            cur.execute(sql3)
            age = int(cur.fetchall()[0][0])
            min_age=math.floor(age/10)*10
            max_age=min_age+10
            sql4="select movieTitle,avg(ratingScore) as ratingScore from user natural join ratings natural join movie where "+str(min_age)+" <=age and age < "+str(max_age)+" group by movieid order by ratingScore desc,movieId desc limit 10;"
            cur.execute(sql4)
            result2=cur.fetchall()
            """기능2"""

            """기능3"""
            sql = "select userid,movieId,movieTitle,ratingScore from user natural join ratings natural join movie"
            cur.execute(sql)
            rows = cur.fetchall()
            moviedata = pd.DataFrame(data=rows, columns=['userid', 'movieId', 'movieTitle', 'ratingScore'])
            moviedata2 = pd.pivot_table(moviedata, index='userid', columns='movieId', values='ratingScore',
                                        aggfunc='max')

            def cosim(userid, dataframe):
                movies = []
                for i in dataframe.loc[userid, :].index:
                    if math.isnan(dataframe.loc[userid, i]) == False:
                        movies.append(i)

                U_df = pd.DataFrame(dataframe.loc[userid, movies]).T

                other_df = dataframe.loc[:, movies].drop(userid, axis=0)
                sim_dict = {}
                for user in other_df.index:
                    u_list = []
                    df_list = []
                    ch1 = 0
                    ch2 = 0
                    pa1 = 0
                    pa2 = 0
                    pa3 = 0
                    result = 0
                    sm = [m for m in U_df.columns if math.isnan(other_df.loc[user, m]) == False]

                    for i in U_df.loc[userid, sm].values:
                        u_list.append(i)
                    for i in other_df.loc[user, sm].values:
                        df_list.append(i)
                    for i in range(len(sm)):
                        ch1 += (u_list[i] * df_list[i])
                        pa1 += u_list[i] * u_list[i]
                        pa2 += df_list[i] * df_list[i]
                    ch2 = sum(u_list) * sum(df_list)
                    pa3 = (pa1 - sum(u_list) * sum(u_list) / (len(sm) + 0.000000001)) * (
                                pa2 - sum(df_list) * sum(df_list) / (len(sm) + 0.000000001))
                    result = (ch1 - ch2 / (len(sm) + 0.000000001)) / ((pow(pa3, 1 / 2) + 0.000000001))
                    sim_dict[user] = result
                ''''''
                sim_mat = sorted(sim_dict.items(), key=operator.itemgetter(1), reverse=True)[:40]

                recommend_list = list(set(dataframe.columns) - set(U_df.columns))
                others_k = [i[0] for i in sim_mat]
                recommender = dict()
                for movie in recommend_list:
                    rating = []
                    sim = []
                    for person in others_k:
                        if math.isnan(dataframe.loc[person, movie]) == False:
                            rating.append(dataframe.loc[person, movie])
                            sim.append(sim_dict[person])

                    aa = len(rating)
                    use_sum = 0
                    for i in range(aa):
                        use_sum += sim[i] * rating[i]
                    pred = use_sum / (sum(sim) + 0.0000001)
                    recommender[movie] = pred

                return sorted(recommender.items(), key=operator.itemgetter(1), reverse=True)[:10]
            result_list=cosim(int(num1),moviedata2)
            movielist=[]
            for i in range(10):
                sql7="select movieid, movietitle from movie where movieid="+str(result_list[i][0])+" order by movieId desc limit 1;"
                cur.execute(sql7)
                movie = cur.fetchall()
                removie=movie[0]
                movielist.append((removie[0],removie[1]))
            """기능3"""

            con.close()
            return render_template(
                "somepage.html", title="SomePage",result=[result,result2,movielist]
            )


    return render_template("somepage.html", title="SomePage")