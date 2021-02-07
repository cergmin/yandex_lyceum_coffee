import sys
import sqlite3
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget


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