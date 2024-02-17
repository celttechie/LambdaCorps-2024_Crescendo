from commands2 import Subsystem, Command, cmd
from phoenix5 import TalonSRX, TalonSRXControlMode
from wpilib import SmartDashboard, AnalogInput, RobotBase
from wpilib.simulation import AnalogInputSim

import constants


class Intake(Subsystem):
    """
    Test class for shooter prototype
    """

    DETECTION_VOLTS_LOWER_BOUND = 1.0
    DETECTION_VOLTS_UPPER_BOUND = 4.0

    def __init__(self):
        super().__init__()

        self._intakeroller = TalonSRX(constants.INTAKE_ROLLER)
        self._intakeroller.configFactoryDefault()
        self._indexroller = TalonSRX(constants.INDEX_ROLLER)
        self._indexroller.configFactoryDefault()
        self._indexleft = TalonSRX(constants.INDEX_LEFT)
        self._indexleft.configFactoryDefault()
        self._indexright = TalonSRX(constants.INDEX_RIGHT)
        self._indexright.configFactoryDefault()

        SmartDashboard.putNumber("IntakeSpeed", 0.3)

        self._detector: AnalogInput = AnalogInput(constants.INTAKE_BEAM_BREAK)

        if RobotBase.isSimulation():
            SmartDashboard.putNumber("SimVolts", 0)
            self._simAnalogInput: AnalogInputSim = AnalogInputSim(0)

    def drive_index(self):
        speed = SmartDashboard.getNumber("IntakeSpeed", 0)
        # def drive_index(self, speed: float):
        self._indexleft.set(TalonSRXControlMode.PercentOutput, speed)
        self._indexright.set(TalonSRXControlMode.PercentOutput, speed)
        self._indexroller.set(TalonSRXControlMode.PercentOutput, speed)
        self._intakeroller.set(TalonSRXControlMode.PercentOutput, speed)

    def stop_indexer(self) -> None:
        self._indexleft.set(TalonSRXControlMode.PercentOutput, 0)
        self._indexright.set(TalonSRXControlMode.PercentOutput, 0)
        self._indexroller.set(TalonSRXControlMode.PercentOutput, 0)
        self._intakeroller.set(TalonSRXControlMode.PercentOutput, 0)

    def has_note(self) -> bool:
        volts = self._detector.getAverageVoltage()

        return (
            volts > self.DETECTION_VOLTS_LOWER_BOUND
            and volts < self.DETECTION_VOLTS_UPPER_BOUND
        )

    def index_note(self, speed: float) -> Command:
        return cmd.run(lambda: self.drive_index()).withTimeout(1).withName("IndexNote")

    def simulationPeriodic(self) -> None:
        self._simAnalogInput.setVoltage(SmartDashboard.getNumber("SimVolts", 0))

    def periodic(self) -> None:
        SmartDashboard.putNumber("RangeVoltage", self._detector.getAverageVoltage())


class IntakeTestCommand(Command):
    """
    Command to run motors of the shooter with a button press
    """

    def __init__(self, intake: Intake):
        super().__init__()
        self._speed = 0
        self._sub = intake

        self.addRequirements(self._sub)

    def initialize(self):
        # self._speed = SmartDashboard.getNumber("IntakeSpeed", 0.3)
        pass

    def execute(self):
        self._sub.drive_index()

    def isFinished(self) -> bool:
        return self._sub.has_note()

    def end(self, interrupted: bool):
        self._sub.stop_indexer()
