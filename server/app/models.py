from app import db

patient_answer= db.Table('patient_answer',
                db.Column('patient_id',db.Integer,db.ForeignKey('patient.id')),
                db.Column('answer_id',db.Integer,db.ForeignKey('answer.id'))
                )


class Patient(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String,nullable=False)
    firstName = db.Column(db.String)
    answer=db.relationship('Answer',secondary=patient_answer,backref="patient")

    def __repr__(self):
        return self.name

class Questions(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    text=db.Column(db.String, nullable=False)

    def __repr__(self):
        return self.text

class Answer(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    text=db.Column(db.String, nullable=False)
    quest=db.Column(db.String, nullable=False)   

    def __repr__(self):

        return f"Réponse : "+self.text +". Question :"+  self.quest

