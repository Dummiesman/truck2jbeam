from rig_common import Node, Beam, Hydro, InternalCamera, Refnodes, Rail, Slidenode, Engine, Engoption, WheelTypeA, WheelTypeB, Flexbody
import re
import sys

def ParseNodeName(name):
  """This function converts nodes1 names into nodes2 style names"""
  if name.isdigit():
      return "node" + name
  else:
    return name


def ParseGroupName(name):
  return name.replace(".mesh","").replace(".","_")




def PrepareLine(line, skip_space_check = False):
  """Component-ize a line"""
  if line[0] == ";" or len(line) == 0:
      return None
  
  # single statement line?
  line_has_spaces = False
  try:
      line.index(' ')
      line_has_spaces = True
  except ValueError:
      # no need to replace spaces
      line_has_spaces = False

  components = None

  line_lst = list(line.lower().replace("\t"," ").replace("\n",""))

  if line_has_spaces and skip_space_check == False:
      line_lst[line.index(' ')] = ','

  # strip empty / bad stuff/ spaces
  line_lst = [x for x in line_lst if x]
  
  rejoined_lst = "".join(line_lst)

  # invalid?
  if len(rejoined_lst) == 0:
      return None
  
  if rejoined_lst.endswith(","):
      rejoined_lst = rejoined_lst[:-1]
  if rejoined_lst.startswith(","):
      rejoined_lst = rejoined_lst[1:]

    
  rejoined_lst = rejoined_lst.replace(",,",",").replace(", ",",").replace(",\t",",")
  components = rejoined_lst.split(',')
  
  for c in range(len(components)):
    components[c] = components[c].strip()
    

  # blank?
  if len(components) == 0:
    return None
  else:
    return components
      
def ParseNode(components, nodes2 = False):
  nid = ParseNodeName(components[0])
  
  nx = float(components[3]) 
  ny = float(components[1])
  nz = float(components[2])
  
  flags = ''
  if len(components) >= 5:
      flags = components[4]
  
  node_object = Node(nid, nx, ny, nz)
  
  # flags parsing
  if 'l' in flags:
      node_object.load_bearer = True
      num_in_flags = re.findall(r"[-+]?\d*\.\d+|\d+", flags)
      if len(num_in_flags) > 0:
        node_object.override_mass = float(num_in_flags[0])
      else:
        num_in_flags = re.findall(r"[-+]?\d*\.\d+|\d+", components[len(components) - 1])
        if len(num_in_flags) > 0:
          node_object.override_mass = float(num_in_flags[0])
  if 'h' in flags:
      node_object.coupler = True
  if 'c' in flags:
      node_object.collision = False
      
  return node_object


def ParseFlexbody(components):
  refnode = ParseNodeName(components[0])
  xnode = ParseNodeName(components[1])
  ynode = ParseNodeName(components[2])
  xoffset = float(components[5])
  yoffset = float(components[3])
  zoffset = float(components[4])
  xrot = float(components[8])
  yrot = float(components[6])
  zrot = float(components[7])
  mesh = components[9]
  return Flexbody(refnode, xnode, ynode, xoffset, yoffset, zoffset, xrot, yrot, zrot, mesh)
  
  
def ParseForset(components):
  ranges = []
  
  for cmps in range(len(components) -1):
    cmp = components[cmps+1]
    if "-" in cmp:
      nodeids = cmp.split("-")
      ranges.append([int(nodeids[0]), int(nodeids[1])])
    else:
      nodeid = int(cmp)
      ranges.append([nodeid, nodeid])
   
  return ranges

  
def ParseRailgroup(components):
  railgroup_id = "railgroup" + components[0]
  railgroup_nodes = []
  
  for g in range(len(components) - 1):
    railgroup_nodes.append(ParseNodeName(components[g]))
    
  return Rail(railgroup_id, railgroup_nodes)
    

def ParseSlidenode(components):
  nodeid = ParseNodeName(components[0])
  rail_nodes = []
  
  spring = 9000000
  tolerance = 0
  strength = 1e400
  railgroup = None
  
  for n in range(len(components) - 1):
    temp_string = components[n+1]
    if not temp_string[0] == "s" or not temp_string[0] == "b" or not temp_string[0] == "t" or not temp_string[0] == "g" or not temp_string[0] == "r" or not temp_string[0] == "d" or not temp_string[0] == "q" or not temp_string[0] == "c":
      rail_nodes.append(ParseNodeName(temp_string))
    elif temp_string[0] == "s":
      spring = float(temp_string[1:])
    elif temp_string[0] == "g":
      railgroup = temp_string[1:]
    elif temp_string[0] == "b":
      strength = float(temp_string[1:])
    elif temp_string[0] == "t":
      tolerance = float(temp_string[1:])
  
  slidenode_object = Slidenode(nodeid, railgroup, spring, strength, tolerance)
  
  if len(rail_nodes) == 0 and railgroup is not None:
    return [slidenode_object, railgroup]
  elif len(rail_nodes) > 0:
    railgroup_id = nodeid + "_rail"
    new_railgroup = Rail(railgroup_id, rail_nodes)
    slidenode_object.rail = railgroup_id
    return [slidenode_object, new_railgroup]
  elif len(rail_nodes) == 0 and railgroup is None:
    print("Incorrect slidenode!! Aborting")
    sys.exit(1)
  
  

def ParseRefnodes(components):
  center = ParseNodeName(components[0])
  back = ParseNodeName(components[1])
  left = ParseNodeName(components[2])
  return Refnodes(center,back,left)


def ParseHydro(components, last_beamspring, last_beamdamp, last_beamstrength, last_beamdeform):
  nid1 = ParseNodeName(components[0])
  nid2 = ParseNodeName(components[1])
      
  factor = float(components[2]) * -1
  
  return Hydro(nid1, nid2, factor, last_beamspring, last_beamdamp, last_beamstrength, last_beamdeform)


def ParseShock2(components, last_beamstrength, last_beamdeform):
  nid1 = ParseNodeName(components[0])
  nid2 = ParseNodeName(components[1])
      
  spring = float(components[2])
  damp = float(components[3])
  shortbound = float(components[10])
  longbound = float(components[11])
  precomp = float(components[12])
  dampout = float(components[7])
  
  # create beam
  beam_obj = Beam(nid1, nid2, spring, damp, last_beamstrength, last_beamdeform)
  beam_obj.type = 'BOUNDED'
  beam_obj.beamShortBound = shortbound
  beam_obj.beamLongBound = longbound
  beam_obj.beamPrecompression = precomp
  beam_obj.beamDampRebound = dampout
  
  return beam_obj
  

def ParseShock(components, last_beamstrength, last_beamdeform):
  nid1 = ParseNodeName(components[0])
  nid2 = ParseNodeName(components[1])
      
  spring = float(components[2])
  damp = float(components[3])
  shortbound = float(components[4])
  longbound = float(components[5])
  precomp = float(components[6])
  
  # create beam
  beam_obj = Beam(nid1, nid2, spring, damp, last_beamstrength, last_beamdeform)
  beam_obj.type = 'BOUNDED'
  beam_obj.beamShortBound = shortbound
  beam_obj.beamLongBound = longbound
  beam_obj.beamPrecompression = precomp
  
  return beam_obj


def ParseEngine(components):
  min_rpm = float(components[0])
  max_rpm = float(components[1])
  torque = float(components[2])
  differential = float(components[3])
  gears = []
  
  # read in gear ratios
  for g in range(len(components) - 4):
    ratio = float(components[g+4])
    if ratio != -1:
      gears.append(ratio)
  
  # fix reverse one
  gears[0] *= -1
  
  return Engine(min_rpm, max_rpm, torque, differential, gears)

  
def ParseEngoption(components):
  num_components = len(components)

  inertia = float(components[0])
  type = components[1]
  
  # get clutch force, default half for cars in RoR
  clutch_force = float(components[2]) if num_components >= 3 else 10000
  if clutch_force == 10000 and num_components < 3:
    if type == "c":
      clutch_force /= 2
  
  # parse other stuff
  shift_time = float(components[3]) if num_components >= 4 else 0.2
  clutch_time = float(components[4]) if num_components >= 5 else 0.5
  post_shift_time = float(components[5]) if num_components >= 6 else 0.2
  stall_rpm = float(components[6]) if num_components >= 7 else 300
  idle_rpm = float(components[7]) if num_components >= 8 else 800
  max_idle_mixture = float(components[8]) if num_components >= 9 else 0.2
  min_idle_mixture = float(components[9]) if num_components >= 10 else 0.0
  
  return Engoption(inertia, type, clutch_force, shift_time, clutch_time, post_shift_time, stall_rpm, idle_rpm, max_idle_mixture, min_idle_mixture)
  
def ParseBeam(components, last_beamspring, last_beamdamp, last_beamstrength, last_beamdeform):
  nid1 = ParseNodeName(components[0])
  nid2 = ParseNodeName(components[1])

  flags = ''
  if len(components) >= 3:
      flags = components[2]
  
  beam_obj = Beam(nid1, nid2, last_beamspring, last_beamdamp, last_beamstrength, last_beamdeform)

  # support beam?
  if 's' in flags:
      beam_obj.beamDamp /= 10
      beam_obj.type = 'SUPPORT'
      beam_obj.beamLongBound = 2.0
      
  return beam_obj

  
def ParseCinecam(components):
  xpos = float(components[2])
  ypos = float(components[0])
  zpos = float(components[1])
  
  n1 = ParseNodeName(components[3])
  n2 = ParseNodeName(components[4])
  n3 = ParseNodeName(components[5])
  n4 = ParseNodeName(components[6])
  n5 = ParseNodeName(components[7])
  n6 = ParseNodeName(components[8])
  
  spring = float(components[11])
  damp = float(components[12])
  
  return InternalCamera(xpos, ypos, zpos, n1, n2, n3, n4, n5, n6, spring, damp)
  

def ParseWheel(components):
  radius = float(components[0])  
  width = float(components[1])
  numrays = int(components[2])
  nid1 = ParseNodeName(components[3])
  nid2 = ParseNodeName(components[4])
  snode = ParseNodeName(components[5])
  braketype = int(components[6])
  drivetype = int(components[7])
  armnode = ParseNodeName(components[8])
  mass = float(components[9])
  spring = float(components[10])
  damp = float(components[11])
  
  # fix negative s node ids
  if snode[0] == "-":
    snode = ParseNodeName(snode[1:])
    
  return WheelTypeA(radius, width, numrays, nid1, nid2, snode, braketype, drivetype, armnode, mass, spring, damp)


def ParseFlexbodyWheel(components):
  tire_radius = float(components[0])
  hub_radius = float(components[1])
  width = float(components[2])
  num_rays = int(components[3])
  nid1 = ParseNodeName(components[4])
  nid2 = ParseNodeName(components[5])
  snode = ParseNodeName(components[6])
  braketype = int(components[7])
  drivetype = int(components[8])
  armnode = ParseNodeName(components[9])
  mass = float(components[10])
  tire_spring = float(components[11])
  tire_damp = float(components[12])
  hub_spring = float(components[13])
  hub_damp = float(components[14])
  
  # fix negative s node ids
  if snode[0] == "-":
    snode = ParseNodeName(snode[1:])

  wheel_obj = WheelTypeB(tire_radius, hub_radius, width, num_rays, nid1, nid2, snode, braketype, drivetype, armnode, mass, tire_spring, tire_damp, hub_spring, hub_damp)
  wheel_obj.subtype = "flexbodywheels"
  return wheel_obj


def ParseMeshWheel(components):
  tire_radius = float(components[0])
  hub_radius = float(components[1])
  width = float(components[2])
  num_rays = int(components[3])
  nid1 = ParseNodeName(components[4])
  nid2 = ParseNodeName(components[5])
  snode = ParseNodeName(components[6])
  braketype = int(components[7])
  drivetype = int(components[8])
  armnode = ParseNodeName(components[9])
  mass = float(components[10])
  hub_spring = float(components[11])
  hub_damp = float(components[12])
  tire_spring = hub_spring
  tire_damp = hub_damp
  
  # fix negative s node ids
  if snode[0] == "-":
    snode = ParseNodeName(snode[1:])
  
  wheel_obj = WheelTypeB(tire_radius, hub_radius, width, num_rays, nid1, nid2, snode, braketype, drivetype, armnode, mass, tire_spring, tire_damp, hub_spring, hub_damp)
  wheel_obj.subtype = "meshwheels"
  return wheel_obj

  
def ParseWheel2(components):
  hub_radius = float(components[0])
  tire_radius = float(components[1])
  width = float(components[2])
  num_rays = int(components[3])
  nid1 = ParseNodeName(components[4])
  nid2 = ParseNodeName(components[5])
  snode = ParseNodeName(components[6])
  braketype = int(components[7])
  drivetype = int(components[8])
  armnode = ParseNodeName(components[9])
  mass = float(components[10])
  hub_spring = float(components[11])
  hub_damp = float(components[12])
  tire_spring = float(components[13])
  tire_damp = float(components[14])
  
  # fix negative s node ids
  if snode[0] == "-":
    snode = ParseNodeName(snode[1:])
    
  wheel_obj = WheelTypeB(tire_radius, hub_radius, width, num_rays, nid1, nid2, snode, braketype, drivetype, armnode, mass, tire_spring, tire_damp, hub_spring, hub_damp)
  wheel_obj.subtype = "wheels2"
  return wheel_obj
  

def ParseSetNodeDefaults(components):
  new_loadweight = float(components[1])
  new_friction = float(components[2])
  new_volume = float(components[3])
  new_surface = float(components[4])
  
  # defaults
  new_loadweight = 0.0 if new_loadweight < 0 else new_loadweight
  new_friction = 1.0 if new_friction < 0 else new_friction
  new_volume = 1.0 if new_volume < 0 else new_volume
  new_surface = 1.0 if new_surface < 0 else new_surface
  
  return [new_loadweight, new_friction, new_volume, new_surface]
  


def ParseSetBeamDefaults(components):
  new_spring = float(components[1])
  new_damp = float(components[2])
  new_deform = float(components[3])
  new_break = float(components[4])
  
  # defaults
  new_spring = 9000000 if new_spring < 0 else new_spring
  new_damp = 12000 if new_damp < 0 else new_damp
  new_deform = 400000 if new_deform < 0 else new_deform
  new_break = 100000 if new_break < 0 else new_break

  return [new_spring, new_damp, new_deform, new_break]

  
def SetBeamBreakgroup(beam, id):
  if id == 0:
    return
  beam.breakGroup = "detacher_group_" + str(id)