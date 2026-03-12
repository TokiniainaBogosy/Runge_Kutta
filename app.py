from flask import Flask,render_template,request,redirect,url_for,jsonify,session
import sqlite3
from db import get_connexion
import os
from dotenv import load_dotenv


load_dotenv() # Charge le fichier .env
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
DB_NAME = "database.db"

def createUser(username,email,password):
    with get_connexion() as conn:
        conn.execute(
            "INSERT INTO utilisateurs (username,email,password) VALUES (?,?,?)",
            (username,email,password)
        )
        initialiseDonnee(email,conn)

def get_all_user():
    with get_connexion() as conn:
        return conn.execute("SELECT * FROM utilisateurs").fetchall()

def verifyUser(email):
    users = get_all_user()
    for user in users:
        if user["email"] == email :
            return True 
        
def verifyPassword(email,password):
    users = get_all_user()
    for user in users:
        if user["email"] == email :
            if user["password"] == password:
                return True
    return False


def get_db():
    return sqlite3.connect(DB_NAME)

def initialiseDonnee(email,conn):
    coefficient = 0
    depenses_fixe = 0
    tauxRevenu = 0
    for i in range(1,13):
        conn.execute(
            "INSERT INTO revenus (mois,taux_revenu,email_user) VALUES (?,?,?)",
            (i,tauxRevenu,email)
        )
        conn.execute(
            "INSERT INTO depenses (mois,coefficient_depense,depense_fixe,email_user) VALUES (?,?,?,?)",
            (i,coefficient,depenses_fixe,email)
        )

def recalculateCapitalSession():
    """Recalcule et met à jour les valeurs de capital en session"""
    from RungeKutta import runge_kutta, dC_dt
    with get_connexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT capital_initial FROM utilisateurs WHERE email = ?",(session['data'],))
        capitalInitial = cursor.fetchone()[0]
    donnees = runge_kutta(dC_dt, 0, capitalInitial, 1, 12)
    capital = [x[1] for x in donnees]
    session['capital'] = capital
    session['capitalmax'] = max(capital)
    session['capitalmin'] = min(capital)
    session['capitalfinal'] = capital[-1]
    session['capitalinitial'] = capitalInitial
    session['benefice'] = session['capitalfinal'] - session['capitalinitial']

def userInfo():
    email = session.get('data')
    with get_connexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM utilisateurs WHERE email = ?",(email,))
        username = cursor.fetchone()[0]
        session['username'] = username
            
@app.route("/")
def home():
    return render_template("connexion.html")

@app.route("/creeationCompte",methods=["POST","GET"])
def creerCompte():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        if verifyUser(email) :
            return "ERROR this user already exist"
        createUser(username,email,password)
        return redirect(url_for("creerCompte"))
    return render_template("connexion.html")

@app.route("/Connexion",methods=["POST","GET"])
def seConnecter():
    if request.method == "POST":   
        email = request.form["email"]
        session['data'] = email
        password = request.form["password"]
        if verifyPassword(email,password) :
            return redirect(url_for("afficher"))
        else:
            return redirect(url_for("seConnecter"))
    return render_template("connexion.html")

@app.route("/Deconnexion",methods=["POST","GET"])
def seDeconnecter():
    session.clear()
    return redirect(url_for("home"))


@app.route("/affichage",methods=["GET"])
def afficher():
    recalculateCapitalSession()
    userInfo()
    capitalmax = round(session.get('capitalmax'))
    capitalmin = round(session.get('capitalmin'))
    capitalInitial = round(session.get('capitalinitial'))
    capitalfinal = round(session.get('capitalfinal'))
    benefice = round(session.get('benefice')) 
    return render_template("design.html",capitalMax=capitalmax,capitalMin=capitalmin,capitalFinal=capitalfinal,capitalInitial=round(capitalInitial),Benefice=benefice,username=session.get('username'))

@app.route("/navigationDashboard" ,methods=["GET"])
def pageDashboard():
    email = session.get('data')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM revenus WHERE email_user = ?""",(email,))
    donneesRevenu = cursor.fetchall()
    cursor.execute("""SELECT * FROM depenses WHERE email_user= ?""",(email,))
    donneesDepenses = cursor.fetchall()
    db.close()
    data = list(zip(donneesRevenu,donneesDepenses))
    capitalMax = round(session.get('capitalmax'))
    capitalmin = round(session.get('capitalmin'))
    capitalInitial = round(session.get('capitalinitial'))
    capitalFinal = round(session.get('capitalfinal'))
    benefice = round(session.get('benefice'))
    userInfo()
    return render_template("design.html",data = data,capitalMax=capitalMax,capitalMin=capitalmin,capitalFinal=capitalFinal,capitalInitial=capitalInitial,Benefice=benefice,username=session.get('username'))

@app.route("/navigationDonnees" ,methods=["GET"])
def pagesDepenses():
    email = session.get('data')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM revenus WHERE email_user = ?""",(email,))
    donneesRevenu = cursor.fetchall()
    cursor.execute("""SELECT * FROM depenses WHERE email_user= ?""",(email,))
    donneesDepenses = cursor.fetchall()
    db.close()
    data = list(zip(donneesRevenu,donneesDepenses))
    userInfo()
    return render_template("Ajout_donees.html",data=data,username=session.get('username'))

@app.route("/navigation" ,methods=["GET"])
def changerDePage():
    boutton = request.args.get("boutton")
    if boutton == "AJOUTER":
        return render_template("Ajout_donees.html")
    if boutton == "AFFICHER":
        return redirect(url_for("afficher"))
    
@app.route("/ajout" ,methods=["POST","GET"])
def ajouter():
    if request.method == "POST":
        mois = request.form["mois"]
        tauxRevenu = request.form["tauxRevenu"]
        coefficientDepense = request.form["coefficientDepense"]
        depenseFixe = request.form["depenseFixe"]

        db = get_db()
        db.execute(
            "INSERT INTO revenus (mois,taux_revenu) VALUES (?,?)",
            (mois,tauxRevenu)
        )
        db.commit()
        db.execute(
            "INSERT INTO depenses (mois,coefficient_depense,depense_fixe) VALUES (?,?,?)",
            (mois,coefficientDepense,depenseFixe)
        )
        db.commit()
        db.close()
        return redirect(url_for("ajouter"))
    return render_template("Ajout_donees.html")

@app.route("/reinitialisation" ,methods=["POST","GET"])
def reinitialiser():
    email = session.get('data')
    if request.method == "POST":
        tauxRevenu = 0
        coefficientDepense = 0
        depenseFixe = 0
        mois = 1
        db = get_db()
        cursor = db.cursor()
        for mois in range(1,13):
            cursor.execute("UPDATE revenus SET taux_revenu = ? WHERE mois = ? and email_user = ?",(tauxRevenu,mois,email))
            cursor.execute("UPDATE depenses SET coefficient_depense = ? WHERE mois = ? and email_user = ? ",(coefficientDepense,mois,email))
            cursor.execute("UPDATE depenses SET depense_fixe = ? WHERE mois = ? and email_user = ?",(depenseFixe,mois,email))
            db.commit()
        db.close()
        recalculateCapitalSession()
        return redirect(url_for("pagesDepenses"))
    return render_template("Ajout_donees.html")

@app.route("/modificatonDonnee" ,methods=["POST","GET"])
def modifier():
    email = session['data']
    if request.method == "POST":
        mois = request.form["mois"]
        tauxRevenu = request.form["tauxRevenu"]
        coefficientDepense = request.form["coefficientDepense"]
        depenseFixe = request.form["depenseFixe"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE revenus SET taux_revenu = ? WHERE mois = ?  and email_user = ? ",(tauxRevenu,mois,email))
        cursor.execute("UPDATE depenses SET coefficient_depense = ? WHERE mois = ?  and email_user = ?",(coefficientDepense,mois,email))
        cursor.execute("UPDATE depenses SET depense_fixe = ? WHERE mois = ?  and email_user = ?",(depenseFixe,mois,email))
        db.commit()
        db.close()
        recalculateCapitalSession()
        return redirect(url_for("pagesDepenses"))
    return render_template("Ajout_donees.html")

@app.route("/ajoutCapitalInitial" ,methods=["POST","GET"])
def ajouterCapitalInitial():
    email = session['data']
    if request.method == "POST":
        capitalInitial = request.form["capitalInitial"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE utilisateurs SET capital_initial = ? WHERE email = ?",(capitalInitial,email))
        db.commit()
        db.close()
        recalculateCapitalSession()
        return redirect(url_for("pagesDepenses"))
    return render_template("Ajout_donees.html")

@app.route("/api/capital")
def capital():
    from RungeKutta import runge_kutta,dC_dt
    with get_connexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT capital_initial FROM utilisateurs WHERE email = ?",(session['data'],))
            capitalInitial = cursor.fetchone()[0]
    donnees = runge_kutta(dC_dt, 0, capitalInitial, 1, 12)
    capital = [x[1] for x in donnees]
    session['capital'] = capital
    session['capitalmax'] = max(capital)
    session['capitalmin'] = min(capital)
    session['capitalfinal'] = capital[-1]
    session['capitalinitial'] = capitalInitial
    return jsonify({
        "mois" : [x[0] for x in donnees ],
        "capital": [x[1] for x in donnees ]
    })

# --- Initialisation de la base au démarrage de Flask ---
with app.app_context():
    from init_db import init_db
    init_db()

if __name__ == "__main__":
    app.run(debug=True)