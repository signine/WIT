import mapreduce as mr
import simplejson as json
from multiprocessing import freeze_support

def map_func(file):
	with open(file, 'r') as file:
		for line in file:
			data = tuple(json.loads(line))
			yield (data, 1)

def reduce_func(data):
	for d in data:
		yield d[0]

def sort_key_provider(data):
	return (data[2], data[3])

def main():
	bldr = mr.JobBuilder()
	bldr.set_name("Find unique")
	bldr.set_mapper(map_func)
	bldr.set_reducer(reduce_func)
	bldr.set_input_dir("C:\/Users\/shamil\/Desktop\/capstone\/mr_test\/input")
	bldr.set_output_dir("C:\/Users\/shamil\/Desktop\/capstone\/mr_test\/output")
	bldr.set_mapper_count(4)
	bldr.set_reducer_count(1)
	bldr.set_sort_key_provider(sort_key_provider)

	job = bldr.build()

	runner = mr.JobRunner()
	r = runner.run(job)

if __name__ == '__main__':
	freeze_support()
	main()
