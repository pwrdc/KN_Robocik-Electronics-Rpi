MODE = 'ROV4' # 'ROV3' or 'ROV4'


class DEFLOG:
    LOG_DIRECTORY = "logs/electro/"

    DEPTH_LOCAL_LOG = True

    AHRS_LOCAL_LOG = True

    HYDROPHONES_LOCAL_LOG = False

    DISTANCE_LOCAL_LOG = True

    MOVEMENTS_LOCAL_LOG = True
    MANIPULATOR_LOCAL_LOG = False
    TORPEDOES_LOCAL_LOG = False

class USB:
    # Default mount point of usb sensors
    SONAR = "/dev/ttyUSB_SONAR"
