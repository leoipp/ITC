from Modelos_db import Database
from PyQt5 import QtWidgets, uic
from sympy import *
import csv
import sys
import os
from pandasmodel import pandasModel
import numpy as np
import pandas as pd
import matplotlib
import resources
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)
matplotlib.use("Qt5Agg")


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MainWD(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi(resource_path("MainGUI.ui"), self)

        # Eventos de botoes
        self.remover.clicked.connect(lambda: self.apagar())
        self.cadastrar.clicked.connect(lambda: self.cadastrar_modelos())
        self.limpar.clicked.connect(lambda: self.limpar_inputs())
        self.salvar.clicked.connect(lambda: self.att_database())
        self.abrir.clicked.connect(lambda: self.abrir_base())
        self.nova_base.clicked.connect(lambda: self.criar_base())
        self.exportar.clicked.connect(lambda: self.exportar_base())
        self.plotar.clicked.connect(lambda: self.pre_processamento())
        self.importar.clicked.connect(lambda: self.importar_dados())
        self.processar.clicked.connect(lambda:self.processamento_valores())

        self.db = None
        self.abs_path = None

        self.Imeses = tuple(np.arange(141))
        self.t = tuple(np.arange(0.1, 11.8, 0.1))

        figure = Figure()
        axis = figure.add_subplot()
        self.initialize_figure(figure, axis)

    def popular_modelos(self):
        self.table_modelos.setRowCount(0)
        for row_number, row_data in enumerate(self.db.fetch_modelos()):
            self.table_modelos.insertRow(row_number)
            for colum_number, data in enumerate(row_data):
                self.table_modelos.setItem(row_number, colum_number, QtWidgets.QTableWidgetItem(str(data)))

        self.table_derivadas.setRowCount(0)
        for row_number, row_data in enumerate(self.db.fetch_derivadas()):
            self.table_derivadas.insertRow(row_number)
            for colum_number, data in enumerate(row_data):
                self.table_derivadas.setItem(row_number, colum_number, QtWidgets.QTableWidgetItem(str(data)))

        self.table_valores.setRowCount(0)
        for row_number, row_data in enumerate(self.db.fetch_valores()):
            self.table_valores.insertRow(row_number)
            for colum_number, data in enumerate(row_data):
                self.table_valores.setItem(row_number, colum_number, QtWidgets.QTableWidgetItem(str(data)))

    def att_database(self):
        row = self.table_modelos.currentRow()
        vals = []
        for i in range(0, 9):
            vals.append(self.table_modelos.item(row, i).text())
        self.db.update_modelos(int(vals[0]), vals[1], vals[2], float(vals[3]),
                               float(vals[4]), float(vals[5]), float(vals[6]), float(vals[7]), vals[8])
        self.popular_modelos()

    def apagar(self):
        row_modelos = self.table_modelos.currentRow()
        if row_modelos >= 0:
            indices = self.table_modelos.selectionModel().selectedRows()
            row = self.table_modelos.currentRow()
            xa = self.table_modelos.item(row, 0).text()
            self.db.remove(xa)
            for each_row in reversed(sorted(indices)):
                self.table_modelos.removeRow(each_row.row())
            for each_row in reversed(sorted(indices)):
                self.table_derivadas.removeRow(each_row.row())
            for each_row in reversed(sorted(indices)):
                self.table_valores.removeRow(each_row.row())
        row_derivadas = self.table_derivadas.currentRow()
        if row_derivadas >= 0:
            indices = self.table_derivadas.selectionModel().selectedRows()
            row = self.table_derivadas.currentRow()
            xa = self.table_derivadas.item(row, 0).text()
            self.db.remove(xa)
            for each_row in reversed(sorted(indices)):
                self.table_modelos.removeRow(each_row.row())
            for each_row in reversed(sorted(indices)):
                self.table_derivadas.removeRow(each_row.row())
            for each_row in reversed(sorted(indices)):
                self.table_valores.removeRow(each_row.row())
    def cadastrar_modelos(self):
        if self.db is not None:
            nome = self.nome_text.text()
            modelo = self.modelo_text.text()
            a = self.a_text.text()
            b = self.b_text.text()
            c = self.c_text.text()
            d = self.d_text.text()
            e = self.e_text.text()
            drel = self.dx_text.text()
            check_parametros_cadastro = [nome, modelo, a, b, c, d, e, drel]
            if len(list(filter(None, check_parametros_cadastro))) == 8:
                self.db.insert_modelos(nome, modelo, float(a), float(b), float(c), float(d), float(e), drel)

                a, b, c, d, e, drel = symbols("a b c d e x")
                xpr = sympify(modelo, convert_xor=True)
                d1 = diff(xpr, drel)
                d2 = diff(xpr, drel, 2)
                d3 = diff(xpr, drel, 3)
                d4 = diff(xpr, drel, 4)
                self.db.insert_derivadas(modelo, str(d1), str(d2), str(d3), str(d4))
                self.popular_modelos()
            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText("Todos campos de input devem ser preenchidos")
                msg.setWindowTitle("Erro CAD")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                retval = msg.exec_()
        elif self.db is None:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Nenhuma DataBase Encontrada - Criar/Importar.")
            msg.setWindowTitle("Erro DB")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            retval = msg.exec_()
        else:
            pass

    def limpar_inputs(self):
        try:
            self.nome_text.setText("")
            self.modelo_text.setText("")
            self.a_text.setText("")
            self.b_text.setText("")
            self.c_text.setText("")
            self.d_text.setText("")
            self.e_text.setText("")
            self.dx_text.setText("")
        except:
            pass

    def abrir_base(self):
        base_path = QtWidgets.QFileDialog.getOpenFileName(self, "Abrir - DB Modelos", "./", "Arquivos SQL (*.db)")
        if not base_path:
            return
        try:
            with open(base_path[0], "r") as f:
                base_path = os.path.normpath(base_path[0])
                self.db = Database(base_path)
                self.abs_path = base_path
                return self.popular_modelos()
        except:
            return

    def criar_base(self):
        base_path = QtWidgets.QFileDialog.getSaveFileName(self, "Criar - DB Modelos", "./", "SQlite3 (*.db)")
        base_path = os.path.normpath(base_path[0])
        if not base_path:
            return
        elif base_path != ".":
            self.abs_path = base_path
            self.db = Database(base_path)

            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Base de dados criada")
            msg.setWindowTitle("Criação de DataBase")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            retval = msg.exec_()
            return self.popular_modelos()
        else:
            pass

    def exportar_base(self):
        base_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Exportar - DB Modelos", "./")
        base_path = os.path.normpath(base_path)
        if self.db is not None and self.abs_path is not None:
            arq_nome = os.path.split(self.abs_path)[-1]
            arq_nome = arq_nome.split(".")[0]
            with open(f"{base_path}\\{arq_nome}_modelos.csv", "w", newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                # csv_writer.writerow([i[0] for i in self.db.headers()])  # write headers
                csv_writer.writerows(self.db.fetch_modelos())
            with open(f"{base_path}\\{arq_nome}_derivadas.csv", "w", newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                # csv_writer.writerow([i[0] for i in self.db.headers()])  # write headers
                csv_writer.writerows(self.db.fetch_derivadas())
            with open(f"{base_path}\\{arq_nome}_valores.csv", "w", newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                # csv_writer.writerow([i[0] for i in self.db.headers()])  # write headers
                csv_writer.writerows(self.db.fetch_valores())

            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Tabelas exportadas com sucesso")
            msg.setWindowTitle("Exportação de tabelas")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            retval = msg.exec_()
        else:
            pass
        return

    # noinspection PyUnusedLocal
    def pre_processamento(self):
        """
        Todas as derivadas que serão utilizadas são calculadas por esta função.
        Y'
        Y''
        Y'''
        Y''''
        :return: Uma lista com todas as derivadas
        """

        row_modelos = self.table_modelos.currentRow()
        row_derivadas = self.table_derivadas.currentRow()
        if row_modelos >= 0:
            row = self.table_modelos.currentRow()
            vals = []
            for i in range(0, 9):
                vals.append(self.table_modelos.item(row, i).text())
            vals2 = []
            for i in range(0, 4):
                vals2.append(self.table_derivadas.item(row, i).text())

            a, b, c, d, e, vals[8] = symbols("a b c d e x")

            m = sympify(vals2[1], convert_xor=True)
            m0 = m.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                         (d, float(vals[6])), (e, float(vals[7]))])
            m0 = [m0.subs(vals[8], v) for v in self.t]
            m1 = diff(m, vals[8], 1)
            m1 = m1.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                          (d, float(vals[6])), (e, float(vals[7]))])
            m1 = [m1.subs(vals[8], v) for v in self.t]
            m2 = diff(m, vals[8], 2)
            m2 = m2.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                         (d, float(vals[6])), (e, float(vals[7]))])
            m2 = [m2.subs(vals[8], v) for v in self.t]
            m3 = diff(m, vals[8], 3)
            m3 = m3.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                         (d, float(vals[6])), (e, float(vals[7]))])
            m3 = [m3.subs(vals[8], v) for v in self.t]
            m4 = diff(m, vals[8], 4)
            m4 = m4.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                         (d, float(vals[6])), (e, float(vals[7]))])
            m4 = [m4.subs(vals[8], v) for v in self.t]
            ima = [prd/t for prd, t in zip(m0, self.t)]

            # Calculando os maximos e minimos para cada caso
            m0max = max(m0)
            m0max_idx = m0.index(m0max)
            idade_m0max = self.t[m0max_idx]
            m0min = min(m0)
            m0min_idx = m0.index(m0min)
            idade_m0min = self.t[m0min_idx]
            m1max = max(m1)
            m1max_idx = m1.index(m1max)
            idade_m1max = self.t[m1max_idx]
            prod_ica = m0[m1max_idx]
            m1min = min(m1)
            m1min_idx = m1.index(m1min)
            idade_m1min = self.t[m1min_idx]
            m2max = max(m2)
            m2max_idx = m2.index(m2max)
            idade_m2max = self.t[m2max_idx]
            acl_max = m0[m2max_idx]
            m2min = min(m2)
            m2min_idx = m2.index(m2min)
            idade_m2min = self.t[m2min_idx]
            acl_min = m0[m2min_idx]
            m3max = max(m3)
            m3max_idx = m3.index(m3max)
            idade_m3max = self.t[m3max_idx]
            m3min = min(m3)
            m3min_idx = m3.index(m3min)
            idade_m3min = self.t[m3min_idx]
            m4max = max(m4)
            m4max_idx = m4.index(m4max)
            idade_m4max = self.t[m4max_idx]
            m4min = min(m4)
            m4min_idx = m4.index(m4min)
            idade_m4min = self.t[m4min_idx]
            imamax = max(ima[19:])
            imamax_idx = ima.index(imamax)
            idade_imamax = self.t[imamax_idx]
            imamin = min(ima[19:])
            imamin_idx = ima.index(imamin)
            idade_imamin = self.t[imamin_idx]

            # Plotando os resultandos
            # Limpando o que estava no grafico antes
            self.ax.clear()
            # Plot data, labels, colors, ...
            self.ax.set_xlabel('Idade (anos)')
            self.ax.set_title(f"{vals[1]}")
            self.ax.plot(self.t, m0)
            # IMA Maximo
            label1 = f"IMAmáx aos {idade_imamax:.1f} = {imamax:.2f}"
            self.ax.plot(idade_imamax, idade_imamax * imamax, "D", label=label1)
            self.ax.legend(loc="best")
            # ICA Maximo
            label2 = f"ICAmáx aos {idade_m1max:.1f}"
            self.ax.plot(idade_m1max, prod_ica, "p", color="yellow", label=label2)
            self.ax.legend(loc="best")
            # Aceleração Maxima
            label3 = f"Acl.máx aos {idade_m2max:.1f}"
            self.ax.plot(idade_m2max, acl_max, "o", color="green", label=label3)
            self.ax.legend(loc="best")
            label4 = f"Dcl.máx aos {idade_m2min:.1f}"
            self.ax.plot(idade_m2min, acl_min, "o", color="green", label=label4)
            self.ax.legend(loc="best")
            # Make sure everything fits inside the canvas
            self.fig.tight_layout()
            # plotar a nova figura na interface
            self.canvas.draw()

            self.ax2.clear()
            self.ax.set_xlabel('Idade (anos)')
            self.ax2.plot(self.t, m1, color="red")
            self.ax2.plot(self.t, m2, color="orange")
            self.ax2.plot(self.t, m3, color="purple")
            self.ax2.hlines(y=0, xmin=0, xmax=12, color='black')
            self.ax.plot(idade_m1max, 0, "p", color="yellow")
            self.ax.plot(idade_m1max, m1max, "p", color="yellow")
            self.ax.plot(idade_m2max, 0, "o", color="green")
            self.ax.plot(idade_m2max, m2max, "o", color="green")
            self.ax.plot(idade_m2min, 0, "o", color="green")
            self.ax.plot(idade_m2min, m2min, "o", color="green")
            self.fig2.tight_layout()
            self.canvas2.draw()

            self.popular_modelos()

        elif row_derivadas >= 0:
            row = self.table_derivadas.currentRow()
            vals = []
            for i in range(0, 9):
                vals.append(self.table_modelos.item(row, i).text())
            vals2 = []
            for i in range(0, 4):
                vals2.append(self.table_derivadas.item(row, i).text())

            a, b, c, d, e, vals[8] = symbols("a b c d e x")

            m = sympify(vals2[1], convert_xor=True)
            m0 = m.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                         (d, float(vals[6])), (e, float(vals[7]))])
            m0 = [m0.subs(vals[8], v) for v in self.t]
            m1 = diff(m, vals[8], 1)
            m1 = m1.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                          (d, float(vals[6])), (e, float(vals[7]))])
            m1 = [m1.subs(vals[8], v) for v in self.t]
            m2 = diff(m, vals[8], 2)
            m2 = m2.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                          (d, float(vals[6])), (e, float(vals[7]))])
            m2 = [m2.subs(vals[8], v) for v in self.t]
            m3 = diff(m, vals[8], 3)
            m3 = m3.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                          (d, float(vals[6])), (e, float(vals[7]))])
            m3 = [m3.subs(vals[8], v) for v in self.t]
            m4 = diff(m, vals[8], 4)
            m4 = m4.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                          (d, float(vals[6])), (e, float(vals[7]))])
            m4 = [m4.subs(vals[8], v) for v in self.t]
            ima = [prd / t for prd, t in zip(m0, self.t)]

            # Calculando os maximos e minimos para cada caso
            m0max = max(m0)
            m0max_idx = m0.index(m0max)
            idade_m0max = self.t[m0max_idx]
            m0min = min(m0)
            m0min_idx = m0.index(m0min)
            idade_m0min = self.t[m0min_idx]
            m1max = max(m1)
            m1max_idx = m1.index(m1max)
            idade_m1max = self.t[m1max_idx]
            prod_ica = m0[m1max_idx]
            m1min = min(m1)
            m1min_idx = m1.index(m1min)
            idade_m1min = self.t[m1min_idx]
            m2max = max(m2)
            m2max_idx = m2.index(m2max)
            idade_m2max = self.t[m2max_idx]
            acl_max = m0[m2max_idx]
            m2min = min(m2)
            m2min_idx = m2.index(m2min)
            idade_m2min = self.t[m2min_idx]
            acl_min = m0[m2min_idx]
            m3max = max(m3)
            m3max_idx = m3.index(m3max)
            idade_m3max = self.t[m3max_idx]
            m3min = min(m3)
            m3min_idx = m3.index(m3min)
            idade_m3min = self.t[m3min_idx]
            m4max = max(m4)
            m4max_idx = m4.index(m4max)
            idade_m4max = self.t[m4max_idx]
            m4min = min(m4)
            m4min_idx = m4.index(m4min)
            idade_m4min = self.t[m4min_idx]
            imamax = max(ima[19:])
            imamax_idx = ima.index(imamax)
            idade_imamax = self.t[imamax_idx]
            imamin = min(ima[19:])
            imamin_idx = ima.index(imamin)
            idade_imamin = self.t[imamin_idx]

            # Plotando os resultandos
            # Limpando o que estava no grafico antes
            self.ax.clear()
            # Plot data, labels, colors, ...
            self.ax.set_xlabel('Idade (anos)')
            self.ax.set_title(f"{vals[1]}")
            self.ax.plot(self.t, m0)
            # IMA Maximo
            label1 = f"IMAmáx aos {idade_imamax:.1f} = {imamax:.2f}"
            self.ax.plot(idade_imamax, idade_imamax * imamax, "D", label=label1)
            self.ax.legend(loc="best")
            # ICA Maximo
            label2 = f"ICAmáx aos {idade_m1max:.1f}"
            self.ax.plot(idade_m1max, prod_ica, "p", color="yellow", label=label2)
            self.ax.legend(loc="best")
            # Aceleração Maxima
            label3 = f"Acl.máx aos {idade_m2max:.1f}"
            self.ax.plot(idade_m2max, acl_max, "o", color="green", label=label3)
            self.ax.legend(loc="best")
            label4 = f"Dcl.máx aos {idade_m2min:.1f}"
            self.ax.plot(idade_m2min, acl_min, "o", color="green", label=label4)
            self.ax.legend(loc="best")
            # Make sure everything fits inside the canvas
            self.fig.tight_layout()
            # plotar a nova figura na interface
            self.canvas.draw()

            self.ax2.clear()
            self.ax.set_xlabel('Idade (anos)')
            self.ax2.plot(self.t, m1, color="red")
            self.ax2.plot(self.t, m2, color="orange")
            self.ax2.plot(self.t, m3, color="purple")
            self.ax2.hlines(y=0, xmin=0, xmax=12, color='black')
            self.ax.plot(idade_m1max, 0, "p", color="yellow")
            self.ax.plot(idade_m1max, m1max, "p", color="yellow")
            self.ax.plot(idade_m2max, 0, "o", color="green")
            self.ax.plot(idade_m2max, m2max, "o", color="green")
            self.ax.plot(idade_m2min, 0, "o", color="green")
            self.ax.plot(idade_m2min, m2min, "o", color="green")
            self.fig2.tight_layout()
            self.canvas2.draw()

            self.popular_modelos()
        else:
            pass

    def processamento_valores(self):
        row_modelos = self.table_modelos.currentRow()
        row_derivadas = self.table_derivadas.currentRow()
        if row_modelos >= 0:
            row = self.table_modelos.currentRow()
            vals = []
            for i in range(0, 9):
                vals.append(self.table_modelos.item(row, i).text())
            vals2 = []
            for i in range(0, 4):
                vals2.append(self.table_derivadas.item(row, i).text())

            a, b, c, d, e, vals[8] = symbols("a b c d e x")

            m = sympify(vals2[1], convert_xor=True)
            m0 = m.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                         (d, float(vals[6])), (e, float(vals[7]))])
            m0 = [m0.subs(vals[8], v) for v in self.t]
            m1 = diff(m, vals[8], 1)
            m1 = m1.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                          (d, float(vals[6])), (e, float(vals[7]))])
            m1 = [m1.subs(vals[8], v) for v in self.t]
            m2 = diff(m, vals[8], 2)
            m2 = m2.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                          (d, float(vals[6])), (e, float(vals[7]))])
            m2 = [m2.subs(vals[8], v) for v in self.t]
            m3 = diff(m, vals[8], 3)
            m3 = m3.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                          (d, float(vals[6])), (e, float(vals[7]))])
            m3 = [m3.subs(vals[8], v) for v in self.t]
            m4 = diff(m, vals[8], 4)
            m4 = m4.subs([(a, float(vals[3])), (b, float(vals[4])), (c, float(vals[5])),
                          (d, float(vals[6])), (e, float(vals[7]))])
            m4 = [m4.subs(vals[8], v) for v in self.t]
            ima = [prd / t for prd, t in zip(m0, self.t)]

            # Calculando os maximos e minimos para cada caso
            m0max = max(m0)
            m0max_idx = m0.index(m0max)
            idade_m0max = self.t[m0max_idx]
            m0min = min(m0)
            m0min_idx = m0.index(m0min)
            idade_m0min = self.t[m0min_idx]
            m1max = max(m1)
            m1max_idx = m1.index(m1max)
            idade_m1max = self.t[m1max_idx]
            prod_ica = m0[m1max_idx]
            m1min = min(m1)
            m1min_idx = m1.index(m1min)
            idade_m1min = self.t[m1min_idx]
            m2max = max(m2)
            m2max_idx = m2.index(m2max)
            idade_m2max = self.t[m2max_idx]
            acl_max = m0[m2max_idx]
            m2min = min(m2)
            m2min_idx = m2.index(m2min)
            idade_m2min = self.t[m2min_idx]
            acl_min = m0[m2min_idx]
            m3max = max(m3)
            m3max_idx = m3.index(m3max)
            idade_m3max = self.t[m3max_idx]
            m3min = min(m3)
            m3min_idx = m3.index(m3min)
            idade_m3min = self.t[m3min_idx]
            m4max = max(m4)
            m4max_idx = m4.index(m4max)
            idade_m4max = self.t[m4max_idx]
            m4min = min(m4)
            m4min_idx = m4.index(m4min)
            idade_m4min = self.t[m4min_idx]
            imamax = max(ima[19:])
            imamax_idx = ima.index(imamax)
            idade_imamax = self.t[imamax_idx]
            imamin = min(ima[19:])
            imamin_idx = ima.index(imamin)
            idade_imamin = self.t[imamin_idx]

            if self.db.fetch_um_valores(vals[1]):
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText("Valores já cadastrados para este modelo")
                msg.setWindowTitle("Processamento inválido")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                retval = msg.exec_()
            else:
                self.db.insert_valores(str(vals[1]), float(imamax), float(idade_imamax), float(idade_m1max),
                                       float(idade_m2max), float(idade_m2min))
                self.popular_modelos()

    def initialize_figure(self, fig, ax):
        # Figure creation (self.fig and self.ax)
        self.fig = fig
        self.ax = ax
        # Canvas creation
        self.canvas = FigureCanvas(self.fig)
        self.plotLayout.addWidget(self.canvas)
        self.canvas.draw()
        # Figure creation (self.fig and self.ax)
        self.fig2 = fig
        self.ax2 = ax
        self.canvas2 = FigureCanvas(self.fig2)
        self.plotLayout2.addWidget(self.canvas2)
        self.canvas2.draw()

    def importar_dados(self):
        self.w = QtWidgets.QDialog()
        uic.loadUi(resource_path("importGUI.ui"), self.w)

        self.w.importar.clicked.connect(lambda: abrir_dados())
        self.w.concluir.clicked.connect(lambda: concluir_importacao())

        self.w.df = None

        def abrir_dados():
            fname1 = QtWidgets.QFileDialog.getOpenFileName(self, "Importação Database", "./", "Arquivos Excel (*.xlsx)")
            if not fname1:
                return
            if fname1:
                df = pd.read_excel(fname1[0])
                self.w.df = df
                items = df.columns.values.tolist()
                self.w.n1.addItems(items)
                self.w.n2.addItems(items)
                self.w.n3.addItems(items)
                self.w.n4.addItems(items)
                self.w.n5.addItems(items)
                self.w.n6.addItems(items)
                self.w.n7.addItems(items)
                self.w.n8.addItems(items)
                model = pandasModel(df)
                self.w.tableView.setModel(model)
            if fname1 is None:
                pass

        def concluir_importacao():
            df_ajustado = self.w.df[[self.w.n1.currentText(), self.w.n2.currentText(), self.w.n3.currentText(),
                                     self.w.n4.currentText(), self.w.n5.currentText(), self.w.n6.currentText(),
                                     self.w.n7.currentText(), self.w.n8.currentText()]]
            if self.db is not None:
                for i, v in df_ajustado.iterrows():
                    self.db.insert_modelos(str(v[0]), str(v[1]), float(v[2]),
                                           float(v[3]), float(v[4]), float(v[5]), float(v[6]), str(v[7]))
                    vals = [str(v[0]), str(v[1]), float(v[2]), float(v[3]),
                            float(v[4]), float(v[5]), float(v[6]), str(v[7])]
                    a, b, c, d, e, vals[7] = symbols("a b c d e x")
                    xpr = sympify(vals[1], convert_xor=True)
                    d1 = diff(xpr, vals[7])
                    d2 = diff(xpr, vals[7], 2)
                    d3 = diff(xpr, vals[7], 3)
                    d4 = diff(xpr, vals[7], 4)
                    self.db.insert_derivadas(vals[1], str(d1), str(d2), str(d3), str(d4))
                    self.popular_modelos()
            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText("Nenhuma DataBase Selecionada")
                msg.setWindowTitle("Erro Database")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                retval = msg.exec_()

        self.w.exec_()


if __name__ == "__main__":
    MainApp = QtWidgets.QApplication(sys.argv)
    App = MainWD()
    App.show()
    sys.exit(MainApp.exec_())


IMACEL = (DB1 + DB2/ 2 * (IMA/0,97) * RD) * VPL