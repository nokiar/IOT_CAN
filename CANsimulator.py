import shutil
import argparse
from canlib import canlib, Frame
import random
import time

# Define available bitrates for CAN communication
bitrates = {
    '1M': canlib.canBITRATE_1M,
    '500K': canlib.canBITRATE_500K,
    '250K': canlib.canBITRATE_250K,
    '125K': canlib.canBITRATE_125K,
    '100K': canlib.canBITRATE_100K,
    '62K': canlib.canBITRATE_62K,
    '50K': canlib.canBITRATE_50K,
    '83K': canlib.canBITRATE_83K,
    '10K': canlib.canBITRATE_10K,
}

# Function to print received CAN frames
def printframe(frame, width):
    form = '═^' + str(width - 1)
    print(format(" Frame received ", form))
    print("id:", frame.id)
    print("hex id:", hex(frame.id))
    print("dataX:", frame.data.hex())
    print("data:", bytes(frame.data))
    print("dlc:", frame.dlc)
    print("flags:", frame.flags)
    print("timestamp:", frame.timestamp)

# Function to simulate sending CAN frames
def simulate_can_frames(channel):
    print("Starting CAN frame simulation...")
    while True:
        try:
            # Generate random CAN frame ID and data
            frame_id = random.randint(0x100, 0x7FF)  # Standard CAN ID range
            data = [random.randint(0, 255) for _ in range(8)]  # Random 8-byte data
            
            # Create and send a simulated CAN frame
            frame = Frame(id_=frame_id, data=data, flags=canlib.MessageFlag.STD)
            channel.write(frame)
            print(f"Simulated Frame Sent -> ID: {hex(frame_id)}, Data: {data}")
            
            time.sleep(1)  # Wait 1 second before sending the next frame
        except KeyboardInterrupt:
            print("Simulation stopped.")
            break

# Function to monitor and simulate a CAN channel
def monitor_and_simulate_channel(channel_number, bitrate, ticktime):
    # Open the CAN channel for monitoring and simulation
    ch = canlib.openChannel(channel_number, canlib.canOPEN_ACCEPT_VIRTUAL, bitrate=bitrate)
    ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
    ch.busOn()

    width, height = shutil.get_terminal_size((80, 20))

    timeout = 0.5
    tick_countup = 0

    if ticktime <= 0:
        ticktime = None
    elif ticktime < timeout:
        timeout = ticktime

    print("Listening and simulating on the CAN channel...")
    
    try:
        # Start simulation in a separate thread or loop
        simulate_can_frames(ch)

        while True:
            try:
                # Read incoming frames from the CAN bus
                frame = ch.read(timeout=int(timeout * 1000))
                printframe(frame, width)
            except canlib.CanNoMsg:
                if ticktime is not None:
                    tick_countup += timeout
                    while tick_countup > ticktime:
                        print("tick")
                        tick_countup -= ticktime
            except KeyboardInterrupt:
                print("Stopped monitoring.")
                break
    finally:
        ch.busOff()
        ch.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Simulate and monitor a CAN channel."
    )
    
    parser.add_argument('channel', type=int, default=0, nargs='?',
                        help="CAN channel number to use.")
    
    parser.add_argument('--bitrate', '-b', default='500k',
                        help="Bitrate for the CAN channel. Options: " + ', '.join(bitrates.keys()))
    
    parser.add_argument('--ticktime', '-t', type=float, default=0,
                        help="If greater than zero, display 'tick' every this many seconds.")
    
    args = parser.parse_args()
    
    monitor_and_simulate_channel(args.channel, bitrates[args.bitrate.upper()], args.ticktime)
