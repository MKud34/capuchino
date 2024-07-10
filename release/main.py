import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QDialog
from main_ui import Ui_MainWindow
from add_edit_coffee_form_ui import Ui_AddEditCoffeeForm


class CoffeeDB:
    def __init__(self):
        self.connection = sqlite3.connect('../data/coffee.sqlite')
        self.cursor = self.connection.cursor()

    def get_all_coffees(self):
        self.cursor.execute("SELECT * FROM coffee")
        return self.cursor.fetchall()

    def get_coffee_by_id(self, coffee_id):
        self.cursor.execute("SELECT * FROM coffee WHERE ID=?", (coffee_id,))
        return self.cursor.fetchone()

    def update_coffee(self, coffee_id, data):
        self.cursor.execute('''UPDATE coffee SET sort_name=?, roast_degree=?, ground_or_whole=?, taste_description=?, price=?, package_volume=? WHERE ID=?''', data + (coffee_id,))
        self.connection.commit()

    def add_coffee(self, data):
        self.cursor.execute('''INSERT INTO coffee (sort_name, roast_degree, ground_or_whole, taste_description, price, package_volume) VALUES (?, ?, ?, ?, ?, ?)''', data)
        self.connection.commit()

    def close(self):
        self.connection.close()


class AddEditCoffeeForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AddEditCoffeeForm()
        self.ui.setupUi(self)
        self.ui.saveButton.clicked.connect(self.save_coffee)
        self.coffee_id = None
        self.db = CoffeeDB()

    def load_coffee(self, coffee_id):
        self.coffee_id = coffee_id
        coffee = self.db.get_coffee_by_id(coffee_id)
        if coffee:
            self.ui.nameLineEdit.setText(coffee[1])
            self.ui.roastLineEdit.setText(coffee[2])
            self.ui.grindLineEdit.setText(coffee[3])
            self.ui.descriptionLineEdit.setText(coffee[4])
            self.ui.priceLineEdit.setText(str(coffee[5]))
            self.ui.volumeLineEdit.setText(str(coffee[6]))

    def save_coffee(self):
        data = (
            self.ui.nameLineEdit.text(),
            self.ui.roastLineEdit.text(),
            self.ui.grindLineEdit.text(),
            self.ui.descriptionLineEdit.text(),
            float(self.ui.priceLineEdit.text()),
            int(self.ui.volumeLineEdit.text())
        )
        if self.coffee_id:
            self.db.update_coffee(self.coffee_id, data)
        else:
            self.db.add_coffee(data)
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.db = CoffeeDB()
        self.load_coffees()
        self.ui.editButton.clicked.connect(self.edit_coffee)
        self.ui.addButton.clicked.connect(self.add_coffee)

    def load_coffees(self):
        coffees = self.db.get_all_coffees()
        self.ui.tableWidget.setRowCount(len(coffees))
        for row_num, coffee in enumerate(coffees):
            for col_num, data in enumerate(coffee):
                self.ui.tableWidget.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def edit_coffee(self):
        selected = self.ui.tableWidget.currentRow()
        if selected >= 0:
            coffee_id = int(self.ui.tableWidget.item(selected, 0).text())
            self.edit_dialog = AddEditCoffeeForm(self)
            self.edit_dialog.load_coffee(coffee_id)
            if self.edit_dialog.exec_() == QDialog.Accepted:
                self.load_coffees()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите кофе для редактирования")

    def add_coffee(self):
        self.add_dialog = AddEditCoffeeForm(self)
        if self.add_dialog.exec_() == QDialog.Accepted:
            self.load_coffees()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
