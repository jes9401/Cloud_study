from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for
from decimal import Decimal
import boto3

app=Flask(__name__)


@app.route('/')
def hello_student_manager():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('UnivStudent')
    response = table.scan()
    print(response)

    return render_template('ViewStudentList.html',student_list=response['Items'])


@app.route('/Add')
def add_student_form():
    return render_template('Add.html')


@app.route('/AddStudent', methods=['POST'])
def add():
    univ_id=request.form['univ_id']
    univ_name=request.form['univ_name']
    major=request.form['major']
    circle=request.form['circle']
    avg_credit=request.form['avg_credit']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('UnivStudent')

    if univ_id!="" and univ_name!="":
        new_student={
            'univ_id':Decimal(univ_id),
            'univ_name':univ_name
        }
        if major!="":
            new_student['major']=major
        if circle!="":
            new_student['circle']=circle
        if avg_credit!="":
            new_student['avg_credit']=Decimal(avg_credit)

        print("new_student = ",new_student)
        table.put_item(Item=new_student)
    return redirect(url_for('hello_student_manager'))

@app.route('/Remove',methods=['POST'])
def remove():
    univ_name=request.form['univ_name']
    univ_id=request.form['univ_id']

    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('UnivStudent')
    will_remove_student={
        'univ_name':univ_name,
        'univ_id':Decimal(univ_id)
    }
    table.delete_item(Key=will_remove_student)

    return redirect(url_for('hello_student_manager'))