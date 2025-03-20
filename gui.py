import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QWidget, QLabel, QFrame, QSplitter, 
                            QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configurar la ventana principal
        self.setWindowTitle("Sistema de Admisión")
        self.setGeometry(100, 100, 900, 600)
        
        # Configurar el estilo de la aplicación
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLabel {
                font-size: 18px;
                color: #2c3e50;
            }
            QFrame {
                border-radius: 10px;
                padding: 20px;
            }
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
                font-family: Consolas, Monaco, monospace;
                font-size: 14px;
            }
        """)
        
        # Crear el widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Crear el layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Crear un layout horizontal para el título y el logo
        header_layout = QHBoxLayout()
        
        # Añadir un espaciador a la izquierda para centrar el contenido
        header_layout.addStretch(1)
        
        # Cargar y añadir el logo
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "logo.png")
        logo_label = QLabel()
        logo_pixmap = QPixmap(logo_path)
        # Escalar el logo a un tamaño más grande
        logo_pixmap = logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(logo_label)
        
        # Añadir un pequeño espacio entre el logo y el título
        header_layout.addSpacing(30)
        
        # Título
        title_label = QLabel("Sistema de Gestión de Admisión")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2c3e50; margin: 15px;")
        header_layout.addWidget(title_label)
        
        # Añadir un espaciador a la derecha para centrar el contenido
        header_layout.addStretch(1)
        
        # Añadir el layout del encabezado al layout principal
        main_layout.addLayout(header_layout)
        
        # Crear los paneles para los botones
        panels_layout = QHBoxLayout()
        
        # Panel para el Generador de Exámenes
        generator_frame = QFrame()
        generator_frame.setStyleSheet("background-color: #e74c3c; padding: 20px; border-radius: 10px;")
        generator_layout = QVBoxLayout(generator_frame)
        
        generator_title = QLabel("Generador de Exámenes")
        generator_title.setStyleSheet("color: white; font-weight: bold;")
        generator_title.setAlignment(Qt.AlignCenter)
        generator_layout.addWidget(generator_title)
        
        generator_description = QLabel("Crea nuevos exámenes y gestiona los tipos de pruebas para el proceso de admisión.")
        generator_description.setStyleSheet("color: white; font-size: 14px;")
        generator_description.setWordWrap(True)
        generator_layout.addWidget(generator_description)
        
        generator_button = QPushButton("Ejecutar Generador")
        generator_button.setStyleSheet("""
            background-color: white;
            color: #e74c3c;
            padding: 15px;
            font-weight: bold;
            border-radius: 5px;
        """)
        generator_button.clicked.connect(self.run_generator)
        generator_layout.addWidget(generator_button)
        
        panels_layout.addWidget(generator_frame)
        
        # Panel para el Calificador
        calificator_frame = QFrame()
        calificator_frame.setStyleSheet("background-color: #2ecc71; padding: 20px; border-radius: 10px;")
        calificator_layout = QVBoxLayout(calificator_frame)
        
        calificator_title = QLabel("Calificador de Exámenes")
        calificator_title.setStyleSheet("color: white; font-weight: bold;")
        calificator_title.setAlignment(Qt.AlignCenter)
        calificator_layout.addWidget(calificator_title)
        
        calificator_description = QLabel("Califica los exámenes y genera reportes con los resultados de los estudiantes.")
        calificator_description.setStyleSheet("color: white; font-size: 14px;")
        calificator_description.setWordWrap(True)
        calificator_layout.addWidget(calificator_description)
        
        calificator_button = QPushButton("Ejecutar Calificador")
        calificator_button.setStyleSheet("""
            background-color: white;
            color: #2ecc71;
            padding: 15px;
            font-weight: bold;
            border-radius: 5px;
        """)
        calificator_button.clicked.connect(self.run_calificator)
        calificator_layout.addWidget(calificator_button)
        
        panels_layout.addWidget(calificator_frame)
        
        main_layout.addLayout(panels_layout)
        
        # Área de estado
        self.status_label = QLabel("Listo para ejecutar")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-top: 10px;")
        main_layout.addWidget(self.status_label)
        
        # Área de consola para mostrar la salida
        console_layout = QHBoxLayout()
        
        console_label = QLabel("Consola de Salida:")
        console_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-top: 5px;")
        console_layout.addWidget(console_label)
        
        main_layout.addLayout(console_layout)
        
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setMinimumHeight(200)
        self.console_output.setMaximumHeight(200)
        self.console_output.setStyleSheet("""
            background-color: #2c3e50;
            color: #ecf0f1;
            border-radius: 5px;
            padding: 10px;
            font-family: Consolas, Monaco, monospace;
            font-size: 14px;
        """)
        main_layout.addWidget(self.console_output)
        
        # Inicializar el proceso
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.readyReadStandardError.connect(self.handle_error)
        self.process.finished.connect(self.process_finished)
    
    def run_generator(self):
        """Ejecuta el generador de exámenes"""
        self.status_label.setText("Ejecutando el generador de exámenes...")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px; margin-top: 20px;")
        self.console_output.clear()
        self.console_output.append("Iniciando el generador de exámenes...\n")
        
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "exam_generator", "main.py")
        
        # Ejecutar el script usando QProcess para capturar la salida
        self.process.setWorkingDirectory(os.path.dirname(os.path.abspath(__file__)))
        self.process.start(sys.executable, [script_path])
    
    def run_calificator(self):
        """Ejecuta el calificador de exámenes"""
        self.status_label.setText("Ejecutando el calificador de exámenes...")
        self.status_label.setStyleSheet("color: #2ecc71; font-size: 14px; margin-top: 20px;")
        self.console_output.clear()
        self.console_output.append("Iniciando el calificador de exámenes...\n")
        
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "calificator", "main.py")
        
        # Ejecutar el script usando QProcess para capturar la salida
        self.process.setWorkingDirectory(os.path.dirname(os.path.abspath(__file__)))
        self.process.start(sys.executable, [script_path])
    
    def handle_output(self):
        """Maneja la salida estándar del proceso"""
        try:
            data = self.process.readAllStandardOutput().data().decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Intentar con otra codificación común en Windows
                data = self.process.readAllStandardOutput().data().decode('latin-1')
            except Exception as e:
                data = f"[Error al decodificar la salida: {str(e)}]"
        
        self.console_output.append(data)
        # Desplazar automáticamente hacia abajo para mostrar la última salida
        self.console_output.verticalScrollBar().setValue(
            self.console_output.verticalScrollBar().maximum()
        )
    
    def handle_error(self):
        """Maneja la salida de error del proceso"""
        try:
            data = self.process.readAllStandardError().data().decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Intentar con otra codificación común en Windows
                data = self.process.readAllStandardError().data().decode('latin-1')
            except Exception as e:
                data = f"[Error al decodificar la salida de error: {str(e)}]"
        
        self.console_output.append(f"<span style='color: #e74c3c;'>{data}</span>")
        self.status_label.setText(f"Error en la ejecución")
        self.status_label.setStyleSheet("color: red; font-size: 14px; margin-top: 20px;")
        # Desplazar automáticamente hacia abajo para mostrar la última salida
        self.console_output.verticalScrollBar().setValue(
            self.console_output.verticalScrollBar().maximum()
        )
    
    def process_finished(self, exit_code, exit_status):
        """Maneja la finalización del proceso"""
        if exit_code == 0:
            self.status_label.setText("Proceso completado correctamente")
            self.status_label.setStyleSheet("color: #2ecc71; font-size: 14px; margin-top: 20px;")
            self.console_output.append("\n<span style='color: #2ecc71; font-weight: bold;'>Proceso completado correctamente</span>")
        else:
            self.status_label.setText(f"Proceso terminado con código de salida: {exit_code}")
            self.status_label.setStyleSheet("color: red; font-size: 14px; margin-top: 20px;")
            self.console_output.append(f"\n<span style='color: #e74c3c; font-weight: bold;'>Proceso terminado con código de salida: {exit_code}</span>")
        
        # Desplazar automáticamente hacia abajo para mostrar la última salida
        self.console_output.verticalScrollBar().setValue(
            self.console_output.verticalScrollBar().maximum()
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
