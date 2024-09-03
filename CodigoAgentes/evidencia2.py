# -*- coding: utf-8 -*-
"""Evidencia2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1FuU-Qf0S1RhOxPx5DoOvj4dPS14FmElc
"""

!pip install agentpy pathfinding owlready2

import agentpy as ap
import pathfinding as pf
import matplotlib.pyplot as plt
from owlready2 import *
import itertools
import random
import IPython
import math

onto = get_ontology("file://onto.owl")

onto.destroy(update_relation = True, update_is_a = True)

with onto:
    class Entity(Thing):
      pass

    class Camera(Entity):
      pass

    class StoreObject(Entity):
      pass

    class SecurityGuard(Entity):
      pass

    class Drone(Entity):
      pass

    class DroneStation(Entity): pass

    class Place(Thing):
      pass

    class is_in_place(ObjectProperty):
      domain = [Entity]
      range = [Place]
      pass

    class has_position(ObjectProperty, FunctionalProperty):
      domain = [Entity]
      range = [str]
      pass

    class object_in_store(ObjectProperty):
      domain = [SecurityGuard]
      range = [int]
      pass


    class object_within_reach(ObjectProperty):
      domain = [Drone]
      range = [int]
      pass

    class drone_sees_object(ObjectProperty):
      domain = [Drone]
      range = [int]
      pass

class cameraAgent(ap.Agent):

    def see(self, e):
        seeRange = (self.model.p.storeSize[0]//2)-1
        Objects = [a for a in e.neighbors(self, distance=seeRange) if a.agentType == 3]
        objects_info = [{
            "id": obj.id,
            "type": obj.object_is,
            "position": self.model.Store.positions[obj]
            } for obj in Objects]

        return objects_info


    def setup(self):
        self.agentType = 0


    def step(self):
      pass

    def update(self):
        pass

    def end(self):
        pass

class objectAgent(ap.Agent):

    def setup(self):
        self.agentType = 3
        PossibleObjects = ["box", "person", "bottle"]
        self.object_is = random.choice(PossibleObjects)

    def step(self):
        pass

    def update(self):
        pass

    def end(self):
        pass

class securityGuardAgent(ap.Agent):

    def setup(self):
        self.agentType = 1
        self.object_in_store = []

    def step(self):
      pass

    def brf(self,p):
      pass

    def update(self):
        pass

    def end(self):
        pass

class droneStationAgent(ap.Agent):

    def setup(self):
        self.agentType = 4

    def step(self):
      pass

    def update(self):
        pass

    def end(self):
        pass

class droneAgent(ap.Agent):


  #BDI functions
  def see_stations(self,a):
    seeRange = 20
    Stations = [a for a in self.model.Store.neighbors(self, distance=seeRange) if a.agentType == 4]
    return Stations

  def brf_stations(self,p):

    for station in self.this_drone.object_within_reach:
      destroy_entity(station.is_in_place[0])
      destroy_entity(station)
    destroy_entity(self.this_drone.is_in_place[0])

    currentPos = self.model.Store.positions[self]
    self.this_drone.is_in_place = [Place(at_position = str(currentPos))]

    for s in p:
      theStation = DroneStation(is_in_place = [Place()])
      theStation.is_in_place[0].at_position = str(self.model.Store.positions[s])
      self.this_drone.object_within_reach.append(theStation)


  def options_stations(self):
        distances = {}

        for onto_obj in self.this_drone.object_within_reach:
            obj_pos = eval(onto_obj.is_in_place[0].at_position)
            drone_pos = eval(self.this_drone.is_in_place[0].at_position)
            d = math.sqrt((obj_pos[0] - drone_pos[0]) ** 2 + (obj_pos[1] - drone_pos[1]) ** 2)
            distances[onto_obj] = d

        return distances

  def filter_stations(self):
      desires = {x: y for x, y in sorted(self.D.items(), key=lambda item: item[1])}
      return list(desires.items())[0][0] if desires else None


  def plan_patrol(self):
    if self.I is None:
      return (0,0)

    thePlanX = []
    thePlanY = []

    stationPos = eval(self.I.is_in_place[0].at_position)
    dronePos = eval(self.this_drone.is_in_place[0].at_position)
    distance2D = (stationPos[0] - dronePos[0], stationPos[1] -  dronePos[1])

    for i in range(abs(distance2D[0])):
      thePlanX.append(1 if distance2D[0] > 0 else -1)

    for j in range(abs(distance2D[1])):
      thePlanY.append(1 if distance2D[1] > 0 else -1)

    thePlanX = list(zip(thePlanX, [0]*len(thePlanX)))
    thePlanY = list(zip([0]*len(thePlanY), thePlanY))

    thePlan = thePlanX + thePlanY

    return thePlan


  def BDI_patrol(self, e):

      self.brf_stations(e)
      if self.IntentionSucceded:
        self.IntentionSucceded = False
        self.D = self.options_stations()
        self.I = self.filter_stations()
        self.currentPlan = self.plan_patrol()




  def execute(self):
      if len(self.currentPlan) > 0:
        currentAction = self.currentPlan.pop(0)

      else:
        currentAction = (0,0)
        self.IntentionSucceded = True

      self.model.Store.move_by(self, currentAction)


  def initBeliefs(self,initPos):
      place = Place(at_position = str(initPos))
      self.this_drone = Drone(is_in_place = [place])

  def initIntentions(self):
      self.IntentionSucceded = True
      self.I = None


  #Agent functions
  def setup(self):
      self.agentType = 2  # Tipo de agente para diferenciación
      self.firstStep = True
      self.currentPlan = []
      self.messages = []
      self.knownObjects = ["Box","Bottle"]


  def step(self):
    if self.firstStep:
      initPos = self.model.Store.positions[self]
      self.initBeliefs(initPos)
      self.initIntentions()
      self.firstStep = False

    self.BDI_patrol(self.see_stations(self.model.Store))
    self.execute()

  def update(self):
    pass

  def end(self):
    pass



class StoreModel(ap.Model):

    def setup(self):
        self.messages = []

        self.objects = ap.AgentList(self, self.p.objects, objectAgent)
        self.cameras = ap.AgentList(self, self.p.cameras, cameraAgent)
        self.securityGuardList = ap.AgentList(self, self.p.securityGuards, securityGuardAgent)
        self.drone = ap.AgentList(self, self.p.drone, droneAgent)
        self.droneStation = ap.AgentList(self, self.p.droneStation, droneStationAgent)

        self.Store = ap.Grid(self, self.p.storeSize, track_empty=True)

        camera_positions = [
            (0, 0),
            (self.p.storeSize[0] - 1, 0),
            (0, self.p.storeSize[1] - 1),
            (self.p.storeSize[0] - 1, self.p.storeSize[1] - 1)
        ]

        drone_position = [
            (self.p.storeSize[0] // 2, self.p.storeSize[1] // 2)
        ]

        droneStation_positions = [
            (self.p.storeSize[0]//2,0),
            (self.p.storeSize[0]//2, self.p.storeSize[1]-1),
            (0, self.p.storeSize[1]//2),
            (self.p.storeSize[0]-1, self.p.storeSize[1]//2)
        ]

        while len(self.cameras) > len(camera_positions):
            self.cameras.remove(random.choice(self.cameras))

        while len(self.drone) > len(drone_position):
            self.drone.remove(random.choice(self.drone))

        while len(self.droneStation) > len(droneStation_positions):
            self.droneStation.remove(random.choice(self.droneStation))

        self.Store.add_agents(self.drone, drone_position, empty=True)
        self.Store.add_agents(self.cameras, camera_positions, empty=True)
        self.Store.add_agents(self.droneStation, droneStation_positions, empty=True)
        self.Store.add_agents(self.objects, random=True, empty=True)

    def step(self):
        self.objects.step()
        self.cameras.step()
        self.securityGuardList.step()
        self.drone.step()

        for drone in self.drone:
          for station in self.droneStation:
            if station in self.Store.positions and self.Store.positions[station] == self.Store.positions[drone]:
              self.Store.remove_agents(station)
              self.droneStation.remove(station)
              break


    def update(self):
        pass

    def end(self):
        pass

#A FUNCTION TO ANIMATE THEE SIMULATION

def animation_plot(model, ax):
    agent_type_grid = model.Store.attr_grid('agentType')
    ap.gridplot(agent_type_grid, cmap='Accent', ax=ax)
    ax.set_title(f"Robot en almacen \n Time-step: {model.t}, ")

#SIMULATION PARAMETERS

#a random variables (0,1)
r = random.random()

#parameters dict
parameters = {
    "cameras" : 4,     #Amount of cameras
    "objects" : 10,      #Amount of objects
    "drone" : 1,      #Amount of drones
    "securityGuards" : 1,
    "droneStation" : 4,#Security Guard
"storeSize" : (15,15),      #Grid size
    "steps" : 50,          #Max steps
    "seed" : 13*r           #seed for random variables (that is random by itself)
}

#============================================================================0

#SIMULATION:

#Create figure (from matplotlib)
fig, ax = plt.subplots()

#Create model
model = StoreModel(parameters)


#Run with animation
#If you want to run it without animation then use instead:
#model.run()
animation = ap.animate(model, fig, ax, animation_plot)
#This step may take a while before you can see anything

#Print the final animation
IPython.display.HTML(animation.to_jshtml())