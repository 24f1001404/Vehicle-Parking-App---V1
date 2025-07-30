from models.user import user_data
from models.parking_lot import parking_lot_data
from models.parking_spot import parking_spot_data
from models.user import user_data
from models import db
from models.reservation import reservation
from datetime import datetime
from models.pre_data import pre_data
from models.query import Queries
import math

class user:
    def __init__( self ):
        self.email = pre_data.get_pre_data_user()
        if ( self.email != " " ):
            self.get()

    def check( self , pwd ):
        return self.data.check_password( pwd )

    def update_email( self , email ):
        self.email = email
        self.get()
        
    def set_pre_data( self ):
        pre_data.set_pre_data_user( self.email )
    
    def check_password( email : str , pwd: str ):
        return user_data.verify_user( email , pwd )
    
    def update( self , email = None , name = None , phone = None , gender = None , dob = None , address = None , vehicle_number = None , pwd = None ):
        self.data.update_user( email , name , phone , gender , dob , address , vehicle_number , pwd )
        
    def get_recent_parking_history(self):
        user_id = self.user_id 
        data = db.session.query(parking_lot_data, reservation).join(
            reservation, reservation.parking_lot_id == parking_lot_data.parking_lot_id
        ).filter(reservation.user_id == user_id).all()

        result = []
        now = datetime.now()

        for p, r in data:
            # Ensure proper datetime parsing
            reserved_time = r.reserved_time
            released_time = r.Released_time

            # Convert to datetime object if they are strings
            if isinstance(reserved_time, str):
                try:
                    if 'T' in reserved_time:
                        reserved_time = datetime.strptime(reserved_time, '%Y-%m-%dT%H:%M')
                    else:
                        reserved_time = datetime.strptime(reserved_time, '%Y-%m-%d %H:%M:%S')
                except:
                    reserved_time = None

            if isinstance(released_time, str):
                try:
                    if 'T' in released_time:
                        released_time = datetime.strptime(released_time, '%Y-%m-%dT%H:%M')
                    else:
                        released_time = datetime.strptime(released_time, '%Y-%m-%d %H:%M:%S')
                except:
                    released_time = None

            # Determine button status
            if released_time:
                button_status = 3  # Over
            elif reserved_time and reserved_time > now:
                button_status = 1  # Park In
            else:
                button_status = 2  # Park Out

            d = {
                'id': r.reservation_id,
                'location': p.address,
                'vehicle_number': r.vehicle_number,
                'reserved_time': reserved_time,
                'Released_time': released_time,
                'price_per_hour': p.price_per_hour,
                'parking_lot_id': p.parking_lot_id,
                'button': button_status
            }
            result.append(d)
        return result     
    
    def get_quick_book_history(self):
        user_id = self.user_id 
        data = db.session.query(parking_lot_data, reservation).join(reservation, reservation.parking_lot_id == parking_lot_data.parking_lot_id).filter(reservation.user_id == user_id).order_by(reservation.reserved_time.desc()).all()

        seen = set()
        result = []

        for p, r in data:
            key = (p.parking_lot_id, r.vehicle_number)
            if key not in seen:
                seen.add(key)
                d = {
                    'id': r.reservation_id,
                    'location': p.address,
                    'vehicle_number': r.vehicle_number,
                    'reserved_time': r.reserved_time,
                    'Released_time': r.Released_time,
                    'price_per_hour': p.price_per_hour,
                    'parking_lot_id': p.parking_lot_id
                }
                result.append(d)
            if len(result) == 3:
                break

        return result

    def search( self , type , name ):
        result = dict()
        result['type'] = type
        empty = True
        if ( type  == 'parking_lot' ):
            data , empty = parking_lot_data.get_by_name( name )
        if ( type  == 'location' ):
            data , empty = parking_lot_data.get_by_location( name )
        if ( type  == 'pin_code' ):
            data , empty = parking_lot_data.get_by_pin_code( name )
        result['empty'] = empty
        parking_lots = []
        if ( empty ):
            return result
        for i in data:
            d = dict()
            d['id'] = i.parking_lot_id
            d["name"] = i.parking_lot_name
            d['total'] = i.total_spots
            d['address'] = i.address
            d['pincode'] = i.pin_code
            d['price_per_hour'] = i.price_per_hour
            occupied = 0
            spot = list()
            spot_data = parking_spot_data.GetParkingLotData( i.parking_lot_id )
            for j in spot_data:
                sd = dict()
                sd['number'] = j.parking_lot_number
                flag = j.status
                sd['occupied'] = False
                if flag  == "O":
                    occupied += 1
                    sd['occupied'] = True
                spot.append( sd )
            d['occupied'] = occupied
            d['spots'] = spot 
            d['available'] = i.total_spots - occupied  
            parking_lots.append( d )
        result['parking_lots'] = parking_lots
        return result
    
    def get( self ):
        if ( self.email != " " and self.email != "" ):
            self.data = user_data.get( self.email )
            self.user_id = self.data.user_id
            self.name = self.data.name
            self.phone = self.data.phone
            self.gender = self.data.gender
            self.DOB = self.data.DOB
            self.address = self.data.address
            self.vechile_number = self.data.vehicle_number
            self.role = "USER"
             
    def book( self , parking_lot_id , parking_spot_id , user_id , status , vehicle , reserved_time):
        if not reserved_time:
            reserved_time = datetime.now().replace( microsecond = 0 )
        reservation_id = reservation.reserve( parking_lot_id , parking_spot_id , user_id , vehicle , reserved_time )

        parking_spot_data.book( parking_lot_id , parking_spot_id , reservation_id )
    
    def Release( self , reservation_id : int , reserved_time , price : int ):
        Released_time = datetime.now().replace( microsecond = 0 )
        reserved_time = datetime.strptime( reserved_time , '%Y-%m-%d %H:%M:%S' )
        time_difference = Released_time - reserved_time
        hours_difference = math.ceil(time_difference.total_seconds() / 3600)
        cost = float( price*hours_difference )

        reservation.Release( reservation_id , Released_time , cost )
        parking_spot_data.Release( reservation_id )

    def Logout( self ):
        pre_data.delete_pre_data_user()
    
    def customer_care( self , query ):
        Queries.insert( self.data.user_id , query )
    
    def all_queries( self ):
        data = Queries.user_queries( self.user_id )
        result = []        
        for d in data:
            di = dict()
            di['query'] = d.query
            di['reply'] = d.reply
            result.append( di )
        return result

    def summary( self ):
        reservation.generate_parking_charts( self.user_id )

    def park_in(self, reservation_id):
        r = reservation.query.get(reservation_id)
        formatted_time = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

        r.reserved_time = formatted_time
        db.session.commit()