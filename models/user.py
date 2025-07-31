from . import db

class user_data( db.Model ):
    __tablename__  =  'user'
    
    user_id  =  db.Column( db.Integer , primary_key = True , autoincrement = True )
    email  =  db.Column( db.Text , unique = True , nullable = False )
    name  =  db.Column( db.Text , nullable = False )
    phone  =  db.Column( db.Text , nullable = False )
    gender  =  db.Column( db.Text , nullable = False )
    DOB  =  db.Column( db.Text , nullable = False )
    address  =  db.Column( db.Text , nullable = False )
    vehicle_number  =  db.Column( db.Text )
    password  =  db.Column( db.Text , nullable = False )
    
    def update_user( self , email = None , name = None , phone = None , gender = None , dob = None , address = None , vehicle_number = None , pwd = None ):
        if email :
            self.email = email
        
        if name :
            self.name = name 
        
        if phone :
            self.phone = phone
        
        if gender :
            self.gender = gender
        
        if dob :
            self.DOB = dob
        
        if address :
            self.address = address
        
        if vehicle_number :
            self.vehicle_number = vehicle_number
        
        if pwd :
            self.password = pwd
        
        db.session.commit()
        
    def check_password( user_id , pwd ):
        d = user_data.query.get(user_id)
        flag = (d.password == pwd)
        print(flag)
        return flag

    def verify_user( email , pwd ):
        u = user_data.query.filter_by( email = email ).first()
        if u.password == pwd:
            return True
        return False
    
    def get_user( email ):
        user = user_data.query.filter_by( email = email ).first()
        return user  
      
    def get_user_by_name( name ):
        u = user_data.query.filter( user_data.name.ilike( f"%{name}%" ) ).all()
        if len( u )  == 0:
            return u , True
        return u , False

    def get( email : str ):
        user = user_data.query.filter_by( email = email ).first()
        return user
    
    def get_by_user_id(id):
        return user_data.query.get(id)
    
    def get_users():
        return user_data.query.all()
    
    def CheckEmail( mail ):
        if user_data.query.filter_by( email = mail ).first():
            return True
        return False
    
    def insert( email , name , phone , gender , DOB , address , vehicle , pwd ):
        new_user = user_data( email = email , name = name , phone = phone , gender = gender , DOB = DOB , address = address , vehicle_number = vehicle , password = pwd )
        db.session.add( new_user )
        db.session.commit()
    
    
    
    
    
    
    
    
    
    