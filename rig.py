from rig_common import truck_sections, truck_inline_sections
import rig_parser as parser
import rig_torquecurves as curves

# TODO : Move this somewhere else?
def VectorDistance(x1, y1, z1, x2, y2, z2):
    nx = x2-x1
    ny = y2-y1
    nz = z2-z1
    return (nx*nx + ny*ny + nz*nz)

    
class Rig:
    def __init__(self):
      self.nodes = []
      self.beams = []
      self.hydros = []
      self.internal_cameras = []
      self.rails = []
      self.slidenodes = []
      self.wheels = []
      self.torquecurve = None
      self.engine = None
      self.engoption = None
      self.refnodes = None
      self.minimass = 50
      self.dry_weight = 10000
      self.load_weight = 10000
    
    def calculate_masses(self):
      """Python version of https://github.com/RigsOfRods/rigs-of-rods/blob/master/source/main/physics/Beam.cpp#L814"""
      numnodes = 0
      numloadnodes = 0
      for n in self.nodes:
          if n.load_bearer:
              numloadnodes += 1
          else:
              numnodes += 1
      
      for n in self.nodes:
          if not n.load_bearer:
              n.mass = 0
          elif n.override_mass == False:
              n.mass = self.load_weight / numloadnodes
          elif n.override_mass != False:
              n.mass = n.override_mass

      avg_lin_dens = 0.0
      for b in self.beams:
          if b.type != 'VIRTUAL':
              node1 = next((x for x in self.nodes if x.name == b.id1), None)
              node2 = next((x for x in self.nodes if x.name == b.id2), None)
              
              if node1 is not None and node2 is not None:
                beam_length = VectorDistance(node1.x, node1.y, node1.z, node2.x, node2.y, node2.z)
                avg_lin_dens += beam_length
              else:
                print("link not found : " + b.id1 + ", " + b.id2)
      for b in self.beams:
          if b.type != 'VIRTUAL':
              node1 = next((x for x in self.nodes if x.name == b.id1), None)
              node2 = next((x for x in self.nodes if x.name == b.id2), None)
              
              if node1 is not None and node2 is not None:
                beam_length = VectorDistance(node1.x, node1.y, node1.z, node2.x, node2.y, node2.z)
                half_mass = beam_length * self.dry_weight / avg_lin_dens / 2
                
                node1.mass += half_mass
                node2.mass += half_mass
              else:
                print("link not found : " + b.id1 + ", " + b.id2)
                
      for n in self.nodes:
          if n.mass < self.minimass:
              n.mass = self.minimass
        
        
    
    def from_file(self, filename):
      # read in trucklines
      trucklines = None
      with open(filename) as f:
          trucklines = f.readlines()
      
      # temp global vars
      last_beamspring = 9000000
      last_beamdamp = 12000
      last_beamdeform = 400000
      last_beamstrength = 1000000
      
      springscale = 1
      dampscale = 1
      deformscale = 1
      strengthscale = 1
      
      cur_detach_group = 0
      
      # parse .truck
      current_section = None
      for line in trucklines:
          # parse line
          line_cmps = parser.PrepareLine(line)
          
          # invalid
          if line_cmps is None:
            continue
          
          num_components = len(line_cmps)
          
          #inline?
          if line_cmps[0] in truck_inline_sections:
              # parse all inlines here
              section_name = line_cmps[0]
              if section_name == "set_beam_defaults" and num_components >= 5:
                  # set public stuff
                  last_beamspring, last_beamdamp, last_beamdeform, last_beamstrength = parser.ParseSetBeamDefaults(line_cmps)
              elif section_name == "set_beam_defaults_scale" and num_components >= 5:
                  springscale, dampscale, deformscale, strengthscale = parser.ParseSetBeamDefaults(line_cmps)
              elif section_name == "detacher_group":
                  cur_detach_group = int(line_cmps[1])
              elif section_name == "end":
                  # stop parsing!
                  break
                  
              continue
              
          # new section?
          if line_cmps[0] in truck_sections:
              current_section = line_cmps[0]
              continue

          #parse sections
          if (current_section == "nodes" or current_section == "nodes2") and num_components >= 4:
              self.nodes.append(parser.ParseNode(line_cmps))
          elif current_section == "beams" and num_components >= 2:
              beam_object = parser.ParseBeam(line_cmps, last_beamspring * springscale, last_beamdamp * dampscale, last_beamstrength * strengthscale, last_beamdeform * deformscale)
              parser.SetBeamBreakgroup(beam_object, cur_detach_group)
              self.beams.append(beam_object)
          elif current_section == "hydros" and num_components >= 3:
              self.hydros.append(parser.ParseHydro(line_cmps, last_beamspring, last_beamdamp, last_beamstrength * strengthscale, last_beamdeform * deformscale))
          elif current_section == "globals" and num_components >= 2:
              self.dry_weight = float(line_cmps[0])
              self.load_weight = float(line_cmps[1])
          elif current_section == "railgroups" and num_components >= 2:
              self.rails.append(parser.ParseRailgroup(line_cmps))
          elif current_section == "slidenodes" and num_components >= 2:
              slidenode, rail = parser.ParseSlidenode(line_cmps)
              
              if not isinstance(rail,str):
                # this is a Railgroup object, add it to self
                self.rails.append(rail)
              
              self.slidenodes.append(slidenode)
          elif current_section == "fixes" and num_components >= 1:
              # set node(s) to fixed
              nid = line_cmps[0]
              if nid.isdigit():
                  nid = "node" + nid

              node = next((x for x in self.nodes if x.name == nid), None)
              node.fixed = True
          elif current_section == "cameras" and num_components >= 3:
              self.refnodes = parser.ParseRefnodes(line_cmps)
          elif current_section == "cinecam" and num_components >= 13:
              self.internal_cameras.append(parser.ParseCinecam(line_cmps))
          elif current_section == "flexbodies" and num_components >= 10:
              # convert flexbodies (WiP!)
              relative_x_offset = float(line_cmps[3])
              relative_y_offset = float(line_cmps[4])
              z_offset = float(line_cmps[5])
              xrot = float(line_cmps[6])
              yrot = float(line_cmps[7])
              zrot = float(line_cmps[8])
              mesh_name = line_cmps[9]
          elif current_section == "minimass" and num_components >= 1:
              self.minimass = float(line_cmps[0])
          elif current_section == "shocks" and num_components >= 7:
              beam_object = parser.ParseShock(line_cmps, last_beamstrength * strengthscale, last_beamdeform * deformscale)
              parser.SetBeamBreakgroup(beam_object, cur_detach_group)
              self.beams.append(beam_object)
          elif current_section == "shocks2" and num_components >= 13:
              beam_object = parser.ParseShock2(line_cmps, last_beamstrength * strengthscale, last_beamdeform * deformscale)
              parser.SetBeamBreakgroup(beam_object, cur_detach_group)
              self.beams.append(beam_object)
          elif current_section == "engine" and num_components >= 7 and self.engine is None:
              self.engine = parser.ParseEngine(line_cmps)
          elif current_section == "engoption" and num_components >= 2 and self.engine is not None:
              self.engoption = parser.ParseEngoption(line_cmps)
          elif current_section == "torquecurve" and num_components >= 2 and self.engine is not None:
              # custom torquecurve model
              if self.torquecurve is None:
                self.torquecurve = []
                
              self.torquecurve.append([float(line_cmps[0]), float(line_cmps[1])])
          elif current_section == "torquecurve" and num_components == 1 and self.engine is not None and self.torquecurve is None:
              # predefined curve
              self.torquecurve = curves.get_curve(line_cmps[0])
          elif current_section == "wheels" and num_components >= 12:
              self.wheels.append(parser.ParseWheel(line_cmps))
       
      # final checks
      if self.torquecurve is None and self.engine is not None:
        self.torquecurve = curves.get_curve("default")
        
      # end parse of .truck
      
    def to_jbeam(self, filename):
      # sort beams by something so the jbeam doesn't look like a total mess
      self.beams.sort(key=lambda x: x.beamSpring, reverse=True)
      
      # open file and write it
      f = open(filename, 'w')
      f.write("{\n\t\"truck2jbeam\":{\n\t\t\"slotType\": \"main\",\n\n\t\t\"information\":{\n\t\t\t\"name\": \"truck2jbeam\",\n\t\t\t\"authors\": \"insert your name here\"\n\t\t}\n\n")
      
      # write refnodes
      if self.refnodes is not None:
          f.write("\t\t\"refNodes\":[\n\t\t\t[\"ref:\", \"back:\", \"left:\", \"up:\"],\n")
          f.write("\t\t\t[\"" + self.refnodes.center + "\", \"" + self.refnodes.back + "\", \"" + self.refnodes.left + "\", \"" + self.refnodes.center + "\"]\n")
          f.write("\t\t],\n\n")
      
      # write torquecurve
      if self.torquecurve is not None:
        f.write("\t\t\"enginetorque\":[\n\t\t\t[\"rpm\", \"torque\"],\n")
        
        # write curve, and multiply torque
        for t in self.torquecurve:
          f.write("\t\t\t[" + str(t[0]) + ", " + str(t[1] * self.engine.torque) + "],\n")
          
        f.write("\t\t],\n\n")
        
      # write engine
      if self.engine is not None:
          f.write("\t\t\"engine\":{\n")
          
          # idle/max RPM
          if self.engoption is None:
            f.write("\t\t\t\"idleRPM\":800,\n")
          else:
            f.write("\t\t\t\"idleRPM\":" + str(self.engoption.idle_rpm) + ",\n")
            
          f.write("\t\t\t\"maxRPM\":" + str(self.engine.max_rpm * 1.25) + ",\n")
          
          # shift RPMs
          f.write("\t\t\t\"shiftDownRPM\":" + str(self.engine.min_rpm) + ",\n")
          f.write("\t\t\t\"shiftUpRPM\":" + str(self.engine.max_rpm) + ",\n")
          
          # diff
          f.write("\t\t\t\"differential\":" + str(self.engine.differential) + ",\n")
          
          # inertia
          if self.engoption is None:
            f.write("\t\t\t\"inertia\":10,\n")
          else:
            f.write("\t\t\t\"inertia\":" + str(self.engoption.inertia) + ",\n")
            
          # ratios
          f.write("\t\t\t\"gears\":[")
          for g in self.engine.gears:
            f.write(str(g) + ", ")
          
          # seek before ratios last comma/spce
          f.seek(f.tell() - 2)
          f.write("],\n")
          
          # rest of engoption stuff
          if self.engoption is not None:
            f.write("\t\t\t\"clutchTorque\":" + str(self.engoption.clutch_force) + ",\n")
            f.write("\t\t\t\"clutchDuration\":" + str(self.engoption.clutch_time) + ",\n")
          
          f.write("\t\t}\n\n")
          
            
            
      # write nodes
      if len(self.nodes) > 0:
          last_node_mass = -1.0
          
          f.write("\t\t\"nodes\":[\n\t\t\t[\"id\", \"posX\", \"posY\", \"posZ\"],\n")
          for n in self.nodes:
              if n.mass != last_node_mass:
                  f.write("\t\t\t{\"nodeWeight\": " + str(n.mass) + "},\n")
                  last_node_mass = n.mass
              
              # write node line
              f.write("\t\t\t[\"" + n.name + "\", " + str(n.x) + ", " + str(n.y) + ", " + str(n.z))

              # write inline stuff
              if n.coupler:
                  f.write(", {\"tag\":\"fifthwheel\"}")
              
              f.write("],\n")
          f.write("\t\t],\n\n")
      
      # write cameras
      if len(self.internal_cameras) > 0:
          last_beam_spring = -1.0
          last_beam_damp = -1.0
          
          #     "camerasInternal":[
          # 
          f.write("\t\t\"camerasInternal\":[\n\t\t\t[\"type\", \"x\", \"y\", \"z\", \"fov\", \"id1:\", \"id2:\", \"id3:\", \"id4:\", \"id5:\", \"id6:\"],\n\t\t\t{\"nodeWeight\": 20},\n")
          for c in self.internal_cameras:
              if c.beamSpring != last_beam_spring:
                  last_beam_spring = c.beamSpring
                  f.write("\t\t\t{\"beamSpring\":" + str(c.beamSpring) + "}\n")
              if c.beamDamp != last_beam_damp:
                  last_beam_damp = c.beamDamp
                  f.write("\t\t\t{\"beamDamp\":" + str(c.beamDamp) + "}\n")
                  
              # write camera line
              f.write("\t\t\t[\"" + c.type + "\", " + str(c.x) + ", " + str(c.y) + ", " + str(c.z) + ", " + str(c.fov) + ", \"" + c.id1 + "\", \"" + c.id2 + "\", \"" + c.id3 + "\", \"" + c.id4 + "\", \"" + c.id5 + "\", \"" + c.id6 + "\"],\n")
          
          f.write("\t\t],\n\n")
          
      # write beams
      if len(self.beams) > 0:
          last_beam_spring = -1.0
          last_beam_damp = -1.0
          last_beam_deform = -1.0
          last_beam_strength = -1.0
          last_beam_shortbound = -1.0
          last_beam_longbound = -1.0
          last_beam_precomp = -1.0
          last_beam_type = 'NONEXISTANT'
          last_beam_damprebound = False
          last_breakgroup = ''
          f.write("\t\t\"beams\":[\n\t\t\t[\"id1:\", \"id2:\"],\n")
          for b in self.beams:
              # write vars if changed
              if b.beamDampRebound != last_beam_damprebound:
                  last_beam_damprebound = b.beamDampRebound
                  f.write("\t\t\t{\"beamDampRebound\":" + str(b.beamDampRebound).lower() + "},\n")
              if b.type != last_beam_type:
                  last_beam_type = b.type
                  f.write("\t\t\t{\"beamType\":\"|" + b.type + "\"},\n")
              if b.beamSpring != last_beam_spring:
                  last_beam_spring = b.beamSpring
                  f.write("\t\t\t{\"beamSpring\":" + str(b.beamSpring) + "}\n")
              if b.beamDamp != last_beam_damp:
                  last_beam_damp = b.beamDamp
                  f.write("\t\t\t{\"beamDamp\":" + str(b.beamDamp) + "}\n")
              if b.beamDeform != last_beam_deform:
                  last_beam_deform = b.beamDeform
                  f.write("\t\t\t{\"beamDeform\":" + str(b.beamDeform) + "}\n")
              if b.beamStrength != last_beam_strength:
                  last_beam_strength = b.beamStrength
                  f.write("\t\t\t{\"beamStrength\":" + str(b.beamStrength) + "}\n")
              if b.beamShortBound != last_beam_shortbound:
                  last_beam_shortbound = b.beamShortBound
                  f.write("\t\t\t{\"beamShortBound\":" + str(b.beamShortBound) + "}\n")
              if b.beamLongBound != last_beam_longbound:
                  last_beam_longbound = b.beamLongBound
                  f.write("\t\t\t{\"beamLongBound\":" + str(b.beamLongBound) + "}\n")
              if b.beamPrecompression != last_beam_precomp:
                  last_beam_precomp = b.beamPrecompression
                  f.write("\t\t\t{\"beamPrecompression\":" + str(b.beamPrecompression) + "}\n")
              if b.breakGroup != last_breakgroup:
                  last_breakgroup = b.breakGroup
                  f.write("\t\t\t{\"breakGroup\":\"" + b.breakGroup + "\"}\n")
              # write beam line
              f.write("\t\t\t[\"" + b.id1 + "\", \"" + b.id2 + "\"],\n")
              
          f.write("\t\t],\n\n")
      
      # write rails (name, nodes are params)
      if len(self.rails) > 0:
        f.write("\t\t\"rails\":{\n")
        for r in self.rails:
          # start write rail line
          f.write("\t\t\t\"" + r.name + "\":{\"links:\":[")
          for n in r.nodes:
            f.write("\"" + n + "\", ")
          
          # seek before last comma, and overwrite it
          f.seek(f.tell() - 2, 0)
          
          # finish writing rail line
          f.write("], \"looped\":false, \"capped\":true}\n")
          
        f.write("\t\t}\n\n")
      
      # write slidenodes
      if len(self.slidenodes) > 0:
        f.write("\t\t\"slidenodes\":[\n\t\t\t[\"id:\", \"railName\", \"attached\", \"fixToRail\", \"tolerance\", \"spring\", \"strength\", \"capStrength\"],\n")
        for s in self.slidenodes:
          # write slidenode line
          f.write("\t\t\t[\"" + s.node + "\", \"" + s.rail + "\", true, true, " + str(s.tolerance) + ", " + str(s.spring) + ", " + str(s.strength).replace("inf", "100000000") + ", 345435],\n")
        f.write("\t\t],\n\n")
        
      # write wheels
      if len(self.wheels) > 0:
          last_wheel_spring = -1.0
          last_wheel_damp = -1.0
          last_numrays = -1
          last_width = -1
          last_radius = -1
          last_propulsed = 0
          last_mass = 0
          
          c_wheel_idx = 0
          f.write("\t\t\"pressureWheels\":[\n\t\t\t[\"name\",\"hubGroup\",\"group\",\"node1:\",\"node2:\",\"nodeS\",\"nodeArm:\",\"wheelDir\"],\n")
          for w in self.wheels:
            # write vars if changed
            if w.drivetype > 0 and last_propulsed == 0:
              last_propulsed = 1
              f.write("\t\t\t{\"propulsed\":" + str(last_propulsed) + "}\n")
            elif w.drivetype == 0 and last_propulsed == 1:
              last_propulsed = 0
              f.write("\t\t\t{\"propulsed\":" + str(last_propulsed) + "}\n")
              
            if w.spring != last_wheel_spring:
              last_wheel_spring = w.spring
              f.write("\t\t\t{\"beamSpring\":" + str(w.spring) + "}\n")
            if w.damp != last_wheel_damp:
              last_wheel_damp = w.damp
              f.write("\t\t\t{\"beamDamp\":" + str(w.damp) + "}\n")
            if w.num_rays != last_numrays:
              last_numrays = w.num_rays
              f.write("\t\t\t{\"numRays\":" + str(w.num_rays) + "}\n")
            if w.width != last_width:
              last_width = w.width
              f.write("\t\t\t{\"hubWidth\":" + str(w.width) + "}\n")
            if w.radius != last_radius:
              last_radius = w.radius
              f.write("\t\t\t{\"hubRadius\":" + str(w.radius) + "}\n")
            if w.mass != last_mass:
              last_mass = w.mass
              f.write("\t\t\t{\"hubWeight\":" + str(w.mass / w.num_rays) + "}\n")
              
            # write wheel line
            if w.type == "wheels":
              snode = "\"" + w.snode + "\"" if w.snode != "node9999" else 9999
              drivetype = -1 if w.drivetype == 2 else w.drivetype
              f.write("\t\t\t[\"rorwheel" + str(c_wheel_idx) + "\", \"none\", \"none\", \"" + w.nid1 + "\", \"" + w.nid2 + "\", "  + str(snode) + ", \"" + w.armnode + "\", " + str(drivetype) + "],\n\n")

            #increment wheel ID
            c_wheel_idx += 1
          f.write("\t\t],\n\n")
      
      # write hydros
      if len(self.hydros) > 0:
          last_beam_spring = -1.0
          last_beam_damp = -1.0
          last_beam_deform = -1.0
          last_beam_strength = -1.0

          f.write("\t\t\"hydros\":[\n\t\t\t[\"id1:\", \"id2:\"],\n")
          for h in self.hydros:
              # write vars if changed
              if h.beamSpring != last_beam_spring:
                  last_beam_spring = h.beamSpring
                  f.write("\t\t\t{\"beamSpring\":" + str(h.beamSpring) + "}\n")
              if h.beamDamp != last_beam_damp:
                  last_beam_damp = h.beamDamp
                  f.write("\t\t\t{\"beamDamp\":" + str(h.beamDamp) + "}\n")
              if h.beamDeform != last_beam_deform:
                  last_beam_deform = h.beamDeform
                  f.write("\t\t\t{\"beamDeform\":" + str(h.beamDeform) + "}\n")
              if h.beamStrength != last_beam_strength:
                  last_beam_strength = h.beamStrength
                  f.write("\t\t\t{\"beamStrength\":" + str(h.beamStrength) + "}\n")
              
              # write hydro line
              f.write("\t\t\t[\"" + h.id1 + "\", \"" + h.id2 + "\", {\"inputSource\": \"steering\", \"inputFactor\": " + str(h.factor) + "}],\n")
              
          f.write("\t\t],\n")
      
      
      f.write("\t}\n}")
      f.close()