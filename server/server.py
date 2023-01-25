import os
from flask import Flask,jsonify,request,json,send_file,Response

app = Flask(__name__)
FOLDER_Q="/home/unravel/IoT/project/server/question"
FOLDER_R="/home/unravel/IoT/project/server/response"
#FOLDER_Q="/home/username/project_IoT/server/questions"
#FOLDER_R="/home/username/project_IoT/server/responses"

@app.route("/",methods=['GET','POST'])
def questions():
    if(request.method=='GET'):
        path= FOLDER_Q+'/questions.json'
        f = open(path)
        data =json.load(f)
        return jsonify(data)

    elif(request.method=='POST'):
        content=request.get_json()
        print(content)
        path =FOLDER_R+'/response.json'
        data= json.dumps(content)
        print(data)
        f = open(path,'a')
        f.write(data) 
        return Response("ok",200)

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
        


if __name__=='__main__':
    app.run(debug=True)