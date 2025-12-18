import sys
import requests
from PySide6 import QtWidgets, QtCore
from asd import Ui_MainWindow


class App(Ui_MainWindow):
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.setupUi(self.MainWindow)
        self.base_url = "http://127.0.0.1:5000/user"
        self.task_base_url = "http://127.0.0.1:5000/task"
        self.session = requests.Session()
        self.current_user = None

        self.setup_connections()
        self.setup_ui()

        self.tabWidget.hide()

        self.MainWindow.show()
        sys.exit(self.app.exec())

    def setup_connections(self):
        self.pushButton_3.clicked.connect(self.register)
        self.pushButton_2.clicked.connect(self.login)
        self.pushButton_4.clicked.connect(self.sort_tasks)
        self.pushButton_6.clicked.connect(self.create_task)
        self.pushButton_7.clicked.connect(self.find_task)
        self.pushButton_10.clicked.connect(self.reload_tasks)

    def setup_ui(self):
        self.pushButton_3.setText("Регистрация")
        self.pushButton_2.setText("Вход")
        self.pushButton_4.setText("Сортировать")
        self.pushButton_6.setText("Создать")
        self.pushButton_7.setText("Искать")
        self.pushButton_9.setText("✅ Отметить выполненной")
        self.pushButton_8.setText("🗑️ Удалить задачу")
        self.pushButton_10.setText("Обновить")

        self.tabWidget.setTabText(0, "Все задачи")
        self.tabWidget.setTabText(1, "Новая задача")
        self.tabWidget.setTabText(2, "Найти задачу")

        self.lineEdit_3.setPlaceholderText("Имя пользователя")
        self.lineEdit_4.setPlaceholderText("Пароль")
        self.lineEdit.setPlaceholderText("Имя пользователя")
        self.lineEdit_2.setPlaceholderText("Пароль")
        self.lineEdit_5.setPlaceholderText("Название задачи")
        self.lineEdit_5.setPlaceholderText("ID задачи")


        self.comboBox.addItems(["По умолчанию", "Приоритет", "Дедлайн", "Статус"])
        self.comboBox_2.addItems(["По убыванию", "По возрастанию"])
        self.comboBox_3.addItems(["low", "medium", "high"])

        self.groupBox.setTitle("Сортировка задач")
        self.groupBox_2.setTitle("Фильтры")
        self.groupBox_3.setTitle("Новая задача")
        self.groupBox_3.setTitle("Поиск задачи")
        self.groupBox_4.setTitle("Задач")

        self.label_14.setText("Название")
        self.label_10.setText("ID:")
        self.label_11.setText("Дедлайн")
        self.label_12.setText("Статус")
        self.label_13.setText("Приоритет")



        self.dateEdit.setDisplayFormat("yyyy-MM-dd")

        self.groupBox.hide()

        for child in self.scrollAreaWidgetContents.children():
            if child != self.scrollAreaWidgetContents:
                child.deleteLater()

        self.scroll_layout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.scroll_layout.setSpacing(10)

    def register(self):
        username = self.lineEdit_3.text().strip()
        password = self.lineEdit_4.text().strip()


        data = {'username': username, 'password': password}

        response = self.session.post(f"{self.base_url}/register_qt", json=data)
        if response.status_code == 201:
            self.current_user = response.json().get('user')
            self.after_login()

    def login(self):
        username = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()


        data = {'username': username, 'password': password}
        response = self.session.post(f"{self.base_url}/login_qt", json=data)
        if response.status_code == 200:
            self.current_user = response.json().get('user')
            self.after_login()


    def after_login(self):
        self.tabWidget.show()
        self.widget_2.hide()
        self.widget.hide()
        self.load_tasks()

    def load_tasks(self):
        response = self.session.get(f"{self.task_base_url}/tasks_json")
        if response.status_code == 200:
            data = response.json()
            if data.get('access'):
                tasks = data.get('tasks', [])
                self.display_tasks(tasks)


    def display_tasks(self, tasks):
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()



        for task in tasks:
            task_group = self.create_task_groupbox(task)
            self.scroll_layout.addWidget(task_group)

        self.scroll_layout.addStretch()

    def create_task_groupbox(self, task):
        task_group = QtWidgets.QGroupBox(f"Задача #{task.get('id', '?')}")


        layout = QtWidgets.QGridLayout(task_group)

        title_label = QtWidgets.QLabel("<b>" + task.get('title', 'Нет названия') + "</b>")
        title_label.setStyleSheet("font-size: 12pt;")
        layout.addWidget(title_label, 0, 0, 1, 2)

        layout.addWidget(QtWidgets.QLabel("ID:"), 1, 0)
        layout.addWidget(QtWidgets.QLabel(str(task.get('id', 'N/A'))), 1, 1)


        layout.addWidget(QtWidgets.QLabel("Дедлайн:"), 2, 0)
        deadline = task.get('deadline', 'Не установлен')
        layout.addWidget(QtWidgets.QLabel(deadline), 2, 1)

        layout.addWidget(QtWidgets.QLabel("Статус:"), 3, 0)
        is_done = task.get('is_done', False)
        status_text = "✅ Выполнена" if is_done else "🔄 В работе"
        status_label = QtWidgets.QLabel(status_text)
        status_label.setStyleSheet("color: green;" if is_done else "color: blue;")
        layout.addWidget(status_label, 3, 1)

        layout.addWidget(QtWidgets.QLabel("Уровень сложности:"), 4, 0)
        priority = task.get('priority', 'Не указан')
        priority_label = QtWidgets.QLabel(priority)

        priority_colors = {
            "low": "color: green;",
            "medium": "color: orange;",
            "high": "color: red;"
        }
        if priority.lower() in priority_colors:
            priority_label.setStyleSheet(priority_colors[priority.lower()])

        layout.addWidget(priority_label, 4, 1)

        buttons_layout = QtWidgets.QHBoxLayout()

        if not is_done:
            btn_done = QtWidgets.QPushButton("✅ Отметить выполненной")
            btn_done.setStyleSheet("background-color: #4CAF50; color: white;")
            task_id = task.get('id')
            btn_done.clicked.connect(lambda checked, tid=task_id: self.mark_task_done(tid))
            buttons_layout.addWidget(btn_done)

        btn_delete = QtWidgets.QPushButton("🗑️ Удалить задачу")
        btn_delete.setStyleSheet("background-color: #f44336; color: white;")
        task_id = task.get('id')
        btn_delete.clicked.connect(lambda checked, tid=task_id: self.delete_task(tid))
        buttons_layout.addWidget(btn_delete)

        layout.addLayout(buttons_layout, 5, 0, 1, 2)

        task_group.setStyleSheet("""
            QGroupBox {
                font-size: 10pt;
                border: 2px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        return task_group

    def mark_task_done(self, task_id):

        response = self.session.post(f"{self.task_base_url}/task/{task_id}/done_json")
        if response.status_code == 200:
            self.load_tasks()

    def delete_task(self, task_id):
        reply = QtWidgets.QMessageBox.question(
            self.MainWindow,
            'Подтверждение удаления',
            f'Вы уверены, что хотите удалить задачу #{task_id}?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            try:
                response = self.session.post(f"{self.task_base_url}/task/{task_id}/delete_json")
                if response.status_code == 200:
                    QtWidgets.QMessageBox.information(self.MainWindow, "Успех", "Задача удалена!")
                    self.load_tasks()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self.MainWindow, "Ошибка", f"Не удалось удалить задачу: {str(e)}")

    def sort_tasks(self):
        sort_by = self.comboBox.currentText()
        order = self.comboBox_2.currentText()

        sort_map = {
            "По умолчанию": "newest",
            "Приоритет": "priority",
            "Дедлайн": "deadline",
            "Статус": "status"
        }

        order_map = {
            "По убыванию": "desc",
            "По возрастанию": "asc"
        }

        params = {
            'sort_by': sort_map.get(sort_by, 'newest'),
            'order': order_map.get(order, 'desc')
        }


        response = self.session.get(f"{self.task_base_url}/tasks_json", params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('access'):
                tasks = data.get('tasks', [])
                self.display_tasks(tasks)



    def create_task(self):
        title = self.lineEdit_5.text().strip()
        priority = self.comboBox_3.currentText()
        deadline = self.dateEdit.text()

        data = {'title': title, 'priority': priority, 'deadline': deadline}

        response = self.session.post(f"{self.task_base_url}/create_task_json", json=data)

        if response.status_code == 200:
            QtWidgets.QMessageBox.information(self.MainWindow, "Успех", "Задача добавлена!")
            self.load_tasks()

    def find_task(self):
        task_id = self.lineEdit_6.text().strip()

        data = {'task_id': task_id}
        response = self.session.post(f"{self.task_base_url}/task_by_id_json", json=data)

        if response.status_code == 200:
            data = response.json()
            if data.get('access'):
                task = data.get('task', {})


                task_id = task.get('id')
                title = task.get('title', 'Нет названия')
                deadline = task.get('deadline', 'Не установлен')
                is_done = task.get('is_done', False)
                priority = task.get('priority', 'Не указан')


                self.label_14.setText(title)
                self.label_10.setText(str(task_id))
                self.label_11.setText(str(deadline))
                self.label_12.setText("✅ Выполнена" if is_done else "🔄 В работе")
                self.label_13.setText(priority)



                self.pushButton_9.clicked.connect(lambda checked, tid=task_id: self.mark_task_done(tid))
                self.pushButton_8.clicked.connect(lambda checked, tid=task_id: self.delete_task(tid))

    def reload_tasks(self):
        self.load_tasks()







if __name__ == '__main__':
    App()