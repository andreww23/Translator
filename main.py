import sys

from googletrans import Translator
from PyQt5 import uic
import pyttsx3
import sqlite3
import hashlib
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox


class RegistrationWindow(QMainWindow, QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('login.ui', self)
        self.setWindowTitle('Login')
        self.initLoginUi()
        self.initRegistrationUi()

    def loginCheck(self):
        con = sqlite3.connect('translate.db')
        cursor = con.cursor()
        name = self.lineEdit.text()
        password = self.lineEdit_2.text()
        passw = bytes(password, 'utf-8')
        sha = hashlib.sha1(passw).hexdigest()
        if not name or not password:
            QMessageBox.information(self, 'Внимание!', 'Вы не заполнили все поля.')
            return

        cursor.execute(f"INSERT INTO user_history(username) VALUES('{name}')")
        con.commit()
        result = cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                                (name, sha))
        if len(result.fetchall()):
            self.openMainWindow()
        else:
            QMessageBox.information(self, 'Внимание!', 'Неправильное имя пользователя или пароль!')
            return

    def registrationCheck(self):
        con = sqlite3.connect('translate.db')
        cursor = con.cursor()
        name = self.lineEdit.text()
        password = self.lineEdit_2.text()
        passw = bytes(password, 'utf-8')
        sha = hashlib.sha1(passw).hexdigest()
        if not name or not password:
            QMessageBox.information(self, 'Внимание!', 'Вы не заполнили все поля.')
            return
        result = cursor.execute("SELECT * FROM users WHERE username = ?", (name,))
        if result.fetchall():
            msg = QMessageBox.information(self, 'Внимание!', 'Пользоватеть с таким именем уже зарегистрирован.')
        else:
            cursor.execute("INSERT INTO USERS VALUES(?, ?)",
                           (name, sha))
            cursor.execute(f"INSERT INTO user_history(username) VALUES('{name}')")
            con.commit()
            self.openMainWindow()

    def initLoginUi(self):
        self.pushButton.clicked.connect(self.loginCheck)

    def initRegistrationUi(self):
        self.pushButton_2.clicked.connect(self.registrationCheck)

    def openMainWindow(self):
        RegistrationWindow.close(self)
        self.wind = MainWindow()
        self.wind.show()


class MainWindow(QMainWindow, QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('translator.ui', self)
        self.setWindowTitle('Translator')
        self.con = sqlite3.connect('translate.db')
        self.cursor = self.con.cursor()

        self.translator = Translator()
        
        self.input_lang = {'Английский': 'en', 'Русский': 'ru', 'Итальянский': 'it', 'Китайский': 'zh-CN',
                           'Французский': 'fr'}
        self.comboBox.addItems(list(self.input_lang.keys()))

        self.output_lang = {'Русский': 'ru', 'Английский': 'en', 'Итальянский': 'it',
                            'Китайский': 'zh-CN', 'Французский': 'fr'}
        self.comboBox_2.addItems(list(self.output_lang.keys()))

        self.initUI()

    def initUI(self):
        self.comboBox.currentTextChanged.connect(self.onInputTextChanged)
        self.comboBox_2.currentTextChanged.connect(self.onOutputTextChanged)
        self.pushButton_6.clicked.connect(self.TranslateText)
        self.pushButton_2.clicked.connect(self.ReproduceOutputAudio)
        self.pushButton_7.clicked.connect(self.ReproduceInputAudio)
        self.pushButton_4.clicked.connect(self.BackToRegistration)
        self.pushButton_3.clicked.connect(self.ShowHistory)

    def onInputTextChanged(self):
        self.label_2.clear()
        self.label_2.setText(self.comboBox.currentText())

    def onOutputTextChanged(self):
        self.label_3.clear()
        self.label_3.setText(self.comboBox_2.currentText())
        try:
            self.checkBoxWasChanged()
        except:
            pass

    def TranslateText(self):
        user = "SELECT * FROM user_history"
        result = self.cursor.execute(user).fetchall()
        current = result[-1]
        self.input_text = self.lineEdit.text()
        try:
            self.output_text = self.translator.translate(self.input_text,
                                                         src=self.input_lang[self.comboBox.currentText()],
                                                         dest=self.output_lang[self.comboBox_2.currentText()])
            self.label_6.setText(self.output_text.text)
            self.cursor.execute(
                f"""INSERT INTO history(input_word, output_word, current_user) 
                VALUES('{self.input_text}', '{self.label_6.text()}', '{current[0]}')""")
            self.con.commit()
        except:
            QMessageBox.information(self, 'Внимание!', 'Ошибка.')

    def checkBoxWasChanged(self):
        user = "SELECT * FROM user_history"
        result = self.cursor.execute(user).fetchall()
        current = result[-1]
        self.input_text = self.lineEdit.text()
        try:
            self.output_text = self.translator.translate(self.input_text,
                                                         src=self.input_lang[self.comboBox.currentText()],
                                                         dest=self.output_lang[self.comboBox_2.currentText()])
            self.label_6.setText(self.output_text.text)
            self.cursor.execute(
                f"""INSERT INTO history(input_word, output_word, current_user) 
                    VALUES('{self.input_text}', '{self.label_6.text()}', '{current[0]}')""")
            self.con.commit()
        except:
            pass

    def ReproduceOutputAudio(self):
        engine_output = pyttsx3.init()
        engine_output.setProperty('rate', 150)
        engine_output.setProperty('volume', 0.9)
        engine_output.say(self.label_6.text())
        engine_output.runAndWait()

    def ReproduceInputAudio(self):
        engine_input = pyttsx3.init()
        engine_input.setProperty('rate', 150)
        engine_input.setProperty('volume', 0.9)
        engine_input.say(self.lineEdit.text())
        engine_input.runAndWait()

    def BackToRegistration(self):
        MainWindow.close(self)
        self.login = RegistrationWindow()
        self.login.show()

    def ShowHistory(self):
        self.history = HistoryWindow()
        self.history.show()

    def chooseLastUser(self):
        user = "SELECT * FROM user_history"
        result = self.cursor.execute(user).fetchone()
        current = result[-1]
        print(current)


class HistoryWindow(QMainWindow, QDialog):
    def __init__(self):
        self.con = sqlite3.connect('translate.db')
        self.cursor = self.con.cursor()
        super().__init__()
        uic.loadUi('history.ui', self)
        self.setWindowTitle('History')
        self.initUI()

    def initUI(self):
        user = "SELECT * FROM user_history"
        result = self.cursor.execute(user).fetchall()
        current = result[-1]
        self.input_list = f"SELECT input_word FROM history WHERE current_user = '{current[0]}'"
        self.output_list = f"SELECT output_word FROM history  WHERE current_user = '{current[0]}'"
        first_result = self.cursor.execute(self.input_list).fetchall()
        second_result = self.cursor.execute(self.output_list).fetchall()
        for word in first_result:
            self.listWidget.addItem(word[0])
        for other_word in second_result:
            self.listWidget_2.addItem(other_word[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RegistrationWindow()
    ex.show()
    sys.exit(app.exec())
