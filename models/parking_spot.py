from . import db
from sqlalchemy import func

class parking_spot_data( db.Model ):
    __tablename__  =  'parking_spot'
    
    parking_spot_id  =  db.Column( db.Integer , primary_key = True , autoincrement = True )
    parking_lot_id  =  db.Column( db.Integer , db.ForeignKey( 'parking_lot.parking_lot_id' , ondelete = "CASCADE" ) , nullable = False )
    parking_lot_number  =  db.Column( db.Integer , nullable = False )
    status  =  db.Column( db.Text , nullable = False )
    reservation_id  =  db.Column( db.Integer , db.ForeignKey( 'reservations.reservation_id' , ondelete = "CASCADE" ) )

    def update_parking_spot( self , new_status = None , new_reservation_id = None ):
        if new_status :
            self.status  =  new_status

        if new_reservation_id :
            self.reservation_id  =  new_reservation_id
    
    
    def GetParkingLotData( parking_lot_id ):
        return  parking_spot_data.query.filter_by( parking_lot_id = parking_lot_id ).order_by( parking_spot_data.parking_lot_number.asc() ).all()
    
    def book( parking_lot_id , number , reservation_id ):
        s = parking_spot_data.query.filter_by( parking_lot_id = parking_lot_id , parking_lot_number = number ).first()
        if s:
            s.status = "O"
            s.reservation_id = reservation_id
            db.session.commit()
            
    def Release( reservation_id ):
        s = parking_spot_data.query.filter_by( reservation_id = reservation_id ).first()
        if s:
            s.status = 'A'
            s.reservation_id = 0
            db.session.commit()
            
    def delete( parking_lot_id , number ):
        spot = parking_spot_data.query.filter_by( parking_lot_id = parking_lot_id , parking_lot_number = number ).first()
        if spot:
            db.session.delete( spot )
            db.session.commit()
    
    def get_parking_spot_id( parking_lot_id : int , number : int ):
        spot = parking_spot_data.query.filter_by( parking_lot_id = parking_lot_id , parking_lot_number = number ).first()
        if spot is None:
            return 0
        return spot.parking_spot_id
    
    def get_reservation_of_spot( parking_lot_id : int , number : int ):
        spot = parking_spot_data.query.filter_by( parking_lot_id = parking_lot_id , parking_lot_number = number ).first()
        if spot is None:
            return 0
        return spot.reservation_id
       
    def parking_lot_spots_status():
        ad = db.session.query( parking_spot_data.parking_lot_id , func.count( parking_spot_data.status ) ).filter_by( status = 'A' ).group_by( parking_spot_data.parking_lot_id ).order_by( parking_spot_data.parking_lot_id ).all()
        od = db.session.query( parking_spot_data.parking_lot_id , func.count( parking_spot_data.status ) ).filter_by( status = 'O' ).group_by( parking_spot_data.parking_lot_id ).order_by( parking_spot_data.parking_lot_id ).all()
        d = dict( od )
        r = [( l , a , d.get( l , 0 ) ) for l , a in ad]
        return r
        
    def delete_parking_spots_by_parking_lot_id( parking_lot_id ):
        parking_spot_data.query.filter_by( parking_lot_id = parking_lot_id ).delete()
        db.session.commit()
    

    def get_free_spot( parking_lot_id ):
        p = parking_spot_data.query.filter_by( parking_lot_id = parking_lot_id , status = 'A' ).first()
        return p.parking_spot_id , p.parking_lot_number

    
    