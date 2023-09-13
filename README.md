# Autonomous Vehicle Prototype

## TODO:

#### Separate concerns between tensorflow lite model and pycamera

#### Create streaming reading of picamera with picamera[array] method
- Every one second capture a frame

#### Implement wheel information and create Odometer Class
- Populate with wheel information and correct methods for managing odometer data
- handle movement mode (forward, backward, rotational)
- update map if rotational
- update for map if forward/backward
- account for vehicle size in map
- account for offset from init of map to handle map updating of objects
- ie. map(index=(i,j)) is a function of (change of position from initialization, distance reading)
    - technically, you could slap current map onto larger map if distance relative to start goes to new extreme.
    - For example. distance from start in beginning iz zero and have 100x100 array. But, if go forward we'll have (101x100) array which we init as zeros and then combine (add) to original at equivalent indicies


#### Implement Occupancy map
