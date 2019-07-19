!/bin/bash
python3 depth.py &
#pytohn3 ahrs.py &
python3 zmq_engine_client.py &
python3 sonar.py &