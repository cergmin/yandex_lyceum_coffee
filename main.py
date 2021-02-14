import sys
import sqlite3
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget


class addEditCoffeeForm(QtWidgets.QDialog):
    def __init__(self, con, data, parent=None):
        super(addEditCoffeeForm, self).__init__(parent)
        uic.loadUi('addEditCoffeeForm.ui', self)
        
        self.parent = parent
        self.data = data
        self.con = con
        cur = self.con.cursor()

        self.id.setText(str(self.data[0]))
        self.name.setText(str(self.data[1]))
        self.description.setPlainText(str(self.data[4]))
        self.price.setValue(float(self.data[5]))
        self.size.setValue(float(self.data[6]))

        # Загрузка видов обжарки
        results = cur.execute('''SELECT * FROM roasting''').fetchall()

        for i, elem in enumerate(results):
            self.roasting.addItem(elem[2] + ' - ' + elem[1])
            self.roasting.setItemData(i, elem[0])

            if self.data[2] == elem[0]:
                self.roasting.setCurrentIndex(i)
        
        # Загрузка формы кофе (молотый/в зернах)
        results = cur.execute('''SELECT * FROM shapes''').fetchall()

        for i, elem in enumerate(results):
            self.shape.addItem(elem[1])
            self.shape.setItemData(i, elem[0])

            if self.data[3] == elem[0]:
                self.shape.setCurrentIndex(i)
        
        self.save_btn.clicked.connect(self.save_data)
    
    def save_data(self):
        cur = self.con.cursor()
        cur.execute("""UPDATE coffee
            SET name = ?, roasting = ?, shape = ?,
                description = ?, price = ?, size = ?
            WHERE id = ?""",
            (
                self.name.text(),
                self.roasting.currentData(),
                self.shape.currentData(),
                self.description.toPlainText(),
                self.price.value(),
                self.size.value(),
                self.data[0]
            )
        )

        self.con.commit()

        self.hide()
        self.parent.show_results()


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.con = sqlite3.connect('coffee.sqlite')
        columns = [
            i[0]
            for i in self.con.execute(
                'SELECT * FROM coffee'
            ).description
        ]

        self.table.setColumnCount(len(columns))

        for i in range(len(columns)):
            self.table.setHorizontalHeaderItem(
                i,
                QtWidgets.QTableWidgetItem(columns[i])
            )
        
        self.show_results()

        self.change_btn.clicked.connect(self.change_row)
        self.add_btn.clicked.connect(self.add_row)
    
    def change_row(self, row_id=None):
        if row_id is None:
            row = self.table.currentRow()
            row_id = self.table.item(row, 0).text()

        cur = self.con.cursor()

        result = cur.execute('''
            SELECT *
            FROM coffee
            WHERE id = ?''', (row_id, )).fetchone()

        self.add_edit_form = addEditCoffeeForm(self.con, result, self)
        self.add_edit_form.show()
    
    def add_row(self):
        cur = self.con.cursor()
        cur.execute("INSERT INTO coffee VALUES(NULL, '', 0, 0, '', 0, 0)")
        self.con.commit()

        self.change_row(row_id=cur.lastrowid)
    
    def show_results(self):
        cur = self.con.cursor()

        results = cur.execute('''
            SELECT c.id, c.name, r.name, s.name, c.description, c.price, c.size
            FROM coffee AS c
            LEFT JOIN roasting AS r
            ON c.roasting = r.id
            LEFT JOIN shapes AS s
            ON c.shape = s.id''').fetchall()
        self.table.setRowCount(len(results))

        for i, elem in enumerate(results):
            for j in range(len(elem)):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(elem[j])))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWidget()
    ex.show()
    sys.exit(app.exec_())