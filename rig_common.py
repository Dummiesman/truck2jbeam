# section lists
truck_sections = ["globals",
                  "nodes",
                  "nodes2",
                  "beams",
                  "cameras",
                  "cinecam",
                  "engine",
                  "engoption",
                  "engturbo",
                  "brakes",
                  "hydros",
                  "animators",
                  "commands",
                  "commands2",
                  "rotators",
                  "rotators2",
                  "wings",
                  "collisionboxes",
                  "rescuer",
                  "managedmaterials",
                  "contacters",
                  "triggers",
                  "lockgroups",
                  "hooks",
                  "submesh",
                  "slidenodes",
                  "railgroups",
                  "ropes",
                  "fixes",
                  "ties",
                  "ropables",
                  "particles",
                  "rigidifiers",
                  "torquecurve",
                  "cruisecontrol",
                  "axles",
                  "shocks",
                  "flares",
                  "flares2",
                  "materialflarebindings",
                  "props",
                  "flexbodies",
                  "flexbodywheels",
                  "meshwheels2",
                  "meshwheels",
                  "wheels",
                  "wheels2",
                  "airbrakes",
                  "turboprops",
                  "fusedrag",
                  "turbojets",
                  "pistonprops",
                  "screwprops",
                  "description",
                  "rollon",
                  "comment"]

truck_inline_sections = ["set_skeleton_settings",
                         "set_beam_defaults",
                         "set_beam_defaults_scale",
                         "set_node_defaults",
                         "enable_advanced_deformation",
                         "end",
                         "guid",
                         "fileformatversion",
                         "author",
                         "fileinfo",
                         "slopebrake",
                         "tractioncontrol",
                         "antilockbrakes",
                         "disable_flexbody_shadow",
                         "flexbody_camera_mode",
                         "prop_camera_mode",
                         "forset"
                         "section",
                         "sectionconfig",
                         "importcommands",
                         "forwardcommands",
                         "forset"]
                         
# storage classes
class Node:
    def __init__(self, name, xpos, ypos, zpos):
        self.name = name
        self.x = xpos
        self.y = ypos
        self.z = zpos
        self.fixed = False
        self.mass = 10
        self.load_bearer = False
        self.override_mass = 0.0
        self.coupler = False
        self.collision = True
        self.selfCollision = False

class Beam:
    def __init__(self, nid1, nid2, spring, damp, strength, deform):
        self.id1 = nid1
        self.id2 = nid2
        self.beamSpring = spring
        self.beamDamp = damp
        self.beamStrength = strength
        self.beamDeform = deform
        self.beamShortBound = 1.0
        self.beamLongBound = 1.0
        self.beamPrecompression = 1.0
        self.type = 'NORMAL'

        
class Hydro:
    def __init__(self, nid1, nid2, factor, spring, damp, strength, deform):
        self.id1 = nid1
        self.id2 = nid2
        self.factor = factor
        self.beamSpring = spring
        self.beamDamp = damp
        self.beamStrength = strength
        self.beamDeform = deform

        
class InternalCamera:
    def __init__(self, name, xpos, ypos, zpos, id1, id2, id3, id4, id5, id6, spring, damp):
        self.name = name
        self.x = xpos
        self.y = ypos
        self.z = zpos
        self.id1 = id1
        self.id2 = id2
        self.id3 = id3
        self.id4 = id4
        self.id5 = id5
        self.id6 = id6

        
class RoRFlexbody:
    def __init__(self, mesh, forset_groups, offsetX, offsetY, offsetZ, rotX, rotY, rotZ):
        self.mesh = mesh
        self.forset_groups = forset_groups
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.offsetZ = offsetZ
        self.rotX = rotX
        self.rotY = rotY
        self.rotZ = rotZ

        
class JBeamInformation:
    def __init__(self):
        self.name = "Untitled"
        self.author = "Insert author information"