import os
from flask import Flask,jsonify,request,json,send_file,Response,render_template,redirect,url_for
from app import app
from app import db 
from app.models import Patient, Questions,Answer

path=path=os.getcwd()
FOLDER_Q=path+"/question"
FOLDER_R=path+"/response"

@app.before_first_request
def init_db():
   # db.drop_all()
    db.create_all()
    patient= Patient(name="Carl")
    patient2= Patient(name="Mason")
    answer1=Answer(text="je vais bien",quest="Comment-allez vous?")
    answer2=Answer(text="53 kilos",quest="Combien pesez-vous?")
    answer3=Answer(text="oui oui", quest="As-tu manger tes médicaments")
    
    patient.answer.append(answer1)
    patient.answer.append(answer2)
    
    patient2.answer.append(answer2)
    patient2.answer.append(answer3)

    db.session.add_all([patient,patient2,answer1,answer2,answer3])
    db.session.commit()
    

@app.route("/question",methods=['GET'])
def questions():
    if(request.method=='GET'):
        quests= Questions.query.all()
        array=[]
        for q in quests:
            array.append(str(q))
        dict={"questions": array}
        return jsonify(dict)
    return Response("",404)

@app.route("/response",methods=['POST'])
def response():
    if(request.method=='POST'):
        content=request.get_json()
        name=content["name"]
        patient=check_patient(name)
        quests= Questions.query.all()
        res=content["responses"]
        print(res)
        for i in range (len(res)):
            rep=Answer(text=str(res[i]),quest=str(quests[i+1]))
            patient.answer.append(rep)
            db.session.add(rep)
        db.session.commit()
        return Response("ok",200)
    return Response("",404)

@app.route('/audio/<id>',methods=['GET','POST'])
def audio(id):
    if (request.method=='GET'):
        path_to_file = FOLDER_Q+"/audio"+str(id)+".wav"
        return send_file(
         path_to_file, 
         mimetype="audio/wav")
    elif(request.method=='POST'):
        save_path=FOLDER_R+"/response_"+str(id)+".wav"
        if 'file'not in request.files:
            print("audio not received")
            return Response("",404) 
        with open(save_path,'wb') as fp :
            fp.write(request.files['file'].read())
        return Response("ok",200)

@app.route('/',methods=['GET'])
def index():
    if(request.method=='GET'):
        quests= Questions.query.all()
        p_list=db.session.execute(db.select(Patient).order_by(Patient.name)).scalars()
        data=json.dumps([1.0,2.0,3.0])
        return render_template('board.html',questionitems= quests,patient_list=p_list, data_json=data)

@app.route('/add-q', methods=['POST'])
def add_question():
    print(request.form['item'])
    quest=Questions(text=request.form['item'])
    db.session.add(quest)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<id>')
def delete(id):
    question_to_delete=Questions.query.get_or_404(id)
    try:
        db.session.delete(question_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "Error while deleting questions"

@app.route('/get-responses/<name>')
def answer(name):
    patient=Patient.query.filter_by(name=str(name)).first()
    print(patient.answer)
    array=[]
    for answer in patient.answer:
        array.append(str(answer))
    return jsonify(array)

@app.route('/get-patient')
def patient():
    list_patient=Patient.query.all()
    array=[]
    for p in list_patient:
        array.append(str(p.name))
    return jsonify(array)

def check_patient(name):
    patient=Patient.query.filter_by(name=name).first()
    if patient is None :
        patient=Patient(name=name)
        db.session.add(patient)
        db.session.commit() 
    return patient



# def get_question():
#     path= FOLDER_Q+'/questions.json'
#     f=open(path)
#     quests=json.load(f)
#     return quests["questions"]

# def get_answer():
#     path=FOLDER_R+'/response.json'
#     f=open(path)
#     resp=json.load(f)
#     return resp["responses"]
