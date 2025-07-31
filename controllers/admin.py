from models.user import user_data
from models.parking_lot import parking_lot_data
from models.parking_spot import parking_spot_data
from models.reservation import reservation
from datetime import datetime
from models.admin import Admin
import matplotlib.pyplot as plt
import os
from models.query import Queries
import matplotlib
import math
matplotlib.use( 'Agg' )  
class admin:
    def __init__( self ):
        self.d = Admin.get()
        self.email = self.d.email
        self.name = self.d.name
        self.DOB = self.d.dob
        self.gender = self.d.gender

    def check_login( self , pwd ):
        return self.d.verify_password( pwd )
    
    def show_parking_lots( self ):
        parking_lots = []
        data = parking_lot_data.GetAll()
        
        for i in data:
            d = dict()
            d['id'] = i.parking_lot_id
            d["name"] = i.parking_lot_name
            d['total'] = i.total_spots
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
            parking_lots.append( d )
        return parking_lots          
                
    def delete_lot( self , lot_id ):
        parking_lot_data.delete( lot_id )
    
    def add_lot( self , parking_lot_name : str , address  : str , pin_code : int , price  : int , total_spots  : int ):
        parking_lot_data.insert( parking_lot_name , address , pin_code , price , total_spots )
    
    def get_lot( self , id ):
        return parking_lot_data.get_by_id( id )
    
    def update_lot( self , parking_lot_id : int ,  parking_lot_name : str , address  : str , pin_code : int , price  : int , total_spots  : int ):
        parking_lot_data.get_by_id( parking_lot_id ).update_parking_lot( parking_lot_name , address , pin_code , price  , total_spots )
 
    def delete_spot( self , parking_lot_id : int , number : int ):
        parking_lot_data.update_totaL_spots( parking_lot_id )
        parking_spot_data.delete( parking_lot_id , number )
    
    def get_users( self ):
        data = user_data.get_users()
        users = []
        for i in data:
            d = dict()
            d['user_id'] = i.user_id 
            d['email_id'] = i.email
            d['full_name'] = i.name
            d['phone_number'] = i.phone
            d['gender'] = i.gender
            d['DOB'] = i.DOB
            users.append( d )
        return users
    
    def search( self , type , name ):
        result = dict()
        if ( type  == "user" ):
            result['type'] = type
            data , empty = user_data.get_user_by_name( name )
            users = []
            result['empty'] = empty
            if ( empty ):
                return result
            for i in data:
                d = dict()
                d['user_id'] = i.user_id
                d['email_id'] = i.email
                d['full_name'] = i.name
                d['phone_number'] = i.phone
                d['gender'] = i.gender
                users.append( d )
            result['users'] = users
        else:
            result['type'] = type
            empty = True
            if ( type  == 'parking_lot' ):
                data , empty = parking_lot_data.get_by_name( name )
            if ( type  == 'location' ):
                data , empty = parking_lot_data.get_by_location( name )
            result['empty'] = empty
            parking_lots = []
            if ( empty ):
                return result
            for i in data:
                d = dict()
                d['id'] = i.parking_lot_id
                d["name"] = i.parking_lot_name
                d['total'] = i.total_spots
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
                parking_lots.append( d )
            result['parking_lots'] = parking_lots
        return result
    
    def update( self , pd ): 
        self.d.update_profile( self.email , self.name , pd , self.DOB , self.gender )
       
    def occupied_spot_detail( self , parking_lot_id , spot_number ):
        user_id , vehicle_number , reserved_time = reservation.get_by_reservation_id( parking_spot_data.get_reservation_of_spot( parking_lot_id , spot_number ) )
        Released_time = datetime.now().replace( microsecond = 0 )
        reserved_time = datetime.strptime( reserved_time , '%Y-%m-%d %H:%M:%S' )
        time_difference = Released_time - reserved_time
        hours_difference = math.ceil(time_difference.total_seconds() / 3600)
        cost = int( parking_lot_data.get_price( parking_lot_id ) )*hours_difference
        cost = round( cost , 2 )
        return ( user_id , vehicle_number , reserved_time , cost )
    
    def diagram( self ):
        reservation.generate_monthly_revenue_bar_chart()
        reservation.generate_revenue_by_lot_pie_chart()
        self.booking_diagram()
    def booking_diagram( self ):
        data = parking_spot_data.parking_lot_spots_status()
        parking_lots = [parking_lot_data.get_parking_lot_name_by_id( id ) for id , a , o in data]
        not_booked = [a for id , a , o in data]
        booked = [o for id , a , o in data]
        fig1 , ax1 = plt.subplots()
        ax1.bar( range( len( parking_lots ) ) , booked , width = 0.5 , label = 'Booked' , color = 'skyblue' )
        ax1.bar( range( len( parking_lots ) ) , not_booked , width = 0.5 , bottom = booked , label = 'Not Booked' , color = 'lightcoral' )
        ax1.set_xticks( range( len( parking_lots ) ) )
        ax1.set_xticklabels( parking_lots )
        ax1.set_ylabel( 'Number of Spots' )
        ax1.legend()
        plt.tight_layout()
        bar_chart_path = os.path.join( 'static/images/booking_bar_chart.png' )
        fig1.savefig( bar_chart_path )
        plt.close( fig1 )
    def get_queries( self ):
        result = Queries.get_unsolved()
        data = list()
        for d in result:
            di = dict()
            di['id'] = d[-1]
            di['name'] = d[0]
            di['query'] = d[1]
            di['date'] = d[2].strftime( '%Y-%m-%d %H:%M' )
            di['status'] = d[3]
            di['reply'] = d[4]
            data.append( di )
        return data
    
    def query_resolved( self , id ):
        Queries.mark_as_resolved( id )
    
    def query_reply( self , id , reply ):
        Queries.reply_query( id , reply )