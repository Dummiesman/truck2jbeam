from rig_common import Node, Beam, Hydro, InternalCamera
import re

def ParseNodeName(name):
  """This function converts nodes1 names into nodes2 style names"""
  if name.isdigit():
      return "node" + name
  else:
    return name

    
def PrepareLine(line):
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

  if line_has_spaces:
      line_lst[line.index(' ')] = ','

  # strip empty / bad stuff/ spaces
  line_lst = [x for x in line_lst if x]
  
  rejoined_lst = "".join(line_lst).replace(",,", ",")

  # invalid?
  if len(rejoined_lst) == 0:
      return None
  
  if rejoined_lst.endswith(","):
      rejoined_lst = rejoined_lst[:-1]

  rejoined_lst = rejoined_lst.replace(" ","")
  components = rejoined_lst.split(',')

  # blank?
  if len(components) == 0:
    return None
  else:
    return components
      
def ParseNode(components, nodes2 = False):
  nid = components[0]
  
  # convert to a more BeamNG style name if not nodes2
  if not nodes2:
    nid = "node" + nid
    
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
  if 'h' in flags:
      node_object.coupler = True
  if 'c' in flags:
      node_object.collision = False
      
  return node_object


def ParseHydro(components, last_beamspring, last_beamdamp, last_beamstrength, last_beamdeform):
  nid1 = ParseNodeName(components[0])
  nid2 = ParseNodeName(components[1])
      
  factor = float(components[2]) * -1
  
  return Hydro(nid1, nid2, factor, last_beamspring, last_beamdamp, last_beamstrength, last_beamdeform)

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
  

def ParseSetBeamDefaults(components):
  new_spring = float(components[1])
  new_damp = float(components[2])
  new_deform = float(components[3])
  new_break = float(components[4])
  
  # defaults
  if new_spring < 0:
      new_spring = 9000000
  if new_damp < 0:
      new_damp = 12000
  if new_deform < 0:
      new_deform = 400000
  if new_break < 0:
      new_break = 100000
      
  return [new_spring, new_damp, new_deform, new_break]
      