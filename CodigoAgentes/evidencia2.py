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

    class has_ponderation(DataProperty, FunctionalProperty):
      domain = [DroneStation]
      range = [float]

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

class Message:
  def __init__(self, sender, receiver, content):
    self.sender = sender
    self.receiver = receiver
    self.content = content

class cameraAgent(ap.Agent):

  def sendMessage(self,receiver,content):
    message = Message(self,receiver,content)
    receiver.receive_message(message)

  def see(self, e):
      seeRange = self.model.p.storeSize[0]//2
      new_objects = [a for a in e.neighbors(self, distance = seeRange)
      if a.agentType == 3 and a.object_is not in self.knownObjects and a not in self.objects_seen]
      self.objects_seen.extend(new_objects)

  def send_objects_seen(self,drone):
    content = {"objects_seen": self.objects_seen}
    self.sendMessage(drone,content)
    print(f"Enviando objetos vistos al dron: {self.objects_seen}")

  def setup(self):
        self.agentType = 0
        self.knownObjects = ["box", "bottle"]
        self.objects_seen = []
        self.input_sent = False

  def step(self):
    self.see(self.model.Store)
    if not self.input_sent:
      self.input_sent = True
      for drone in self.model.drone:
        self.send_objects_seen(drone)

  def update(self):
        pass

  def end(self):
        pass

class objectAgent(ap.Agent):

    def setup(self):
        self.agentType = 3
        PossibleObjects = ["box", "person", "bottle", "toy"]
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
        self.ponderation = 0

    def step(self):
      pass

    def update(self):
        pass

    def end(self):
        pass

class droneAgent(ap.Agent):


  def receive_message(self, message):
    self.message_queue.append(message)
    print("Mensaje recibido")

  def process_messages(self):
    while self.message_queue:
      message = self.message_queue.pop(0)
      print(f"Procesando mensaje de {message.sender}: {message.content}")
      if "objects_seen" in message.content:
        obj_received = message.content["objects_seen"]
        for obj in obj_received:
          if obj not in self.collectedObjects:
            self.collectedObjects.append(obj)
        print(f"Camara {message.sender} ha detectado {message.content['objects_seen']}")

  def collectObjects(self, a):
    seeRange = 5
    new_objects = [obj for obj in a.neighbors(self, distance = seeRange)
    if obj.agentType == 3 and obj.object_is not in self.knownObjects and obj not in self.collectedObjects]

    self.collectedObjects.extend(new_objects)

  #BDI functions
  def see_stations(self,a):
    seeRange = self.model.p.storeSize[0]
    Stations = [a for a in self.model.Store.neighbors(self, distance=seeRange) if a.agentType == 4]
    return Stations

  def brf_stations(self,p):

    for station in self.this_drone.object_within_reach:
      destroy_entity(station.is_in_place[0])
      #destroy_entity(station.has_ponderation)
      destroy_entity(station)
    destroy_entity(self.this_drone.is_in_place[0])

    currentPos = self.model.Store.positions[self]
    self.this_drone.is_in_place = [Place(at_position = str(currentPos))]

    for s in p:
      theStation = DroneStation(is_in_place = [Place()])
      theStation.is_in_place[0].at_position = str(self.model.Store.positions[s])
      theStation.has_ponderation = s.ponderation
      self.this_drone.object_within_reach.append(theStation)


  def options_stations(self):
        ponderations = {}

        for onto_obj in self.this_drone.object_within_reach:
            obj_pos = eval(onto_obj.is_in_place[0].at_position)
            drone_pos = eval(self.this_drone.is_in_place[0].at_position)
            obj_pond = onto_obj.has_ponderation
            ponderations[onto_obj] = obj_pond

        return ponderations

  def filter_stations(self):
      desires = {x: y for x, y in sorted(self.D.items(), key=lambda item: item[1])}
      return list(desires.items())[0][0] if desires else None


  def plan_patrol(self):
    if self.I is None:
      return [(0,0)]

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
      self.knownObjects = ["box","bottle"]
      self.collectedObjects = []
      self.is_patrol_over = False
      self.received_input_from_cameras = False
      self.message_queue = []


  def step(self):
    if self.firstStep:
      initPos = self.model.Store.positions[self]
      if not self.received_input_from_cameras:
        self.process_messages()
        self.received_input_from_cameras = True
      self.initBeliefs(initPos)
      self.initIntentions()
      self.firstStep = False

    if not self.is_patrol_over:
      self.BDI_patrol(self.see_stations(self.model.Store))
      self.collectObjects(self.model.Store)

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
            (self.p.storeSize[0]-1, self.p.storeSize[1]//2)
        ]

        droneStation_positions = [
            (self.p.storeSize[0]//2,0),
            (self.p.storeSize[0]//2, self.p.storeSize[1]-1),
            (0, self.p.storeSize[1]//2),
            (self.p.storeSize[0]-1, self.p.storeSize[1]//2),
            (self.p.storeSize[0]//2, self.p.storeSize[1]//2)
        ]

        self._adjust_agent_count(self.cameras, camera_positions)
        self._adjust_agent_count(self.drone, drone_position)
        self._adjust_agent_count(self.droneStation, droneStation_positions)


        self.Store.add_agents(self.drone, drone_position, empty=True)
        self.Store.add_agents(self.cameras, camera_positions, empty=True)
        self.Store.add_agents(self.droneStation, droneStation_positions, empty=True)
        self.Store.add_agents(self.objects, random=True, empty=True)
        for station in self.droneStation:
          station.ponderation += 1
        for obj in self.objects:
          print(f"El objeto: {obj.id} es: {obj.object_is}")



    def _adjust_agent_count(self, agent_list, positions):
      while len(agent_list) > len(positions):
        agent_list.remove(random.choice(agent_list))

    def step(self):
        self.objects.step()
        self.cameras.step()
        self.securityGuardList.step()
        self.drone.step()

        for drone in self.drone:
          print(drone.collectedObjects)
          for station in self.droneStation:
            if station in self.Store.positions and self.Store.positions[station] == self.Store.positions[drone]:
              self.Store.remove_agents(station)
              self.droneStation.remove(station)
              break

        if len(self.droneStation) == 0:
          for drone in self.drone:
            drone.is_patrol_over = True


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
    "cameras" : 5,     #Amount of cameras
    "objects" : 10,      #Amount of objects
    "drone" : 1,      #Amount of drones
    "securityGuards" : 1,
    "droneStation" : 4,#Security Guard
"storeSize" : (15,15),      #Grid size
    "steps" : 70,          #Max steps
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