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
                  "shocks2",
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
                  "comment",
                  "soundsources",
                  "minimass",
                  "disabledefaultsounds"]

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
                         "forset",
                         "detacher_group"]
                         
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
        self.override_mass = False
        self.coupler = False
        self.collision = True
        self.selfCollision = False
        self.frictionCoef = 1.0
        self.group = []
        
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
        self.beamDampRebound = False
        self.beamLimitSpring = spring * 2
        self.beamLimitDamp = damp / 2
        self.type = 'NORMAL'
        self.breakGroup = ''

        
class Engine:
    def __init__(self, min_rpm, max_rpm, torque, differential, gears):
        self.min_rpm = min_rpm
        self.max_rpm = max_rpm
        self.torque = torque
        self.differential = differential
        self.gears = gears


class Engoption:
    def __init__(self, inertia, type, clutch_force, shift_time, clutch_time, post_shift_time, stall_rpm, idle_rpm, max_idle_mixture, min_idle_mixture):
        self.inertia = inertia
        self.type = type
        self.clutch_force = clutch_force
        self.shift_time = shift_time
        self.clutch_time = clutch_time
        self.post_shift_time = post_shift_time
        self.stall_rpm = stall_rpm
        self.idle_rpm = idle_rpm
        self.max_idle_mixture = max_idle_mixture
        self.min_idle_mixture = min_idle_mixture


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
    def __init__(self, xpos, ypos, zpos, id1, id2, id3, id4, id5, id6, spring, damp):
        self.x = xpos
        self.y = ypos
        self.z = zpos
        self.id1 = id1
        self.id2 = id2
        self.id3 = id3
        self.id4 = id4
        self.id5 = id5
        self.id6 = id6
        self.beamSpring = spring
        self.beamDamp = damp
        self.fov = 60
        self.type = "rorcam"


class Slidenode:
    def __init__(self, node, rail, spring, strength, tolerance):
        self.node = node
        self.rail = rail
        self.spring = spring
        self.strength = strength
        self.tolerance = tolerance

        
class Rail:
    def __init__(self, name, nodes):
        self.name = name
        self.nodes = nodes

        
class Refnodes:
    def __init__(self, center, back, left):
        self.center = center
        self.back = back
        self.left = left


class Flexbody:
    def __init__(self, refnode, xnode, ynode, offsetX, offsetY, offsetZ, rotX, rotY, rotZ, mesh):
        self.mesh = mesh
        self.refnode = refnode
        self.xnode = xnode
        self.ynode = ynode
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
        

class Axle:
    def __init__(self, wid1, wid2, type, state):
        self.wid1 = wid1
        self.wid2 = wid2
        self.type = type
        self.state = state
        
class WheelTypeA:
    def __init__(self, radius, width, num_rays, nid1, nid2, snode, braketype, drivetype, armnode, mass, spring, damp):
        self.radius = radius
        self.width = width
        self.num_rays = num_rays
        self.nid1 = nid1
        self.nid2 = nid2
        self.snode = snode
        self.braketype = braketype
        self.drivetype = drivetype
        self.armnode = armnode
        self.mass = mass
        self.spring = spring
        self.damp = damp
        self.type = "wheels"
        

class WheelTypeB:
    def __init__(self, tire_radius, hub_radius, width, num_rays, nid1, nid2, snode, braketype, drivetype, armnode, mass, tire_spring, tire_damp, hub_spring, hub_damp):
        self.tire_radius = tire_radius
        self.hub_radius = hub_radius
        self.width = width
        self.num_rays = num_rays
        self.nid1 = nid1
        self.nid2 = nid2
        self.snode = snode
        self.braketype = braketype
        self.drivetype = drivetype
        self.armnode = armnode
        self.mass = mass
        self.tire_spring = tire_spring
        self.tire_damp = tire_damp
        self.hub_spring = hub_spring
        self.hub_damp = hub_damp
        self.type = "wheels.advanced"
        self.subtype = "None"