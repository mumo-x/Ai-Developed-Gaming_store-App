import sys
import os
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, 
                            QRadioButton, QButtonGroup, QTableWidget, QTableWidgetItem, 
                            QFileDialog, QMessageBox, QGroupBox, QFormLayout, QSpinBox,
                            QDateEdit, QCheckBox, QSplitter, QFrame, QStackedWidget)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont, QPainter, QColor
from PyQt5.QtCore import Qt, QTimer, QDate, QSize, QBuffer, pyqtSignal, QThread
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

# Import custom modules
from database_manager import DatabaseManager
from qr_utils import QRCodeManager
from rt_generator import ReportGenerator

# Define the main application class
class PSGamingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PS Gamers Management")
        self.setMinimumSize(1200, 800)
        
        # Create status bar for user feedback
        self.statusBar().showMessage("Welcome to PS Gamers Management", 5000)
        
        # Set application icon
        # Try to find the PS Gamers logo in various locations
        logo_paths = ["PS Gamers.png", "ps_gamers.png", "logo.png"]
        logo_found = False
        
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                self.setWindowIcon(QIcon(logo_path))
                self.logo_path = logo_path
                logo_found = True
                break
        
        if not logo_found:
            # Create a simple icon if logo not found
            self.logo_path = None
            self.setWindowIcon(QIcon())
        
        # Initialize camera variables
        self.camera = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera)
        
        # Initialize database
        self.initialize_database()
        
        # Setup UI
        self.setup_ui()
    
    def initialize_database(self):
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Get dataframes from database manager
        self.customers_df = self.db_manager.customers_df
        self.visits_df = self.db_manager.visits_df
        
        # Initialize QR code manager
        self.qr_manager = QRCodeManager(logo_path=self.logo_path)
        
        # Initialize report generator
        self.report_generator = ReportGenerator(logo_path=self.logo_path)
        
        # Create necessary directories
        os.makedirs('qr_codes', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
    
    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create header with logo
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        
        if self.logo_path and os.path.exists(self.logo_path):
            logo_pixmap = QPixmap(self.logo_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            # Create a text label if logo not found
            logo_label.setText("PS")
            logo_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #6a1b9a;")
            
        header_layout.addWidget(logo_label)
        
        title_label = QLabel("PS GAMING")
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #6a1b9a;")
        header_layout.addWidget(title_label, 1)
        
        main_layout.addLayout(header_layout)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #6a1b9a;
                background-color: #f5f5f5;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #9575cd;
                color: white;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #6a1b9a;
                font-weight: bold;
            }
        """)
        
        # Create tabs
        self.create_checkin_tab()
        self.create_customer_management_tab()
        self.create_visits_tab()
        self.create_analytics_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Set dark theme styling
        self.set_gaming_style()
    
    def set_gaming_style(self):
        # Set a gaming-themed style for the application
        self.setStyleSheet("""
            QMainWindow {
                background-color: #212121;
                color: #ffffff;
            }
            QWidget {
                background-color: #212121;
                color: #ffffff;
            }
            QPushButton {
                background-color: #6a1b9a;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #9c27b0;
            }
            QPushButton:pressed {
                background-color: #4a148c;
            }
            QLineEdit, QComboBox, QSpinBox, QDateEdit {
                background-color: #424242;
                color: white;
                border: 1px solid #6a1b9a;
                border-radius: 3px;
                padding: 5px;
            }
            QTableWidget {
                background-color: #424242;
                color: white;
                gridline-color: #6a1b9a;
                border: 1px solid #6a1b9a;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #6a1b9a;
                color: white;
                padding: 5px;
                border: 1px solid #4a148c;
            }
            QLabel {
                color: white;
            }
            QGroupBox {
                border: 1px solid #6a1b9a;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                color: #bb86fc;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
    
    def create_checkin_tab(self):
        checkin_tab = QWidget()
        checkin_layout = QVBoxLayout(checkin_tab)
        
        # Create stacked widget for check-in and register pages
        self.checkin_stacked = QStackedWidget()
        
        # Create check-in page
        checkin_page = QWidget()
        checkin_page_layout = QVBoxLayout(checkin_page)
        
        # QR Scanner section
        scanner_group = QGroupBox("QR Code Scanner")
        scanner_layout = QVBoxLayout()
        
        self.camera_label = QLabel("Camera feed will appear here")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumHeight(300)
        self.camera_label.setStyleSheet("border: 2px dashed #6a1b9a; padding: 10px;")
        scanner_layout.addWidget(self.camera_label)
        
        camera_button_layout = QHBoxLayout()
        self.scan_button = QPushButton("Scan QR Code")
        self.scan_button.setIcon(QIcon("qr_icon.png"))
        self.scan_button.clicked.connect(self.start_camera)
        camera_button_layout.addWidget(self.scan_button)
        
        self.stop_scan_button = QPushButton("Stop Scanning")
        self.stop_scan_button.setEnabled(False)
        # Connect with explicit lambda to ensure proper connection
        self.stop_scan_button.clicked.connect(lambda: self.stop_camera())
        # Set a distinctive style for the stop button
        self.stop_scan_button.setStyleSheet("background-color: #d32f2f; color: white;")
        camera_button_layout.addWidget(self.stop_scan_button)
        
        scanner_layout.addLayout(camera_button_layout)
        scanner_group.setLayout(scanner_layout)
        checkin_page_layout.addWidget(scanner_group)
        
        # Customer details form after scanning
        details_group = QGroupBox("Visit Details")
        details_layout = QFormLayout()
        
        # Game Genre
        self.game_genre_combo = QComboBox()
        self.game_genre_combo.addItems(["Racing", "Shooting", "Action/Adventure", "Football", "Sports", "Horror", "Other"])
        details_layout.addRow("Game Genre:", self.game_genre_combo)
        
        # Console
        self.console_combo = QComboBox()
        self.console_combo.addItems(["PS4", "PS5"])
        details_layout.addRow("Console:", self.console_combo)
        
        # Payment Method
        payment_layout = QHBoxLayout()
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["Cash", "Mobile Money (MPESA)", "Card", "Transfer"])
        self.payment_amount = QLineEdit()
        self.payment_amount.setPlaceholderText("Amount")
        payment_layout.addWidget(self.payment_method_combo)
        payment_layout.addWidget(self.payment_amount)
        details_layout.addRow("Game Payment:", payment_layout)
        
        # Snack Amount with details
        snacks_layout = QHBoxLayout()
        self.snacks_amount = QLineEdit()
        self.snacks_amount.setPlaceholderText("Amount")
        self.snacks_details = QLineEdit()
        self.snacks_details.setPlaceholderText("Snack details (e.g., Soda, Chips)")
        snacks_layout.addWidget(self.snacks_amount)
        snacks_layout.addWidget(self.snacks_details)
        details_layout.addRow("Snack Amount:", snacks_layout)
        
        # Friends Number (formerly Referrals)
        self.referrals = QSpinBox()
        self.referrals.setRange(0, 20)
        details_layout.addRow("Friends Number:", self.referrals)
        
        # Customer info display with manual entry option
        customer_layout = QVBoxLayout()
        
        # QR code customer info display
        self.customer_info_label = QLabel("Scan a QR code to see customer details")
        self.customer_info_label.setStyleSheet("font-weight: bold; color: #bb86fc;")
        customer_layout.addWidget(self.customer_info_label)
        
        # Manual customer entry option
        manual_customer_layout = QHBoxLayout()
        self.manual_customer_checkbox = QCheckBox("Manual Entry")
        self.manual_customer_checkbox.toggled.connect(self.toggle_manual_customer)
        manual_customer_layout.addWidget(self.manual_customer_checkbox)
        
        self.manual_customer_name = QLineEdit()
        self.manual_customer_name.setPlaceholderText("Customer Name or Phone")
        self.manual_customer_name.setEnabled(False)  # Disabled by default
        manual_customer_layout.addWidget(self.manual_customer_name)
        
        self.manual_customer_phone = QLineEdit()
        self.manual_customer_phone.setPlaceholderText("Phone Number (optional)")
        self.manual_customer_phone.setEnabled(False)  # Disabled by default
        manual_customer_layout.addWidget(self.manual_customer_phone)
        
        # Add search button
        self.search_customer_button = QPushButton("Search")
        self.search_customer_button.clicked.connect(self.search_customer)
        self.search_customer_button.setEnabled(False)  # Disabled by default
        manual_customer_layout.addWidget(self.search_customer_button)
        
        customer_layout.addLayout(manual_customer_layout)
        details_layout.addRow("Customer:", customer_layout)
        
        details_group.setLayout(details_layout)
        checkin_page_layout.addWidget(details_group)
        
        # Submit button
        self.submit_checkin_button = QPushButton("Submit Check-in")
        self.submit_checkin_button.clicked.connect(self.submit_checkin)
        checkin_page_layout.addWidget(self.submit_checkin_button)
        
        # Register new customer button
        self.register_button = QPushButton("Register New Customer")
        self.register_button.clicked.connect(lambda: self.checkin_stacked.setCurrentIndex(1))
        checkin_page_layout.addWidget(self.register_button)
        
        # Add check-in page to stacked widget
        self.checkin_stacked.addWidget(checkin_page)
        
        # Create register page
        register_page = QWidget()
        register_layout = QVBoxLayout(register_page)
        
        register_form_group = QGroupBox("Customer Registration")
        register_form_layout = QFormLayout()
        
        # Name
        self.reg_name = QLineEdit()
        register_form_layout.addRow("Name:", self.reg_name)
        
        # Phone number
        self.reg_phone = QLineEdit()
        self.reg_phone.setPlaceholderText("10-digit phone number")
        self.reg_phone.textChanged.connect(self.validate_phone)
        register_form_layout.addRow("Phone Number:", self.reg_phone)
        
        # Age Group
        self.reg_age_group = QComboBox()
        age_groups = ["5-10 years", "11-15 years", "16-20 years", "21-25 years", 
                      "26-30 years", "31-35 years", "36-40 years"]
        self.reg_age_group.addItems(age_groups)
        register_form_layout.addRow("Age Group:", self.reg_age_group)
        
        # Location
        self.reg_location = QLineEdit()
        register_form_layout.addRow("Location:", self.reg_location)
        
        # Occupation
        self.reg_occupation = QComboBox()
        self.reg_occupation.addItems(["Student", "Professional"])
        register_form_layout.addRow("Occupation:", self.reg_occupation)
        
        register_form_group.setLayout(register_form_layout)
        register_layout.addWidget(register_form_group)
        
        # QR Code preview
        qr_preview_group = QGroupBox("QR Code Preview")
        qr_preview_layout = QVBoxLayout()
        
        self.qr_preview_label = QLabel("QR code will be generated after submission")
        self.qr_preview_label.setAlignment(Qt.AlignCenter)
        self.qr_preview_label.setMinimumHeight(200)
        self.qr_preview_label.setStyleSheet("border: 2px dashed #6a1b9a; padding: 10px;")
        qr_preview_layout.addWidget(self.qr_preview_label)
        
        qr_preview_group.setLayout(qr_preview_layout)
        register_layout.addWidget(qr_preview_group)
        
        # Register buttons
        register_buttons_layout = QHBoxLayout()
        
        self.submit_registration_button = QPushButton("Register Customer")
        self.submit_registration_button.clicked.connect(self.register_customer)
        register_buttons_layout.addWidget(self.submit_registration_button)
        
        self.back_to_checkin_button = QPushButton("Back to Check-in")
        self.back_to_checkin_button.clicked.connect(lambda: self.checkin_stacked.setCurrentIndex(0))
        register_buttons_layout.addWidget(self.back_to_checkin_button)
        
        register_layout.addLayout(register_buttons_layout)
        
        # Add register page to stacked widget
        self.checkin_stacked.addWidget(register_page)
        
        # Add stacked widget to tab
        checkin_layout.addWidget(self.checkin_stacked)
        
        # Add tab to tab widget
        self.tabs.addTab(checkin_tab, "Check-in / Register")
        
        # Initialize camera variables
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.current_customer_id = None
    
    def create_customer_management_tab(self):
        customer_tab = QWidget()
        customer_layout = QVBoxLayout(customer_tab)
        
        # Search and filter section
        search_group = QGroupBox("Search and Filter")
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, phone, or location...")
        self.search_input.textChanged.connect(self.filter_customers)
        search_layout.addWidget(self.search_input, 3)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Student", "Professional", "Age Group"])
        self.filter_combo.currentTextChanged.connect(self.filter_customers)
        search_layout.addWidget(self.filter_combo, 1)
        
        search_group.setLayout(search_layout)
        customer_layout.addWidget(search_group)
        
        # Customer table
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(7)
        self.customer_table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone", "Age Group", "Location", "Occupation", "Registration Date"
        ])
        self.customer_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customer_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.customer_table.cellClicked.connect(self.select_customer)
        customer_layout.addWidget(self.customer_table)
        
        # Customer actions
        actions_layout = QHBoxLayout()
        
        self.view_qr_button = QPushButton("View QR Code")
        self.view_qr_button.clicked.connect(self.view_customer_qr)
        self.view_qr_button.setEnabled(False)  # Disabled until a customer is selected
        actions_layout.addWidget(self.view_qr_button)
        
        self.regenerate_qr_button = QPushButton("Regenerate QR Code")
        self.regenerate_qr_button.clicked.connect(self.regenerate_qr)
        self.regenerate_qr_button.setEnabled(False)  # Disabled until a customer is selected
        actions_layout.addWidget(self.regenerate_qr_button)
        
        self.edit_customer_button = QPushButton("Edit Customer")
        self.edit_customer_button.clicked.connect(self.edit_customer)
        self.edit_customer_button.setEnabled(False)  # Disabled until a customer is selected
        actions_layout.addWidget(self.edit_customer_button)
        
        self.delete_customer_button = QPushButton("Delete Customer")
        self.delete_customer_button.clicked.connect(self.delete_customer)
        self.delete_customer_button.setEnabled(False)  # Disabled until a customer is selected
        actions_layout.addWidget(self.delete_customer_button)
        
        customer_layout.addLayout(actions_layout)
        
        # Add tab to tab widget
        self.tabs.addTab(customer_tab, "Customer Management")
        
        # Load initial customer data
        self.load_customers()
    
    def create_analytics_tab(self):
        analytics_tab = QWidget()
        analytics_layout = QVBoxLayout(analytics_tab)
        
        # Date range filter
        date_filter_group = QGroupBox("Date Range")
        date_filter_layout = QHBoxLayout()
        
        date_filter_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.from_date.setCalendarPopup(True)
        date_filter_layout.addWidget(self.from_date)
        
        date_filter_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        date_filter_layout.addWidget(self.to_date)
        
        self.apply_date_filter_button = QPushButton("Apply Filter")
        self.apply_date_filter_button.clicked.connect(self.update_analytics)
        date_filter_layout.addWidget(self.apply_date_filter_button)
        
        date_filter_group.setLayout(date_filter_layout)
        analytics_layout.addWidget(date_filter_group)
        
        # Charts section
        charts_layout = QHBoxLayout()
        
        # Sales chart
        sales_chart_group = QGroupBox("Sales Analysis")
        sales_chart_layout = QVBoxLayout()
        
        self.sales_chart_label = QLabel("Sales chart will appear here")
        self.sales_chart_label.setAlignment(Qt.AlignCenter)
        self.sales_chart_label.setMinimumHeight(300)
        self.sales_chart_label.setStyleSheet("border: 2px dashed #6a1b9a; padding: 10px; color: white;")
        sales_chart_layout.addWidget(self.sales_chart_label)
        
        sales_chart_group.setLayout(sales_chart_layout)
        charts_layout.addWidget(sales_chart_group)
        
        # Customer visits chart
        visits_chart_group = QGroupBox("Customer Visits")
        visits_chart_layout = QVBoxLayout()
        
        self.visits_chart_label = QLabel("Visits chart will appear here")
        self.visits_chart_label.setAlignment(Qt.AlignCenter)
        self.visits_chart_label.setMinimumHeight(300)
        self.visits_chart_label.setStyleSheet("border: 2px dashed #6a1b9a; padding: 10px; color: white;")
        visits_chart_layout.addWidget(self.visits_chart_label)
        
        visits_chart_group.setLayout(visits_chart_layout)
        charts_layout.addWidget(visits_chart_group)
        
        analytics_layout.addLayout(charts_layout)
        
        # Sales summary card
        summary_card_group = QGroupBox("Sales Summary")
        summary_card_layout = QHBoxLayout()
        
        # Game sales summary
        self.game_sales_sum_label = QLabel("Game Sales: KES 0.00")
        self.game_sales_sum_label.setStyleSheet("font-weight: bold; color: white; font-size: 14px;")
        summary_card_layout.addWidget(self.game_sales_sum_label)
        
        # Snacks sales summary
        self.snacks_sales_sum_label = QLabel("Snack Sales: KES 0.00")
        self.snacks_sales_sum_label.setStyleSheet("font-weight: bold; color: white; font-size: 14px;")
        summary_card_layout.addWidget(self.snacks_sales_sum_label)
        
        # Number of customers
        self.customer_count_label = QLabel("Customers: 0")
        self.customer_count_label.setStyleSheet("font-weight: bold; color: white; font-size: 14px;")
        summary_card_layout.addWidget(self.customer_count_label)
        
        summary_card_group.setLayout(summary_card_layout)
        analytics_layout.addWidget(summary_card_group)
        
        # Export and report section
        export_group = QGroupBox("Reports and Exports")
        export_layout = QHBoxLayout()
        
        self.export_excel_button = QPushButton("Export Data")
        self.export_excel_button.clicked.connect(self.export_to_excel)
        self.export_excel_button.setStyleSheet("background-color: #2e7d32; color: white;")  # Make it stand out
        self.export_excel_button.setToolTip("Export data to CSV files that can be opened in Excel")
        export_layout.addWidget(self.export_excel_button)
        
        self.generate_shift_report_button = QPushButton("Generate End of Shift Report")
        self.generate_shift_report_button.clicked.connect(self.generate_shift_report)
        export_layout.addWidget(self.generate_shift_report_button)
        
        export_group.setLayout(export_layout)
        analytics_layout.addWidget(export_group)
        
        # Add tab to tab widget
        self.tabs.addTab(analytics_tab, "Analytics")
        
        # Initialize analytics data
        self.update_analytics()
    
    def create_visits_tab(self):
        """Create a tab to display visit information (read-only)"""
        visits_tab = QWidget()
        visits_layout = QVBoxLayout(visits_tab)
        
        # Date filter section
        filter_group = QGroupBox("Filter Visits")
        filter_layout = QHBoxLayout()
        
        # Date range selection
        filter_layout.addWidget(QLabel("From:"))
        self.visits_from_date = QDateEdit()
        self.visits_from_date.setCalendarPopup(True)
        self.visits_from_date.setDate(QDate.currentDate().addDays(-30))  # Default to last 30 days
        filter_layout.addWidget(self.visits_from_date)
        
        filter_layout.addWidget(QLabel("To:"))
        self.visits_to_date = QDateEdit()
        self.visits_to_date.setCalendarPopup(True)
        self.visits_to_date.setDate(QDate.currentDate())  # Default to today
        filter_layout.addWidget(self.visits_to_date)
        
        # Apply filter button
        self.apply_visits_filter_button = QPushButton("Apply Filter")
        self.apply_visits_filter_button.clicked.connect(self.load_visits_data)
        filter_layout.addWidget(self.apply_visits_filter_button)
        
        filter_group.setLayout(filter_layout)
        visits_layout.addWidget(filter_group)
        
        # Visits table
        self.visits_table = QTableWidget()
        self.visits_table.setColumnCount(10)
        self.visits_table.setHorizontalHeaderLabels([
            "Visit ID", "Customer Name", "Date", "Time", "Game Genre", 
            "Console", "Payment Method", "Payment Amount", "Snacks Amount", "Points"
        ])
        
        # Set table properties
        self.visits_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        self.visits_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.visits_table.setAlternatingRowColors(True)
        self.visits_table.horizontalHeader().setStretchLastSection(True)
        self.visits_table.verticalHeader().setVisible(False)
        
        visits_layout.addWidget(self.visits_table)
        
        # Summary section
        summary_group = QGroupBox("Summary")
        summary_layout = QHBoxLayout()
        
        # Total visits
        self.total_visits_label = QLabel("Total Visits: 0")
        self.total_visits_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.total_visits_label)
        
        # Total gaming revenue
        self.total_gaming_label = QLabel("Total Gaming: KES 0.00")
        self.total_gaming_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.total_gaming_label)
        
        # Total snacks revenue
        self.total_snacks_label = QLabel("Total Snacks: KES 0.00")
        self.total_snacks_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.total_snacks_label)
        
        # Total revenue
        self.total_revenue_label = QLabel("Total Revenue: KES 0.00")
        self.total_revenue_label.setStyleSheet("font-weight: bold; color: #6a1b9a;")
        summary_layout.addWidget(self.total_revenue_label)
        
        summary_group.setLayout(summary_layout)
        visits_layout.addWidget(summary_group)
        
        # Add tab to tab widget
        self.tabs.addTab(visits_tab, "Visits")
        
        # Load initial visits data
        self.load_visits_data()
    
    # Camera and QR code functions
    def start_camera(self):
        """Start the camera for QR code scanning"""
        # Show a message to indicate camera is starting
        self.camera_label.setText("Starting camera, please wait...")
        self.camera_label.repaint()  # Force immediate update of the UI
        
        # Disable scan button and enable stop button immediately
        self.scan_button.setEnabled(False)
        self.stop_scan_button.setEnabled(True)
        
        # Initialize camera directly in the main thread for better error handling
        try:
            # First, make sure any existing camera is released
            if hasattr(self, 'camera') and self.camera is not None:
                try:
                    self.camera.release()
                    self.camera = None
                except:
                    pass
            
            # Try to open the camera - try multiple camera indices
            # Try more indices and different configurations
            camera_indices = [0, 1, 2, 3, -1]  # Try these camera indices (-1 is auto-detect)
            
            # Show progress in the UI
            self.camera_label.setText("Searching for camera...")
            self.camera_label.repaint()
            
            for idx in camera_indices:
                try:
                    print(f"Attempting to open camera at index {idx}")
                    self.camera_label.setText(f"Trying camera {idx}...")
                    self.camera_label.repaint()
                    
                    # Create a new VideoCapture object with specific parameters
                    self.camera = cv2.VideoCapture(idx)
                    
                    # Set camera properties for better performance
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    
                    # Check if camera opened successfully
                    if self.camera.isOpened():
                        # Try to read a test frame to confirm it's working
                        ret, test_frame = self.camera.read()
                        if ret and test_frame is not None and test_frame.size > 0:
                            print(f"Successfully opened camera at index {idx}")
                            
                            # Display the test frame
                            try:
                                rgb_frame = cv2.cvtColor(test_frame, cv2.COLOR_BGR2RGB)
                                h, w, ch = rgb_frame.shape
                                bytes_per_line = ch * w
                                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                                self.camera_label.setPixmap(QPixmap.fromImage(qt_image))
                                
                                # Start the timer to update camera feed
                                if hasattr(self, 'timer') and self.timer is not None:
                                    self.timer.stop()  # Stop any existing timer
                                
                                self.timer = QTimer(self)
                                self.timer.timeout.connect(self.update_camera)
                                self.timer.start(30)  # Update every 30ms
                                
                                # Show success message
                                print("Camera started successfully")
                                return
                            except Exception as e:
                                print(f"Error displaying test frame: {str(e)}")
                                self.camera.release()
                                self.camera = None
                        else:
                            print(f"Camera at index {idx} opened but couldn't read frame")
                            self.camera.release()
                            self.camera = None
                    else:
                        print(f"Failed to open camera at index {idx}")
                except Exception as e:
                    print(f"Error trying camera index {idx}: {str(e)}")
                    if hasattr(self, 'camera') and self.camera is not None:
                        self.camera.release()
                        self.camera = None
            
            # If we get here, no camera was successfully opened
            QMessageBox.warning(self, "Camera Error", 
                              "Could not open any camera. Please check your camera connection and permissions.\n\n"
                              "Make sure your camera is connected and not being used by another application.")
            self.scan_button.setEnabled(True)
            self.stop_scan_button.setEnabled(False)
            self.camera_label.setText("Camera feed will appear here")
            
        except Exception as e:
            # Handle any exceptions during camera initialization
            QMessageBox.warning(self, "Camera Error", f"Error initializing camera: {str(e)}")
            self.scan_button.setEnabled(True)
            self.stop_scan_button.setEnabled(False)
            self.camera_label.setText("Camera feed will appear here")
    
    def toggle_manual_customer(self, checked):
        """Enable or disable manual customer entry fields"""
        self.manual_customer_name.setEnabled(checked)
        self.manual_customer_phone.setEnabled(checked)
        self.search_customer_button.setEnabled(checked)
        
        # If manual entry is enabled, clear the QR code customer info
        if checked:
            self.customer_info_label.setText("Enter customer name or phone number")
            # Clear any previously selected customer
            if hasattr(self, 'current_customer_id'):
                delattr(self, 'current_customer_id')
        else:
            self.customer_info_label.setText("Scan a QR code to see customer details")
            
    def search_customer(self):
        """Search for a customer by name or phone number"""
        search_text = self.manual_customer_name.text().strip()
        phone_text = self.manual_customer_phone.text().strip()
        
        if not search_text and not phone_text:
            QMessageBox.warning(self, "Search Error", "Please enter a customer name or phone number to search.")
            return
        
        # Search by name or phone
        found_customer = False
        
        # Clean phone number from the phone field first
        phone_digits = ''.join(c for c in phone_text if c.isdigit())
        
        # Clean phone number from the name field as fallback
        name_digits = ''.join(c for c in search_text if c.isdigit())
        
        # First try exact phone match from the phone field
        if phone_digits and len(phone_digits) == 10:
            # Convert all phone numbers to string for comparison
            customer_match = self.customers_df[self.customers_df['phone'].astype(str) == phone_digits]
            if not customer_match.empty:
                customer = customer_match.iloc[0]
                self.current_customer_id = customer['id']
                self.customer_info_label.setText(f"Customer: {customer['name']} | Phone: {customer['phone']}")
                found_customer = True
        
        # If not found, try exact phone match from the name field
        if not found_customer and name_digits and len(name_digits) == 10:
            customer_match = self.customers_df[self.customers_df['phone'].astype(str) == name_digits]
            if not customer_match.empty:
                customer = customer_match.iloc[0]
                self.current_customer_id = customer['id']
                self.customer_info_label.setText(f"Customer: {customer['name']} | Phone: {customer['phone']}")
                found_customer = True
        
        # If not found by phone, try name (case-insensitive)
        if not found_customer and search_text:
            # Try partial name match (case-insensitive)
            for _, customer in self.customers_df.iterrows():
                if search_text.lower() in str(customer['name']).lower():
                    self.current_customer_id = customer['id']
                    self.customer_info_label.setText(f"Customer: {customer['name']} | Phone: {customer['phone']}")
                    found_customer = True
                    break
        
        # If still not found, try partial phone match from either field
        if not found_customer:
            # Try phone field first
            if phone_digits:
                for _, customer in self.customers_df.iterrows():
                    if phone_digits in str(customer['phone']):
                        self.current_customer_id = customer['id']
                        self.customer_info_label.setText(f"Customer: {customer['name']} | Phone: {customer['phone']}")
                        found_customer = True
                        break
            
            # Then try digits from name field
            if not found_customer and name_digits:
                for _, customer in self.customers_df.iterrows():
                    if name_digits in str(customer['phone']):
                        self.current_customer_id = customer['id']
                        self.customer_info_label.setText(f"Customer: {customer['name']} | Phone: {customer['phone']}")
                        found_customer = True
                        break
        
        if not found_customer:
            # Customer not found
            self.customer_info_label.setText("Customer not registered. Register customer")
            
            # Ask if they want to register
            reply = QMessageBox.question(self, "Customer Not Found", 
                                      "Customer not registered. Would you like to register this customer?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                # Pre-fill registration form with search text and phone
                self.checkin_stacked.setCurrentIndex(1)
                
                # Use the phone field if provided
                if phone_digits and len(phone_digits) == 10:
                    self.reg_phone.setText(phone_digits)
                # Otherwise check if name field contains a valid phone
                elif name_digits and len(name_digits) == 10:
                    self.reg_phone.setText(name_digits)
                
                # Set the name if provided
                if search_text and not (name_digits and len(name_digits) == 10):
                    self.reg_name.setText(search_text)
            return
        
        # Show success message if customer found
        QMessageBox.information(self, "Customer Found", 
                              f"Found customer: {self.customers_df[self.customers_df['id'] == self.current_customer_id].iloc[0]['name']}")
    
    def stop_camera(self):
        """Stop the camera and clean up resources"""
        print("Stopping camera...")
        
        # Stop the timer first
        if hasattr(self, 'timer') and self.timer is not None:
            try:
                self.timer.stop()
                print("Timer stopped")
            except Exception as e:
                print(f"Error stopping timer: {str(e)}")
        
        # Release the camera
        try:
            if hasattr(self, 'camera') and self.camera is not None:
                self.camera.release()
                self.camera = None
                print("Camera released")
            else:
                print("No camera to release")
        except Exception as e:
            print(f"Error releasing camera: {str(e)}")
        
        # Update UI
        self.scan_button.setEnabled(True)
        self.stop_scan_button.setEnabled(False)
        self.camera_label.setText("Camera feed will appear here")
        
        # Force update of the UI
        self.camera_label.repaint()
        print("Camera stopped successfully")
        

    
    def update_camera(self):
        """Update the camera feed and detect QR codes"""
        try:
            # Check if camera is initialized
            if self.camera is None or not self.camera.isOpened():
                print("Camera is not available in update_camera")
                self.stop_camera()
                return
            
            # Read frame from camera
            ret, frame = self.camera.read()
            if not ret or frame is None or frame.size == 0:
                print("Failed to read frame from camera")
                self.stop_camera()
                QMessageBox.warning(self, "Camera Error", "Failed to read frame from camera. Please try again.")
                return
            
            # Make a copy of the frame for QR detection to avoid modifying the original
            detection_frame = frame.copy()
            
            # Add a status indicator to the frame
            cv2.putText(frame, "Scanning for QR code...", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            
            # Use our QR code manager to detect QR codes
            data = self.qr_manager.read_qr_code(detection_frame)
            
            # Try to detect QR code with OpenCV for visualization
            try:
                detector = cv2.QRCodeDetector()
                _, bbox, _ = detector.detectAndDecode(detection_frame)
                
                if bbox is not None:
                    # Draw bounding box around QR code
                    bbox = bbox.astype(int)
                    for i in range(len(bbox[0])):
                        cv2.line(frame, tuple(bbox[0][i]), tuple(bbox[0][(i+1) % len(bbox[0])]), (0, 255, 0), 3)
                        
                    # Add text to indicate QR code is detected
                    cv2.putText(frame, "QR Code Detected", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            except Exception as e:
                print(f"Error in QR detection visualization: {str(e)}")
                # Continue without visualization if it fails
            
            # Convert frame to QImage and display
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.camera_label.setPixmap(QPixmap.fromImage(qt_image))
            except Exception as e:
                print(f"Error converting frame to QImage: {str(e)}")
                return
            
            # Process QR code data if detected
            if data:
                # QR code detected - stop camera first
                self.stop_camera()
                
                # Display the QR code data for debugging
                QMessageBox.information(self, "QR Code Detected", f"QR Code Content: {data}")
                
                try:
                    # Process QR code data
                    self.process_qr_data(data)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error processing QR code: {str(e)}")
                    # Log the error
                    print(f"Error processing QR code: {str(e)}")
                    # Don't restart camera automatically - let user decide
                    return
            
        except Exception as e:
            # Handle any unexpected errors
            print(f"Error in update_camera: {str(e)}")
            self.stop_camera()
    
    def process_qr_data(self, data):
        """Process QR code data and find the corresponding customer"""
        
        # Display the customer info label with the QR data for debugging
        self.customer_info_label.setText(f"QR Data: {data}")
        
        # Check if the QR code data is empty
        if not data:
            QMessageBox.warning(self, "Invalid QR Code", 
                              "The QR code doesn't contain any data. Please try again or register a new customer.")
            return
        
        try:
            # First, try to find the customer by QR code data
            found_customer = False
            
            # Try to parse the QR data to extract customer ID if it's in our new format
            # Format: TRINIX-CUSTOMER:{id}:{name}:{phone}
            if data.startswith("TRINIX-CUSTOMER:"):
                try:
                    parts = data.split(":")
                    if len(parts) >= 4:
                        # Try to extract customer ID from the data
                        potential_id = parts[1]
                        try:
                            customer_id = int(potential_id)
                            # Look up customer by ID
                            customer_match = self.customers_df[self.customers_df['id'] == customer_id]
                            if not customer_match.empty:
                                self.current_customer_id = customer_id
                                found_customer = True
                                # Skip the rest of the search
                        except (ValueError, TypeError):
                            # If ID conversion fails, continue with other matching methods
                            pass
                except Exception as parsing_error:
                    print(f"Error parsing QR data: {parsing_error}")
                    # Continue with other matching methods
            
            # If we didn't find a match by ID, try other methods
            if not found_customer:
                # Check if this is a customer we've registered before
                for _, customer in self.customers_df.iterrows():
                    # Try different matching strategies
                    
                    # 1. Direct match with the QR data format we use
                    customer_data = f"TRINIX-CUSTOMER:{customer['name']}:{customer['phone']}:{customer['location']}"
                    if data == customer_data:
                        self.current_customer_id = customer['id']
                        found_customer = True
                        break
                    
                    # 1.1 Try the old format without the prefix
                    old_format = f"{customer['name']}:{customer['phone']}:{customer['location']}"
                    if data == old_format:
                        self.current_customer_id = customer['id']
                        found_customer = True
                        break
                    
                    # 2. Check if the data contains the customer's phone number
                    if str(customer['phone']) in data:
                        self.current_customer_id = customer['id']
                        found_customer = True
                        break
                    
                    # 3. Check if the data contains the customer's name
                    if str(customer['name']) in data:
                        self.current_customer_id = customer['id']
                        found_customer = True
                        break
            
            if not found_customer:
                # If no match found, show a message and redirect to registration
                reply = QMessageBox.question(self, "Customer Not Found", 
                                          "This QR code doesn't match any registered customer. Would you like to register this customer?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                
                if reply == QMessageBox.Yes:
                    self.checkin_stacked.setCurrentIndex(1)
                return
            
            # If we get here, we found a customer
            print(f"Found customer with ID: {self.current_customer_id}, type: {type(self.current_customer_id)}")
            
            # Debug: Print all customer IDs in the database to check for type mismatches
            print("Customer IDs in database:")
            for idx, cust in self.customers_df.iterrows():
                print(f"  ID: {cust['id']}, type: {type(cust['id'])}")
            
            # Try to match by ID, ensuring type consistency
            try:
                # Convert to int to ensure type consistency
                customer_id_int = int(self.current_customer_id)
                customer_match = self.customers_df[self.customers_df['id'] == customer_id_int]
                
                # If that doesn't work, try string comparison
                if customer_match.empty:
                    customer_id_str = str(self.current_customer_id)
                    customer_match = self.customers_df[self.customers_df['id'].astype(str) == customer_id_str]
                
                # If still empty, try a more flexible approach
                if customer_match.empty:
                    # Try to find by approximate ID match
                    for idx, cust in self.customers_df.iterrows():
                        if str(cust['id']).strip() == str(self.current_customer_id).strip():
                            customer_match = self.customers_df.iloc[[idx]]
                            break
            except Exception as e:
                print(f"Error matching customer ID: {e}")
                # Try as string
                customer_id_str = str(self.current_customer_id)
                customer_match = self.customers_df[self.customers_df['id'].astype(str) == customer_id_str]
            
            if customer_match.empty:
                error_msg = f"Customer with ID {self.current_customer_id} found but could not be retrieved from database."
                print(error_msg)
                QMessageBox.warning(self, "Error", error_msg)
                
                # Offer to search by name or phone instead
                reply = QMessageBox.question(self, "Alternative Search", 
                                          "Would you like to search for this customer by name or phone instead?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                
                if reply == QMessageBox.Yes:
                    # Show manual entry option
                    self.manual_customer_checkbox.setChecked(True)
                    self.toggle_manual_customer(True)
                return
                
            customer = customer_match.iloc[0]
            
            # Display customer info
            self.customer_info_label.setText(f"Customer: {customer['name']} | Phone: {customer['phone']}")
            
            # Show success message
            QMessageBox.information(self, "Customer Found", 
                                  f"Welcome back, {customer['name']}! Please fill in the visit details.")
                
        except Exception as e:
            # Handle any errors
            QMessageBox.warning(self, "Error", f"Error processing QR code: {str(e)}")
            # Log the error for debugging
            print(f"QR Code Processing Error: {str(e)}")
            print(f"QR Data: {data}")
            
            # Offer to register a new customer
            reply = QMessageBox.question(self, "Error Reading QR Code", 
                                      "There was an error processing this QR code. Would you like to register a new customer instead?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                self.checkin_stacked.setCurrentIndex(1)
    
    def generate_qr_code(self, data, customer_id, customer_name=None):
        # Use QR code manager to generate QR code with customer name in filename
        return self.qr_manager.generate_qr_code(data, customer_id, customer_name)
    
    # Customer registration functions
    def validate_phone(self):
        """Validate phone number to ensure it's exactly 10 digits without decimals"""
        phone = self.reg_phone.text().strip()
        
        # Remove any non-digit characters the user might have entered
        digits_only = ''.join(c for c in phone if c.isdigit())
        
        # If the user entered something but it's not valid, show error styling
        if phone and not (digits_only.isdigit() and len(digits_only) == 10):
            self.reg_phone.setStyleSheet("background-color: #424242; color: white; border: 2px solid red;")
            
            # If the text contains a decimal, show a specific message
            if '.' in phone:
                self.statusBar().showMessage("Phone number should not contain decimals", 3000)
            # If the length is wrong, show a message about the required length
            elif len(digits_only) != 10:
                self.statusBar().showMessage(f"Phone number must be exactly 10 digits (currently {len(digits_only)})", 3000)
        else:
            self.reg_phone.setStyleSheet("background-color: #424242; color: white; border: 1px solid #6a1b9a;")
            
            # If the phone has non-digit characters, replace the text with digits only
            if phone and phone != digits_only:
                # Temporarily disconnect the signal to avoid recursion
                self.reg_phone.textChanged.disconnect(self.validate_phone)
                self.reg_phone.setText(digits_only)
                self.reg_phone.textChanged.connect(self.validate_phone)
                self.statusBar().showMessage("Non-digit characters removed from phone number", 2000)
    
    def register_customer(self):
        # Validate inputs
        name = self.reg_name.text().strip()
        phone = self.reg_phone.text().strip()
        age_group = self.reg_age_group.currentText()
        location = self.reg_location.text().strip()
        occupation = self.reg_occupation.currentText()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a name.")
            return
        
        # Clean and validate phone number
        digits_only = ''.join(c for c in phone if c.isdigit())
        
        if not digits_only or len(digits_only) != 10:
            QMessageBox.warning(self, "Validation Error", 
                              "Please enter a valid 10-digit phone number without any decimals or special characters.")
            return
        
        # Use the cleaned phone number
        phone = digits_only
        
        if not location:
            QMessageBox.warning(self, "Validation Error", "Please enter a location.")
            return
        
        # Generate QR code data - include a unique identifier to avoid parsing issues
        # Format: PS-CUSTOMER:{id}:{name}:{phone}
        # Note: We'll add the ID after we get it from the database
        
        # Add customer to database and get customer ID
        customer_id = self.db_manager.add_customer(
            name=name,
            phone=phone,
            age_group=age_group,
            location=location,
            occupation=occupation,
            qr_code_path=""  # Temporary empty path
        )
        
        # Now create the QR data with the customer ID
        qr_data = f"PS-CUSTOMER:{customer_id}:{name}:{phone}"
        
        # Generate and save QR code with customer name in filename
        qr_path = self.generate_qr_code(qr_data, customer_id, name)
        
        # Update customer with QR code path
        self.db_manager.update_customer(customer_id, qr_code_path=qr_path)
        
        # Update local dataframe
        self.customers_df = self.db_manager.customers_df
        
        # Display QR code
        qr_pixmap = QPixmap(qr_path)
        self.qr_preview_label.setPixmap(qr_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # Show success message
        QMessageBox.information(self, "Success", f"Customer {name} registered successfully!")
        
        # Refresh customer table
        self.load_customers()
        
        # Clear form
        self.reg_name.clear()
        self.reg_phone.clear()
        self.reg_location.clear()
    
    def submit_checkin(self):
        # Check if using manual entry or QR code
        using_manual_entry = self.manual_customer_checkbox.isChecked()
        
        if not using_manual_entry and not hasattr(self, 'current_customer_id'):
            QMessageBox.warning(self, "Error", "Please scan a customer QR code or use manual entry.")
            return
        
        if using_manual_entry and not self.manual_customer_name.text().strip():
            QMessageBox.warning(self, "Error", "Please enter a customer name for manual entry.")
            return
        
        # Get form data
        game_genre = self.game_genre_combo.currentText()
        console = self.console_combo.currentText()
        payment_method = self.payment_method_combo.currentText()
        
        try:
            payment_amount = float(self.payment_amount.text()) if self.payment_amount.text() else 0
            snacks_amount = float(self.snacks_amount.text()) if self.snacks_amount.text() else 0
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Please enter valid amounts.")
            return
        
        # Get friends number (formerly referrals)
        friends_number = self.referrals.value()
        snacks_details = self.snacks_details.text().strip()
        
        # Handle manual customer entry
        if using_manual_entry:
            # If we already have a current_customer_id from search, use that
            if hasattr(self, 'current_customer_id') and self.current_customer_id is not None:
                customer_id = self.current_customer_id
            else:
                manual_name = self.manual_customer_name.text().strip()
                manual_phone = self.manual_customer_phone.text().strip()
                
                # Clean phone number - remove any non-digit characters
                if manual_phone:
                    digits_only = ''.join(c for c in manual_phone if c.isdigit())
                    
                    # Validate phone number if provided
                    if digits_only and len(digits_only) != 10:
                        QMessageBox.warning(self, "Validation Error", 
                                          "Phone number must be exactly 10 digits without any decimals or special characters.")
                        return
                    
                    manual_phone = digits_only
                
                # First try to find by name if provided
                found_by_name = False
                if manual_name:
                    for _, customer in self.customers_df.iterrows():
                        if manual_name.lower() in str(customer['name']).lower():
                            customer_id = customer['id']
                            found_by_name = True
                            QMessageBox.information(self, "Existing Customer", 
                                                  f"Found customer by name: {customer['name']}")
                            break
                
                # If not found by name, try phone
                if not found_by_name and manual_phone:
                    existing_customer = self.customers_df[self.customers_df['phone'] == manual_phone]
                    if not existing_customer.empty:
                        # Use existing customer
                        customer_id = existing_customer.iloc[0]['id']
                        QMessageBox.information(self, "Existing Customer", 
                                              f"Found customer by phone: {existing_customer.iloc[0]['name']}")
                    else:
                        # Customer not found - ask to register
                        reply = QMessageBox.question(self, "Customer Not Found", 
                                                  "Customer not registered. Would you like to register this customer?",
                                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                        
                        if reply == QMessageBox.Yes:
                            # Pre-fill registration form
                            self.checkin_stacked.setCurrentIndex(1)
                            if manual_name:
                                self.reg_name.setText(manual_name)
                            if manual_phone:
                                self.reg_phone.setText(manual_phone)
                            return
                        else:
                            # Create a new temporary customer
                            customer_id = self.db_manager.add_customer(
                                name=manual_name if manual_name else "Temporary Customer",
                                phone=manual_phone if manual_phone else "0000000000",
                                age_group="Unknown",
                                location="Manual Entry",
                                occupation="Unknown",
                                qr_code_path=""
                            )
                            # Update local dataframe
                            self.customers_df = self.db_manager.customers_df
                elif not found_by_name:
                    # Neither name nor phone found a match
                    # Customer not found - ask to register
                    reply = QMessageBox.question(self, "Customer Not Found", 
                                              "Customer not registered. Would you like to register this customer?",
                                              QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    
                    if reply == QMessageBox.Yes:
                        # Pre-fill registration form
                        self.checkin_stacked.setCurrentIndex(1)
                        if manual_name:
                            self.reg_name.setText(manual_name)
                        if manual_phone:
                            self.reg_phone.setText(manual_phone)
                        return
                    else:
                        # Create a new temporary customer
                        customer_id = self.db_manager.add_customer(
                            name=manual_name if manual_name else "Temporary Customer",
                            phone=manual_phone if manual_phone else "0000000000",
                            age_group="Unknown",
                            location="Manual Entry",
                            occupation="Unknown",
                            qr_code_path=""
                        )
                        # Update local dataframe
                        self.customers_df = self.db_manager.customers_df
        else:
            # Using QR code customer
            customer_id = self.current_customer_id
        
        # Add visit to database with snacks details
        visit_id = self.db_manager.add_visit(
            customer_id=customer_id,
            game_genre=game_genre,
            console=console,
            payment_method=payment_method,
            payment_amount=payment_amount,
            snacks_amount=snacks_amount,
            referrals=friends_number,  # Pass friends_number to the referrals parameter
            snacks_details=snacks_details
        )
        
        # Update local dataframe
        self.visits_df = self.db_manager.visits_df
        
        # Show success message
        if using_manual_entry:
            customer_name = self.manual_customer_name.text().strip()
        else:
            customer_name = self.customers_df[self.customers_df['id'] == customer_id].iloc[0]['name']
            
        QMessageBox.information(self, "Success", f"Check-in for {customer_name} completed successfully!")
        
        # Clear form
        self.payment_amount.clear()
        self.snacks_amount.clear()
        self.snacks_details.clear()
        self.referrals.setValue(0)
        
        # Reset manual customer fields
        if using_manual_entry:
            self.manual_customer_name.clear()
            self.manual_customer_phone.clear()
            self.customer_info_label.setText("Enter customer name or phone number")
        else:
            # Clear customer selection
            if hasattr(self, 'current_customer_id'):
                delattr(self, 'current_customer_id')
            self.customer_info_label.setText("Scan a QR code to see customer details")
        
        # Reset customer ID
        self.current_customer_id = None
    
    # Customer management functions
    def load_customers(self):
        self.customer_table.setRowCount(0)
        
        for _, customer in self.customers_df.iterrows():
            row_position = self.customer_table.rowCount()
            self.customer_table.insertRow(row_position)
            
            # Convert all values to strings to avoid type errors
            self.customer_table.setItem(row_position, 0, QTableWidgetItem(str(customer['id'])))
            self.customer_table.setItem(row_position, 1, QTableWidgetItem(str(customer['name'])))
            self.customer_table.setItem(row_position, 2, QTableWidgetItem(str(customer['phone'])))
            self.customer_table.setItem(row_position, 3, QTableWidgetItem(str(customer['age_group'])))
            self.customer_table.setItem(row_position, 4, QTableWidgetItem(str(customer['location'])))
            self.customer_table.setItem(row_position, 5, QTableWidgetItem(str(customer['occupation'])))
            self.customer_table.setItem(row_position, 6, QTableWidgetItem(str(customer['registration_date'])))
    
    def filter_customers(self):
        search_text = self.search_input.text().lower()
        filter_option = self.filter_combo.currentText()
        
        self.customer_table.setRowCount(0)
        
        for _, customer in self.customers_df.iterrows():
            # Apply search filter
            if search_text and not (
                search_text in customer['name'].lower() or
                search_text in customer['phone'].lower() or
                search_text in customer['location'].lower()
            ):
                continue
            
            # Apply category filter
            if filter_option == "Student" and customer['occupation'] != "Student":
                continue
            elif filter_option == "Professional" and customer['occupation'] != "Professional":
                continue
            elif filter_option == "Age Group":
                # This would be expanded with a secondary filter in a real application
                pass
            
            # Add row to table
            row_position = self.customer_table.rowCount()
            self.customer_table.insertRow(row_position)
            
            # Convert all values to strings to avoid type errors
            self.customer_table.setItem(row_position, 0, QTableWidgetItem(str(customer['id'])))
            self.customer_table.setItem(row_position, 1, QTableWidgetItem(str(customer['name'])))
            self.customer_table.setItem(row_position, 2, QTableWidgetItem(str(customer['phone'])))
            self.customer_table.setItem(row_position, 3, QTableWidgetItem(str(customer['age_group'])))
            self.customer_table.setItem(row_position, 4, QTableWidgetItem(str(customer['location'])))
            self.customer_table.setItem(row_position, 5, QTableWidgetItem(str(customer['occupation'])))
            self.customer_table.setItem(row_position, 6, QTableWidgetItem(str(customer['registration_date'])))
    
    def select_customer(self, row, column):
        try:
            # Get the ID from the first column
            id_text = self.customer_table.item(row, 0).text().strip()
            
            # Try to convert to integer, handle non-integer values
            try:
                self.selected_customer_id = int(float(id_text))
            except ValueError:
                # If conversion fails, try to find the customer by name
                name = self.customer_table.item(row, 1).text()
                matching_customers = self.customers_df[self.customers_df['name'] == name]
                
                if not matching_customers.empty:
                    self.selected_customer_id = int(matching_customers.iloc[0]['id'])
                else:
                    raise ValueError(f"Could not determine customer ID for {name}")
            
            # Highlight the selected row for better user feedback
            self.customer_table.selectRow(row)
            
            # Enable buttons now that a customer is selected
            self.view_qr_button.setEnabled(True)
            self.regenerate_qr_button.setEnabled(True)
            self.edit_customer_button.setEnabled(True)
            self.delete_customer_button.setEnabled(True)
            
            # Show a status message
            customer_name = self.customer_table.item(row, 1).text()
            self.statusBar().showMessage(f"Selected customer: {customer_name} (ID: {self.selected_customer_id})", 3000)
            
            print(f"Selected customer ID: {self.selected_customer_id}, Name: {customer_name}")
        except Exception as e:
            print(f"Error selecting customer: {e}")
            QMessageBox.warning(self, "Selection Error", f"Error selecting customer: {e}")
    
    def view_customer_qr(self):
        try:
            if not hasattr(self, 'selected_customer_id'):
                QMessageBox.warning(self, "Selection Error", "Please select a customer first.")
                return
            
            # Convert selected_customer_id to int to ensure proper comparison
            customer_id = int(self.selected_customer_id)
            
            # Try to find the customer by ID
            customer = self.customers_df[self.customers_df['id'] == customer_id]
            
            if customer.empty:
                QMessageBox.warning(self, "Error", f"Customer with ID {customer_id} not found.")
                return
            
            qr_path = customer.iloc[0]['qr_code_path']
            
            # Check if QR code path exists
            if not qr_path or not os.path.exists(qr_path):
                # QR code doesn't exist, offer to generate one
                reply = QMessageBox.question(self, "QR Code Missing", 
                                          "QR code not found. Would you like to generate one?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                
                if reply == QMessageBox.Yes:
                    self.regenerate_qr()
                return
            
            # Display QR code in a dialog
            qr_dialog = QMessageBox()
            qr_dialog.setWindowTitle("Customer QR Code")
            qr_dialog.setText(f"QR Code for {customer.iloc[0]['name']}")
            
            qr_pixmap = QPixmap(qr_path)
            qr_dialog.setIconPixmap(qr_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            qr_dialog.exec_()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error viewing QR code: {str(e)}")
            print(f"Error viewing QR code: {str(e)}")
    
    def regenerate_qr(self):
        try:
            if not hasattr(self, 'selected_customer_id'):
                QMessageBox.warning(self, "Selection Error", "Please select a customer first.")
                return
            
            # Convert selected_customer_id to int to ensure proper comparison
            customer_id = int(self.selected_customer_id)
            
            # Try to find the customer by ID
            customer_idx = self.customers_df[self.customers_df['id'] == customer_id].index
            
            if len(customer_idx) == 0:
                QMessageBox.warning(self, "Error", f"Customer with ID {customer_id} not found.")
                return
            
            customer = self.customers_df.loc[customer_idx[0]]
            
            # Generate QR code data - include a unique identifier to avoid parsing issues
            # Format: PS-CUSTOMER:{id}:{name}:{phone}
            customer_id = int(customer['id'])
            qr_data = f"PS-CUSTOMER:{customer_id}:{customer['name']}:{customer['phone']}"
            
            # Generate and save QR code with customer name using the QR manager
            qr_path = self.qr_manager.generate_qr_code(
                data=qr_data, 
                customer_id=int(customer['id']), 
                customer_name=str(customer['name'])
            )
            
            # Update database
            self.customers_df.at[customer_idx[0], 'qr_code_path'] = qr_path
            self.db_manager.save_customers(self.customers_df)
            
            # Show success message
            QMessageBox.information(self, "Success", "QR code regenerated successfully!")
            
            # Show the new QR code
            self.view_customer_qr()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error regenerating QR code: {str(e)}")
            print(f"Error regenerating QR code: {str(e)}")
    
    def edit_customer(self):
        try:
            if not hasattr(self, 'selected_customer_id'):
                QMessageBox.warning(self, "Selection Error", "Please select a customer first.")
                return
            
            # Convert selected_customer_id to int to ensure proper comparison
            customer_id = int(self.selected_customer_id)
            
            # Try to find the customer by ID
            customer_idx = self.customers_df[self.customers_df['id'] == customer_id].index
            
            if len(customer_idx) == 0:
                QMessageBox.warning(self, "Error", f"Customer with ID {customer_id} not found.")
                return
            
            customer = self.customers_df.loc[customer_idx[0]]
            
            # Create a dialog for editing customer details
            from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
            
            edit_dialog = QDialog(self)
            edit_dialog.setWindowTitle(f"Edit Customer: {customer['name']}")
            edit_dialog.setMinimumWidth(400)
            
            dialog_layout = QVBoxLayout(edit_dialog)
            form_layout = QFormLayout()
            
            # Create input fields with current values - convert all values to strings
            name_input = QLineEdit(str(customer['name']))
            phone_input = QLineEdit(str(customer['phone']))
            
            age_group_combo = QComboBox()
            age_groups = ["5-10 years", "11-15 years", "16-20 years", "21-25 years", 
                          "26-30 years", "31-35 years", "36-40 years"]
            age_group_combo.addItems(age_groups)
            current_index = age_groups.index(str(customer['age_group'])) if str(customer['age_group']) in age_groups else 0
            age_group_combo.setCurrentIndex(current_index)
            
            location_input = QLineEdit(str(customer['location']))
            
            occupation_combo = QComboBox()
            occupation_combo.addItems(["Student", "Professional"])
            occupation_combo.setCurrentText(str(customer['occupation']))
            
            # Add fields to form
            form_layout.addRow("Name:", name_input)
            form_layout.addRow("Phone:", phone_input)
            form_layout.addRow("Age Group:", age_group_combo)
            form_layout.addRow("Location:", location_input)
            form_layout.addRow("Occupation:", occupation_combo)
            
            dialog_layout.addLayout(form_layout)
            
            # Add buttons
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(edit_dialog.accept)
            button_box.rejected.connect(edit_dialog.reject)
            dialog_layout.addWidget(button_box)
            
            # Show dialog and process result
            if edit_dialog.exec_() == QDialog.Accepted:
                try:
                    # Get and validate phone number
                    phone = phone_input.text().strip()
                    digits_only = ''.join(c for c in phone if c.isdigit())
                    
                    if not digits_only or len(digits_only) != 10:
                        raise ValueError("Phone number must be exactly 10 digits without any decimals or special characters")
                    
                    # Update customer data
                    self.customers_df.at[customer_idx[0], 'name'] = name_input.text().strip()
                    self.customers_df.at[customer_idx[0], 'phone'] = digits_only  # Use cleaned phone number
                    self.customers_df.at[customer_idx[0], 'age_group'] = age_group_combo.currentText()
                    self.customers_df.at[customer_idx[0], 'location'] = location_input.text().strip()
                    self.customers_df.at[customer_idx[0], 'occupation'] = occupation_combo.currentText()
                    
                    # Save changes to database
                    self.db_manager.save_customers(self.customers_df)
                    
                    # Refresh the table
                    self.load_customers()
                    
                    # Show success message
                    QMessageBox.information(self, "Success", "Customer details updated successfully!")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to update customer: {str(e)}")
            else:
                # User cancelled
                pass
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error editing customer: {str(e)}")
            print(f"Error editing customer: {str(e)}")
    
    def delete_customer(self):
        try:
            if not hasattr(self, 'selected_customer_id'):
                QMessageBox.warning(self, "Selection Error", "Please select a customer first.")
                return
            
            # Convert selected_customer_id to int to ensure proper comparison
            customer_id = int(self.selected_customer_id)
            
            # Try to find the customer by ID
            customer_idx = self.customers_df[self.customers_df['id'] == customer_id].index
            
            if len(customer_idx) == 0:
                QMessageBox.warning(self, "Error", f"Customer with ID {customer_id} not found.")
                return
            
            customer = self.customers_df.loc[customer_idx[0]]
            
            # Confirm deletion
            reply = QMessageBox.question(self, "Confirm Deletion", 
                                        f"Are you sure you want to delete {customer['name']}?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Delete customer using database manager
                self.db_manager.delete_customer(self.selected_customer_id)
                
                # Update local dataframe
                self.customers_df = self.db_manager.customers_df
                
                # Refresh table
                self.load_customers()
                
                # Reset selected customer
                if hasattr(self, 'selected_customer_id'):
                    delattr(self, 'selected_customer_id')
                
                # Disable buttons again
                self.view_qr_button.setEnabled(False)
                self.regenerate_qr_button.setEnabled(False)
                self.edit_customer_button.setEnabled(False)
                self.delete_customer_button.setEnabled(False)
                
                # Show success message
                QMessageBox.information(self, "Success", "Customer deleted successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error deleting customer: {str(e)}")
            print(f"Error deleting customer: {str(e)}")
    
    # Analytics functions
    def update_analytics(self):
        # In a real application, this would generate charts based on actual data
        # For this example, we'll generate sample charts
        
        # Generate sales chart
        self.generate_sales_chart()
        
        # Generate visits chart
        self.generate_visits_chart()
    
    def generate_sales_chart(self):
        # Create a sample sales chart
        plt.figure(figsize=(8, 4))
        
        # Sample data
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        gaming_sales = [4500, 5200, 3800, 4100, 6700, 8500, 7200]
        snacks_sales = [1200, 1400, 1100, 1300, 1800, 2200, 1900]
        
        # Create stacked bar chart
        plt.bar(days, gaming_sales, color='#6a1b9a', label='Gaming')
        plt.bar(days, snacks_sales, bottom=gaming_sales, color='#9c27b0', label='Snacks')
        
        plt.title('Weekly Sales Breakdown')
        plt.xlabel('Day of Week')
        plt.ylabel('Sales (KES)')
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Save chart to buffer
        buf = QBuffer()
        buf.open(QBuffer.ReadWrite)
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', 
                   facecolor='#212121', edgecolor='none')
        plt.close()
        
        # Display chart
        buf.seek(0)
        chart_pixmap = QPixmap()
        chart_pixmap.loadFromData(buf.data())
        self.sales_chart_label.setPixmap(chart_pixmap)
        buf.close()
    
    def generate_visits_chart(self):
        # Create a sample visits chart
        plt.figure(figsize=(8, 4))
        
        # Sample data
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        visits = [12, 15, 10, 14, 22, 35, 28]
        
        # Create line chart
        plt.plot(days, visits, marker='o', linewidth=3, color='#bb86fc')
        
        plt.title('Weekly Customer Visits')
        plt.xlabel('Day of Week')
        plt.ylabel('Number of Visits')
        plt.grid(linestyle='--', alpha=0.7)
        
        # Fill area under the line
        plt.fill_between(days, visits, alpha=0.3, color='#bb86fc')
        
        # Save chart to buffer
        buf = QBuffer()
        buf.open(QBuffer.ReadWrite)
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                   facecolor='#212121', edgecolor='none')
        plt.close()
        
        # Display chart
        buf.seek(0)
        chart_pixmap = QPixmap()
        chart_pixmap.loadFromData(buf.data())
        self.visits_chart_label.setPixmap(chart_pixmap)
        buf.close()
    
    def export_to_excel(self):
        """Export data to CSV files that can be opened in Excel"""
        # Show a message that export is starting
        self.export_excel_button.setEnabled(False)
        self.export_excel_button.setText("Exporting...")
        
        try:
            # Get date range
            start_date = self.from_date.date().toString("yyyy-MM-dd")
            end_date = self.to_date.date().toString("yyyy-MM-dd")
            
            print(f"Exporting data from {start_date} to {end_date}")
            
            # Get filtered data
            visits = self.db_manager.get_visits_by_date_range(start_date, end_date)
            
            if visits.empty:
                QMessageBox.information(self, "No Data", 
                                      "No data available for the selected date range.")
                self.export_excel_button.setEnabled(True)
                self.export_excel_button.setText("Export Data")
                return
            
            # Make sure the reports directory exists
            os.makedirs('reports', exist_ok=True)
            
            # Generate a unique timestamp for filenames
            now = datetime.now()
            timestamp = now.strftime('%Y%m%d_%H%M%S')
            
            # Calculate total points for each customer
            customer_points = {}
            for _, visit in visits.iterrows():
                customer_id = visit['customer_id']
                points = visit['points'] if 'points' in visit else self.db_manager._calculate_points(visit['payment_amount'])
                
                if customer_id in customer_points:
                    customer_points[customer_id] += points
                else:
                    customer_points[customer_id] = points
            
            # Create a copy of customers dataframe to add total points
            customers_with_points = self.customers_df.copy()
            
            # Add total points column
            customers_with_points['total_points'] = 0
            for customer_id, points in customer_points.items():
                # Find the customer in the dataframe
                customer_idx = customers_with_points[customers_with_points['id'] == customer_id].index
                if len(customer_idx) > 0:
                    customers_with_points.at[customer_idx[0], 'total_points'] = points
            
            # Export to CSV files
            visits_file = os.path.join('reports', f"visits_{timestamp}.csv")
            customers_file = os.path.join('reports', f"customers_{timestamp}.csv")
            
            # Save to CSV
            visits.to_csv(visits_file, index=False)
            customers_with_points.to_csv(customers_file, index=False)
            
            # Create combined CSV with customer and visit data
            combined_file = os.path.join('reports', f"combined_{timestamp}.csv")
            
            # Merge visits with customer data
            combined_df = pd.merge(
                visits,
                customers_with_points[['id', 'name', 'phone', 'age_group', 'location', 'occupation', 'total_points']],
                left_on='customer_id',
                right_on='id',
                how='left'
            )
            
            # Save combined data
            combined_df.to_csv(combined_file, index=False)
            
            # Create a readme file explaining the exports
            readme_file = os.path.join('reports', f"README_{timestamp}.txt")
            with open(readme_file, 'w') as f:
                f.write(f"Trinix Gaming Export - {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=================================================\n\n")
                f.write(f"Date Range: {start_date} to {end_date}\n\n")
                f.write("Files included in this export:\n")
                f.write(f"1. {os.path.basename(visits_file)} - All visits in the selected date range\n")
                f.write(f"2. {os.path.basename(customers_file)} - All customers with total points\n")
                f.write(f"3. {os.path.basename(combined_file)} - Combined customer and visit data\n\n")
                f.write("To view these files, you can open them in Excel or any spreadsheet application.\n")
            
            # Create a zip file containing all exports
            import zipfile
            zip_file = os.path.join('reports', f"trinix_export_{timestamp}.zip")
            
            with zipfile.ZipFile(zip_file, 'w') as zipf:
                zipf.write(visits_file, os.path.basename(visits_file))
                zipf.write(customers_file, os.path.basename(customers_file))
                zipf.write(combined_file, os.path.basename(combined_file))
                zipf.write(readme_file, os.path.basename(readme_file))
            
            # Show success message with option to open the folder
            reply = QMessageBox.information(self, "Export Successful", 
                                          f"Data exported successfully!\n\nFiles saved to:\n{os.path.abspath('reports')}\n\n"
                                          f"Would you like to open the reports folder?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            # Open the folder if requested
            if reply == QMessageBox.Yes:
                try:
                    os.startfile(os.path.abspath('reports'))
                except Exception as e:
                    print(f"Error opening reports folder: {str(e)}")
                    QMessageBox.warning(self, "Error", f"Could not open the reports folder: {str(e)}")
        except Exception as e:
            print(f"Error exporting data: {str(e)}")
            QMessageBox.warning(self, "Error", f"Error exporting data: {str(e)}")
        finally:
            # Re-enable the export button
            self.export_excel_button.setEnabled(True)
            self.export_excel_button.setText("Export Data")
    
    def load_visits_data(self):
        """Load visits data into the visits table based on date filter"""
        try:
            # Get date range from filter
            from_date = self.visits_from_date.date().toString("yyyy-MM-dd")
            to_date = self.visits_to_date.date().toString("yyyy-MM-dd")
            
            # Get visits data from database manager
            visits_df = self.db_manager.get_visits_by_date_range(from_date, to_date)
            
            # Ensure points column exists
            if 'points' not in visits_df.columns:
                # Calculate points based on payment amount
                def calculate_points(amount):
                    try:
                        amount_float = float(amount)
                        if amount_float <= 50:
                            return 3
                        elif amount_float <= 70:
                            return 5
                        elif amount_float <= 100:
                            return 8
                        elif amount_float <= 170:
                            return 10
                        elif amount_float <= 200:
                            return 15
                        else:
                            return 20
                    except (ValueError, TypeError):
                        # Default points if conversion fails
                        print(f"Warning: Could not convert payment amount '{amount}' to float. Using default points.")
                        return 3
                
                visits_df['points'] = visits_df['payment_amount'].apply(calculate_points)
            
            # Clear existing table data
            self.visits_table.setRowCount(0)
            
            if visits_df.empty:
                # Show message if no data
                self.total_visits_label.setText("Total Visits: 0")
                self.total_gaming_label.setText("Total Gaming: KES 0.00")
                self.total_snacks_label.setText("Total Snacks: KES 0.00")
                self.total_revenue_label.setText("Total Revenue: KES 0.00")
                return
            
            # Calculate summary data
            total_visits = len(visits_df)
            total_gaming = visits_df['payment_amount'].sum()
            total_snacks = visits_df['snacks_amount'].sum()
            total_revenue = total_gaming + total_snacks
            
            # Update summary labels
            self.total_visits_label.setText(f"Total Visits: {total_visits}")
            self.total_gaming_label.setText(f"Total Gaming: KES {total_gaming:.2f}")
            self.total_snacks_label.setText(f"Total Snacks: KES {total_snacks:.2f}")
            self.total_revenue_label.setText(f"Total Revenue: KES {total_revenue:.2f}")
            
            # Populate table with visits data
            self.visits_table.setRowCount(total_visits)
            
            # Get customer names for each visit
            for i, (_, visit) in enumerate(visits_df.iterrows()):
                # Get customer name
                customer_id = visit['customer_id']
                customer_name = "Unknown"
                
                # Try to get customer name from database
                customer = self.db_manager.get_customer(customer_id)
                if customer:
                    customer_name = customer['name']
                
                # Add visit data to table
                self.visits_table.setItem(i, 0, QTableWidgetItem(str(visit['visit_id'])))
                self.visits_table.setItem(i, 1, QTableWidgetItem(customer_name))
                self.visits_table.setItem(i, 2, QTableWidgetItem(str(visit['date'])))
                self.visits_table.setItem(i, 3, QTableWidgetItem(str(visit['time'])))
                self.visits_table.setItem(i, 4, QTableWidgetItem(str(visit['game_genre'])))
                self.visits_table.setItem(i, 5, QTableWidgetItem(str(visit['console'])))
                self.visits_table.setItem(i, 6, QTableWidgetItem(str(visit['payment_method'])))
                self.visits_table.setItem(i, 7, QTableWidgetItem(f"KES {visit['payment_amount']:.2f}"))
                self.visits_table.setItem(i, 8, QTableWidgetItem(f"KES {visit['snacks_amount']:.2f}"))
                
                # Add points column
                # Check if points column exists in the dataframe
                if 'points' in visit:
                    points = visit['points']
                else:
                    # Calculate points based on payment amount if not in dataframe
                    try:
                        payment_amount = float(visit['payment_amount'])
                        if payment_amount <= 50:
                            points = 3
                        elif payment_amount <= 70:
                            points = 5
                        elif payment_amount <= 100:
                            points = 8
                        elif payment_amount <= 170:
                            points = 10
                        elif payment_amount <= 200:
                            points = 15
                        else:
                            points = 20
                    except (ValueError, TypeError):
                        # Default points if conversion fails
                        print(f"Warning: Could not convert payment amount to float. Using default points.")
                        points = 3
                
                # Create a points item with a distinctive style
                points_item = QTableWidgetItem(str(points))
                points_item.setTextAlignment(Qt.AlignCenter)
                # Set a background color based on points value to make it stand out
                if points >= 15:
                    points_item.setBackground(QColor(76, 175, 80, 100))  # Green for high points
                elif points >= 8:
                    points_item.setBackground(QColor(255, 193, 7, 100))  # Amber for medium points
                else:
                    points_item.setBackground(QColor(255, 87, 34, 100))  # Orange for low points
                
                self.visits_table.setItem(i, 9, points_item)
            
            # Resize columns to content
            self.visits_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error loading visits data: {str(e)}")
            QMessageBox.warning(self, "Error", f"Error loading visits data: {str(e)}")
    
    def create_analytics_tab(self):
        """Create the analytics tab with charts and summary data"""
        analytics_tab = QWidget()
        analytics_layout = QVBoxLayout(analytics_tab)
        
        # Create filter section
        filter_group = QGroupBox("Date Filter")
        filter_layout = QHBoxLayout()
        
        # From date
        from_label = QLabel("From:")
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))  # Default to 1 month ago
        
        # To date
        to_label = QLabel("To:")
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())  # Default to today
        
        # Apply filter button
        self.apply_filter_button = QPushButton("Apply Filter")
        self.apply_filter_button.clicked.connect(self.update_analytics)
        
        # Add widgets to filter layout
        filter_layout.addWidget(from_label)
        filter_layout.addWidget(self.from_date)
        filter_layout.addWidget(to_label)
        filter_layout.addWidget(self.to_date)
        filter_layout.addWidget(self.apply_filter_button)
        
        # Add export reports button
        self.export_reports_button = QPushButton("Export Reports")
        self.export_reports_button.clicked.connect(self.export_reports)
        filter_layout.addWidget(self.export_reports_button)
        
        # Add shift summary button
        self.shift_summary_button = QPushButton("Shift Summary")
        self.shift_summary_button.clicked.connect(self.generate_shift_report)
        filter_layout.addWidget(self.shift_summary_button)
        
        filter_layout.addStretch()
        
        filter_group.setLayout(filter_layout)
        analytics_layout.addWidget(filter_group)
        
        # Create summary section
        summary_group = QGroupBox("Summary")
        summary_layout = QHBoxLayout()
        
        # Create summary labels
        self.game_sales_sum_label = QLabel("Game Sales: KES 0.00")
        self.game_sales_sum_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #bb86fc;")
        
        self.snacks_sales_sum_label = QLabel("Snack Sales: KES 0.00")
        self.snacks_sales_sum_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #bb86fc;")
        
        self.customer_count_label = QLabel("Customers: 0")
        self.customer_count_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #bb86fc;")
        
        # Add labels to summary layout
        summary_layout.addWidget(self.game_sales_sum_label)
        summary_layout.addWidget(self.snacks_sales_sum_label)
        summary_layout.addWidget(self.customer_count_label)
        
        summary_group.setLayout(summary_layout)
        analytics_layout.addWidget(summary_group)
        
        # Create charts section
        charts_group = QGroupBox("Charts")
        charts_layout = QHBoxLayout()
        
        # Create sales chart frame
        self.sales_chart_frame = QFrame()
        self.sales_chart_frame.setMinimumHeight(300)
        self.sales_chart_frame.setStyleSheet("background-color: #424242; border: 1px solid #6a1b9a;")
        sales_chart_layout = QVBoxLayout(self.sales_chart_frame)
        sales_chart_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create customer visits chart frame
        self.visits_chart_frame = QFrame()
        self.visits_chart_frame.setMinimumHeight(300)
        self.visits_chart_frame.setStyleSheet("background-color: #424242; border: 1px solid #6a1b9a;")
        visits_chart_layout = QVBoxLayout(self.visits_chart_frame)
        visits_chart_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add chart frames to charts layout
        charts_layout.addWidget(self.sales_chart_frame)
        charts_layout.addWidget(self.visits_chart_frame)
        
        charts_group.setLayout(charts_layout)
        analytics_layout.addWidget(charts_group)
        
        # Add tab to tab widget
        self.tabs.addTab(analytics_tab, "Analytics")
        
        # Initial update
        self.update_analytics()
    
    def update_analytics(self):
        """Update analytics charts and summary data"""
        try:
            # Get date range from filter
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            
            # Get visits data from database manager for the selected date range
            visits_df = self.db_manager.get_visits_by_date_range(from_date, to_date)
            
            if visits_df.empty:
                # Show message if no data
                self.game_sales_sum_label.setText("Game Sales: KES 0.00")
                self.snacks_sales_sum_label.setText("Snack Sales: KES 0.00")
                self.customer_count_label.setText("Customers: 0")
                
                # Clear charts
                self._clear_chart(self.sales_chart_frame)
                self._clear_chart(self.visits_chart_frame)
                return
            
            # Calculate summary data
            total_game_sales = visits_df['payment_amount'].sum()
            total_snack_sales = visits_df['snacks_amount'].sum()
            
            # Count unique customers
            unique_customers = visits_df['customer_id'].nunique()
            
            # Update summary labels
            self.game_sales_sum_label.setText(f"Game Sales: KES {total_game_sales:.2f}")
            self.snacks_sales_sum_label.setText(f"Snack Sales: KES {total_snack_sales:.2f}")
            self.customer_count_label.setText(f"Customers: {unique_customers}")
            
            # Update sales analysis chart
            self._update_sales_chart(visits_df)
            
            # Update customer visits chart
            self._update_visits_chart(visits_df)
            
        except Exception as e:
            print(f"Error updating analytics: {str(e)}")
            QMessageBox.warning(self, "Error", f"Error updating analytics: {str(e)}")
    
    def _clear_chart(self, chart_frame):
        """Clear a chart frame by removing all widgets"""
        # Remove all widgets from the layout
        if chart_frame.layout():
            while chart_frame.layout().count():
                item = chart_frame.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
    
    def _update_sales_chart(self, visits_df):
        """Update the sales analysis chart"""
        try:
            # Clear previous chart
            self._clear_chart(self.sales_chart_frame)
            
            # Group data by date
            daily_sales = visits_df.groupby('date').agg({
                'payment_amount': 'sum',
                'snacks_amount': 'sum'
            }).reset_index()
            
            # Sort by date
            daily_sales = daily_sales.sort_values('date')
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(8, 4), facecolor='#424242')
            
            # Plot data
            x = range(len(daily_sales))
            width = 0.35
            
            # Plot gaming sales
            gaming_bars = ax.bar([i - width/2 for i in x], daily_sales['payment_amount'], 
                                width, label='Gaming', color='#bb86fc')
            
            # Plot snack sales
            snack_bars = ax.bar([i + width/2 for i in x], daily_sales['snacks_amount'], 
                               width, label='Snacks', color='#03dac6')
            
            # Set labels and title
            ax.set_title('Sales Analysis', color='white', fontsize=14)
            ax.set_xlabel('Date', color='white')
            ax.set_ylabel('Amount (KES)', color='white')
            
            # Set x-axis ticks
            ax.set_xticks(x)
            ax.set_xticklabels(daily_sales['date'], rotation=45, ha='right', color='white')
            
            # Set y-axis ticks color
            ax.tick_params(axis='y', colors='white')
            
            # Add legend
            ax.legend(facecolor='#424242', edgecolor='#6a1b9a', labelcolor='white')
            
            # Set grid
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # Set background color
            ax.set_facecolor('#424242')
            
            # Add value labels on bars
            for bar in gaming_bars:
                height = bar.get_height()
                ax.annotate(f'{height:.0f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom',
                            color='white', fontsize=8)
            
            for bar in snack_bars:
                height = bar.get_height()
                ax.annotate(f'{height:.0f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom',
                            color='white', fontsize=8)
            
            # Adjust layout
            plt.tight_layout()
            
            # Convert matplotlib figure to QPixmap
            buf = QBuffer()
            buf.open(QBuffer.ReadWrite)
            fig.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            
            # Create QPixmap from buffer
            pixmap = QPixmap()
            pixmap.loadFromData(buf.data())
            
            # Create label to display the chart
            chart_label = QLabel()
            chart_label.setPixmap(pixmap)
            chart_label.setAlignment(Qt.AlignCenter)
            
            # Add label to chart frame
            self.sales_chart_frame.layout().addWidget(chart_label)
            
            # Close the figure to free memory
            plt.close(fig)
            
        except Exception as e:
            print(f"Error updating sales chart: {str(e)}")
            error_label = QLabel(f"Error creating sales chart: {str(e)}")
            error_label.setStyleSheet("color: red;")
            self.sales_chart_frame.layout().addWidget(error_label)
    
    def _update_visits_chart(self, visits_df):
        """Update the customer visits chart"""
        try:
            # Clear previous chart
            self._clear_chart(self.visits_chart_frame)
            
            # Count customers by date
            daily_customers = visits_df.groupby('date')['customer_id'].nunique().reset_index()
            daily_customers.columns = ['date', 'customer_count']
            
            # Sort by date
            daily_customers = daily_customers.sort_values('date')
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(8, 4), facecolor='#424242')
            
            # Plot data - bar chart
            bars = ax.bar(
                daily_customers['date'], 
                daily_customers['customer_count'],
                color='#bb86fc',
                edgecolor='#6a1b9a',
                alpha=0.8
            )
            
            # Set title and labels
            ax.set_title('Customer Visits', color='white', fontsize=14)
            ax.set_xlabel('Date', color='white')
            ax.set_ylabel('Number of Customers', color='white')
            
            # Set x-axis ticks
            ax.set_xticks(range(len(daily_customers)))
            ax.set_xticklabels(daily_customers['date'], rotation=45, ha='right', color='white')
            
            # Set y-axis ticks color
            ax.tick_params(axis='y', colors='white')
            
            # Set grid
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # Set background color
            ax.set_facecolor('#424242')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{int(height)}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom',
                            color='white', fontsize=9)
            
            # Adjust layout
            plt.tight_layout()
            
            # Convert matplotlib figure to QPixmap
            buf = QBuffer()
            buf.open(QBuffer.ReadWrite)
            fig.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            
            # Create QPixmap from buffer
            pixmap = QPixmap()
            pixmap.loadFromData(buf.data())
            
            # Create label to display the chart
            chart_label = QLabel()
            chart_label.setPixmap(pixmap)
            chart_label.setAlignment(Qt.AlignCenter)
            
            # Add label to chart frame
            self.visits_chart_frame.layout().addWidget(chart_label)
            
            # Close the figure to free memory
            plt.close(fig)
            
        except Exception as e:
            print(f"Error updating visits chart: {str(e)}")
            error_label = QLabel(f"Error creating visits chart: {str(e)}")
            error_label.setStyleSheet("color: red;")
            self.visits_chart_frame.layout().addWidget(error_label)
    
    def export_reports(self):
        """Export data to Excel reports"""
        try:
            # Get date range from filter
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            
            # Get data from database manager for the selected date range
            visits_df = self.db_manager.get_visits_by_date_range(from_date, to_date)
            
            if visits_df.empty:
                QMessageBox.information(self, "No Data", 
                                      "No data available for the selected date range.")
                return
            
            # Create timestamp for filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export visits data
            visits_file = f"visits_{timestamp}.csv"
            visits_path = os.path.join("reports", visits_file)
            visits_df.to_csv(visits_path, index=False)
            
            # Export customers data with total points
            customers_file = f"customers_{timestamp}.csv"
            customers_path = os.path.join("reports", customers_file)
            
            # Calculate total points for each customer
            customer_points = visits_df.groupby('customer_id')['points'].sum().reset_index()
            customer_points.rename(columns={'points': 'total_points'}, inplace=True)
            
            # Merge with customers dataframe
            customers_with_points = pd.merge(
                self.customers_df,
                customer_points,
                left_on='id',
                right_on='customer_id',
                how='left'
            )
            
            # Fill NaN values with 0 for customers with no visits in the date range
            customers_with_points['total_points'] = customers_with_points['total_points'].fillna(0)
            
            # Drop the redundant customer_id column from the merge
            if 'customer_id' in customers_with_points.columns:
                customers_with_points = customers_with_points.drop('customer_id', axis=1)
                
            # Export the enhanced customers dataframe
            customers_with_points.to_csv(customers_path, index=False)
            
            # Export combined data (merge visits with customer info)
            combined_df = pd.merge(
                visits_df, 
                self.customers_df[['id', 'name', 'phone', 'age_group', 'location', 'occupation']], 
                left_on='customer_id', 
                right_on='id', 
                how='left'
            )
            combined_file = f"combined_{timestamp}.csv"
            combined_path = os.path.join("reports", combined_file)
            combined_df.to_csv(combined_path, index=False)
            
            # Create a README file with export info
            readme_file = f"README_{timestamp}.txt"
            readme_path = os.path.join("reports", readme_file)
            
            with open(readme_path, 'w') as f:
                f.write(f"Trinix Gaming Shop - Data Export\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Date Range: {from_date} to {to_date}\n\n")
                f.write(f"Files included:\n")
                f.write(f"1. {visits_file} - Visit records\n")
                f.write(f"2. {customers_file} - Customer records (includes total_points column)\n")
                f.write(f"3. {combined_file} - Combined visit and customer data\n\n")
                f.write(f"Total records:\n")
                f.write(f"- Visits: {len(visits_df)}\n")
                f.write(f"- Customers: {len(self.customers_df)}\n")
            
            # Show success message with option to open the reports folder
            reply = QMessageBox.information(self, "Export Successful", 
                                          f"Data exported successfully to the reports folder!\n"
                                          f"Files:\n- {visits_file}\n- {customers_file} (includes total points)\n- {combined_file}",
                                          QMessageBox.Open | QMessageBox.Ok, QMessageBox.Ok)
            
            # Open the reports folder if requested
            if reply == QMessageBox.Open:
                os.startfile("reports")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error exporting data: {str(e)}")
    
    def generate_shift_report(self):
        # Get shift summary from database manager
        shift_data = self.db_manager.get_shift_summary()
        
        if shift_data['total_customers'] == 0:
            QMessageBox.information(self, "No Data", 
                                   "No data available for today. Please check back after customers have visited.")
            return
        
        try:
            # Generate report using report generator
            report_path = self.report_generator.generate_shift_report(shift_data)
            
            # Show success message with option to open the report
            reply = QMessageBox.information(self, "Report Generated", 
                                          f"End-of-shift report generated successfully!\nPath: {report_path}",
                                          QMessageBox.Open | QMessageBox.Ok, QMessageBox.Ok)
            
            # Open the report if requested
            if reply == QMessageBox.Open:
                os.startfile(report_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error generating report: {str(e)}")


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PSGamingApp()
    window.show()
    sys.exit(app.exec_())
