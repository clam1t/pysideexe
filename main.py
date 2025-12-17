import sys
import random
import json
import requests
from PySide6 import QtCore, QtWidgets, QtGui
from untitled import Ui_Form
from asd import Ui_MainWindow

class App(Ui_MainWindow):
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.setupUi(self.MainWindow)
        self.base_url = "http://127.0.0.1:5000/user"
        self.task_base_url = "http://127.0.0.1:5000/task"

        self.current_user = None
        self.selected_task_id = None

        self.setup_connections()
        self.setup_ui()

        self.MainWindow.show()

        sys.exit(self.app.exec())

    def setup_connections(self):
        self.pushButton_3.clicked.connect(self.register)
        self.pushButton_2.clicked.connect(self.login)
        self.pushButton.clicked.connect(self.mark_task_done)
        self.pushButton_4.clicked.connect(self.sort_tasks)
        self.pushButton_5.clicked.connect(self.delete_task)

    def setup_ui(self):
        self.tabWidget.hide()
        self.pushButton_3.setText("Регистрация")
        self.pushButton_2.setText("Вход")
        self.pushButton.setText("Отметить выполненной")
        self.pushButton_4.setText("Сортировать")
        self.pushButton_5.setText("Удалить задачу")

        self.tabWidget.setTabText(0, "Все задачи")
        self.tabWidget.setTabText(1, "Новая задача")
        self.tabWidget.setTabText(2, "Найти задачу")

        self.lineEdit_3.setPlaceholderText("Имя пользователя")
        self.lineEdit_4.setPlaceholderText("Пароль")
        self.lineEdit.setPlaceholderText("Имя пользователя")
        self.lineEdit_2.setPlaceholderText("Пароль")

        self.comboBox.addItems(["По умолчанию", "Приоритет", "Дедлайн", "Статус"])
        self.comboBox_2.addItems(["По убыванию", "По возрастанию"])

        self.groupBox.setTitle("Задача")
        self.groupBox_2.setTitle("Сортировка задач")

        self.label_3.setText("Название:")
        self.label_4.setText("ID:")
        self.label_5.setText("Дедлайн:")
        self.label_6.setText("Статус:")
        self.label_7.setText("Уровень сложности:")

        # Создаем контейнер для задач в scrollArea
        self.tasks_container = QtWidgets.QVBoxLayout()
        self.scrollAreaWidgetContents.setLayout(self.tasks_container)

        # Создаем метки для отображения значений (справа от label)
        self.task_title_value = QtWidgets.QLabel("")
        self.task_id_value = QtWidgets.QLabel("")
        self.task_deadline_value = QtWidgets.QLabel("")
        self.task_status_value = QtWidgets.QLabel("")
        self.task_priority_value = QtWidgets.QLabel("")

        # Создаем layout для groupBox с двумя колонками
        # Левая колонка - метки, правая - значения
        details_layout = QtWidgets.QGridLayout()

        # Добавляем метки и значения в сетку
        details_layout.addWidget(self.label_3, 0, 0)  # Название (метка)
        details_layout.addWidget(self.task_title_value, 0, 1)  # Значение названия

        details_layout.addWidget(self.label_4, 1, 0)  # ID (метка)
        details_layout.addWidget(self.task_id_value, 1, 1)  # Значение ID

        details_layout.addWidget(self.label_5, 2, 0)  # Дедлайн (метка)
        details_layout.addWidget(self.task_deadline_value, 2, 1)  # Значение дедлайна

        details_layout.addWidget(self.label_6, 3, 0)  # Статус (метка)
        details_layout.addWidget(self.task_status_value, 3, 1)  # Значение статуса

        details_layout.addWidget(self.label_7, 4, 0)  # Уровень сложности (метка)
        details_layout.addWidget(self.task_priority_value, 4, 1)  # Значение приоритета

        # Устанавливаем растяжение для второй колонки
        details_layout.setColumnStretch(1, 1)

        # Кнопки действий
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(self.pushButton)  # Отметить выполненной
        buttons_layout.addWidget(self.pushButton_5)  # Удалить задачу

        # Основной layout для groupBox
        main_group_layout = QtWidgets.QVBoxLayout()
        main_group_layout.addLayout(details_layout)
        main_group_layout.addLayout(buttons_layout)
        main_group_layout.addStretch()

        self.groupBox.setLayout(main_group_layout)


    def register(self):
        username = self.lineEdit_3.text().strip()
        password = self.lineEdit_4.text().strip()

        data = {'username': username, 'password': password}


        response = requests.post(f"{self.base_url}/register_qt", json=data)

        if response.status_code == 201:
            self.after_login(username)

    def login(self):
        username = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()

        data = {'username': username, 'password': password}


        response = requests.post(f"{self.base_url}/login_qt", json=data)

        if response.status_code == 200:
            self.after_login(username)


    def after_login(self, username):
        self.tabWidget.show()
        self.widget_2.hide()
        self.widget.hide()
        username = self.current_user.get('username')
        self.load_tasks()

    def load_tasks(self):
        response = requests.get(f"{self.task_base_url}/tasks_json")

        if response.status_code == 200:
            data = response.json()
            if data.get('access'):
                tasks = data.get('tasks', [])
                self.display_tasks(tasks)
                self.status_label.setText(f"Загружено задач: {len(tasks)}")
                self.clear_task_details()

    def display_tasks(self, tasks):
        """Отображение задач в scrollArea"""
        # Очищаем контейнер
        for i in reversed(range(self.tasks_container.count())):
            widget = self.tasks_container.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not tasks:
            no_tasks_label = QtWidgets.QLabel("Задачи не найдены")
            no_tasks_label.setAlignment(QtCore.Qt.AlignCenter)
            self.tasks_container.addWidget(no_tasks_label)
            return

        for task in tasks:
            task_widget = self.create_task_widget(task)
            self.tasks_container.addWidget(task_widget)

        self.tasks_container.addStretch()

    def create_task_widget(self, task):
        """Создание виджета для одной задачи"""
        task_id = task.get('id', '?')
        task_title = task.get('title', 'Без названия')
        is_done = task.get('is_done', False)
        priority = task.get('priority', 'medium')

        # Создаем текст кнопки
        status_icon = '✅' if is_done else '⏳'

        task_btn = QtWidgets.QPushButton(f"#{task_id}: {task_title} {status_icon}")




        # При клике показываем детали
        task_btn.clicked.connect(lambda checked, t=task: self.show_task_details(t))

        return task_btn

    def show_task_details(self, task):
        """Показать детали выбранной задачи"""
        self.selected_task_id = task['id']

        # Заполняем значения в правой панели
        self.task_title_value.setText(task.get('title', 'Нет названия'))
        self.task_id_value.setText(str(task.get('id', 'N/A')))

        # Дедлайн
        deadline = task.get('deadline', 'Не установлен')
        self.task_deadline_value.setText(deadline)

        # Статус
        is_done = task.get('is_done', False)
        status_text = "Выполнена ✅" if is_done else "В работе ⏳"
        self.task_status_value.setText(status_text)

        # Приоритет/уровень сложности
        priority = task.get('priority', 'Не указан')
        priority_text = f"{self.get_priority_icon(priority)} {priority.upper()}"
        self.task_priority_value.setText(priority_text)

        # Настраиваем стили
        self.update_details_style(is_done, priority, deadline)

    def mark_task_done(self):
        """Отметить выбранную задачу как выполненную"""
        if not self.selected_task_id:
            QtWidgets.QMessageBox.warning(self.MainWindow, "Ошибка",
                                          "Сначала выберите задачу из списка")
            return

        try:
            response = requests.post(f"{self.task_base_url}/task/{self.selected_task_id}/done_json")

            if response.status_code == 200:
                QtWidgets.QMessageBox.information(self.MainWindow, "Успех", "Задача отмечена как выполненная")
                self.load_tasks()
            else:
                error_msg = response.json().get('error', 'Неизвестная ошибка')
                QtWidgets.QMessageBox.warning(self.MainWindow, "Ошибка", f"Ошибка: {error_msg}")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self.MainWindow, "Ошибка", f"Ошибка сети: {str(e)}")

    def delete_task(self):
        """Удалить выбранную задачу"""
        if not self.selected_task_id:
            QtWidgets.QMessageBox.warning(self.MainWindow, "Ошибка",
                                          "Сначала выберите задачу из списка")
            return

        reply = QtWidgets.QMessageBox.question(
            self.MainWindow,
            'Подтверждение удаления',
            f'Вы уверены, что хотите удалить задачу #{self.selected_task_id}?\n'
            f'"{self.task_title_value.text()}"',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            try:
                response = requests.post(f"{self.task_base_url}/task/{self.selected_task_id}/delete_json")

                if response.status_code == 200:
                    QtWidgets.QMessageBox.information(self.MainWindow, "Успех", "Задача удалена")
                    self.load_tasks()
                else:
                    error_msg = response.json().get('error', 'Неизвестная ошибка')
                    QtWidgets.QMessageBox.warning(self.MainWindow, "Ошибка", f"Ошибка: {error_msg}")

            except Exception as e:
                QtWidgets.QMessageBox.critical(self.MainWindow, "Ошибка", f"Ошибка сети: {str(e)}")

    def sort_tasks(self):
        """Сортировка задач"""
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

        if not self.current_user:
            QtWidgets.QMessageBox.warning(self.MainWindow, "Ошибка", "Сначала войдите в систему")
            return

        try:
            params = {
                'sort_by': sort_map.get(sort_by, 'newest'),
                'order': order_map.get(order, 'desc')
            }

            response = requests.get(f"{self.task_base_url}/tasks_json", params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get('access'):
                    tasks = data.get('tasks', [])
                    self.display_tasks(tasks)
                    self.status_label.setText(f"Задач: {len(tasks)} ({sort_by}, {order})")
                else:
                    QtWidgets.QMessageBox.warning(self.MainWindow, "Ошибка",
                                                  data.get('error', 'Ошибка доступа'))
            else:
                QtWidgets.QMessageBox.warning(self.MainWindow, "Ошибка",
                                              f"Ошибка сервера: {response.status_code}")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self.MainWindow, "Ошибка", f"Ошибка: {str(e)}")

    def logout(self):
        """Выход из системы"""
        self.current_user = None
        self.selected_task_id = None
        self.tabWidget.hide()
        self.widget_2.show()
        self.widget.show()
        self.status_label.setText("Выход выполнен")
        self.clear_task_details()

        for i in reversed(range(self.tasks_container.count())):
            widget = self.tasks_container.itemAt(i).widget()
            if widget:
                widget.deleteLater()

if __name__ == '__main__':
    App()
