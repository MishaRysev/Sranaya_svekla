import sys
import algs
import pyqtgraph
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import *
from PySide6.QtCore import QFile, QIODevice, Slot

def LoadGUI(name: str):
    ui_file_name = name
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
        sys.exit(-1)
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    return window





uiclass, baseclass = pyqtgraph.Qt.loadUiType("app.ui")

class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.gr.addLegend()
        self.gr.setBackground("#EDF5E1")
        self.gr.setMouseEnabled(x=False, y=False)
        self.pushButton.clicked.connect(self.get_values)

    @Slot()
    def get_values(self):
        values = dict()
        values["batch_count"] = int(self.batch_count.text())
        values["min_sug"] = float(self.min_s.text())
        values["max_sug"] = float(self.max_s.text())
        values["min_deg"] = float(self.min_d.text())
        values["max_deg"] = float(self.max_s.text())
        values["dop_cond"] = self.dop_condition.isChecked()
        values["rip_per"] = int(self.rip_per.text())
        values["minK"] = 4.8
        values["maxK"] = 7.05
        values["minNa"] = 0.21
        values["maxNa"] = 0.28
        values["minN"] = 1.58
        values["maxN"] = 2.8
        values["minRip"] = float(self.min_r.text())
        values["maxRip"] = float(self.max_r.text())
        self.run(values)

    def run(self, values: dict):

        count_of_exp = int(self.exp_count.text())
        coef_rip = algs.gen_random_matrix(values["batch_count"], values["rip_per"], values["minRip"], values["maxRip"])
        coef_deg = algs.gen_random_matrix(values["batch_count"], values["batch_count"] - values["rip_per"],
                                          values["minRip"], values["maxRip"])
        matr = algs.merge_matrices(coef_rip, coef_deg)
        matr_to_algs = algs.gen_random_base_matrix(values["batch_count"], values["min_sug"], values["max_sug"], matr)
        if values["dop_cond"]:
            inorganic_matr = algs.gen_inorganic_matrix(values["batch_count"], values["minK"], values["maxK"],
                                                       values["minNa"], values["maxNa"], values["minN"], values["maxN"])
            matr_to_algs = algs.get_inorganic(matr_to_algs, inorganic_matr)

        days = [i for i in range(1, values["batch_count"] + 1)]
        hun_mean = [0 for i in range(values["batch_count"])]
        gready_mean = [0 for i in range(values["batch_count"])]
        thrifty_mean = [0 for i in range(values["batch_count"])]
        gvt_mean = [0 for i in range(values["batch_count"])]
        tvg_mean = [0 for i in range(values["batch_count"])]
        results = dict()

        for i in range(count_of_exp):

            m = algs.hungarian_max_algorithm(matr_to_algs)[0]
            for j in range(len(m)): hun_mean[j] += m[j] / count_of_exp
            results["венгерский максимальный"] = hun_mean[len(m) - 1]

            m = algs.greedy_algorithm(matr_to_algs)[0]
            for j in range(len(m)): gready_mean[j] += m[j] / count_of_exp
            results["жадный"] = gready_mean[len(m) - 1]

            m = algs.thrifty_algorithm(matr_to_algs)[0]
            for j in range(len(m)): thrifty_mean[j] += m[j] / count_of_exp
            results["бережливый"] = thrifty_mean[len(m) - 1]

            m = algs.greedy_v_thrifty_algorithm(matr_to_algs, values["rip_per"])[0]
            for j in range(len(m)): gvt_mean[j] += m[j] / count_of_exp
            results["жадный/бережливый"] = gvt_mean[len(m) - 1]

            m = algs.thrifty_v_greedy_algorithm(matr_to_algs, values["rip_per"])[0]
            for j in range(len(m)): tvg_mean[j] += m[j] / count_of_exp
            results["бережливый/жадный"] = tvg_mean[len(m) - 1]

        self.gr.clear()
        self.plot(days, hun_mean, "Венгреский максимальный", "#f74040")
        self.plot(days, gready_mean, "Жадный", "#a334f7")
        self.plot(days, thrifty_mean, "Бережливый", "#14b54a")
        self.plot(days, gvt_mean, "Жадный/Бережливый", "#e8a51e")
        self.plot(days, tvg_mean, "Бережлиый/Жадный", "#fa7528")

        for key in results.keys():
            if results[key] == max(results.values()):
                self.good.setText(f"Лучший результат выдал {key} алгоритм")
            if results[key] == min(results.values()):
                self.bad.setText(f"Худший результат выдал {key} алгоритм")

    def plot(self, x, y, name, color):
        pen = pyqtgraph.mkPen(color=color, width=3)
        self.gr.plot(x, y, name=name, pen=pen)



if __name__ == "__main__":

    app = QApplication(sys.argv)
    Window = MainWindow()


    Window.show()
    sys.exit(app.exec())