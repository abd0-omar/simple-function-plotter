import sys
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox

class FunctionPlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Function Plotter')
        self.setGeometry(100, 100, 800, 600)
        
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout()
        
        # input layout
        input_layout = QHBoxLayout()
        
        self.function_input = QLineEdit(self)
        self.function_input.setPlaceholderText("Enter a function of x")
        input_layout.addWidget(self.function_input)
        
        self.x_min_input = QLineEdit(self)
        self.x_min_input.setPlaceholderText("Min x")
        input_layout.addWidget(self.x_min_input)
        
        self.x_max_input = QLineEdit(self)
        self.x_max_input.setPlaceholderText("Max x")
        input_layout.addWidget(self.x_max_input)
        
        plot_button = QPushButton("Plot", self)
        plot_button.clicked.connect(self.plot_function)
        input_layout.addWidget(plot_button)
        
        main_layout.addLayout(input_layout)
        
        # matplotlib
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    
    def plot_function(self):
        function_text = self.function_input.text()
        x_min_text = self.x_min_input.text()
        x_max_text = self.x_max_input.text()
        
        if not function_text:
            self.show_error("Please enter a function.")
            return
        
        # check for letters
        for letter in function_text:
            if letter.isalpha() and letter != 'x':
                self.show_error("Invalid function variables. Please check your syntax.")
                return

        try:
            x_min = float(x_min_text)
        except ValueError:
            self.show_error("Invalid minimum value for x.")
            return
        
        try:
            x_max = float(x_max_text)
        except ValueError:
            self.show_error("Invalid maximum value for x.")
            return
        
        if x_min >= x_max:
            self.show_error("Minimum x must be less than maximum x.")
            return
        
        x = sp.symbols('x')
        
        try:
            function = sp.sympify(function_text.replace('^', '**'), locals={'log10': sp.log, 'sqrt': sp.sqrt})
        except sp.SympifyError:
            self.show_error("Invalid function input. Please check your syntax.")
            return
        
        x_values = np.linspace(x_min, x_max, 400)
        
        f_lambdified = sp.lambdify(x, function, modules=['numpy'])
        y_values = f_lambdified(x_values)
        
        self.ax.clear()
        self.ax.plot(x_values, y_values, label=f'${sp.latex(function)}$')
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('f(x)')
        self.ax.set_title('Plot of the function')
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()
    
    def show_error(self, message):
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setText(message)
        error_msg.setWindowTitle("Error")
        error_msg.exec_()

def main():
    app = QApplication(sys.argv)
    window = FunctionPlotter()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
