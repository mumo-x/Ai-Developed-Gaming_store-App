import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                            QMessageBox, QTextEdit)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2

class QRCodeViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trinix QR Code Viewer")
        self.setMinimumSize(600, 500)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create QR code display area
        self.qr_label = QLabel("QR code will appear here")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setMinimumHeight(300)
        self.qr_label.setStyleSheet("border: 2px dashed #6a1b9a; padding: 10px;")
        main_layout.addWidget(self.qr_label)
        
        # Create QR code data display
        self.data_text = QTextEdit()
        self.data_text.setPlaceholderText("QR code data will appear here")
        self.data_text.setMaximumHeight(100)
        main_layout.addWidget(self.data_text)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Load QR Code")
        self.load_button.clicked.connect(self.load_qr_code)
        button_layout.addWidget(self.load_button)
        
        self.scan_button = QPushButton("Scan QR Code")
        self.scan_button.clicked.connect(self.scan_qr_code)
        button_layout.addWidget(self.scan_button)
        
        main_layout.addLayout(button_layout)
        
        # Initialize camera
        self.camera = None
    
    def load_qr_code(self):
        # Open file dialog to select QR code image
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open QR Code", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if not file_path:
            return
        
        # Load and display QR code image
        pixmap = QPixmap(file_path)
        self.qr_label.setPixmap(pixmap.scaled(
            self.qr_label.width(), self.qr_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        
        # Read QR code data
        self.read_qr_code(file_path)
    
    def read_qr_code(self, file_path):
        # Read image
        image = cv2.imread(file_path)
        if image is None:
            QMessageBox.warning(self, "Error", f"Could not read image from {file_path}")
            return
        
        # Create QR code detector
        detector = cv2.QRCodeDetector()
        
        # Detect and decode QR code
        data, bbox, _ = detector.detectAndDecode(image)
        
        if bbox is not None and data:
            self.data_text.setText(f"QR Code Data (OpenCV):\n{data}")
            return
        
        # Try with pyzbar if available
        try:
            import pyzbar.pyzbar as pyzbar
            
            # Convert image to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Decode QR code
            decoded_objects = pyzbar.decode(gray)
            
            if decoded_objects:
                data = decoded_objects[0].data.decode('utf-8')
                self.data_text.setText(f"QR Code Data (pyzbar):\n{data}")
            else:
                self.data_text.setText("No QR code detected")
        except ImportError:
            self.data_text.setText("No QR code detected with OpenCV\npyzbar not available")
    
    def scan_qr_code(self):
        QMessageBox.information(self, "Not Implemented", 
                              "QR code scanning from camera is not implemented in this utility.\n\n"
                              "Please use the main application for scanning QR codes.")

def main():
    app = QApplication(sys.argv)
    window = QRCodeViewer()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()