import math
import random 

import pyglet
from pyglet.window import key

import shapes
import coord
import gamemap
import action
import percept

class Player(pyglet.sprite.Sprite, key.KeyStateHandler):

	acceleration = 200.

	def __init__(self, img, batch, background, foreground, polygons, window_width, window_height, pos_x, pos_y, pos_rot):
		super(Player, self).__init__(img, pos_x, pos_y, batch=batch, group=foreground)
		Player.center_anchor(img)
		self.scale = 0.5
		self.rotation = pos_rot
		self.dx = 0
		self.dy = 0
		self.rotation_x = 0
		self.rotation_y = 0
		self.__window_width = window_width
		self.__window_height = window_height
		self.__polygons = polygons
		self.__action = None
		self.__current_percept = percept.GraphicsPercept([],[],[],[])
		self.__prev_x = None
		self.__prev_y = None
		self.__prev_rotation = None

		# Visibility polygon setup
		self.__num_rays = 10
		self.__visibility_angle = 45
		# self.__visibility_color = (149, 165, 166)
		self.__visibility_color = 28, 40, 51  
		self.__visibility_polygon = None

		self.__num_vertices = self.__num_rays + 1
		num_triangles = self.__num_vertices - 2
		triangle_list = [0 for i in range(num_triangles * 3)]

		i = 1
		j = 1
		while i < num_triangles * 3:
			triangle_list[i] = j
			i += 3
			j += 1

		i = 2
		j = 2
		while i < num_triangles * 3:
			triangle_list[i] = j
			i += 3
			j += 1

		color_list = []
		for i in range(11):
			# 149, 165, 166
			color_list.append(self.__visibility_color[0])
			color_list.append(self.__visibility_color[1])
			color_list.append(self.__visibility_color[2])
		color_tuple = tuple(color_list)
 
		self.__visibility_vertices = batch.add_indexed(self.__num_vertices, pyglet.gl.GL_TRIANGLES, background, 
		triangle_list,
		('v2i', tuple([0 for i in range(self.__num_vertices * 2)])),
		('c3B', color_tuple)
		)

	def remove(self):
		self.__visibility_vertices.vertices = [0 for i in range(self.__num_vertices * 2)]
		self.__visibility_vertices.delete
		self.delete

	@staticmethod
	def center_anchor(img):
		img.anchor_x = img.width // 2
		img.anchor_y = img.height // 2

	@staticmethod
	def to_radians(degrees):
		return math.pi * degrees / 180.0

	@staticmethod
	def wrap(value, length):
	    if value > length:
	        value -= length
	    if value < 0:
	        value += length
	    return value	

	def revert_configuration(self):
		self.x = self.__prev_x
		self.y = self.__prev_y
		self.rotation = self.__prev_rotation
		self.__update_visibility()

	def set_action(self, act):
		assert(act, action.Action)
		self.__action = act

	def set_visibility(self, visibility):
		self.visible = visibility

	def set_position(self, position):
		self.x = position.get_x()
		self.y = position.get_y()

	def get_position(self):
		return coord.Coord(self.x, self.y)

	def get_visibility_polygon(self):
		return self.__visibility_polygon

	def get_current_coordinate(self):
		return coord.Coord(self.x, self.y)

	def set_percept(self, current_percept):
		self.__current_percept = current_percept

	def get_percept(self):
		return self.__current_percept

	def update(self, dt):
		# Update rotation
		# print('Reached update:',dt)

		self.dx = 0
		self.dy = 0

		flag = False

		self.__prev_x = self.x
		self.__prev_y = self.y
		self.__prev_rotation = self.rotation

		if self.__action == action.Action.East:
			self.rotation = 0.1
			flag = True
		elif self.__action == action.Action.SouthEast:
			self.rotation = 45.1
			flag = True
		elif self.__action == action.Action.South:
			self.rotation = 90.1
			flag = True
		elif self.__action == action.Action.SouthWest:
			self.rotation = 135.1
			flag = True
		elif self.__action == action.Action.West:
			self.rotation = 180.1
			flag = True
		elif self.__action == action.Action.NorthWest:
			self.rotation = 225.1
			flag = True
		elif self.__action == action.Action.North:
			self.rotation = 270.1
			flag = True
		elif self.__action == action.Action.NorthEast:
			self.rotation = 315.1
			flag = True


		if self[key.NUM_6]:
			self.rotation = 0.1
			flag = True 
		elif self[key.NUM_3]:
			self.rotation = 45.1
			flag = True
		elif self[key.NUM_2]:
			self.rotation = 90.1
			flag = True
		elif self[key.NUM_1]:
			self.rotation = 135.1
			flag = True
		elif self[key.NUM_4]:
			self.rotation = 180.1
			flag = True
		elif self[key.NUM_7]:
			self.rotation = 225.1
			flag = True
		elif self[key.NUM_8]:
			self.rotation = 270.1
			flag = True
		elif self[key.NUM_9]:
			self.rotation = 315.1
			flag = True

		if flag:
			self.rotation_x = math.cos(Player.to_radians(-self.rotation))
			self.rotation_y = math.sin(Player.to_radians(-self.rotation))
			self.dx = Player.acceleration * self.rotation_x 
			self.dy = Player.acceleration * self.rotation_y
		
		self.x = Player.wrap(self.x + self.dx * dt, self.__window_width)
		self.y = Player.wrap(self.y + self.dy * dt, self.__window_height)

		# if not self.__check_configuration_validity():
		# 	self.revert_configuration()

		# position = self.get_current_coordinate()

		# # The last polygon is the boundary which does not need to be checked
		# # , thats why len(polygon)-1
		# collision = False
		# for i in range(len(self.__polygons) - 1):
		# 	polygon = self.__polygons[i]
		# 	if polygon.is_point_inside(position):
		# 		collision = True
		# 		break

		self.__update_visibility()


	def __update_visibility(self):
		c = coord.Coord(self.x, self.y)
		vis_points = [int(c.get_x()), int(c.get_y())]

		rotation = self.rotation - self.__visibility_angle
		offset = (self.__visibility_angle * 2.0)/self.__num_rays
		while rotation < self.rotation + self.__visibility_angle:
			rotation_x = math.cos(Player.to_radians(-rotation))
			rotation_y = math.sin(Player.to_radians(-rotation))
			r = coord.Coord(self.x + rotation_x, self.y + rotation_y)
			ray = shapes.Line(c, r)
			# print('ray:', ray)
			closest_intersect = None
			for polygon in self.__polygons:
				# print('polygon:',polygon)
				for i in range(polygon.get_num_lines()):
					
					intersect = shapes.Line.get_intersection(ray, polygon.get_line(i))
					if not intersect:
						continue
					if not closest_intersect or intersect[1] < closest_intersect[1]:
						closest_intersect = intersect

			# print(closest_intersect[0])

			vis_points.append(int(closest_intersect[0].get_x()))
			vis_points.append(int(closest_intersect[0].get_y()))

			rotation += offset

		vis_points_tuple = tuple(vis_points)
		self.__visibility_vertices.vertices = vis_points_tuple
		self.__visibility_polygon = shapes.Polygon(vis_points_tuple)



class Graphics(pyglet.window.Window):

	def __init__(self, window_width, window_height, num_hiders, num_seekers, polygon_map):
		super(Graphics, self).__init__(window_width, window_height)
		pyglet.resource.path.append('resources')
		pyglet.resource.reindex()
		self.__background = pyglet.graphics.OrderedGroup(0)
		self.__foreground = pyglet.graphics.OrderedGroup(1)
		self.__static_batch = pyglet.graphics.Batch()
		self.__dynamic_batch = pyglet.graphics.Batch()
		self.__hider_image = pyglet.resource.image('wanderer.png')
		self.__seeker_image = pyglet.resource.image('seeker.png')
		self.__num_hiders = num_hiders
		self.__num_seekers = num_seekers
		assert(isinstance(polygon_map, gamemap.PolygonMap))
		self.__polygon_map = polygon_map
		self.__polygons = [] # By polygons we refer to the background obstacles only


		self.__num_polygons = polygon_map.get_num_polygons()
		for i in range(self.__num_polygons):
			polygon = self.__polygon_map.get_polygon(i)
			self.__polygons.append(polygon)
			self.__add_batch_polygon(polygon)

		self.__boundary_polygon = polygon_map.get_boundary_polygon()
		self.__add_batch_polygon(self.__boundary_polygon)

		hider_polygons = []
		seeker_polygons = []
		for i in range(self.__num_polygons):
			hider_polygons.append(self.__polygons[i])
			seeker_polygons.append(self.__polygons[i])
		hider_polygons.append(self.__boundary_polygon)
		seeker_polygons.append(self.__boundary_polygon)

			
		self.__hiders = [Player(self.__hider_image, self.__dynamic_batch, self.__background, self.__foreground, hider_polygons, window_width, window_height, 0, 0, random.random() * 360) for i in range(num_hiders)]
		self.__seekers = [Player(self.__seeker_image, self.__dynamic_batch, self.__background, self.__background, seeker_polygons, window_width, window_height, 0, 0, random.random() * 360) for i in range(num_seekers)]
		
		self.__hider_active = [True for i in range(num_hiders)]
		self.__seeker_active = [True for i in range(num_seekers)]

		# pyglet.clock.schedule_interval(self.update, 1/60.)
		self.push_handlers(self.__seekers[0])

	def __add_batch_polygon(self, polygon):
		if polygon.get_num_vertices() == 4:
			self.__static_batch.add_indexed(4, pyglet.gl.GL_LINES, self.__background, 
			[0,1,1,2,2,3,3,0],
			('v2i', polygon.get_points_tuple()),)
		if polygon.get_num_vertices() == 3:
			self.__static_batch.add_indexed(3, pyglet.gl.GL_LINES, self.__background, 
			[0,1,1,2,2,0],
			('v2i', polygon.get_points_tuple() ),)


	def set_hider_inactive(self, hider_idx):
		assert(hider_idx < self.__num_hiders)
		assert(self.__hider_active[hider_idx])
		self.__hider_active[hider_idx] = False
		self.__hiders[hider_idx].remove()
		self.__hiders[hider_idx] = None

	def set_seeker_inactive(self, seeker_idx):
		assert(seeker_idx < self.__num_seekers)
		assert(self.__seeker_active[seeker_idx])
		self.__seeker_active[seeker_idx] = False
		self.__seekers[seeker_idx].remove()
		self.__seekers[seeker_idx] = None

	def set_hider_action(self, hider_idx, act):
		assert(hider_idx < self.__num_hiders)
		assert(self.__hider_active[hider_idx])
		self.__hiders[hider_idx].set_action(act)

	def set_seeker_action(self, seeker_idx, act):
		assert(seeker_idx < self.__num_seekers)
		assert(self.__seeker_active[seeker_idx])
		self.__seekers[seeker_idx].set_action(act)

	def get_hider_percept(self, hider_idx):
		assert(hider_idx < self.__num_hiders)
		assert(self.__hider_active[hider_idx])
		return self.__hiders[hider_idx].get_percept()

	def get_seeker_percept(self, seeker_idx):
		assert(seeker_idx < self.__num_seekers)
		assert(self.__seeker_active[seeker_idx])
		return self.__seekers[seeker_idx].get_percept()

	def set_hider_position(self, hider_idx, position):
		assert(hider_idx < self.__num_hiders)
		assert(self.__hider_active[hider_idx])
		self.__hiders[hider_idx].set_position(position)

	def set_seeker_position(self, seeker_idx, position):
		assert(seeker_idx < self.__num_seekers)
		assert(self.__seeker_active[seeker_idx])
		self.__seekers[seeker_idx].set_position(position)

	def get_hider_position(self, hider_idx):
		assert(hider_idx < self.__num_hiders)
		assert(self.__hider_active[hider_idx])
		return self.__hiders[hider_idx].get_position()

	def get_seeker_position(self, seeker_idx):
		assert(seeker_idx < self.__num_seekers)
		assert(self.__seeker_active[seeker_idx])
		return self.__seekers[seeker_idx].get_position()

	def on_draw(self):
		self.clear()
		self.__static_batch.draw()
		self.__dynamic_batch.draw()

	def __get_visible_players(self, visibility_polygon, ignore_hiders, ignore_seekers):
		hider_coords = []
		hider_idxs = []
		for i in range(self.__num_hiders):
			if self.__hider_active[i]:
				if i in ignore_hiders:
					continue
				position = self.__hiders[i].get_current_coordinate()
				if visibility_polygon.is_point_inside(position):
					hider_coords.append(position)
					hider_idxs.append(i)

		seeker_coords = []
		seeker_idxs = []
		for i in range(self.__num_seekers):
			if self.__seeker_active[i]:
				if i in ignore_seekers:
					continue
				position = self.__seekers[i].get_current_coordinate()
				if visibility_polygon.is_point_inside(position):
					seeker_coords.append(position)
					seeker_idxs.append(i)

		return hider_coords, seeker_coords, hider_idxs, seeker_idxs

	def __update_percepts(self):
		'''
			Iterates over each players visibility region to check if any other 
			player is visible or not, preparing the percept accordingly.
		'''
		for i in range(self.__num_hiders):
			if self.__hider_active[i]:
				hider = self.__hiders[i]
				visibility_polygon = hider.get_visibility_polygon()
				ignore_hiders = [i]
				ignore_seekers = []
				hider_coords, seeker_coords, hider_idxs, seeker_idxs = self.__get_visible_players(visibility_polygon, ignore_hiders, ignore_seekers)
				# if hider_coords:
				# 	print('Hider spotted:', hider_coords)
				# if seeker_coords:
				# 	print('Seeker spotted:', seeker_coords)
				current_percept = percept.GraphicsPercept(hider_coords, seeker_coords, hider_idxs, seeker_idxs)
				hider.set_percept(current_percept)

		for i in range(self.__num_seekers):
			if self.__seeker_active[i]:
				seeker = self.__seekers[i]
				visibility_polygon = seeker.get_visibility_polygon()
				ignore_hiders = []
				ignore_seekers = [i]
				hider_coords, seeker_coords, hider_idxs, seeker_idxs = self.__get_visible_players(visibility_polygon, ignore_hiders, ignore_seekers)
				# if hider_coords:
				# 	print('Hider spotted:', hider_coords)
				# if seeker_coords:
				# 	print('Seeker spotted:', seeker_coords)
				current_percept = percept.GraphicsPercept(hider_coords, seeker_coords, hider_idxs, seeker_idxs)
				seeker.set_percept(current_percept)

	def update(self, dt):
		occupied_positions = []
		for i in range(self.__num_hiders):
			if self.__hider_active[i]:
				self.__hiders[i].update(dt)
				current_position = self.__hiders[i].get_current_coordinate()
				collided = self.__polygon_map.check_obstacle_collision(current_position)
				obstructed = current_position in occupied_positions
				if collided or obstructed:
					 self.__hiders[i].revert_configuration()
				else:
					occupied_positions.append(current_position)
		for i in range(self.__num_seekers):
			if self.__seeker_active[i]:
				self.__seekers[i].update(dt)
				current_position = self.__seekers[i].get_current_coordinate()
				collided = self.__polygon_map.check_obstacle_collision(current_position)
				obstructed = current_position in occupied_positions
				if collided or obstructed:
					 self.__seekers[i].revert_configuration()
				else:
					occupied_positions.append(current_position)
		self.__update_percepts()
