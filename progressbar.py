from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QLabel, QLineEdit, QProgressBar, \
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QDialogButtonBox

class ProgressBar(QDialog):
    def __init__(self, fileIndex, filenum, parent=None):
        super(ProgressBar, self).__init__(parent)

        self.fileIndex = fileIndex
        self.filenum = filenum

        self.resize(350, 100)
        self.setWindowTitle(self.tr("Processing progress"))

        self.TipLabel = QLabel(self.tr("Processing:" + "  " + str(fileIndex) + "/" + str(filenum)))
        self.FeatLabel = QLabel(self.tr("Synthesizing:"))

        self.FeatProgressBar = QProgressBar(self)
        self.FeatProgressBar.setMinimum(0)
        self.FeatProgressBar.setMaximum(filenum)  # 总进程换算为100
        self.FeatProgressBar.setValue(0)  # 进度条初始值为0

        TipLayout = QHBoxLayout()
        TipLayout.addWidget(self.TipLabel)

        FeatLayout = QHBoxLayout()
        FeatLayout.addWidget(self.FeatLabel)
        FeatLayout.addWidget(self.FeatProgressBar)

        self.cancelButton = QPushButton('cancel', self)

        self.cancelButton.setDisabled(True)

        buttonlayout = QHBoxLayout()
        buttonlayout.addStretch(1)
        buttonlayout.addWidget(self.cancelButton)

        layout = QVBoxLayout()
        layout.addLayout(FeatLayout)
        layout.addLayout(TipLayout)
        layout.addLayout(buttonlayout)
        self.setLayout(layout)

        self.cancelButton.clicked.connect(self.onCancel)

    def setValue(self, value):
        self.FeatProgressBar.setValue(value)
        self.TipLabel.setText(self.tr("Processing:" + "  " + str(value) + "/" + str(self.filenum)))
        if value == self.filenum:
            self.cancelButton.setEnabled(True)

    def onCancel(self, event):
        self.close()