from . import db
from .parking_spot import parking_spot_data
from sqlalchemy import func
import matplotlib.pyplot as plt
import os
import pandas as pd

OUTPUT_DIR = 'static/images'
os.makedirs( OUTPUT_DIR , exist_ok = True )

class parking_lot_data( db.Model ):
    __tablename__  =  "parking_lot"
    parking_lot_id  =  db.Column( db.Integer , primary_key = True , autoincrement = True )
    parking_lot_name  =  db.Column( db.Text , nullable = False )
    address  =  db.Column( db.Text , nullable = False )
    pin_code  =  db.Column( db.Integer , nullable = False )
    price_per_hour  =  db.Column( db.Integer , nullable = False )
    total_spots  =  db.Column( db.Integer , nullable = False )
    
    def update_parking_lot( self , name = None , address = None , pin_code = None , price_per_hour = None , total_spots = None ):
        if name :
            self.parking_lot_name = name
        if address :
            self.address = address
        if pin_code :
            self.pin_code = pin_code
        if price_per_hour :
            self.price_per_hour = price_per_hour
        if total_spots :
            if int( total_spots ) < self.total_spots:
                d = db.session.query( parking_spot_data ).filter_by( parking_lot_id = self.parking_lot_id , status = 'A' ).limit( self.total_spots - int( total_spots ) ).all()
                for i in d:
                    db.session.delete( i )
            if int( total_spots ) > self.total_spots:
                m = db.session.query( func.max( parking_spot_data.parking_lot_number ) ).filter_by( parking_lot_id = self.parking_lot_id ).scalar() + 1
                for i in range( m , m +  int( total_spots ) - self.total_spots ):
                    ns = parking_spot_data( parking_lot_id = self.parking_lot_id , parking_lot_number = i , status = "A" , reservation_id = 0 )
                    db.session.add( ns )
            self.total_spots = total_spots    
        db.session.commit()
    
    def get_by_name( name ):
        data = parking_lot_data.query.filter( parking_lot_data.parking_lot_name.like( f"%{name}%" ) ).all()
        if not data:
            return ( "No Matching Data" , True )
        return ( data , False )
    
    def get_by_location( location ):
        data = parking_lot_data.query.filter( parking_lot_data.address.like( f"%{location}%" ) ).all()
        if not data:
            return ( "No Matching Data" , True )
        return ( data , False )
    
    def get_by_pin_code( pin ):
        data = parking_lot_data.query.filter_by( pin_code = pin ).all()
        if not data:
            return ( "No Matching Data" , True )
        return ( data , False )
    
    def GetAll():
        return parking_lot_data.query.all()
    
    def delete( parking_lot_id ):
        lot = parking_lot_data.query.get( parking_lot_id )
        parking_spot_data.delete_parking_spots_by_parking_lot_id( parking_lot_id )
        db.session.delete( lot )
        db.session.commit()
    
    def insert( parking_lot_name , address , pin_code , price , total_spots : int ):
        l = parking_lot_data( parking_lot_name = parking_lot_name , address = address , pin_code = pin_code , price_per_hour = price , total_spots = total_spots )

        db.session.add( l )
        db.session.commit()

        parking_lot_id = l.parking_lot_id

        for i in range( 1 , int( total_spots ) + 1 ):
            new_spot = parking_spot_data ( parking_lot_id = parking_lot_id , parking_lot_number = i , status = "A" , reservation_id = 0 )
            db.session.add( new_spot )
        db.session.commit()
    
    def get_by_id( parking_lot_id : int ):
        return parking_lot_data.query.get( parking_lot_id )
    
    def update_totaL_spots( parking_lot_id : int ):
        parking_lot = parking_lot_data.query.get( parking_lot_id )
        if parking_lot:
            parking_lot.total_spots -= 1
            db.session.commit()
      
    def get_price( parking_lot_id : int ):
        l = parking_lot_data.query.filter_by( parking_lot_id = parking_lot_id ).first()
        return l.price_per_hour

    def get_parking_lot_name_by_id( parking_lot_id ):
        p = parking_lot_data.query.filter_by( parking_lot_id = parking_lot_id ).first()
        if p:
            return p.parking_lot_name
        return "Error"
