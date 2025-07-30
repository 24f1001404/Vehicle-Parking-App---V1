from .user import user_data
from . import db
from datetime import datetime

class Queries( db.Model ):
    __tablename__ = 'query'
    
    query_id = db.Column( db.Integer , primary_key = True , autoincrement = True ) 
    user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    query = db.Column( db.Text , nullable = False )
    asked_date = db.Column( db.DateTime , nullable = False , default = datetime.now )
    status = db.Column( db.Text , nullable = False , default = 'pending' )
    reply = db.Column( db.Text )

    def insert( user_id , query ):
        q = Queries( user_id  =  user_id , query  =  query )
        db.session.add( q )
        db.session.commit()
        
    def update_query( self , status = None , reply = None ):
        if status:
            self.status = status
        
        if reply:
            self.reply = reply
    
    def user_queries( user_id ):
        return db.session.query( Queries ).filter( Queries.user_id  == user_id ).all()
    
    def get_unsolved():
        return db.session.query( user_data.name , Queries.query , Queries.asked_date , Queries.status , Queries.reply , Queries.query_id ).join( Queries , user_data.user_id  == Queries.user_id ).filter( Queries.status  == 'pending' ).all()

    def mark_as_resolved( id ):
        query = db.session.query( Queries ).get( id )
        query.status = 'resolved'
        db.session.commit()

    def reply_query( id , reply ):
        q = db.session.query( Queries ).get( id )
        q.reply = reply
        q.status = 'resolved'
        db.session.commit()
        

  