import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QDialog


class CoffeeDB:
    def __init__(self):
        self.connection = sqlite3.connect('coffee.sqlite')
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
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.saveButton.clicked.connect(self.save_coffee)
        self.coffee_id = None
        self.db = CoffeeDB()

    def load_coffee(self, coffee_id):
        self.coffee_id = coffee_id
        coffee = self.db.get_coffee_by_id(coffee_id)
        if coffee:
            self.nameLineEdit.setText(coffee[1])
            self.roastLineEdit.setText(coffee[2])
            self.grindLineEdit.setText(coffee[3])
            self.descriptionLineEdit.setText(coffee[4])
            self.priceLineEdit.setText(str(coffee[5]))
            self.volumeLineEdit.setText(str(coffee[6]))

    def save_coffee(self):
        data = (
            self.nameLineEdit.text(),
            self.roastLineEdit.text(),
            self.grindLineEdit.text(),
            self.descriptionLineEdit.text(),
            float(self.priceLineEdit.text()),
            int(self.volumeLineEdit.text())
        )
        if self.coffee_id:
            self.db.update_coffee(self.coffee_id, data)
        else:
            self.db.add_coffee(data)
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.db = CoffeeDB()
        self.load_coffees()
        self.editButton.clicked.connect(self.edit_coffee)
        self.addButton.clicked.connect(self.add_coffee)

    def load_coffees(self):
        coffees = self.db.get_all_coffees()
        self.tableWidget.setRowCount(len(coffees))
        for row_num, coffee in enumerate(coffees):
            for col_num, data in enumerate(coffee):
                self.tableWidget.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def edit_coffee(self):
        selected = self.tableWidget.currentRow()
        if selected >= 0:
            coffee_id = int(self.tableWidget.item(selected, 0).text())
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
