from . import db

class pre_data( db.Model ):
    __tablename__ = "pre_data_user"
    
    email = db.Column( db.Text , primary_key = True )
    
    def get_pre_data_user():
        u = pre_data.query.all()
        if u:
            return u[0].email
        return " "
    
    def set_pre_data_user( email ):
        pre_data.query.delete()
        new_pre_data = pre_data( email = email )
        db.session.add( new_pre_data )
        db.session.commit()
        
    def delete_pre_data_user():
        pre_data.query.delete()
        db.session.commit()