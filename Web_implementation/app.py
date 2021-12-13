#!/usr/bin/python
# -*- coding: utf-8 -*-

# import flask dependencies for web GUI
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha256_crypt
from functools import wraps
import admin_manager
from forms import *
import new_encryption_module
import time


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
def log_in_user(username):
    session['logged_in'] = True
    session['username'] = username
    session['username'] = name


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
        if user_password is None:
            flash('User name is not valid', 'danger')
            return redirect(url_for('login'))
        else:
            try:
                if new_encryption_module.hashing_function(str(candidate_password)) == new_encryption_module.hashing_function(str(user_password)):
                    flash('You are now logged in', 'success')
                    log_in_user(username)
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
    app.run('0.0.0.0', 5000, debug=True)

