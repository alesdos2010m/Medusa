from abc import ABCMeta, abstractmethod


import message
import agent
import mapmanager

class Team(object):
	'''
		An abstract base class describing the Team framework which controls and
		manages the individual agents of a particular team of hiders/seekers.
	'''

	__metaclass__ = ABCMeta

	ranks = 0 
	# ranks denote the hierarchy of the team, rank 1 means a flat hierarchy team,
	# rank 2 means there are higher level players who control lower level players 
	# and so on

	def __init__(self, num_agents):
		'''
			_members is a list of lists, each list contains members
			of the particular rank which corresponds to the index at which
			this list is stored.
		'''
		self._num_agents = num_agents
		self._team_messenger = message.TeamMessenger()
		self._members = None # which type of members to recruit ?
		self._map_managers = None # which map manager to assign to each hierarchy level ?
		self._active = None # a list denoting which of the agents are still in the game
	
	def create_agent_messenger(self, agent_id):
		return self._team_messenger.create_agent_messenger(agent_id)

	def get_ranks(self):
		return self.ranks


	def get_num_rankers(self, rank):
		'''
			Returns number of units having a particular rank
		'''
		assert(rank < self.ranks)
		return len(self._members[rank])

	def set_percept(self, rank, idx, current_percept):
		assert(rank < self.ranks)
		assert(idx < len(self._members[rank]))
		assert(self._active[rank][idx])
		member = self._members[rank][idx]
		member.set_percept(current_percept)

	def get_percept(self, rank, idx):
		assert(rank < self.ranks)
		assert(idx < len(self._members[rank]))
		assert(self._active[rank][idx])
		member = self._members[rank][idx]
		return member.get_percept()

	def get_action(self, rank, idx):
		assert(rank < self.ranks)
		assert(idx < len(self._members[rank]))
		assert(self._active[rank][idx])
		member = self._members[rank][idx]
		return member.get_action()

	def set_position(self, rank, idx, position):
		assert(rank < self.ranks)
		assert(idx < len(self._members[rank]))
		assert(self._active[rank][idx])
		self._members[rank][idx].set_position(position)

	def get_position(self, rank, idx):
		assert(rank < self.ranks)
		assert(idx < len(self._members[rank]))
		assert(self._active[rank][idx])
		return self._members[rank][idx].get_position()

	def set_member_inactive(self, rank, idx):
		assert(rank < self.ranks)
		assert(idx < len(self._members[rank]))
		assert(self._active[rank][idx])
		self._active[rank][idx] = False

	def is_member_active(self, rank, idx):
		assert(rank < self.ranks)
		assert(idx < len(self._members[rank]))
		return self._active[rank][idx]

	def __enable_message_generation(self):
		''' 
		Based on the percept obtained, generate messages and pass them
		according to the team hierarchy, starting from the highest ranking
		agents to the lowest ranking agents
		'''
		for i in reversed(range(0, self.ranks)):
			for j in range(len(self._members[i])):
				if self._active[i][j]:
					member = self._members[i][j]
					member.generate_messages()

	def __enable_message_analysis(self):
		'''
		The messages are analyzed, starting from high ranking agents to lower
		level agents. Based on this analysis some temporary state may be 
		changed affecting the chosen action
		'''
		for i in reversed(range(0, self.ranks)):
			for j in range(len(self._members[i])):
				if self._active[i][j]:
					member = self._members[i][j]
					member.analyze_messages()

	def __enable_action_selection(self):
		'''
		Based on the percept as well as temporary state changes(due to prior)
		message analysis, action is chosen
		'''
		for i in reversed(range(0, self.ranks)):
			for j in range(len(self._members[i])):
				if self._active[i][j]:
					member = self._members[i][j]
					member.select_action()

	def __enable_temporal_state_clearance(self):
		'''
		Clear any temporary state changes caused by message analysis
		to their normal values
		'''
		for i in reversed(range(0, self.ranks)):
			for j in range(len(self._members[i])):
				if self._active[i][j]:
					member = self._members[i][j]
					member.clear_temporary_state()



	def select_actions(self):
		'''
			Assigns actions to each of its members.

			Based on the current percept, as well as the message passed 
			b/w the members, each agent takes an action
		'''
		
		self.__enable_message_generation()
		self.__enable_message_analysis()
		self.__enable_action_selection()
		self.__enable_temporal_state_clearance()
		

	@abstractmethod
	def team_type(self):
		pass

class HiderTeam(Team):

	__metaclass__ = ABCMeta

	def team_type(self):
		return 'hider_team'

class SeekerTeam(Team):

	__metaclass__ = ABCMeta

	def team_type(self):
		return 'seeker_team'

class RandomHiderTeam(HiderTeam):

	ranks = 2

	def __init__(self, num_agents, mapworld, fps, velocity):
		super(RandomHiderTeam, self).__init__(num_agents)

		# prepare a rank 1 hierarchy member list and map managers
		self._map_managers = [] # one map manager for one level
		self._members = [[], []]
		self._active = [[], []]

		# assign a basic map manager to the only level
		map_manager = mapmanager.BasicMapManager(mapworld, fps, velocity)
		self._map_managers.append(map_manager)

		# recruit the commander of the random team
		agent_id = 'RH' + str(0)
		commander_member = agent.RandomHiderCommanderAgent(agent_id, self, self._map_managers[0])
		self._members[1].append(commander_member)
		self._active[1].append(True)

		# recruit agents for the team
		for i in range(self._num_agents - 1):
			agent_id = 'RH' + str(i)
			member = agent.RandomHiderAgent(agent_id, self, self._map_managers[0])
			self._members[0].append(member)
			self._active[0].append(True)

		# Get the opening positions from the commader member and set each agents
		# position accordingly
		for i in reversed(range(self.ranks)):
			for j in range(self.get_num_rankers(i)):
				position = commander_member.get_opening_position(i, j)
				self._members[i][j].set_position(position)

class RandomSeekerTeam(SeekerTeam):

	ranks = 2

	def __init__(self, num_agents, mapworld, fps, velocity):
		super(RandomSeekerTeam, self).__init__(num_agents)
		assert(num_agents > 0)
		# prepare a rank 1 hierarchy member list and map managers
		self._map_managers = [] # one map manager for one level
		self._members = [[], []]
		self._active = [[], []]

		# assign a basic map manager to the only level
		map_manager = mapmanager.BasicMapManager(mapworld, fps, velocity)
		self._map_managers.append(map_manager)

		# recruit the commander of the random team
		agent_id = 'RS' + str(0)
		commander_member = agent.RandomSeekerCommanderAgent(agent_id, self, self._map_managers[0])
		self._members[1].append(commander_member)
		self._active[1].append(True)

		# recruit agents for the team
		for i in range(self._num_agents - 1):
			agent_id = 'RS' + str(i)
			member = agent.RandomSeekerAgent(agent_id, self, self._map_managers[0])
			self._members[0].append(member)
			self._active[0].append(True)

		# Get the opening positions from the commader member and set each agents
		# position accordingly
		for i in reversed(range(self.ranks)):
			for j in range(self.get_num_rankers(i)):
				position = commander_member.get_opening_position(i, j)
				self._members[i][j].set_position(position)

class BayesianHiderTeam(HiderTeam):

	ranks = 2

	def __init__(self, num_agents, mapworld, fps, velocity):
		super(BayesianHiderTeam, self).__init__(num_agents)

		# prepare a rank 1 hierarchy member list and map managers
		self._map_managers = [] # one map manager for one level
		self._members = [[], []]
		self._active = [[], []]

		# assign a basic map manager to the only level
		map_manager = mapmanager.BasicMapManager(mapworld, fps, velocity)
		self._map_managers.append(map_manager)

		# recruit the commander of the random team
		agent_id = 'RH' + str(0)
		commander_member = agent.RandomSeekerCommanderAgent(agent_id, self, self._map_managers[0])
		self._members[1].append(commander_member)
		self._active[1].append(True)

		# recruit agents for the team
		for i in range(self._num_agents - 1):
			agent_id = 'RH' + str(i)
			member = agent.BayesianHiderAgent(agent_id, self, self._map_managers[0])
			self._members[0].append(member)
			self._active[0].append(True)

		# Get the opening positions from the commader member and set each agents
		# position accordingly
		for i in reversed(range(self.ranks)):
			for j in range(self.get_num_rankers(i)):
				position = commander_member.get_opening_position(i, j)
				self._members[i][j].set_position(position)
