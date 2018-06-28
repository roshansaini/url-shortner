# IMPORTING SECTION

from flask import Flask
from flask import render_template
import sqlite3
from flask import request
import requests
from urllib.parse import urlparse
import base64
from math import floor
from flask import redirect
import sys

app = Flask(__name__)

host='http://127.0.0.1:5000/'

# DECLARANG LISTS
base = []
alphabet=[]

# CREATING BASE LIST

for letter in range(97, 123):
    base.append(chr(letter))
for letter in range(65, 91):
    base.append(chr(letter))
for letter in range(48, 58):
    base.append(chr(letter))

# ENCODING THE INPUT URL TO BASE62 USING BASE 62 ALGORITHM
    # This function takes user URL as a parameter
    # This function is returning a base62 encode url link.

def toencode(num, b=62):
    if b <= 0 or b > 62:
        return 0

    r = num % b
    res = base[r];
    q = floor(num / b)
    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res
    return res

# DECODING THE SHORT URL TO BASE10 USING BASE 10 ALGORITHM
    # This function takes user SHORTED URL as a parameter
    # This function is returning a base10 decode ID WHERE the original URL is Saved in the database.


def decode(string, alphabet=base):
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num

# ENTRY POINT (HOME PAGE FOR THE USER)

@app.route('/')
def hello_world():
    return render_template("practice.html")
@app.route('/ok')
def about_us():
    return render_template('output.html')

# FETCHING THE URL FROM HOME PAGE END CALLING TO toencode() To CONVERT THE URL IN BASE62 FROMAT
    # WE ARE ALSO SAVING THE URL TO THE DATABASE

@app.route('/add_url',methods=['GET','POST'])
def add_data():
    if request.method=='POST':  # CHECKING WHETHER SUMBIT BUTTON IS CLICKED OR NOT

            url=request.form['surl'].encode()
            if url=="":
                return render_template('practice.html')  # IF NOT URL IS ENTERED REDIRECT TO HOME PAGE

            if urlparse(url).scheme=='': # CHECKING WHETHER LINK IS STARTING WITH HTTPS OR NOT
                url='https//'+url
            else:
                url=url
            try:
                page = requests.get(url) # CHECKING WHETHER  URL IS CORRECT OR NOT
                if page.status_code==200:
                    with sqlite3.connect("Url.db") as con:  # OPENING CONNECTION TO DATABASE
                        cur = con.cursor()
                        try:
                            last_id = cur.execute("INSERT INTO URLTABLE(URL,SURL)VALUES(?,?)", (url, 'Hello'));
                        except sqlite3.OperationalError: # HANDLING FOR INSERTION ERROR
                            msg="Insertion Failed"
                            return render_template('practice.html',msg=msg)
                        except sqlite3.IntegrityError:  # HANDLING DUPLICATE URLS
                            cur.execute('SELECT SURL FROM URLTABLE WHERE URL=?',(url,))
                            okk=cur.fetchone()[0]
                            return render_template('practice.html', shrt_url=host + okk)
                        con.commit()
                        short_url = toencode(last_id.lastrowid)
                        murl = last_id.lastrowid

                        cur.execute('UPDATE URLTABLE SET SURL="{0}" WHERE ID={1}'.format(short_url, murl))
                        con.commit()

                        return render_template('practice.html', shrt_url=host + short_url)
                        con.close()
            except requests.exceptions.MissingSchema: # HANDLING HTTP ERROR IF LINK DOESN'T EXISTS
                 msg="Link doesn't Exist."
                 return render_template('practice.html',msg=msg)

# REDIRECT THE USER TO THE URL WHEN HE CLICKS ON THE SHORT LINK

@app.route('/<short_url>')
def redirect_to(short_url):
    decoded = decode(short_url) # DECODING THE URL TO BASE 62 FROMAT
    url = host
    with sqlite3.connect('Url.db') as con:  # CONNECTING TO DATABASE
        cursor = con.cursor()
        res = cursor.execute('SELECT URL FROM URLTABLE WHERE ID=?', [decoded])  # FETCHING THE ORIGINAL URL FROM THE DATABASE
        try:
            short = res.fetchone() # FETCHING THE URL FROM CURSOR
            if short is not None:
                url = short[0]
        except Exception as e:
            print(e)
    return redirect(url) # REDIRECTING TO THE URL PAGE





@app.route('/print_table')
def print_table():
    con=sqlite3.connect("Url.db")

    cur=con.cursor()
    cur.execute("SELECT * FROM URLTABLE")

    row=cur.fetchall()

    return render_template('data.html',rows=row)

if __name__ == '__main__':
    app.run()
