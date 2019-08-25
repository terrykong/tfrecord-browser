
from google.protobuf import text_format
from google.protobuf.json_format import MessageToJson, MessageToDict
import tensorflow as tf
from collections import OrderedDict
'''
import tensorflow as tf

for example in tf.python_io.tf_record_iterator("data/foobar.tfrecord"):
    print(tf.train.Example.FromString(example))
'''

import struct
from collections import deque

class bidirectional_tfrecord_iterator:
	def __init__(self, path):
		self.path = path
		self.handle = open(path, 'rb')
		self.pos = 0
		self.record_id = 0
		self.record_offsets = [self.pos]

	def next(self):
		self.pos = orig_pos = self.record_offsets[-1]
		self.handle.seek(self.pos)
		header_str = self.handle.read(8)
		if len(header_str) != 8:
			self.pos = orig_pos
			return None, None
		header = struct.unpack('Q', header_str)
		self.pos += 12  # 8byte header len + 4byte crc
		self.handle.seek(self.pos)

		# Skipping crc header
		# Read the crc32, which is 4 bytes, and check it against the
		# crc32 of the header
		# crc_header_str = buf[n:n+4]
		# crc_header = struct.unpack('I', crc_header_str)
		# n += 4
		# header_crc_calc = masked_crc32c(header_str)
		# assert header_crc_calc == crc_header[0], \
		#     'Header crc\'s dont match'

		header_len = int(header[0])
		message_str = self.handle.read(header_len)
		if len(message_str) != header_len:
			self.pos = orig_pos
			return None, None
		
		self.pos += header_len + 4
		self.handle.seek(self.pos)

		self.record_offsets.append(self.handle.tell())
		self.record_id += 1
		return MessageToDict(tf.train.Example.FromString(message_str))['features']['feature'], header_len

	def prev(self):
		if len(self.record_offsets) == 1:
			return None, None
		self.record_offsets.pop()
		self.pos = self.record_offsets[-1]
		self.handle.seek(self.pos)

		orig_pos = self.pos
		header_str = self.handle.read(8)
		header = struct.unpack('Q', header_str)
		self.pos += 12  # 8byte header len + 4byte crc
		self.handle.seek(self.pos)

		header_len = int(header[0])
		message_str = self.handle.read(header_len)
		
		self.pos += header_len + 4
		self.handle.seek(self.pos)
		
		self.record_id -= 1
		return MessageToDict(tf.train.Example.FromString(message_str))['features']['feature'], header_len

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.handle.close()

class smart_bidirectional_tfrecord_iterator(bidirectional_tfrecord_iterator):
    def __init__(self, path):
        super(smart_bidirectional_tfrecord_iterator, self).__init__(path)

    def _parse_features(self, example):
        result = OrderedDict()
        for feature_name,v in sorted(example.items(), key=lambda x: x[0]):
            assert len(v) == 1
            feature_type = list(v.keys())[0]
            feature_value = v[feature_type]['value']
            if feature_type in ('int64List','floatList'):
                result[feature_name] = feature_value
            elif feature_type == 'bytesList':
                result[feature_name] = feature_value
                #if len(feature_value) > 1:
                #    # very likely this is a list of strings
                #    result[feature_name] = feature_value
                #else:
                #    # either this is a tensor or a list of a single string
                #    result[feature_name] = tf.io.parse_tensor(tf.convert_to_tensor(feature_value[0]), tf.float32)
            else:
                pass
        return result

    def next(self):
        example, bytes = super(smart_bidirectional_tfrecord_iterator, self).next()
        return self._parse_features(example), bytes

    def prev(self):
        example, bytes = super(smart_bidirectional_tfrecord_iterator, self).prev()
        return self._parse_features(example), bytes


class tfrecord_iterator:

    def __init__(self, path):
        self.dataset = tf.data.TFRecordDataset(path)
        self.iterator = iter(self.dataset)

    def next(self):
        try:
            example = tf.train.Example.FromString(next(self.iterator).numpy())
        #except tf.errors.OutOfRangeError:
        except StopIteration:
            return None, None
        result = OrderedDict()
        for k,v in example.features.feature.items():
            if v.int64_list.value:
                result[k] = v.int64_list.value
            elif v.float_list.value:
                result[k] = v.float_list.value
            elif v.bytes_list.value:
                #result[k] = v.bytes_list.value
                try:
                    result[k] = tf.io.parse_tensor(v.bytes_list.value[0],tf.float32)
                except:
                    result[k] = v.bytes_list.value
            else:
                raise ValueError('Unrecognized type')
        return result, None

#for example in tf.python_io.tf_record_iterator("test0.tfrecord"):
#	print(list(MessageToDict(tf.train.Example.FromString(example)).keys()))
#	break

##with bidirectional_tfrecord_iterator('test0.tfrecord') as iter:
##	print('read forward----')
##	record, bytes = iter.next()
##	print(iter.record_id-1 ,bytes, iter.record_offsets)
##	record, bytes = iter.next()
##	print(iter.record_id-1 ,bytes, iter.record_offsets)
##	record, bytes = iter.next()
##	print(iter.record_id-1 ,bytes, iter.record_offsets)
##
##
##	print('read backward----')
##	record, bytes = iter.prev()
##	print(iter.record_id-1 ,bytes, iter.record_offsets)
##	record, bytes = iter.prev()
##	print(iter.record_id-1 ,bytes, iter.record_offsets)
##	record, bytes = iter.prev()
##	print(iter.record_id-1 ,bytes, iter.record_offsets)
##	record, bytes = iter.prev()
##	print(iter.record_id-1 ,bytes, iter.record_offsets)
##
##
##	print('read forward----')
##	record, bytes = iter.next()
##	print(iter.record_id-1 ,bytes, iter.record_offsets)
##	record, bytes = iter.next()
##	print(iter.record_id-1 ,bytes, iter.record_offsets)
##	record, bytes = iter.next()
##	print(iter.record_id-1 ,bytes, iter.record_offsets)
##
##with bidirectional_tfrecord_iterator('test0.tfrecord') as iter:
##    record, bytes = iter.next()
##    print(record)
##
##with smart_bidirectional_tfrecord_iterator('test0.tfrecord') as iter:
##    record, bytes = iter.next()
##    print(record)
