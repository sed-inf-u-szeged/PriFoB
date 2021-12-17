#!/usr/bin/python
# -*- coding: utf-8 -*-

# import flask dependencies for web GUI
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha256_crypt
from functools import wraps
import admin_manager
import shared_functions
from forms import *
import new_encryption_module
import terminology
import my_address
import msg_constructor
import client
import os
import output


app = Flask(__name__)
app.config['MYSQL_USER'] = 'Hamza'
app.config['MYSQL_PASSWORD'] = '1234'
admins = admin_manager.AdminManager()


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, *kwargs)
        else:
            flash('Unauthorized. Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


# log in the user by updating session
def log_in_user(username, gateway_address):
    session['logged_in'] = True
    session['username'] = username
    session['name'] = username
    session['address'] = my_address.provide_my_address()
    session['gatewayAddress'] = gateway_address


@app.route("/publish_my_DID", methods=['GET', 'POST'])
@is_logged_in
def publish_my_DID():
    form = DIDRequestForm(request.form)
    issuer_name = form.issuer_name.data
    publish_info, file_exists = shared_functions.open_saved_file('local_files/DID_info/DID_info.txt')
    DID_is_published = publish_info['is_published']
    if request.method == 'POST' and form.validate():
        try:
            my_public_key = new_encryption_module.prepare_key_for_use(terminology.public, 'DID')
        except:
            string_pri_key, string_pub_key = new_encryption_module.generate_PKI_keys('DID')
            my_public_key = new_encryption_module.prepare_key_for_use(terminology.public, 'DID')
        deserialized_public_key = new_encryption_module.deserialize_key(my_public_key)
        DID_transaction = msg_constructor.new_did_transaction(issuer_name, session.get('address'), deserialized_public_key)
        message = msg_constructor.construct_new_block_request(terminology.DID_publication_request, DID_transaction)
        # client.send(message, session.get('gatewayAddress'))
        flash(output.present_dictionary(message))
        flash('DID publication request was sent. Once a positive response arrives, you can publish new schemes and issue new credentials.')
        session['issuer_name'] = issuer_name
    return render_template("publish_my_DID.html", form=form, did_is_published=DID_is_published)


@app.route("/add_schema", methods=['GET', 'POST'])
@is_logged_in
def add_schema():
    form = SchemaRequestForm(request.form)
    schema_transaction = {
    # 'institution_name': session['issuer_name'],
                          'institution_address': session['address'],
                          terminology.identifier: ''}
                           # 'schema_public_key': public_key,
                           # 'schema_attributes': attributes}
    # private_key, public_key = shared_functions.select_keys(schema_transaction[terminology.identifier])
    # schema_public_key = new_encryption_module.prepare_key_for_use(terminology.public,
    #                                                               schema_transaction[terminology.identifier], None)
    # deserialized_public_key = new_encryption_module.deserialize_key(schema_public_key)
    # print('keys of the new schema are generated')
    # schema_transaction['schema_public_key'] = deserialized_public_key
    # schema_transaction[terminology.DID_index] = self.DID_index
    # print('schema public key is added to the request')

    return render_template("add_schema.html", form=form, schema=schema_transaction)


@app.route("/issue_VC", methods=['GET', 'POST'])
@is_logged_in
def issue_VC():
    return render_template("issue_VC.html")

@app.route("/schemes", methods=['GET', 'POST'])
@is_logged_in
def schemes():
    list_of_schema_titles = os.listdir("local_files/schemes/")
    form = SchemaRequestForm(request.form)
    return render_template("schemes.html", form=form, list_of_schema_titles=list_of_schema_titles)


@app.route("/credentials", methods=['GET', 'POST'])
@is_logged_in
def credentials():
    list_of_VC_titles = os.listdir("local_files/credentials/")
    form = VCIssueForm(request.form)
    return render_template("credentials.html", form=form, list_of_schema_titles=list_of_VC_titles)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user_name = form.username.data
        if admins.admin_registered(user_name) is None:
            password = sha256_crypt.encrypt(form.password.data)
            admins.admins[len(admins.admins)] = admin_manager.initiate_admin(user_name, password)
            flash('Registration request has been sent. One of the admins must accept your request before you can login')
            return redirect(url_for('dashboard'))
        else:
            flash('User already exists', 'danger')
            return redirect(url_for('dashboard'))
    return render_template('register.html', form=form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        candidate_password = request.form['password']
        user_password = admins.admin_registered(username)
        gateway_address = request.form['gatewayAddress']
        if user_password is None:
            flash('User name is not valid', 'danger')
            return redirect(url_for('login'))
        else:
            try:
                if new_encryption_module.hashing_function(str(candidate_password)) == new_encryption_module.hashing_function(str(user_password)):
                    flash('You are now logged in', 'success')
                    log_in_user(username, gateway_address)
                    return redirect(url_for('dashboard'))
                else:
                    flash('Password is incorrect', 'danger')
                    return redirect(url_for('login'))
            except Exception as e:
                flash('Something went wrong', 'danger')
                flash(str(e))
                return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('Logout success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.secret_key = '1234'
    # app.run('0.0.0.0', 5000, debug=True)
    app.run(debug=True)

