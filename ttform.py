import json	
class TimeTable:
	def __init__(self, subj):
		self.subjs = subj

	def formTT(self):
		tt = []
		slm = 1
		sle = 31
		for i in range(0,5):
			day = []
			for j in range(0,6):
				day.append(slm)
				slm = slm + 1
			for j in range(6,12):
				day.append(sle)
				sle = sle + 1
			tt.append(day)
		subjects = json.loads(self.subjs)
		subjects = subjects['subjects']
		for subject in subjects:
			
			slot = subject['slot']
			cnum = subject['cnum']

			#Deciding whether the given class is a lab or a theory slot 
			if slot[0] != 'L':
				#Deciding whether the slot is morning or evening
				if slot[1] == '1':
					eveshift = 0
				else:
					eveshift = 6

				#Assigning the class numbers to the respective slots in the timetable array
				if slot[0] == 'A' and len(slot) == 2:
					tt[0][0+eveshift] = cnum
					tt[3][1+eveshift] = cnum
				elif slot[0] == 'A' and len(slot) == 6:
					tt[0][0+eveshift] = cnum
					tt[3][1+eveshift] = cnum
					tt[1][3+eveshift] = cnum
				elif slot[0] == 'B' and len(slot) == 2:
					tt[1][0+eveshift] = cnum
					tt[4][1+eveshift] = cnum
				elif slot[0] == 'B' and len(slot) == 6:
					tt[1][0+eveshift] = cnum
					tt[4][1+eveshift] = cnum
					tt[2][3+eveshift] = cnum
				elif slot[0] == 'C' and len(slot) == 2:
					tt[0][2+eveshift] = cnum
					tt[2][0+eveshift] = cnum
					tt[3][3+eveshift] = cnum
				elif slot[0] == 'C' and len(slot) == 6:
					tt[0][2+eveshift] = cnum
					tt[2][0+eveshift] = cnum
					tt[3][3+eveshift] = cnum
					tt[4][4+eveshift] = cnum
				elif slot[0] == 'D' and len(slot) == 2:
					tt[1][2+eveshift] = cnum
					tt[3][0+eveshift] = cnum
					tt[4][3+eveshift] = cnum
				elif slot[0] == 'D' and len(slot) == 6:
					tt[1][2+eveshift] = cnum
					tt[3][0+eveshift] = cnum
					tt[4][3+eveshift] = cnum
					tt[0][4+eveshift] = cnum
				elif slot[0] == 'E' and len(slot) == 2:
					tt[0][3+eveshift] = cnum
					tt[2][2+eveshift] = cnum
					tt[4][0+eveshift] = cnum
				elif slot[0] == 'E' and len(slot) == 6:
					tt[0][3+eveshift] = cnum
					tt[2][2+eveshift] = cnum
					tt[4][0+eveshift] = cnum
					tt[3][4+eveshift] = cnum
				elif slot[0] == 'F' and len(slot) == 2:
					tt[0][1+eveshift] = cnum
					tt[2][1+eveshift] = cnum
					tt[3][2+eveshift] = cnum
				elif slot[0] == 'F' and len(slot) == 6:
					tt[0][1+eveshift] = cnum
					tt[2][1+eveshift] = cnum
					tt[3][2+eveshift] = cnum
					tt[1][4+eveshift] = cnum
				elif slot[0] == 'G' and len(slot) == 2:
					tt[1][1+eveshift] = cnum
					tt[4][2+eveshift] = cnum
				elif slot[0] == 'G' and len(slot) == 6:
					tt[1][1+eveshift] = cnum
					tt[4][2+eveshift] = cnum
					tt[2][4+eveshift] = cnum
			else:
				x = 0
				y = slot.find('L')
				labs = []
				while True:
					x = slot.find('L', y if y != 0 else 1)
					if x != -1:
						labs.append(int(slot[y if y!=0 else 1:x-1]))
						y = x + 1
					else:
						labs.append(int(slot[y if y!=0 else 1:]))
						break
				for lab in labs:
					for i in range(0,5):
						flag = False
						for j in range(0,12):
							if tt[i][j] == lab:
								tt[i][j] = cnum
								flag = True
								break
						if flag == True:
							break
		ttjson = {}
		for i in range(0,5):
			ttj = []
			for j in range(0,12):
				tt[i][j] = tt[i][j] if tt[i][j]>999 else 0
				ttj.append(int(tt[i][j]))
			if i == 0:
				ttjson.update({"Monday":ttj})
			elif i == 1:
				ttjson.update({"Tuesday":ttj})
			elif i == 2:
				ttjson.update({"Wednesday":ttj})
			elif i == 3:
				ttjson.update({"Thursday":ttj})
			elif i == 4:
				ttjson.update({"Friday":ttj})
		return ttjson