import mapreduce as mr
import simplejson as json
from multiprocessing import freeze_support

def map_func(file):
	with open(file, 'r') as file:
		for line in file:
			data = tuple(json.loads(line))
			yield ((data[2], data[3]), 1)

def reduce_func(data):
	data = map(lambda x: (x[0], sum(x[1])), data)
	for d in sorted(data, key=lambda x: x[1]):
		yield d

def main():
	bldr = mr.JobBuilder()
	bldr.set_name("Histogram")
	bldr.set_mapper(map_func)
	bldr.set_reducer(reduce_func)
	bldr.set_input_dir("C:\/Users\/shamil\/Desktop\/capstone\/mr_test\/output")
	bldr.set_output_dir("C:\/Users\/shamil\/Desktop\/capstone\/mr_test\/")
	bldr.set_mapper_count(4)
	bldr.set_reducer_count(1)

	job = bldr.build()

	runner = mr.JobRunner()
	r = runner.run(job)

if __name__ == '__main__':
	freeze_support()
	main()
