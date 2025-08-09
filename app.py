from flask import Flask, render_template, request, redirect, url_for, send_file
from database import (
    init_db,
    get_all_clients,
    add_client,
    get_client,
    update_client,
    delete_client,
    search_clients,
    add_comment,
    get_comments,
)
import io
from openpyxl import Workbook

app = Flask(__name__)
init_db()

@app.route('/')
def index():
    return redirect(url_for('list_clients'))

@app.route('/clients')
def list_clients():
    q = request.args.get('q', '').strip()
    if q:
        clients = search_clients(q)
    else:
        clients = get_all_clients()
    return render_template('clients.html', clients=clients, q=q)

@app.route('/clients/new', methods=['GET', 'POST'])
def new_client():
    if request.method == 'POST':
        loan_number = request.form['loan_number'].strip()
        name = request.form['name'].strip()
        id_number = request.form['id_number'].strip()
        address = request.form['address'].strip()
        locality = request.form['locality'].strip()
        note = request.form['note'].strip()
        if loan_number and name and id_number:
            add_client(loan_number, name, id_number, address, locality, note)
            return redirect(url_for('list_clients'))
    return render_template('client_form.html', client={}, action='Crear')

@app.route('/clients/<loan_number>/edit', methods=['GET', 'POST'])
def edit_client(loan_number):
    client = get_client(loan_number)
    if not client:
        return redirect(url_for('list_clients'))
    if request.method == 'POST':
        name = request.form['name'].strip()
        id_number = request.form['id_number'].strip()
        address = request.form['address'].strip()
        locality = request.form['locality'].strip()
        note = request.form['note'].strip()
        update_client(loan_number, name, id_number, address, locality, note)
        return redirect(url_for('list_clients'))
    return render_template('client_form.html', client=client, action='Editar')

@app.route('/clients/<loan_number>/delete', methods=['POST'])
def remove_client(loan_number):
    delete_client(loan_number)
    return redirect(url_for('list_clients'))

@app.route('/clients/<loan_number>', methods=['GET', 'POST'])
def client_detail(loan_number):
    client = get_client(loan_number)
    if not client:
        return redirect(url_for('list_clients'))
    if request.method == 'POST':
        text = request.form['comment'].strip()
        if text:
            add_comment(loan_number, text)
        return redirect(url_for('client_detail', loan_number=loan_number))
    comments = get_comments(loan_number)
    return render_template('client_detail.html', client=client, comments=comments)

@app.route('/export')
def export_clients():
    wb = Workbook()
    ws = wb.active
    ws.append(['Loan Number', 'Name', 'ID', 'Address', 'Locality', 'Note', 'Created', 'Updated'])
    for c in get_all_clients():
        ws.append([
            c['loan_number'],
            c['name'],
            c['id_number'],
            c.get('address', ''),
            c.get('locality', ''),
            c.get('note', ''),
            c['created_at'],
            c['updated_at'],
        ])
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return send_file(
        stream,
        as_attachment=True,
        download_name='clients.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )

if __name__ == '__main__':
    app.run(debug=True)
