import math
import sqlite3
from flask import session

def dC_dt(t, C):
    mois = (int(t) % 12) or 12
    a, b, d = get_revenu_depense(mois)
    if C == None:
        C = 0
    if C <= 0:
        return -d
    return a * C - b * math.sqrt(C) - d

def get_revenu_depense(mois):
    email = session.get('data')
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT taux_revenu FROM revenus WHERE mois = ? and email_user = ?", (mois,email))
    taux_revenu = cursor.fetchone()
    if taux_revenu:
        taux_revenu = taux_revenu[0]
    else:
        taux_revenu = 0.04  # valeur par défaut si rien trouvé

    cursor.execute("SELECT coefficient_depense, depense_fixe FROM depenses WHERE mois = ? and email_user = ?", (mois,email))
    depenses = cursor.fetchone()
    if depenses:
        coefficient_depense, depense_fixe = depenses
    else:
        coefficient_depense, depense_fixe = 10, 500  # valeurs par défaut

    conn.close()
    return taux_revenu, coefficient_depense, depense_fixe

