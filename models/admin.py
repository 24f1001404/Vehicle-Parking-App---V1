from . import db

class Admin( db.Model ):
    __tablename__ = 'admin'

    email = db.Column( db.Text , primary_key = True , nullable = False )  
    name = db.Column( db.Text , nullable = False )
    password = db.Column( db.Text , nullable = False )
    dob = db.Column( db.Text , nullable = False )  
    gender = db.Column( db.Text , nullable = False )
    
    def get():
        data = Admin.query.first()
        if data:
            return data
        else:
            a = Admin( email = "admin@gmail.com" , name = "admin" , password = "admin" , dob = "1999-01-01" , gender = "male" )
            db.session.add(a)
            db.session.commit()
        return Admin.get()

    def verify_password( self , pwd ):
        return ( self.password  == pwd )

    def update_profile( self , email = None , name = None , pwd = None , dob = None , gender = None ):
        if email:
            self.email = email

        if name:
            self.name = name

        if pwd:
            self.password = pwd

        if dob:
            self.dob = dob

        if gender:
            self.gender = gender