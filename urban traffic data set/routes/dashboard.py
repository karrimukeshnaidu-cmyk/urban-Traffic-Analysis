from flask import Blueprint, render_template, request
import pandas as pd
from models.db import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def home():
    selected_day = request.args.get('day')
    selected_location = request.args.get('location')

    # Safe SQL query building
    filter_query = "WHERE 1=1"
    params = []

    if selected_day:
        filter_query += " AND day = %s"
        params.append(selected_day)

    if selected_location:
        try:
            # location in DB is INT, convert safely
            filter_query += " AND location = %s"
            params.append(int(selected_location))
        except ValueError:
            pass # Ignore invalid location value

    # Open connection
    conn = get_db_connection()
    try:
        # 1. Traffic by Hour
        df_hour = pd.read_sql(f"""
            SELECT hour, AVG(vehicle_count) as avg_traffic
            FROM traffic_data
            {filter_query}
            GROUP BY hour ORDER BY hour
        """, conn, params=params)

        # 2. Traffic by Day
        df_day = pd.read_sql(f"""
            SELECT day, AVG(vehicle_count) as avg_traffic
            FROM traffic_data
            {filter_query}
            GROUP BY day
        """, conn, params=params)

        # 3. Traffic by Location
        df_loc = pd.read_sql(f"""
            SELECT location, AVG(vehicle_count) as avg_traffic
            FROM traffic_data
            {filter_query}
            GROUP BY location
        """, conn, params=params)

        # 4. Peak vs Non-Peak
        df_peak = pd.read_sql(f"""
            SELECT 
            CASE 
                WHEN hour BETWEEN 8 AND 11 OR hour BETWEEN 17 AND 20 
                THEN 'Peak'
                ELSE 'Non-Peak'
            END as traffic_type,
            AVG(vehicle_count) as avg_traffic
            FROM traffic_data
            {filter_query}
            GROUP BY traffic_type
        """, conn, params=params)

        # 5. Top 5 Locations
        df_top = pd.read_sql(f"""
            SELECT location, AVG(vehicle_count) as traffic
            FROM traffic_data
            {filter_query}
            GROUP BY location
            ORDER BY traffic DESC
            LIMIT 5
        """, conn, params=params)

        # 6. Trend
        df_trend = pd.read_sql(f"""
            SELECT DATE(timestamp) as date, AVG(vehicle_count) as traffic
            FROM traffic_data
            {filter_query}
            GROUP BY date
            ORDER BY date
        """, conn, params=params)

        # 7. Weekday vs Weekend
        df_week = pd.read_sql(f"""
            SELECT 
            CASE 
                WHEN day IN ('Saturday','Sunday') THEN 'Weekend'
                ELSE 'Weekday'
            END as day_type,
            AVG(vehicle_count) as traffic
            FROM traffic_data
            {filter_query}
            GROUP BY day_type
        """, conn, params=params)

        # KPIs
        total_traffic = int(df_hour['avg_traffic'].sum()) if not df_hour.empty else 0
        peak_hour = int(df_hour.loc[df_hour['avg_traffic'].idxmax()]['hour']) if not df_hour.empty else 0
        busy_location = str(df_loc.loc[df_loc['avg_traffic'].idxmax()]['location']) if not df_loc.empty else "N/A"

        # FILTER DROPDOWN DATA (No parameters needed here as these are static listings)
        all_days = pd.read_sql("SELECT DISTINCT day FROM traffic_data", conn)
        
        # Sort days nicely: Monday, Tuesday...
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        all_days['day'] = pd.Categorical(all_days['day'], categories=day_order, ordered=True)
        all_days = all_days.sort_values('day')

        all_locations = pd.read_sql("SELECT DISTINCT location FROM traffic_data ORDER BY location", conn)

    finally:
        # Crucial to close the connection to return it to the pool
        conn.close()

    return render_template("index.html",
        hours=list(df_hour['hour']) if not df_hour.empty else [], 
        hour_values=list(df_hour['avg_traffic']) if not df_hour.empty else [],
        days=list(df_day['day']) if not df_day.empty else [], 
        day_values=list(df_day['avg_traffic']) if not df_day.empty else [],
        locations=list(df_loc['location']) if not df_loc.empty else [], 
        loc_values=list(df_loc['avg_traffic']) if not df_loc.empty else [],

        peak_labels=list(df_peak['traffic_type']) if not df_peak.empty else [], 
        peak_values=list(df_peak['avg_traffic']) if not df_peak.empty else [],
        top_locations=list(df_top['location']) if not df_top.empty else [], 
        top_values=list(df_top['traffic']) if not df_top.empty else [],
        trend_dates=list(df_trend['date'].astype(str)) if not df_trend.empty else [], 
        trend_values=list(df_trend['traffic']) if not df_trend.empty else [],
        week_labels=list(df_week['day_type']) if not df_week.empty else [], 
        week_values=list(df_week['traffic']) if not df_week.empty else [],

        total_traffic=total_traffic,
        peak_hour=peak_hour,
        busy_location=busy_location,

        all_days=list(all_days['day']),
        all_locations=list(all_locations['location']),
        
        # Keep selected filter values in template for sticky state
        selected_day=selected_day or "",
        selected_location=selected_location or ""
    )
