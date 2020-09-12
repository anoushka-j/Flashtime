from flask import Flask, render_template, url_for, request, redirect, session
import sqlite3
app = Flask(__name__)
app.secret_key = "key"
conn = sqlite3.connect('FT.db')
c = conn.cursor()

def executeQuery(conn, query):
  conn = sqlite3.connect('FT.db')
  # try: 
  c = conn.cursor()
  c.execute(query)
  conn.commit()
  result = c.fetchall()
  return result

def updateTable(conn, query): 
  # try: 
  conn = sqlite3.connect('FT.db')
  c = conn.cursor()
  c.execute(query)
  conn.commit()

Q1 = """CREATE TABLE IF NOT EXISTS user_data (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT ,
  user_name TEXT NOT NULL, 
  user_pass TEXT NOT NULL
)"""

Q2 = """CREATE TABLE IF NOT EXISTS user_decks (
  deck_id INTEGER PRIMARY KEY AUTOINCREMENT, 
  user_deck_id INTEGER NOT NULL, 
  deck_name TEXT NOT NULL, 
  deck_desc TEXT,
  user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id)
    REFERENCES user_data (user_id) 
)"""

Q3 = """CREATE TABLE IF NOT EXISTS user_cards (
  card_id INTEGER PRIMARY KEY, 
  card_question TEXT NOT NULL, 
  card_answer TEXT NOT NULL,
  in_deck_id INTEGER NOT NULL, 
  user_id INTEGER NOT NULL, 
  user_deck_id INTEGER NOT NULL, FOREIGN KEY (user_deck_id) REFERENCES user_decks (user_deck_id)
)"""

executeQuery(conn, Q2)
executeQuery(conn, Q3)

@app.route("/", methods=['POST', 'GET'])
def returnSite() : 
  if request.method: 
    return render_template("index.html")

@app.route("/signIn", methods=['POST', 'GET'])
def signIn() : 
  userCanExist = False 
  if request.method : 
    session['username'] = request.form['username']
    username = session['username']
    print("The current username is: " + username)
    password = request.form['password']
    get_user_name_length_query = "SELECT count(user_name) FROM user_data"
    user_name_length = [user_name[0] for user_name in executeQuery(conn,get_user_name_length_query)] 
    if user_name_length[0] > 0 : 
      user_names = [user_name[0] for user_name in executeQuery(conn, "SELECT user_name FROM user_data")] 
      for name in user_names : 
        if username == name: 
          return "Sorry, username is taken!"
        else :
          userCanExist = True 
    if userCanExist : 
      current_user_id = [user_id[0] for user_id in executeQuery(conn, f"SELECT user_id FROM user_data WHERE user_name='{username}'")] 
      new_user = f"""INSERT INTO user_data(user_name, user_pass) VALUES ("{username}", "{password}")"""
      updateTable(conn, new_user)
  return render_template('newhomepage.html', current_user_id=current_user_id, password=password)

@app.route("/login", methods=['POST', 'GET']) 
def login(): 
  return render_template('login.html')

@app.route("/checkLogin", methods=['POST', 'GET']) 
def checkLogin() : 
  userDataEqual = False
  if request.method: 
    session['username']= request.form['username']
    username=session['username']
    password = request.form['password']
    user_names = [user_name[0] for user_name in executeQuery(conn, "SELECT user_name FROM user_data")]  
    passwords = [user_pass[0] for user_pass in executeQuery(conn, "SELECT user_pass FROM user_data")]   
    for name, word in zip(user_names, passwords) : 
      if username == name and password == word : 
        userDataEqual = True 
    if userDataEqual : 
      current_user_id = [user_id[0] for user_id in executeQuery(conn, f"SELECT user_id FROM user_data WHERE user_name='{username}'")]  
      return redirect(url_for('loginpage', current_user_id=current_user_id[0]))
    else : 
      return "No such user"


@app.route("/decks", methods=['POST', 'GET'])
def decks() : 
  current_user_id = request.args.get('current_user_id')
  if request.method : 
    return render_template('createdeck.html', current_user_id=current_user_id)

@app.route("/makedeck", methods=['POST', 'GET']) 
def makeDeck() : 
  current_user_id = request.args.get('current_user_id')
  print("current user id : " + str(current_user_id))
  if request.method : 
    deckName = request.form['deckName']
    deckDesc = request.form['deckDesc']
    print(deckName, deckDesc)
    if deckName != "" and deckDesc != "" : 
      print("Current user id: " +  str(current_user_id))
      this_deck_num = [deck_id[0] for deck_id in executeQuery(conn, f"SELECT count(user_deck_id) FROM user_decks WHERE user_id='{current_user_id}'")]  
      print("this_deck_num" + str(this_deck_num))
      this_deck_num = this_deck_num[0]
      if this_deck_num == 0 : 
        this_deck_num = 1
      else :
        this_deck_num = this_deck_num + 1
      session['this_deck_num'] = this_deck_num
      deck_update = f"""INSERT INTO user_decks (deck_name, deck_desc, user_deck_id, user_id) VALUES("{deckName}", "{deckDesc}", {this_deck_num}, {current_user_id[0]})"""
      updateTable(conn, deck_update)
      return render_template('createcard.html', current_user_id=current_user_id, this_deck_num=session['this_deck_num'], deckName=deckName, deckDesc=deckDesc)
    else : 
      return "Please enter a deck name AND a deck description"

@app.route('/makecards', methods=['POST', 'GET'])
def makecards() : 
  current_user_id = request.args['current_user_id']
  this_deck_num = request.args['this_deck_num']
  deckName = request.args['deckName']
  deckDesc = request.args['deckDesc']
  if request.method: 
    question = request.form['question']
    answer = request.form['answer']
    if question != "" and answer != "" : 
      this_card_num = [card_id[0] for card_id in executeQuery(conn, f"SELECT count(card_id) FROM user_cards WHERE user_deck_id='{this_deck_num}' ")]  
      this_card_num = this_card_num[0] + 1
      card_update = f"""INSERT INTO user_cards (user_id, card_question, card_answer, in_deck_id, user_deck_id) VALUES("{current_user_id}", "{question}", "{answer}", {this_card_num}, {this_deck_num})"""
      updateTable(conn, card_update) 
      return render_template('createcard.html', current_user_id=current_user_id, this_deck_num=session['this_deck_num'], deckName=deckName, deckDesc=deckDesc)
    else :
      return redirect(url_for('loginpage', current_user_id=current_user_id[0]))
      
@app.route("/displaycards", methods=['POST', 'GET'])
def displaycards() : 
  current_user_id = request.args['current_user_id']
  current_deck = request.args['current_deck']
  print("current deck: " + str(current_deck))
  card_questions = executeQuery(conn, f"SELECT card_question FROM user_cards WHERE user_deck_id='{current_deck}' AND user_id={current_user_id}")
  print("card questions: " + str(card_questions))
  card_answers = executeQuery(conn, f"SELECT card_answer FROM user_cards WHERE user_deck_id='{current_deck}' AND user_id={current_user_id}")
  print("card answers: " + str(card_answers))
  card_id_num = [card_id[0] for card_id in executeQuery(conn, f"SELECT count(card_id) FROM user_cards WHERE user_deck_id='{current_deck}' AND user_id={current_user_id}")] 
  card_num = 0
  current_state = 1
  return render_template('displaycards.html', current_state=current_state, current_user_id=current_user_id, card_num=card_num, current_deck=current_deck, card_questions=card_questions, card_answers=card_answers, card_id_num=card_id_num)

@app.route("/nextCard", methods=['POST', 'GET'])
def nextCard() :
  current_user_id = request.args['current_user_id']
  card_num = request.args['card_num']
  button_type = request.args['id']
  print("the button type is: " + button_type)
  current_deck = request.args['current_deck']
  current_state = request.args['current_state']
  print(type(current_state))
  print("the current_state is : " + str(current_state))
  card_questions = executeQuery(conn, f"SELECT card_question FROM user_cards WHERE user_deck_id='{current_deck}' AND user_id={current_user_id}")
  print("card questions: " + str(card_questions))
  card_answers = executeQuery(conn, f"SELECT card_answer FROM user_cards WHERE user_deck_id='{current_deck}' AND user_id={current_user_id}")
  print("card answers: " + str(card_answers))
  card_id_num = [card_id[0] for card_id in executeQuery(conn, f"SELECT count(card_id) FROM user_cards WHERE user_deck_id='{current_deck}' AND user_id={current_user_id}")] 
  card_num = int(card_num)
  if button_type == "next" : 
    card_num = card_num + 1  
    current_state = int(current_state)
  if button_type == "back" : 
    card_num = card_num - 1
    current_state = int(current_state)
  if button_type == "flip" : 
    card_num = int(card_num)
    current_state = int(current_state)
    if current_state == 1 : 
      current_state = 0
    else : 
      current_state = 1
  return render_template('displaycards.html', current_user_id=current_user_id, current_state=current_state, card_num=card_num, card_answers=card_answers, current_deck=current_deck, card_questions=card_questions, card_id_num=card_id_num)

@app.route('/loginpage/<current_user_id>', methods=['POST', 'GET'])
def loginpage(current_user_id) : 
  warning = request.args['warning']
  user_deck_ids = executeQuery(conn, f"SELECT user_deck_id FROM user_decks WHERE user_id='{current_user_id}'")
  # print(user_deck_ids)
  deck_names = executeQuery(conn, f"SELECT deck_name FROM user_decks WHERE user_id='{current_user_id}'")
  # print(deck_names)
  deck_descs = executeQuery(conn, f"SELECT deck_desc FROM user_decks WHERE user_id='{current_user_id}'")
  # print(deck_descs)  
  warning = 'False' 
  return render_template('loginhomepage.html', current_user_id=current_user_id, user_deck_ids=user_deck_ids, deck_names=deck_names, deck_descs=deck_descs, warning=warning)



if __name__ == "__main__": 
  app.run(debug=True)