from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
import sqlite3, io

app = Flask(__name__)
DB = 'data.db'

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS prodotto (id INTEGER PRIMARY KEY, nome, codice, qty)')
        conn.execute('CREATE TABLE IF NOT EXISTS cliente (id INTEGER PRIMARY KEY, nome)')
        conn.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    init_db()
    conn = sqlite3.connect(DB); c = conn.cursor()
    if request.method == 'POST' and request.form.get('nome'):
        c.execute(
            'INSERT INTO prodotto (nome, codice, qty) VALUES (?,?,?)',
            (request.form['nome'], request.form['codice'], request.form['qty'])
        )
        conn.commit()
    prodotti = c.execute('SELECT * FROM prodotto').fetchall()
    clienti = c.execute('SELECT * FROM cliente').fetchall()
    conn.close()
    return render_template('index.html', prodotti=prodotti, clienti=clienti)

@app.route('/genera', methods=['POST'])
def genera():
    prodotti_sel = request.form.getlist('prod_id')
    cliente_id = request.form.get('cliente')
    conn = sqlite3.connect(DB); c = conn.cursor()
    cliente = c.execute('SELECT nome FROM cliente WHERE id=?', (cliente_id,)).fetchone()
    prodotti = c.execute(
        f"SELECT nome, codice, qty FROM prodotto WHERE id IN ({','.join('?'*len(prodotti_sel))})",
        prodotti_sel
    ).fetchall()
    conn.close()
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(50, 800, f"Packing List per: {cliente[0]}")
    y = 760
    for nome, codice, qty in prodotti:
        pdf.drawString(50, y, f"{nome} | {codice} | qty: {qty}")
        y -= 20
    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="packing_list.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
