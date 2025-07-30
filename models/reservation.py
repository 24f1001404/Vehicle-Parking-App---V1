import matplotlib.pyplot as plt
from datetime import datetime , timedelta
from collections import defaultdict , Counter
import os
from sqlalchemy import func
from . import db
from models.parking_lot import parking_lot_data
OUTPUT_DIR = 'static/images'
os.makedirs( OUTPUT_DIR , exist_ok = True )

class reservation(db.Model):
    __tablename__ = 'reservations'

    reservation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.parking_lot_id'), nullable=False)
    parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.parking_spot_id'), nullable=False )
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    vehicle_number = db.Column(db.Text, nullable=False)
    reserved_time = db.Column(db.Text, nullable=False)
    Released_time = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def reserve( parking_lot_id, parking_spot_id, user_id, vehicle_number, reserved_time ):
        # If reserved_time is a string, convert to datetime object
        if isinstance(reserved_time, str):
            try:
                if 'T' in reserved_time:
                    reserved_time = datetime.strptime(reserved_time, '%Y-%m-%dT%H:%M')
                elif '.' in reserved_time:
                    reserved_time = datetime.strptime(reserved_time, '%Y-%m-%d %H:%M:%S.%f')
                else:
                    reserved_time = datetime.strptime(reserved_time, '%Y-%m-%d %H:%M:%S')
            except Exception:
                reserved_time = datetime.now()

        # Remove microseconds by formatting and re-parsing
        reserved_time = datetime.strptime(reserved_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

        d = reservation(
            parking_lot_id=parking_lot_id,
            parking_spot_id=parking_spot_id,
            user_id=user_id,
            vehicle_number=vehicle_number,
            reserved_time=reserved_time,
            Released_time="",
            amount=0.0
        )
        db.session.add(d)
        db.session.commit()

        return d.reservation_id if d.reservation_id else 0

    def Release( r_id , Released_time , amount ):
        r = reservation.query.filter_by( reservation_id = r_id ).first()

        r.Released_time = Released_time
        r.amount = amount
        db.session.commit()

    def get_by_reservation_id( reservation_id ):
        r = reservation.query.get( reservation_id )
        return r.user_id , r.vehicle_number , r.reserved_time

    def income_by_parking_lot():
        return db.session.query( reservation.parking_lot_id , func.sum( reservation.amount ) ).group_by( reservation.parking_lot_id ).all()

    def get_spot_details_by_reseravtion( reservation_id ):
        r = reservation.query.get( reservation_id )
        return r

    def get_user_parking_summary_data( user_id ):
        data = db.session.query( 
            reservation.reserved_time , 
            reservation.amount , 
            reservation.parking_lot_id
        ).filter_by( user_id = user_id ).all()

        return [
            {
                'reserved_time': row.reserved_time , 
                'amount': row.amount , 
                'parking_lot_id': row.parking_lot_id
            }
            for row in data
        ]

    def generate_parking_charts(user_id):
        raw_parking_data = reservation.get_user_parking_summary_data(user_id)

        monthly_amounts = defaultdict(float)
        monthly_bookings = defaultdict(int)
        lot_booking_counts = Counter()
        lot_ids_involved = set()

        today = datetime.now()
        past_six_months = []
        for i in range(6):
            month_dt = today - timedelta(days=30 * i)
            past_six_months.append(month_dt.strftime('%B %Y'))
        past_six_months.reverse()

        for month_year_key in past_six_months:
            monthly_amounts[month_year_key] = 0.0
            monthly_bookings[month_year_key] = 0

        for entry in raw_parking_data:
            try:
                reserved_dt = datetime.strptime(entry['reserved_time'], '%Y-%m-%d %H:%M:%S')
                month_year_key = reserved_dt.strftime('%B %Y')

                if month_year_key in past_six_months:
                    monthly_amounts[month_year_key] += entry['amount']
                    monthly_bookings[month_year_key] += 1
                lot_booking_counts[entry['parking_lot_id']] += 1
                lot_ids_involved.add(entry['parking_lot_id'])
            except ValueError as e:
                continue

        lot_names_map = {}
        if lot_ids_involved:
            parking_lots = db.session.query(
                parking_lot_data.parking_lot_id,
                parking_lot_data.parking_lot_name
            ).filter(parking_lot_data.parking_lot_id.in_(list(lot_ids_involved))).all()
            lot_names_map = {lot.parking_lot_id: lot.parking_lot_name for lot in parking_lots}

        amounts = [monthly_amounts[month] for month in past_six_months]
        bookings = [monthly_bookings[month] for month in past_six_months]

        plt.rcParams.update({'font.size': 12})

        plt.figure(figsize=(12, 7))
        plt.bar(past_six_months, amounts, color='skyblue')
        plt.xlabel('Month', fontsize=14)
        plt.ylabel('Amount Spent (₹)', fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.yticks(fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        monthly_amount_img_path = os.path.join(OUTPUT_DIR, f'monthly_amount_user.png')
        plt.savefig(monthly_amount_img_path)
        plt.close()

        plt.figure(figsize=(12, 7))
        plt.bar(past_six_months, bookings, color='lightcoral')
        plt.xlabel('Month', fontsize=14)
        plt.ylabel('Number of Bookings', fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.yticks(fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        monthly_bookings_img_path = os.path.join(OUTPUT_DIR, f'monthly_bookings_user.png')
        plt.savefig(monthly_bookings_img_path)
        plt.close()

        if lot_booking_counts:
            lot_labels = [lot_names_map.get(lot_id, f'Unknown Lot (ID: {lot_id})') for lot_id in lot_booking_counts.keys()]
            lot_sizes = list(lot_booking_counts.values())

            plt.figure(figsize=(9, 9))
            plt.pie(lot_sizes, labels=lot_labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors, textprops={'fontsize': 11})
            plt.axis('equal')
            plt.tight_layout()
            lot_distribution_img_path = os.path.join(OUTPUT_DIR, f'lot_distribution_user.png')
            plt.savefig(lot_distribution_img_path)
            plt.close()
        else:
            plt.figure(figsize=(9, 9))
            plt.text(0.5, 0.5, 'No Booking Data Available',
                    ha='center',
                    va='center',
                    fontsize=20,
                    color='gray')
            plt.axis('off')
            lot_distribution_img_path = os.path.join(OUTPUT_DIR, f'lot_distribution_user.png')
            plt.savefig(lot_distribution_img_path, bbox_inches='tight')
            plt.close()

    def generate_revenue_by_lot_pie_chart():
        all_lots = parking_lot_data.query.all()
        
        lot_name_map = {lot.parking_lot_id: lot.parking_lot_name for lot in all_lots}
        
        reservations = reservation.query.all()
        lot_revenue = defaultdict(float)
        current_year = datetime.now().year
        DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

        for res in reservations:
            try:
                res_date = datetime.datetime.strptime(res.reserved_time, DATE_FORMAT)
                if res_date.year == current_year:
                    lot_revenue[res.parking_lot_id] += res.amount
            except (ValueError, IndexError):
                continue

        if not lot_revenue:
            plt.figure(figsize=(8, 8))
            plt.text(0.5, 0.5, 'No Revenue Data Available',
                    ha='center',  
                    va='center',  
                    fontsize=20,
                    color='gray')
            plt.axis('off') 
            
            
            filepath = os.path.join(OUTPUT_DIR, 'revenue_by_lot_pie.png')
            plt.savefig(filepath, bbox_inches='tight')
            plt.close()
            return f'images/revenue_by_lot_pie.png'

        total_revenue = sum(lot_revenue.values())
        
        labels = [lot_name_map.get(id, f'Lot ID: {id}') for id in lot_revenue.keys()]
        sizes = list(lot_revenue.values())

        def make_autopct(values):
            def my_autopct(pct):
                total = sum(values)
                val = int(round(pct * total / 100.0))
                return f'{pct:.1f}%\n(₹{val:,.0f})'
            return my_autopct

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, autopct=make_autopct(sizes), startangle=140,
                wedgeprops={"edgecolor": "white", 'linewidth': 1})
        
        plt.axis('equal')
        
        filepath = os.path.join(OUTPUT_DIR, 'revenue_by_lot_pie.png')
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()
        return f'images/revenue_by_lot_pie.png'
  
    def generate_monthly_revenue_bar_chart():
        reservations = reservation.query.all()
        monthly_revenue = defaultdict( float )
        DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
        for res in reservations:
            try:
                res_date = datetime.strptime( res.reserved_time , DATE_FORMAT )
                month_key = res_date.strftime( '%Y-%m' )
                monthly_revenue[month_key] += res.amount
            except ( ValueError , IndexError ):
                continue

        today = datetime.now()
        month_keys = []
        current_date = today
        for _ in range( 6 ):
            month_keys.append( current_date.strftime( '%Y-%m' ) )
            current_date = current_date.replace( day = 1 ) - timedelta( days = 1 )

        month_keys.reverse()

        labels = [datetime.strptime( m , '%Y-%m' ).strftime( '%b %Y' ) for m in month_keys]
        revenues = [monthly_revenue.get( m , 0.0 ) for m in month_keys]

        plt.figure( figsize = ( 10 , 6 ) )
        bars = plt.bar( labels , revenues , color = 'c' )
        
        plt.ylabel( 'Total Revenue ( ₹ )' )
        plt.xlabel( 'Month' )
        plt.xticks( fontsize = 'medium' )

        for bar in bars:
            yval = bar.get_height()
            plt.text( bar.get_x() + bar.get_width()/2.0 , yval , f'₹{yval:,.0f}' ,
                    va = 'bottom' , ha = 'center' , fontsize = 10 )

        plt.tight_layout()
        filepath = os.path.join( OUTPUT_DIR , 'monthly_revenue_bar.png' )
        plt.savefig( filepath )
        plt.close()
