from flask import render_template , request , redirect , url_for , session , flash , g , Blueprint
from flask import current_app as app
from models.user import user_data
from models.parking_spot import parking_spot_data
from models.parking_lot import parking_lot_data
from .admin import admin
from .user import user
from models.reservation import reservation
from models import db
from datetime import datetime
from .proxies import current_user, current_admin
main_routes = Blueprint('main_routes', __name__)

@main_routes.route( '/' , methods = ['GET' , 'POST'] )
def IndexPage():
    if ( current_user.email != "" and current_user.email != None and current_user.email != " " ):
        session['user'] = current_user.email
        session['role'] = 'user'
    else:
        session.pop( 'user' , None )
        session.pop( 'role' , None )   
    return render_template( 'index.html' , user = current_user )

@main_routes.route( '/login' , methods = ['GET' , 'POST'] )  
def LoginPage(): 
    if ( request.method  == "POST" ):
        email = request.form.get( 'email' , "None" )
        pwd = request.form.get( 'password' , "None" )
        session['user'] = email
        if ( ( current_admin.email  == email ) and ( current_admin.check_login( pwd ) ) ):
            session['role'] = 'admin'
            return redirect( url_for( 'main_routes.AdminHomePage' ) )
        
        session['role'] = 'user'
        if ( user_data.verify_user( email , pwd ) ):
            global current_user 
            current_user.update_email( email )
            current_user.set_pre_data()
            return redirect( url_for( 'main_routes.IndexPage' ) )
        else:
            flash( "Invalid Email or Password" , 'danger' )
    return render_template( 'login.html' )

@main_routes.route( '/signup' , methods = ['GET' , 'POST'] )
def SignUpPage():
    if ( request.method  == "POST" ):
        email = request.form.get( 'email' , "None" )
        password = request.form.get( "password" , "None" )
        if ( password != request.form.get( "check_password" , "None" ) ):
            flash( "Password and confirm Password are not same" , "danger" )
            return render_template( 'signup.html' )
        if user_data.CheckEmail( email ):
            flash( "the current user email is already registered." , "danger" )
            return redirect( url_for( "main_routes.LoginPage" ) )
        else:
            user_data.insert( email , 
                    request.form.get( "full_name" , "None" ) , 
                    request.form.get( "phone_number" , "None" ) , 
                    request.form.get( "gender" , "Other" ) , 
                    request.form.get( "DOB" , "None" ) , 
                    request.form.get( "address" , "None" ) , 
                    request.form.get( "vehicle" , "None" ) , 
                    password )
            return redirect( url_for( "main_routes.LoginPage" ) )
    return render_template( 'signup.html' )

@main_routes.route('/user/home', methods=['GET', 'POST'])
def HomePage():
    if 'user' not in session:
        flash('You must be logged to view this page.', 'danger')
        return redirect(url_for('main_routes.IndexPage'))

    global current_user
    data = current_user.get_recent_parking_history()
    quick_book_data = current_user.get_quick_book_history()

    return render_template(
        'home.html',
        user=current_user,
        result=data,
        l=len(data),
        quick_book=quick_book_data
    )

@main_routes.route( '/user/book' , methods = ['GET' , 'POST'] )
def BookPage():
    if 'user' not in session:
        flash( 'You must be logged to view this page.' , 'danger' )
        return redirect( url_for( 'main_routes.IndexPage' ) )
    if ( request.method  == "POST" ):
        search_type = request.form.get( 'type' )
        name = request.form.get( 'query' )
        result = current_user.search( search_type , name )
        return render_template( 'book.html' , user = current_user ,  result = result , not_empty = True )
    return render_template( 'book.html' , user = current_user ,  result = "" , not_empty = False )

@main_routes.route( '/book_page' , methods = ['POST'] )
def BookingPage():
    if 'role' not in session or ( session['role'] != 'user' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    parking_lot_id = request.form.get( 'lot_id' )
    price = request.form.get( 'price' )
    s_id , n = parking_spot_data.get_free_spot( parking_lot_id )
    return render_template( 'book_page.html' , user = current_user , lot_id = parking_lot_id , number = n , s_id = s_id , price = price , vehicle = current_user.vechile_number )

@main_routes.route( '/user/summary' , methods = ['GET' , 'POST'] )
def SummaryPage():
    if 'user' not in session:
        flash( 'You must be logged to view this page.' , 'danger' )
        return redirect( url_for( 'main_routes.IndexPage' ) )
    current_user.summary()
    return render_template( 'summary.html' , user = current_user )

@main_routes.route( '/user/view-profile' , methods = ['GET' , 'POST'] )
def ViewProfile():
    if 'role' not in session or ( session['role'] != 'user' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    return render_template( 'view_profile.html' , user = current_user )

@main_routes.route( '/user/edit-profile' , methods = ['GET' , 'POST'] )
def EditProfile():
    if 'role' not in session or ( session['role'] != 'user' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    if ( request.method  == "POST" ):
        pwd = request.form.get( "password" )
        if (not current_user.check( pwd ) ):
            flash( "Wrong Password! Please try again" , "danger" )
        elif( request.form.get( "conform_password" , "NA" ) != request.form.get( "new_password" , "NA" ) ):
            flash( "New password and Confirm password didn't match" , "danger" )
        else:
                current_user.name = request.form.get( 'name' )
                current_user.email = request.form.get( 'email' )
                current_user.phone = request.form.get( 'phone' )
                current_user.address = request.form.get( 'address' )
                current_user.gender = request.form.get( 'gender' )
                current_user.DOB = request.form.get( 'DOB' )
                current_user.vechile_number = request.form.get( 'vehicle_number' )
                new_password = request.form.get( "new_password" )
                if ( len( new_password ) > 0 ):
                  current_user.update(new_password)
                else:
                    current_user.update()
                return redirect( url_for( 'main_routes.IndexPage' ) )
    return render_template( 'edit_profile.html' , user = current_user )

@main_routes.route( '/submit-query' , methods = ['GET' , 'POST'] )
def SubmitQuery():
    query = request.form['query']
    current_user.customer_care( query )
    return redirect( url_for( 'main_routes.ContactUsPage' ) )

@main_routes.route( '/contact_us' , methods = ['GET' , 'POST'] )
def ContactUsPage():
    if 'user' not in session:
        flash( 'You must be logged to view this page.' , 'danger' )
        return redirect( url_for( 'main_routes.IndexPage' ) )
    queries = current_user.all_queries()
    return render_template( 'contact_us.html' , user = current_user , queries = queries )

@main_routes.route( '/admin/home' , methods = ['GET' , 'POST'] )
def AdminHomePage():
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    return render_template( 'admin_home.html' , admin = current_admin , parking_lots = current_admin.show_parking_lots() )

@main_routes.route( '/admin/users' , methods = ['GET' , 'POST'] )
def AdminUserPage():
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    return render_template( 'admin_user.html' , admin = current_admin , users = current_admin.get_users() , n = len( current_admin.get_users() ) )

@main_routes.route( '/admin/search' , methods = ['GET' , 'POST'] )
def AdminSearchPage():
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    if ( request.method  == 'POST' ):
        search_type = request.form.get( 'type' )
        name = request.form.get( 'query' )
        result = current_admin.search( search_type , name )
    
        return render_template( 'admin_search.html' , admin = current_admin , result = result , not_empty = True )
    return render_template( 'admin_search.html' , admin = current_admin , result = "" , not_empty = False )

@main_routes.route( '/admin/summary' , methods = ['GET' , 'POST'] )
def AdminSummaryPage():
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    current_admin.diagram()
    return render_template( 'admin_summary.html' , admin = current_admin )

@main_routes.route( '/delete_lot/<int:lot_id>' , methods = ['POST'] )
def DeleteLot( lot_id ):
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    occupied = request.form.get( 'occupied' )
    global current_admin
    if ( int( occupied ) > 0 ):
        flash( "Lot can be Deleted if it has No occupied Spots" , "danger" )
    else:
        current_admin.delete_lot( lot_id )
    return redirect( url_for( 'main_routes.AdminHomePage' ) )

@main_routes.route( '/admin/edit-lot/<int:lot_id>' , methods = ['GET' , 'POST'] )
def AdminEditLot( lot_id ):
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    global current_admin
    data = current_admin.get_lot( lot_id )
    if ( request.method  == 'POST' ):
        parking_lot_name = request.form.get( "parking_lot_name" , "None" )
        address = request.form.get( "address" , "None" )
        pin_code = request.form.get( "pin_code" , 0 )
        price = request.form.get( "price" , 0 )
        total_spots = request.form.get( "maximum_spots" , 0 )
        
        current_admin.update_lot( lot_id , parking_lot_name , address , pin_code , price , total_spots )

        return redirect( url_for( 'main_routes.AdminHomePage' ) )
    return render_template( 'admin_edit_lot.html' , data = data , lot_id = lot_id , admin = current_admin )

@main_routes.route( '/admin/add-parking-lot' , methods = ['GET' , 'POST'] )
def AddParkingLot():
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    if request.method  == 'POST':
        parking_lot_name = request.form.get( "parking_lot_name" , "None" )
        address = request.form.get( "address" , "None" )
        pin_code = request.form.get( "pin_code" , 0 )
        price = request.form.get( "price" , 0 )
        total_spots = request.form.get( "maximum_spots" , 0 )
        
        current_admin.add_lot( parking_lot_name , address , pin_code , price , total_spots )
        
        return redirect( url_for( 'main_routes.AdminHomePage' ) )
    return render_template( 'admin_add_lot.html' , admin = current_admin )

@main_routes.route( '/admin/view-spot' , methods = ['POST'] )
def AdminViewSpot():
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    parking_lot_id = request.form.get( 'lot_id' )
    number = request.form.get( 'spot_number' )
    status = request.form.get( 'spot_status' )
    p = parking_lot_data.get_by_id(int(parking_lot_id))
    parking_lot_name = p.parking_lot_name
    return render_template( 'admin_spot_details.html', parking_lot_name = parking_lot_name , lot_id = parking_lot_id , number = number , status = status , admin = current_admin )

@main_routes.route( '/admin/delete-spot' , methods = ['POST'] )
def DeleteSpot():
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    parking_lot_id = request.form.get( 'lot_id' )
    number = request.form.get( 'spot_number' )
    status = request.form.get( 'status' )
    if ( status  == "Occupied" ):
        flash( "Spot is already Occupied. Can't Delete at present" , "danger" )
        return render_template( 'admin_spot_details.html' ,  lot_id = parking_lot_id , number = number , status = status , admin = current_admin )
    current_admin.delete_spot( parking_lot_id , number )
    return redirect( url_for( 'main_routes.AdminHomePage' ) )

@main_routes.route( '/reserve-spot' , methods = ['POST'] )
def ReserveSpot():
    if 'role' not in session or ( session['role'] != 'user' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    parking_lot_id = request.form.get( 'lot_id' )
    number = request.form.get( 'spot_number' )
    status = request.form.get( 'spot_status' )
    vehicle = request.form.get( 'vehicle_number' )
    reserve_time_str = request.form.get('reserve_time')

    if reserve_time_str:
        reserve_time = datetime.strptime(reserve_time_str, '%Y-%m-%dT%H:%M')
    else:
        reserve_time = datetime.now()
    current_user.book( parking_lot_id , number , current_user.user_id , status , vehicle , reserve_time)
    return redirect( url_for( 'main_routes.HomePage' ) )

@main_routes.route('/parkin', methods=['POST'])
def ParkIn():
    reservation_id = request.form.get('id')
    reserved_time = request.form.get('reserved_time')
    
    current_user.park_in(reservation_id)

    return redirect(url_for('main_routes.HomePage'))

@main_routes.route( '/Release' , methods = ['POST'] )
def Release():
    if 'role' not in session or ( session['role'] != 'user' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    flag = request.form.get( "flag" )
    reservation_id = request.form.get( 'id' )
    price = int( request.form.get( 'price' , "100" ) )
    Release_time = datetime.now().strftime( '%Y-%m-%d %H:%M:%S')
    reserved_time = request.form.get( 'reserved_time' )

    if ( flag  == "True" ):
        id = reservation_id
        current_user.Release( id , reserved_time , price )
        return redirect( url_for( "main_routes.HomePage" ) )
        
    r = reservation.get_spot_details_by_reseravtion( reservation_id )
    spot_id = r.parking_spot_id
    lot_id = r.parking_lot_id
    vn = r.vehicle_number
    return render_template( 'Release.html' , reservation_id = reservation_id , spot_id = spot_id , vehicle_number = vn , reserve_time = reserved_time , Release_time = Release_time , lot_id = lot_id , total_cost = price , user = current_user )

@main_routes.route( '/admin/occupied-spot-details' , methods = ['POST'] )
def AdminOccupiedSpotDetails():
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    parking_lot_id = request.form.get( 'lot_id' )
    spot_number = int( request.form.get( 'spot_number' ) )
    ( user_id , vehicle_number , reserved_time , cost ) = current_admin.occupied_spot_detail( parking_lot_id , spot_number )
    if (cost < 0):
      cost = 0
    p = parking_lot_data.get_by_id(int(parking_lot_id))
    parking_lot_name = p.parking_lot_name
    u = user_data.get_by_user_id(int(user_id))
    user_name = u.name
    return render_template( 'admin_occupied_spot_details.html',parking_lot_name = parking_lot_name , user_name = user_name , parking_lot_id = parking_lot_id , spot_number = spot_number , user_id = user_id , vehicle_number = vehicle_number , date_time = reserved_time , parking_cost = cost , admin = current_admin )

@main_routes.route( '/Logout' , methods = ['GET' , 'POST'] )
def Logout():
    if 'role' not in session or ( session['role'] != 'user' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    
    d = session.pop( 'user' , None )
    global current_user
    current_user.Logout()
    current_user = user()
    
    return redirect( url_for( 'main_routes.IndexPage' ) )

@main_routes.route( '/admin/view-profile' , methods = ['GET' , 'POST'] )
def AdminViewPage():
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    return render_template( 'admin_view_page.html' , user = current_admin , admin = current_admin )

@main_routes.route( '/admin/edit-profile' , methods = ['GET' , 'POST'] )
def AdminEditPage():
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    if ( request.method  == "POST" ):
        check_password = request.form.get( "password" )
        if not current_admin.check_login( check_password ):
            flash( "Wrong Password! Please try again" , "danger" )
        elif( request.form.get( "conform_password" , "NA" ) != request.form.get( "new_password" , "NA" ) ):
            flash( "New password and conform password didn't match" , "danger" )
        else:
                current_admin.name = request.form.get( 'name' )
                current_admin.email = request.form.get( 'email' )
                current_admin.gender = request.form.get( 'gender' )
                current_admin.DOB = request.form.get( 'DOB' )
                new_password = request.form.get( "new_password" )
               
                current_admin.update( new_password )
                return redirect( url_for( 'main_routes.AdminViewPage' ) )
    return render_template( 'admin_edit_page.html' , user = current_admin , admin = current_admin )

@main_routes.route( '/admin/query' , methods = ['GET' , 'POST'] )
def AdminQueryPage():
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    return render_template( 'admin_query.html' , admin = current_admin , queries = current_admin.get_queries() )

@main_routes.route( '/mark-resolved/<int:query_id>' , methods = ['GET' , 'POST'] )
def AdminQueryresolved( query_id ):
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    global current_admin
    current_admin.query_resolved( query_id )
    return redirect( url_for( 'main_routes.AdminQueryPage' ) )

@main_routes.route( '/reply/<int:query_id>' , methods = ['GET' , 'POST'] )
def AdminQueryReply( query_id ):
    if 'role' not in session or ( session['role'] != 'admin' ):
        return redirect( url_for( 'main_routes.IndexPage' ) )
    global current_admin
    reply = request.form.get( 'reply' , "None" )
    current_admin.query_reply( query_id , reply )
    return redirect( url_for( 'main_routes.AdminQueryPage' ) )
