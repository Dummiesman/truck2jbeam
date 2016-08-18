import sys, os
from rig import Rig

if __name__ == "__main__":
  # have enough args?
  args = sys.argv[1:]
  if len(args) == 0:
    print("Usage: truck2jbeam.py <RoR Rig File (e.g. mycar.truck)>")
    sys.exit(1)
  
  # file exists?
  rigfile = args[0]
  if not os.path.isfile(rigfile):
    print(args[0] + " doesn't exist! Aborting :(")
    sys.exit(1)
    
  # convert file
  r = Rig()
  r.type = os.path.splitext(rigfile)[1][1:].lower()
  print("Parsing *." + r.type + " file...")
  r.from_file(rigfile)
  
  
  print("Calculating node masses...")
  r.calculate_masses()
  
  print("Writing JBeam...")
  r.to_jbeam(os.path.splitext(rigfile)[0] + ".jbeam")
  
  print("Conversion complete!")