import os
import pandas as pd
import json
from datetime import datetime

class DatabaseManager:
    """
    Simple database manager for Trinix Gaming Shop
    Uses CSV files to store customer and visit data
    """
    
    def __init__(self, data_dir="data"):
        """Initialize the database manager"""
        self.data_dir = data_dir
        self.customers_file = os.path.join(data_dir, "customers.csv")
        self.visits_file = os.path.join(data_dir, "visits.csv")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize dataframes
        self.customers_df = self._load_customers()
        self.visits_df = self._load_visits()
    
    def _load_customers(self):
        """Load customers from CSV file or create empty dataframe"""
        if os.path.exists(self.customers_file):
            # Load the dataframe
            df = pd.read_csv(self.customers_file)
            
            # Ensure ID column is integer
            if 'id' in df.columns:
                # First convert to float to handle any potential NaN values
                df['id'] = pd.to_numeric(df['id'], errors='coerce')
                # Then convert to integer, filling NaN with -1
                df['id'] = df['id'].fillna(-1).astype(int)
                
                # Print debug info
                print(f"Loaded {len(df)} customers with ID types: {df['id'].dtype}")
            
            # Ensure all text columns are stored as strings
            text_columns = ['name', 'phone', 'age_group', 'location', 'occupation', 
                           'qr_code_path', 'registration_date']
            
            for col in text_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str)
                    # Replace 'nan' strings with empty strings
                    df[col] = df[col].replace('nan', '')
            
            return df
        else:
            return pd.DataFrame(columns=[
                'id', 'name', 'phone', 'age_group', 'location', 'occupation', 
                'qr_code_path', 'registration_date'
            ])
    
    def _load_visits(self):
        """Load visits from CSV file or create empty dataframe"""
        if os.path.exists(self.visits_file):
            df = pd.read_csv(self.visits_file)
            # Add snacks_details column if it doesn't exist
            if 'snacks_details' not in df.columns:
                df['snacks_details'] = ""
            # Add points column if it doesn't exist
            if 'points' not in df.columns:
                # Calculate points based on payment amount
                df['points'] = df['payment_amount'].apply(self._calculate_points)
            return df
        else:
            return pd.DataFrame(columns=[
                'visit_id', 'customer_id', 'date', 'time', 'game_genre', 
                'console', 'payment_method', 'payment_amount', 
                'snacks_amount', 'snacks_details', 'referrals', 'points'
            ])
            
    def _calculate_points(self, payment_amount):
        """Calculate points based on payment amount"""
        try:
            # Convert payment_amount to float to ensure proper comparison
            amount = float(payment_amount)
            if amount <= 50:
                return 3
            elif amount <= 70:
                return 5
            elif amount <= 100:
                return 8
            elif amount <= 170:
                return 10
            elif amount <= 200:
                return 15
            else:
                return 20
        except (ValueError, TypeError):
            # If conversion fails, return default points
            print(f"Warning: Could not convert payment amount '{payment_amount}' to float. Using default points.")
            return 3
    
    def save_customers(self, df=None):
        """Save customers to CSV file
        
        Args:
            df: Optional dataframe to save. If None, saves self.customers_df
        """
        if df is not None:
            # Update the internal dataframe
            self.customers_df = df
        
        # Save to file
        self.customers_df.to_csv(self.customers_file, index=False)
    
    def save_visits(self):
        """Save visits to CSV file"""
        self.visits_df.to_csv(self.visits_file, index=False)
    
    def add_customer(self, name, phone, age_group, location, occupation, qr_code_path):
        """Add a new customer to the database"""
        # Find the next available ID
        if len(self.customers_df) > 0:
            # Get the maximum ID and add 1
            try:
                max_id = self.customers_df['id'].max()
                # Ensure it's an integer
                if pd.isna(max_id):
                    customer_id = 1
                else:
                    customer_id = int(max_id) + 1
            except Exception as e:
                print(f"Error determining next customer ID: {e}")
                # Fallback to length + 1
                customer_id = len(self.customers_df) + 1
        else:
            customer_id = 1
        
        # Ensure customer_id is an integer
        customer_id = int(customer_id)
        
        print(f"Adding new customer with ID: {customer_id}, type: {type(customer_id)}")
        
        new_customer = {
            'id': customer_id,
            'name': str(name),
            'phone': str(phone),  # Ensure phone is stored as string
            'age_group': str(age_group),
            'location': str(location),
            'occupation': str(occupation),
            'qr_code_path': str(qr_code_path),
            'registration_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.customers_df = pd.concat([self.customers_df, pd.DataFrame([new_customer])], ignore_index=True)
        
        # Ensure ID column is integer type after concat
        self.customers_df['id'] = self.customers_df['id'].astype(int)
        
        self.save_customers()
        
        return customer_id
    
    def update_customer(self, customer_id, **kwargs):
        """Update customer details"""
        try:
            # Try to convert to integer for consistent comparison
            customer_id_int = int(customer_id)
            customer_idx = self.customers_df[self.customers_df['id'] == customer_id_int].index
            
            if len(customer_idx) == 0:
                # If not found, try string comparison
                customer_id_str = str(customer_id)
                customer_idx = self.customers_df[self.customers_df['id'].astype(str) == customer_id_str].index
            
            if len(customer_idx) == 0:
                print(f"Customer with ID {customer_id} not found for update")
                return False
            
            for key, value in kwargs.items():
                if key in self.customers_df.columns:
                    # Ensure text values are stored as strings
                    if key in ['name', 'phone', 'age_group', 'location', 'occupation', 'qr_code_path']:
                        self.customers_df.at[customer_idx[0], key] = str(value)
                    else:
                        self.customers_df.at[customer_idx[0], key] = value
            
            self.save_customers()
            return True
        except Exception as e:
            print(f"Error updating customer with ID {customer_id}: {e}")
            return False
    
    def delete_customer(self, customer_id):
        """Delete a customer from the database"""
        try:
            # Try to convert to integer for consistent comparison
            customer_id_int = int(customer_id)
            customer_idx = self.customers_df[self.customers_df['id'] == customer_id_int].index
            
            if len(customer_idx) == 0:
                # If not found, try string comparison
                customer_id_str = str(customer_id)
                customer_idx = self.customers_df[self.customers_df['id'].astype(str) == customer_id_str].index
            
            if len(customer_idx) == 0:
                print(f"Customer with ID {customer_id} not found for deletion")
                return False
            
            self.customers_df = self.customers_df.drop(customer_idx)
            self.save_customers()
            return True
        except Exception as e:
            print(f"Error deleting customer with ID {customer_id}: {e}")
            return False
    
    def get_customer(self, customer_id):
        """Get customer details by ID"""
        try:
            # Try to convert to integer for consistent comparison
            customer_id_int = int(customer_id)
            customer = self.customers_df[self.customers_df['id'] == customer_id_int]
            
            if customer.empty:
                # If not found, try string comparison
                customer_id_str = str(customer_id)
                customer = self.customers_df[self.customers_df['id'].astype(str) == customer_id_str]
            
            if customer.empty:
                print(f"Customer with ID {customer_id} not found")
                return None
            
            return customer.iloc[0].to_dict()
        except Exception as e:
            print(f"Error getting customer with ID {customer_id}: {e}")
            # Try as string
            try:
                customer_id_str = str(customer_id)
                customer = self.customers_df[self.customers_df['id'].astype(str) == customer_id_str]
                
                if not customer.empty:
                    return customer.iloc[0].to_dict()
            except Exception as inner_e:
                print(f"Error in string fallback: {inner_e}")
            
            return None
    
    def add_visit(self, customer_id, game_genre, console, payment_method, 
                 payment_amount, snacks_amount, referrals, snacks_details=""):
        """
        Add a new visit to the database
        
        Note: The 'referrals' parameter is now used to store the 'friends_number' value
        but the database column name remains 'referrals' for backward compatibility
        """
        visit_id = len(self.visits_df) + 1
        
        # Calculate points based on payment amount
        points = self._calculate_points(payment_amount)
        
        new_visit = {
            'visit_id': visit_id,
            'customer_id': customer_id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'game_genre': game_genre,
            'console': console,
            'payment_method': payment_method,
            'payment_amount': payment_amount,
            'snacks_amount': snacks_amount,
            'snacks_details': snacks_details,
            'referrals': referrals,  # This stores the friends_number value
            'points': points  # Add points based on payment amount
        }
        
        self.visits_df = pd.concat([self.visits_df, pd.DataFrame([new_visit])], ignore_index=True)
        self.save_visits()
        
        return visit_id
    
    def get_visits_by_customer(self, customer_id):
        """Get all visits for a specific customer"""
        visits = self.visits_df[self.visits_df['customer_id'] == customer_id]
        
        # Ensure points column exists
        if 'points' not in visits.columns and not visits.empty:
            # Calculate points based on payment amount
            visits['points'] = visits['payment_amount'].apply(self._calculate_points)
            
        return visits
    
    def get_visits_by_date_range(self, start_date, end_date):
        """Get all visits within a date range"""
        # Convert date columns to string for safe comparison
        date_col = self.visits_df['date'].astype(str)
        
        # Filter by date range
        visits = self.visits_df[
            (date_col >= start_date) & 
            (date_col <= end_date)
        ]
        
        # Ensure points column exists
        if 'points' not in visits.columns and not visits.empty:
            # Calculate points based on payment amount
            visits['points'] = visits['payment_amount'].apply(self._calculate_points)
            
        return visits
    
    def get_sales_by_date_range(self, start_date, end_date):
        """Get sales data within a date range"""
        visits = self.get_visits_by_date_range(start_date, end_date)
        
        if visits.empty:
            return {
                'total_gaming': 0,
                'total_snacks': 0,
                'total_sales': 0,
                'daily_sales': {}
            }
        
        # Calculate totals
        total_gaming = visits['payment_amount'].sum()
        total_snacks = visits['snacks_amount'].sum()
        total_sales = total_gaming + total_snacks
        
        # Group by date
        daily_sales = visits.groupby('date').agg({
            'payment_amount': 'sum',
            'snacks_amount': 'sum',
            'visit_id': 'count'
        }).rename(columns={'visit_id': 'visit_count'})
        
        # Convert to dictionary
        daily_sales_dict = {}
        for date, row in daily_sales.iterrows():
            daily_sales_dict[date] = {
                'gaming': row['payment_amount'],
                'snacks': row['snacks_amount'],
                'total': row['payment_amount'] + row['snacks_amount'],
                'visits': row['visit_count']
            }
        
        return {
            'total_gaming': total_gaming,
            'total_snacks': total_snacks,
            'total_sales': total_sales,
            'daily_sales': daily_sales_dict
        }
    
    def get_customer_visit_frequency(self, customer_id):
        """Get visit frequency for a specific customer"""
        visits = self.get_visits_by_customer(customer_id)
        
        if visits.empty:
            return {
                'total_visits': 0,
                'first_visit': None,
                'last_visit': None,
                'frequency': 'N/A'
            }
        
        # Sort visits by date
        visits = visits.sort_values('date')
        
        # Calculate frequency
        first_visit = visits.iloc[0]['date']
        last_visit = visits.iloc[-1]['date']
        total_visits = len(visits)
        
        # Convert dates to datetime objects
        first_date = datetime.strptime(first_visit, '%Y-%m-%d')
        last_date = datetime.strptime(last_visit, '%Y-%m-%d')
        
        # Calculate days between first and last visit
        days_diff = (last_date - first_date).days
        
        if days_diff == 0:
            frequency = 'First Visit'
        elif days_diff <= 7:
            frequency = 'Weekly'
        elif days_diff <= 30:
            frequency = 'Monthly'
        else:
            frequency = 'Occasional'
        
        return {
            'total_visits': total_visits,
            'first_visit': first_visit,
            'last_visit': last_visit,
            'frequency': frequency
        }
    
    def get_shift_summary(self, date=None):
        """Get summary for the current shift (or specified date)"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        visits = self.visits_df[self.visits_df['date'] == date]
        
        if visits.empty:
            return {
                'date': date,
                'total_customers': 0,
                'total_gaming': 0,
                'total_snacks': 0,
                'total_sales': 0,
                'payment_methods': {},
                'consoles': {},
                'game_genres': {}
            }
        
        # Calculate totals
        total_customers = len(visits['customer_id'].unique())
        total_gaming = visits['payment_amount'].sum()
        total_snacks = visits['snacks_amount'].sum()
        total_sales = total_gaming + total_snacks
        
        # Payment methods breakdown
        payment_methods = visits.groupby('payment_method').agg({
            'payment_amount': 'sum',
            'visit_id': 'count'
        }).rename(columns={'visit_id': 'count'})
        
        payment_methods_dict = {}
        for method, row in payment_methods.iterrows():
            payment_methods_dict[method] = {
                'amount': row['payment_amount'],
                'count': row['count']
            }
        
        # Consoles breakdown
        consoles = visits.groupby('console').size().to_dict()
        
        # Game genres breakdown
        game_genres = visits.groupby('game_genre').size().to_dict()
        
        return {
            'date': date,
            'total_customers': total_customers,
            'total_gaming': total_gaming,
            'total_snacks': total_snacks,
            'total_sales': total_sales,
            'payment_methods': payment_methods_dict,
            'consoles': consoles,
            'game_genres': game_genres
        }