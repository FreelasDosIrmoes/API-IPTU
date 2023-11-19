from rpa.rpa import Automation


robot = Automation()
robot.process_flux('51502046')
robot.extract_dados_web()
