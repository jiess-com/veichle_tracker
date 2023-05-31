import subprocess
path="./videos/1.mp4"
def v_track():
    command = "python tools/demo_track.py image -f exps/example/mot/war.py -c ./models/car.pth.tar --path "+path+" --fp16 --fuse --save_result"
    subprocess.run(command, shell=True)