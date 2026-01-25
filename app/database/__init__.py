class Report:
    def __init__(self, content):
        self.content = content

    def generate(self):
        return f"Report: {self.content}"


class ReportSaver:
    def save_to_file(self, report):
        with open("report.txt", "w") as file:
            file.write(report.generate())


class ReportPrinter:
    def print_report(self, report):
        print(report.generate())
